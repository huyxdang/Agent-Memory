"""Prepare, launch, collect or stop one bounded cloud-owned Qwen experiment."""
import argparse
import copy
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
from longmemeval_qwen_inputs import inputs as longmemeval_inputs
from locomo_qwen_inputs import inputs as locomo_inputs
from third_party.mem0 import locomo_prompts

DIRECTORY = ROOT/'work/qwen_beam_vllm'
VOLUME = 'adaption-qwen-experiments-v2'
CACHE = 'adaption-qwen-cache-v2'
RATE = .000542 + 4*.00003942 + 32*.00000667
CODE = ('qwen_vllm.py','qwen_vllm_worker.py','beam_final_inputs.py','longmemeval_qwen_inputs.py','locomo_qwen_inputs.py','benchmarks.py','third_party/mem0/locomo_prompts.py','longmemeval_eval.py','checkpoint_io.py','memory.py','modal_pilot_core.py','beam_baseline_answers.py')


def now():
    return datetime.now(timezone.utc).isoformat()


def prepare(directory, smoke, concurrency, structured, benchmark='beam', pilot_histories=None, reuse_from=None):
    if pilot_histories is not None and (smoke or pilot_histories < 1 or benchmark=='beam'):
        raise ValueError('Full-history pilots require LoCoMo/LongMemEval and cannot use --smoke')
    if benchmark not in ('beam','longmemeval','locomo') or concurrency not in (1,2,4,8,16):
        raise ValueError('Unsupported benchmark or concurrency')
    if benchmark == 'beam' and concurrency > 4:
        raise ValueError('BEAM concurrency remains limited to the existing settings')
    loader = {'beam':inputs,'longmemeval':longmemeval_inputs,'locomo':locomo_inputs}[benchmark]
    payload, grouped, settings = loader()
    payload.update(concurrency=concurrency, structured_output=structured,
        updates_per_history=2 if smoke else None, experiment='vllm-0.21.0',
        precision='bfloat16', code_sha256={p:ev.sha256_file(ROOT/p) for p in CODE})
    if smoke:
        payload['histories'] = payload['histories'][:{'beam':2,'longmemeval':16,'locomo':10}[benchmark]]
    if pilot_histories is not None:
        if pilot_histories >= len(payload['histories']):
            raise ValueError('Pilot must be smaller than the final set')
        payload['histories'] = payload['histories'][:pilot_histories]
    grouped = {r['history_sha256']:grouped[r['history_sha256']] for r in payload['histories']}
    payload['fingerprint'] = digest(payload)
    config = dict(payload=payload, settings=settings, scope='smoke' if smoke else
        {'beam':'BEAM final 90','longmemeval':'LongMemEval final 100','locomo':'LoCoMo final 50'}[benchmark],
        historical_run='work/qwen_beam_baseline', no_checkpoint_import=True)
    if benchmark in ('longmemeval','locomo'):
        config.update(benchmark=benchmark, questions=grouped, historical_run=None,
            mem0_revision=ev.MEM0_CODE_REVISION,
            judge_prompt=locomo_prompts.JUDGE_PROMPT if benchmark=='locomo' else ev.JUDGE_PROMPT)
        if benchmark == 'locomo':
            config['judge_system_prompt'] = locomo_prompts.JUDGE_SYSTEM_PROMPT
    if pilot_histories is not None:
        config['scope'] = f'{benchmark} full-history pilot {pilot_histories}'
    if reuse_from is not None:
        config['checkpoint_import'] = import_completed(reuse_from, directory, config)
        config['no_checkpoint_import'] = False
    path = directory/'configuration.json'
    if path.exists():
        if json.loads(path.read_text()) != config:
            raise ValueError('Prepared run differs; select a new directory')
    else:
        save(path, config)
        save(directory/'payload.json', payload)
    return config


