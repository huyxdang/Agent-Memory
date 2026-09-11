"""Bounded L40S sizing: identical prompts, sequential versus a two-row batch."""
import argparse
import gc
import json
import os
import time
from pathlib import Path

from modal_pilot_core import digest, output_valid, prompt_ids, validate_payload

ROOT = Path(__file__).resolve().parent
RATE = .000542 + 2 * .00003942 + 32 * .00000667
TIMEOUT = 1200
RESERVE = .50


def trim_output(tokens, eos):
    for index, token in enumerate(tokens):
        if token in eos:
            return tokens[:index + 1], 'stop'
    return tokens, 'length'


def left_pad(rows, pad):
    width = max(map(len, rows))
    return ([[pad] * (width - len(row)) + row for row in rows],
            [[0] * (width - len(row)) + [1] * len(row) for row in rows])


def emit(event):
    print('SIZING_EVENT ' + json.dumps(event), flush=True)


def worker(payload):
    import torch
    from transformers import AutoModelForImageTextToText, AutoTokenizer
    import importlib.metadata
    validate_payload(payload)
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(payload['model'], revision=payload['revision'])
    rows = payload['examples']
    ids = [prompt_ids(tokenizer, row['messages']) for row in rows]
    for row, tokens in zip(rows, ids):
        if len(tokens) != row['input_tokens'] or len(tokens) + payload['max_output_tokens'] > payload['context_window']:
            raise ValueError('Prompt mismatch or overflow; refusing truncation')
    model = AutoModelForImageTextToText.from_pretrained(payload['model'], revision=payload['revision'],
        dtype=torch.bfloat16, device_map='cuda', attn_implementation='sdpa').eval()
    eos = model.generation_config.eos_token_id
    eos = eos if isinstance(eos, list) else [eos]
    emit({'event': 'loaded', 'load_seconds': time.monotonic() - started,
          'gpu': torch.cuda.get_device_name(), 'gpu_total_bytes': torch.cuda.get_device_properties(0).total_memory,
          'versions': {p: importlib.metadata.version(p) for p in ('torch', 'transformers', 'accelerate')},
          'precision': 'bfloat16', 'thinking': False})
    # Two repetitions expose warm-up/order effects without changing the workload.
    for trial, mode, indexes in [(1, 'single', [0]), (1, 'single', [1]), (1, 'batch', [0, 1]),
                                  (2, 'batch', [0, 1]), (2, 'single', [0]), (2, 'single', [1])]:
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        event = {'event': 'measurement', 'trial': trial, 'mode': mode, 'indexes': indexes, 'status': 'error'}
        try:
            padded, masks = left_pad([ids[i] for i in indexes], tokenizer.eos_token_id)
            inputs = torch.tensor(padded, device='cuda')
            attention = torch.tensor(masks, device='cuda')
            with torch.inference_mode():
                generated = model.generate(input_ids=inputs, attention_mask=attention,
                    max_new_tokens=payload['max_output_tokens'], do_sample=False,
                    pad_token_id=tokenizer.eos_token_id)
            torch.cuda.synchronize()
            event['inference_seconds'] = time.monotonic() - started
            outputs = []
            for index, sequence in zip(indexes, generated):
                tokens, finish = trim_output(sequence[inputs.shape[1]:].tolist(), eos)
                text = tokenizer.decode(tokens, skip_special_tokens=True)
                outputs.append({'example_id': rows[index]['example_id'], 'input_tokens': len(ids[index]),
                    'output_tokens': len(tokens), 'finish_reason': finish, 'valid_json': output_valid(text),
                    'output': text, 'source_fidelity': 'not_graded'})
            event.update(status='ok', outputs=outputs, padded_input_tokens=sum(map(len, padded)))
            del inputs, attention, generated
        except torch.OutOfMemoryError:
            event.update(status='out_of_memory', inference_seconds=time.monotonic() - started)
        event.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                     peak_reserved_bytes=torch.cuda.max_memory_reserved())
        emit(event)


