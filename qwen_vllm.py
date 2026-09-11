"""Prepare, launch, collect or stop one bounded cloud-owned Qwen experiment."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import time

from dotenv import load_dotenv
from checkpoint_io import save, exclusive
from modal_pilot_core import digest
import longmemeval_eval as ev
from beam_final_inputs import inputs, ROOT
from beam_baseline_answers import Answers

DIRECTORY = ROOT/'work/qwen_beam_vllm'
VOLUME = 'adaption-qwen-experiments-v2'
CACHE = 'adaption-qwen-cache-v2'
RATE = .000542 + 4*.00003942 + 32*.00000667
CODE = ('qwen_vllm.py','qwen_vllm_worker.py','beam_final_inputs.py','checkpoint_io.py','memory.py','modal_pilot_core.py','beam_baseline_answers.py')


def now():
    return datetime.now(timezone.utc).isoformat()


def prepare(directory, smoke, concurrency, structured):
    payload, grouped, settings = inputs()
    payload.update(concurrency=concurrency, structured_output=structured,
        updates_per_history=2 if smoke else None, experiment='vllm-0.21.0',
        precision='bfloat16', code_sha256={p:ev.sha256_file(ROOT/p) for p in CODE})
    if smoke:
        payload['histories'] = payload['histories'][:2]
    payload['fingerprint'] = digest(payload)
    config = dict(payload=payload, settings=settings, scope='smoke' if smoke else 'BEAM final 90',
        historical_run='work/qwen_beam_baseline', no_checkpoint_import=True)
    path = directory/'configuration.json'
    if path.exists():
        if json.loads(path.read_text()) != config:
            raise ValueError('Prepared run differs; select a new directory')
    else:
        save(path, config)
        save(directory/'payload.json', payload)
    return config


def cloud():
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    import modal
    return modal, modal.Volume.from_name(VOLUME, create_if_missing=True, version=2)


def launch(directory, budget):
    if not math.isfinite(budget) or not 0 < budget <= 10:
        raise ValueError('Explicit budget must be in (0, 10]')
    config = json.loads((directory/'configuration.json').read_text())
    for name, sha in config['payload']['code_sha256'].items():
        if ev.sha256_file(ROOT/name) != sha:
            raise ValueError('Code changed after preparation')
    ledger = directory/'cloud.json'
    if ledger.exists():
        raise ValueError('Run already launched; collect or reconcile, never blindly replace')
    # Previous baseline allocations remain charged across the new execution variant.
    prior = sum(a.get('accounted_usd',a['reserved_usd']) for a in json.loads(
        (ROOT/'work/qwen_beam_baseline/modal_attempts.json').read_text()))
    other = 0
    for path in (ROOT/'work').glob('*/cloud.json'):
        r = json.loads(path.read_text())
        if r.get('runner') == 'qwen_vllm':
            other += r.get('accounted_usd',r['reserved_usd'])
    if prior+other+budget > 10:
        raise ValueError(f'Baseline allocation exceeded: prior {prior+other:.4f} plus requested {budget}')
    timeout = min(7200, int((budget-.50)/RATE))
    if timeout < 300:
        raise ValueError('Budget insufficient for startup and validation')
    modal, volume = cloud()
    run_id = 'qwen-'+config['payload']['fingerprint'][:16]
    record = dict(runner='qwen_vllm', run_id=run_id, status='building', started_at=now(),
        reserved_usd=budget, prior_accounted_usd=prior+other, timeout_seconds=timeout,
        rate_usd_s=RATE, actual_invoice_cost_usd=None)
    save(ledger, record)
    app = modal.App.lookup('adaption-qwen-vllm', create_if_missing=True)
    # Build dependencies before allocating a GPU. The image and both caches are reusable.
    image = (modal.Image.from_registry('nvidia/cuda:12.9.0-devel-ubuntu22.04', add_python='3.12')
        .entrypoint([]).uv_pip_install('vllm==0.21.0')
        .env({'HF_HOME':'/cache/huggingface','VLLM_CACHE_ROOT':'/cache/vllm'}))
    for name in ('qwen_vllm_worker.py','checkpoint_io.py','memory.py','modal_pilot_core.py'):
        image = image.add_local_file(ROOT/name, '/app/'+name, copy=True)
    try:
        image = image.build(app)
        record['image_id'] = image.object_id
        with volume.batch_upload() as batch:
            batch.put_file(directory/'payload.json', f'/{run_id}/payload.json')
        cache = modal.Volume.from_name(CACHE, create_if_missing=True, version=2)
        record.update(status='creating', gpu_started_at=now())
        save(ledger, record)
        sb = modal.Sandbox.create('python','-u','/app/qwen_vllm_worker.py',f'/state/{run_id}/payload.json',
            app=app, name=run_id, image=image, gpu='L40S', cpu=(4,4), memory=(32768,32768),
            volumes={'/state':volume, '/cache':cache}, timeout=timeout)
        record.update(status='running', sandbox_id=sb.object_id)
        save(ledger, record)
        print(json.dumps(record, indent=2))
    except BaseException as error:
        record.update(status='launch_failed', error_type=type(error).__name__)
        save(ledger, record)
        raise


def volume_json(volume, path):
    try:
        return json.loads(b''.join(volume.read_file(path)))
    except FileNotFoundError:
        return None


def collect(directory, watch, evaluate):
    from openai import OpenAI
    modal, volume = cloud()
    config = json.loads((directory/'configuration.json').read_text())
    ledger = directory/'cloud.json'
    record = json.loads(ledger.read_text())
    if not record.get('sandbox_id'):
        raise ValueError('Launch outcome unresolved; inspect ledger before retry')
    _, grouped, _ = inputs()
    payload = config['payload']
    if evaluate and float(os.environ.get('SPENDING_LIMIT_USD','0')) < 30:
        raise ValueError('Requires the authorized combined $30 OpenAI cap')
    prior_api = [json.loads(p.read_text()) for p in (ROOT/'work/qwen_beam_baseline/api_calls').glob('*.json')]
    remaining_api = 20-sum(c.get('accounted_usd',c['reserved_usd']) for c in prior_api)
    answers = Answers(directory, OpenAI(max_retries=0, timeout=180), config['settings'], remaining_api) if evaluate else None
    if evaluate and config['scope'] != 'BEAM final 90':
        raise ValueError('Smoke memories must never answer final questions')
    futures = {}; seen = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        while True:
            sb = modal.Sandbox.from_id(record['sandbox_id'])
            stopped = sb.poll() is not None
            for row in payload['histories']:
                key = row['history_sha256']
                progress = volume_json(volume, f"{record['run_id']}/progress/{key}.json")
                if progress and seen.get(key) != progress:
                    state = volume_json(volume, f"{record['run_id']}/memories/{key}.json")
                    if state['payload_sha256'] != payload['fingerprint']:
                        raise ValueError('Cloud checkpoint fingerprint mismatch')
                    save(directory/'memories'/f'{key}.json', state)
                    seen[key] = progress
                    if answers and state['status'] == 'complete':
                        for item in grouped[key]:
                            if item['question_id'] not in futures:
                                futures[item['question_id']] = pool.submit(answers.evaluate, item, state)
            for name in ('loaded','finished','fatal'):
                data = volume_json(volume, f"{record['run_id']}/{name}.json")
                if data is not None:
                    save(directory/f'{name}.json', data)
            if stopped:
                elapsed = (datetime.now(timezone.utc)-datetime.fromisoformat(record['gpu_started_at'])).total_seconds()
                record.update(status='stopped', termination='confirmed', finished_at=now(),
                    accounted_usd=min(record['reserved_usd'],record.get('prior_run_accounted_usd',0)+elapsed*record['rate_usd_s']+.50))
                save(ledger, record)
            if stopped or not watch:
                break
            time.sleep(15)
        for future in futures.values():
            future.result()
    expected = [r['question_id'] for rows in grouped.values() for r in rows]
    results = [json.loads(p.read_text()) for p in (directory/'results').glob('*.json')]
    valid = [r['question_id'] for r in results if r['status']=='success']
    save(directory/'summary.json', dict(expected=90, valid=len(valid), missing=sorted(set(expected)-{r['question_id'] for r in results}),
        failed=[r['question_id'] for r in results if r['status']!='success'], complete=len(valid)==90,
        scope=config['scope']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','launch','collect','stop'])
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--concurrency', type=int, choices=[1,2,4], default=2)
    parser.add_argument('--unconstrained', action='store_true')
    parser.add_argument('--budget-usd', type=float)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    load_dotenv(ROOT/'.env', override=False)
    if args.command == 'stop':
        modal, _ = cloud()
        record = json.loads((args.directory/'cloud.json').read_text())
        modal.Sandbox.from_id(record['sandbox_id']).terminate()
        print('Sandbox termination confirmed. Collect final checkpoints separately.')
        raise SystemExit(0)
    with exclusive(args.directory):
        if args.command == 'prepare':
            prepare(args.directory, args.smoke, args.concurrency, not args.unconstrained)
            print('Prepared only; no cloud resources created.')
        elif args.command == 'launch':
            if args.budget_usd is None:
                parser.error('--budget-usd required')
            launch(args.directory,args.budget_usd)
        elif args.command == 'collect':
            collect(args.directory,args.watch,args.evaluate)