def import_completed(source, directory, config):
    if source.resolve()==directory.resolve():
        raise ValueError('Import requires separate run directories')
    old=json.loads((source/'configuration.json').read_text())
    if old.get('benchmark')!=config.get('benchmark') or old['settings']!=config['settings']:
        raise ValueError('Imported model/benchmark settings differ')
    def invariant(payload):
        result={k:v for k,v in payload.items() if k not in ('histories','fingerprint')}
        result['code_sha256']={k:v for k,v in payload['code_sha256'].items() if k!='qwen_vllm.py'}
        return result
    if invariant(old['payload'])!=invariant(config['payload']):
        raise ValueError('Imported extraction configuration differs')
    old_rows={r['history_sha256']:r for r in old['payload']['histories']}
    imported={}
    for row in config['payload']['histories']:
        key=row['history_sha256']
        if key not in old_rows:continue
        if row!=old_rows[key]:raise ValueError('Imported source history changed')
        state=json.loads((source/'memories'/f'{key}.json').read_text())
        if (state['payload_sha256']!=old['payload']['fingerprint'] or state['status']!='complete'
            or state['sessions_done']!=len(row['history']) or any(c['status']!='complete' for c in state['calls'])):
            raise ValueError('Only complete, certain histories may be imported')
        state=copy.deepcopy(state)
        state['payload_sha256']=config['payload']['fingerprint']
        path=directory/'memories'/f'{key}.json'
        save(path,state)
        save(directory/'progress'/path.name,dict(status='complete',sessions_done=state['sessions_done']))
        imported[key]=ev.sha256_file(path)
    if not imported:raise ValueError('No complete histories to import')
    return dict(source_directory=str(source.resolve()), source_fingerprint=old['payload']['fingerprint'],
        state_sha256=imported, source_code_sha256=old['payload']['code_sha256'],
        note='Completed pilot extraction reused; orchestration code may differ, all worker/prompt/model hashes must match. Answering calls remain separately accounted in source.')


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
    cap=10
    if config.get('benchmark') in ('locomo','longmemeval'):
        # New user-authorized final evaluations share the original $30 total.
        # Reserve full earlier $2 limits for both pilots and the sizing study.
        prior += 6
        cap=30
    if prior+other+budget > cap:
        raise ValueError(f'Baseline allocation exceeded: prior {prior+other:.4f} plus requested {budget}')
    timeout = min(7200, int((budget-.50)/RATE))
    if timeout < 300:
        raise ValueError('Budget insufficient for startup and validation')
    modal, volume = cloud()
    run_id = 'qwen-'+config['payload']['fingerprint'][:16]
    record = dict(runner='qwen_vllm', run_id=run_id, status='building', started_at=now(),
        reserved_usd=budget, prior_accounted_usd=prior+other, timeout_seconds=timeout,
        rate_usd_s=RATE, actual_invoice_cost_usd=None, total_allocation_usd=cap)
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
            imported = config.get('checkpoint_import',{}).get('state_sha256',{})
            for key, sha in imported.items():
                path = directory/'memories'/f'{key}.json'
                if ev.sha256_file(path) != sha:
                    raise ValueError('Imported checkpoint changed before launch')
                batch.put_file(path, f'/{run_id}/memories/{key}.json')
                batch.put_file(directory/'progress'/f'{key}.json', f'/{run_id}/progress/{key}.json')
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
    for attempt in range(3):
        try:
            return json.loads(b''.join(volume.read_file(path)).decode('utf-8'))
        except FileNotFoundError:
            return None
        except (UnicodeError,json.JSONDecodeError):
            if attempt==2:raise
            print(f'Incomplete checkpoint download; retry {attempt+1}/2: {path}',flush=True)
            time.sleep(attempt+1)


def prior_api_cost(directory):
    calls={}
    for path in (ROOT/'work').glob('*/api_calls/*.json'):
        if path.parent.parent.resolve()==directory.resolve():continue
        call=json.loads(path.read_text())
        identity=call.get('response',{}).get('response_id') or str(path.resolve())
        calls[identity]=max(calls.get(identity,0),call.get('accounted_usd',call['reserved_usd']))
    return sum(calls.values())