def execute(retry_setup_failure=False):
    import certifi
    # Python.org macOS builds may have no default CA bundle. Keep TLS verification on.
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    import modal
    from checkpoint_io import exclusive, save
    from modal_pilot import REMOTE_PACKAGES, now
    import longmemeval_eval as ev
    directory = ROOT / 'work/qwen_gpu_sizing_l40s'
    with exclusive(directory):
        ledger = directory / 'run.json'
        previous_attempts = []
        if ledger.exists():
            previous = json.loads(ledger.read_text())
            if not (retry_setup_failure and previous['status'] == 'failed'
                    and previous.get('error_type') == 'SSLCertVerificationError'
                    and previous.get('termination') == 'confirmed'
                    and not (directory/'events.jsonl').exists()):
                raise ValueError('Sizing already attempted; reconcile before spending again')
            previous_attempts = previous.get('previous_attempts', []) + [
                {k: v for k, v in previous.items() if k != 'previous_attempts'}]
        prior_accounted = sum(r['resource_estimate_usd'] + RESERVE for r in previous_attempts)
        timeout = min(TIMEOUT, int((2 - prior_accounted - RESERVE) / RATE))
        if timeout < 600:
            raise ValueError('Insufficient sizing budget for a replacement attempt')
        payload = json.loads((ROOT / 'work/modal_qwen_pilot_new_account/payload.json').read_text())
        validate_payload(payload)
        if len({r['history_sha256'] for r in payload['examples']}) != 2:
            raise ValueError('Batch needs independent histories')
        if TIMEOUT * RATE + RESERVE > 2:
            raise ValueError('Sizing envelope exceeds $2')
        modal.Client.from_env()
        save(directory / 'payload.json', payload)
        run = {'status': 'starting', 'started_at': now(), 'gpu': 'L40S',
               'payload_sha256': digest(payload), 'limit_usd': 2, 'timeout_seconds': timeout,
               'resource_rate_usd_s': RATE, 'reserved_usd': timeout * RATE + RESERVE,
               'previous_attempts': previous_attempts, 'prior_accounted_usd': prior_accounted,
               'pricing_source': 'https://modal.com/pricing', 'pricing_checked': '2026-09-11',
               'actual_invoice_cost_usd': None, 'code': ev.git_metadata(),
               'code_sha256': {p: ev.sha256_file(ROOT / p) for p in ('qwen_gpu_sizing.py', 'modal_pilot_core.py')},
               'scope': 'Hardware microbenchmark on frozen pilot prompts, not BEAM accuracy',
               'prior_baseline_ledger': 'work/qwen_beam_baseline/modal_attempts.json'}
        save(ledger, run)
        sb = None
        started = time.monotonic()
        try:
            app = modal.App.lookup('adaption-extractor-pilot', create_if_missing=True)
            sb = modal.Sandbox.create(app=app, image=modal.Image.debian_slim(python_version='3.12'),
                gpu='L40S', cpu=(2, 2), memory=(32768, 32768), timeout=timeout)
            run.update(status='installing', sandbox_id=sb.object_id)
            save(ledger, run)
            for local, remote in [(directory / 'payload.json', '/sizing/payload.json'),
                    (ROOT / 'qwen_gpu_sizing.py', '/sizing/qwen_gpu_sizing.py'),
                    (ROOT / 'modal_pilot_core.py', '/sizing/modal_pilot_core.py')]:
                sb.filesystem.copy_from_local(local, remote)
            setup = sb.exec('python', '-m', 'pip', 'install', *REMOTE_PACKAGES, timeout=600)
            with (directory / 'setup.log').open('w') as log:
                log.write(setup.stdout.read()); log.write(setup.stderr.read())
            setup.wait()
            if setup.returncode:
                raise RuntimeError('Dependency installation failed')
            run['status'] = 'measuring'
            save(ledger, run)
            process = sb.exec('python', '-u', '/sizing/qwen_gpu_sizing.py', '--worker', timeout=timeout)
            count = 0
            with (directory / 'events.jsonl').open('x') as stream:
                for line in process.stdout:
                    if line.startswith('SIZING_EVENT '):
                        event = json.loads(line[len('SIZING_EVENT '):])
                        stream.write(json.dumps(event) + '\n'); stream.flush()
                        count += event['event'] == 'measurement'
                        print(json.dumps({k: v for k, v in event.items() if k != 'outputs'}), flush=True)
            with (directory / 'worker.log').open('w') as log:
                log.write(process.stderr.read())
            process.wait()
            run.update(worker_exit_code=process.returncode, measurements=count,
                       status='complete' if process.returncode == 0 and count == 6 else 'incomplete')
        except BaseException as error:
            run.update(status='failed', error_type=type(error).__name__)
            raise
        finally:
            if sb is not None:
                try:
                    sb.terminate()
                    run['termination'] = 'confirmed'
                except Exception as error:
                    run.update(termination='unconfirmed', termination_error=type(error).__name__)
            elapsed = time.monotonic() - started
            run.update(finished_at=now(), elapsed_seconds=elapsed,
                       resource_estimate_usd=min(elapsed, timeout) * RATE)
            save(ledger, run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--retry-setup-failure', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(json.loads(Path('/sizing/payload.json').read_text()))
    else:
        execute(args.retry_setup_failure)
