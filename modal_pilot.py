"""Prepare locally; explicitly invoke one bounded Modal GPU sandbox."""
import argparse
import importlib.metadata
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import longmemeval_eval as ev
from modal_pilot_core import (MODEL,GPU,CONTEXT,MAX_OUTPUT,budget_plan,select_examples,
                              validate_payload,account_results,digest)

ROOT=Path(__file__).resolve().parent
DEFAULT_SOURCE=ROOT/'work/training_copies_v1/copy_1_original/train.jsonl'
REMOTE_PACKAGES=('torch==2.14.0','transformers==5.17.0','accelerate==1.15.0','jinja2==3.1.6')


def now():
    return datetime.now(timezone.utc).isoformat()


def prepare(source, destination):
    if destination.exists():
        raise ValueError('Refusing to overwrite prepared pilot')
    from huggingface_hub import HfApi
    from transformers import AutoTokenizer
    revision=HfApi().model_info(MODEL).sha
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=revision)
    with source.open() as stream:
        examples,count=select_examples((json.loads(line) for line in stream),tokenizer)
    payload={'model':MODEL,'revision':revision,'context_window':CONTEXT,'max_output_tokens':MAX_OUTPUT,
             'examples':examples}
    destination.mkdir(parents=True)
    ev.atomic_json(destination/'payload.json',payload)
    report={'source':str(source),'source_sha256':ev.sha256_file(source),'source_rows':count,
        'selection':'lower median and maximum of exact Qwen chat-template input token counts; stable ID ties',
        'pilot_scope':'Teacher-forced extractor calls, not student memory rollout or benchmark accuracy',
        'tokenizer_version':importlib.metadata.version('transformers'),
        'examples':[{k:v for k,v in r.items() if k!='messages'} for r in examples],
        'budget':budget_plan(2),'status':'prepared'}
    try:
        validate_payload(payload)
    except ValueError as error:
        report.update(status='preflight_failed',error=str(error))
    ev.atomic_json(destination/'preflight.json',report)
    print(json.dumps(report,indent=2))


def execute(prepared, limit):
    import modal
    payload=json.loads((prepared/'payload.json').read_text())
    validate_payload(payload)
    budget=budget_plan(limit)
    ledger=prepared/'run.json'
    # One execution per prepared pilot: retries require explicit reconciliation.
    if ledger.exists():
        raise ValueError('Run already attempted; reconcile its cost before any new run')
    modal.Client.from_env()  # authenticate before creating resources
    run={'run_id':now().replace(':','-'),'status':'starting','started_at':now(),
         'payload_sha256':digest(payload),'budget':budget,'code':ev.git_metadata(),
         'code_sha256':{p:ev.sha256_file(ROOT/p) for p in ('modal_pilot.py','modal_pilot_worker.py','modal_pilot_core.py')},
         'modal_version':importlib.metadata.version('modal'),'remote_packages':REMOTE_PACKAGES,
         'gpu':GPU,'cpu_limit':2,'memory_limit_mib':32768}
    ev.atomic_json(ledger,run)
    sb=None; results=[]; start=time.monotonic()
    try:
        app=modal.App.lookup('adaption-extractor-pilot',create_if_missing=True)
        image=modal.Image.debian_slim(python_version='3.12')
        sb=modal.Sandbox.create(app=app,image=image,gpu=GPU,cpu=(2,2),memory=(32768,32768),
                                timeout=budget['sandbox_timeout_s'],idle_timeout=60)
        run['sandbox_id']=sb.object_id; ev.atomic_json(ledger,run)
        for local,remote in [(prepared/'payload.json','/pilot/payload.json'),
                             (ROOT/'modal_pilot_worker.py','/pilot/modal_pilot_worker.py'),
                             (ROOT/'modal_pilot_core.py','/pilot/modal_pilot_core.py')]:
            sb.filesystem.copy_from_local(local,remote)
        # Installation is inside the same lifetime limit as downloads and inference.
        setup=sb.exec('python','-m','pip','install',*REMOTE_PACKAGES,timeout=600)
        with (prepared/'setup.log').open('w') as log:
            log.write(setup.stdout.read()); log.write(setup.stderr.read())
        setup.wait()
        if setup.returncode!=0:
            raise RuntimeError('Remote dependency installation failed; see setup.log')
        process=sb.exec('python','-u','/pilot/modal_pilot_worker.py','/pilot/payload.json',timeout=budget['sandbox_timeout_s'])
        with (prepared/'events.jsonl').open('x') as events, (prepared/'worker.log').open('w') as log:
            for line in process.stdout:
                if line.startswith('PILOT_EVENT '):
                    event=json.loads(line[len('PILOT_EVENT '):]); events.write(json.dumps(event)+'\n'); events.flush()
                    if event['event']=='result':
                        results.append(event)
                        print(f"{event['label']}: {event['status']}",flush=True)
                else:
                    log.write(line)
            log.write(process.stderr.read())
        process.wait()
        run['worker_exit_code']=process.returncode
        accounting=account_results(payload['examples'],results)
        run['status']='complete' if process.returncode==0 and not any(accounting.values()) else 'incomplete'
    except BaseException as error:
        run.update(status='failed',error_type=type(error).__name__)
        raise
    finally:
        if sb is not None:
            try:
                sb.terminate(); run['termination']='confirmed'
            except Exception as error:
                run['termination']='unconfirmed';run['termination_error']=type(error).__name__
                run['status']='cleanup_unconfirmed'
        run.update(finished_at=now(),elapsed_seconds=time.monotonic()-start,
                   accounting=account_results(payload['examples'],results),actual_invoice_cost_usd=None)
        ev.atomic_json(ledger,run)
        ev.atomic_jsonl(prepared/'results.jsonl',results)
        lines=['# Qwen Modal pilot', '', f"Status: {run['status']}", '',
               '| Example | Status | Input tokens | Output tokens | Inference seconds |',
               '|---|---|---:|---:|---:|']
        for r in results:
            lines.append(f"| {r['label']} | {r['status']} | {r['input_tokens']} | {r.get('output_tokens')} | {r['inference_seconds']:.3f} |")
        lines.extend(['', 'Accounting: '+json.dumps(run['accounting']), '',
            'Actual provider cost: unverified. Resource envelope and overhead reserve are estimates.',
            'Output schema checks are not factual grading. This is not an end-to-end benchmark score.'])
        ev.atomic_text(prepared/'summary.md','\n'.join(lines)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run'])
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--directory',type=Path,default=ROOT/'work/modal_qwen_pilot')
    parser.add_argument('--budget-usd',type=float,default=2)
    args=parser.parse_args()
    if args.command=='prepare':
        prepare(args.source,args.directory)
    else:
        execute(args.directory,args.budget_usd)