def collect(directory, watch, evaluate):
    collection_started = time.monotonic()
    from openai import OpenAI
    modal, volume = cloud()
    config = json.loads((directory/'configuration.json').read_text())
    ledger = directory/'cloud.json'
    record = json.loads(ledger.read_text())
    if not record.get('sandbox_id'):
        raise ValueError('Launch outcome unresolved; inspect ledger before retry')
    benchmark = config.get('benchmark','beam')
    if benchmark in ('longmemeval','locomo'):
        grouped = config['questions']
    else:
        _, grouped, _ = inputs()
    payload = config['payload']
    if evaluate and float(os.environ.get('SPENDING_LIMIT_USD','0')) < 30:
        raise ValueError('Requires the authorized combined $30 OpenAI cap')
    remaining_api = 20-prior_api_cost(directory)
    answers = Answers(directory, OpenAI(max_retries=0, timeout=180), config['settings'], remaining_api,
        benchmark=benchmark) if evaluate else None
    if evaluate and config['scope'] == 'smoke':
        raise ValueError('Smoke memories must never answer final questions')
    futures = {}; seen = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        while True:
            sb = modal.Sandbox.from_id(record['sandbox_id'])
            stopped = sb.poll() is not None
            for row in payload['histories']:
                key = row['history_sha256']
                progress = volume_json(volume, f"{record['run_id']}/progress/{key}.json")
                changed = progress and seen.get(key) != progress
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
                if progress and (changed or progress.get('last_call_status')=='in_flight'):
                    state=json.loads((directory/'memories'/f'{key}.json').read_text())
                    stream_key=state['calls'][-1].get('stream_key') if state['calls'] else None
                    if stream_key:
                        diagnostic=volume_json(volume,f"{record['run_id']}/streams/{stream_key}.json")
                        if diagnostic is not None:save(directory/'streams'/f'{stream_key}.json',diagnostic)
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
    summary = summarize(directory, grouped, config['scope'])
    summary.update(collection_elapsed_seconds=time.monotonic()-collection_started,
        checked_at=now(), pipeline_started_at=record.get('started_at'))
    if summary['complete'] and record.get('started_at'):
        summary['pipeline_elapsed_seconds'] = (datetime.now(timezone.utc)-datetime.fromisoformat(record['started_at'])).total_seconds()
        summary['timing_note'] = 'Launch through this collection finalization; includes startup and offline collector gaps. Not a sum of overlapping calls.'
    save(directory/'summary.json',summary)


def summarize(directory, grouped, scope):
    expected = [r['question_id'] for rows in grouped.values() for r in rows]
    if len(expected) != len(set(expected)):
        raise ValueError('Duplicate expected questions')
    results = [json.loads(p.read_text()) for p in (directory/'results').glob('*.json')]
    ids = [r['question_id'] for r in results]
    valid = [r['question_id'] for r in results if r['status']=='success' and r['question_id'] in expected]
    missing = sorted(set(expected)-set(ids))
    unexpected = sorted(set(ids)-set(expected))
    duplicates = sorted({qid for qid in ids if ids.count(qid)>1})
    failed = [r['question_id'] for r in results if r['status']!='success']
    summary = dict(expected=len(expected), valid=len(valid), missing=missing, unexpected=unexpected,
        duplicates=duplicates, failed=failed, complete=not (missing or unexpected or duplicates or failed), scope=scope)
    save(directory/'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','launch','collect','stop'])
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--benchmark', choices=['beam','longmemeval','locomo'], default='beam')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--pilot-histories', type=int)
    parser.add_argument('--reuse-from', type=Path)
    parser.add_argument('--concurrency', type=int, choices=[1,2,4,8,16], default=2)
    parser.add_argument('--unconstrained', action='store_true')
    parser.add_argument('--budget-usd', type=float)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    if args.directory is None:
        args.directory = ROOT/f'work/qwen_{args.benchmark}_vllm'
    load_dotenv(ROOT/'.env', override=False)
    if args.command == 'stop':
        modal, _ = cloud()
        record = json.loads((args.directory/'cloud.json').read_text())
        modal.Sandbox.from_id(record['sandbox_id']).terminate()
        print('Sandbox termination confirmed. Collect final checkpoints separately.')
        raise SystemExit(0)
    with exclusive(args.directory):
        if args.command == 'prepare':
            prepare(args.directory, args.smoke, args.concurrency, not args.unconstrained, args.benchmark,
                args.pilot_histories,args.reuse_from)
            print('Prepared only; no cloud resources created.')
        elif args.command == 'launch':
            if args.budget_usd is None:
                parser.error('--budget-usd required')
            launch(args.directory,args.budget_usd)
        elif args.command == 'collect':
            collect(args.directory,args.watch,args.evaluate)
