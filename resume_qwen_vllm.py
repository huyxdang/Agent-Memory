"""Explicitly resume a stopped cloud worker from safe, committed checkpoints."""
import argparse
import json
import math
from pathlib import Path

from checkpoint_io import exclusive, save
from qwen_vllm import ROOT, RATE, CACHE, cloud, now, volume_json


def validate_resume(states):
    for state in states:
        if state['status'] in ('unknown_outcome','invalid_output','context_limit'):
            raise ValueError('Failed/uncertain history needs explicit reconciliation, not blind replay')
        if state['calls'] and state['calls'][-1]['status'] not in ('complete','response_saved','queued'):
            raise ValueError('Uncertain in-flight request cannot be replayed')


def resume(directory, budget):
    if not math.isfinite(budget) or not 0 < budget <= 10:
        raise ValueError('Explicit positive remaining budget required')
    with exclusive(directory):
        path = directory/'cloud.json'
        old = json.loads(path.read_text())
        if old.get('termination') != 'confirmed' or old['status'] != 'stopped':
            raise ValueError('Stop and collect the existing attempt before resuming')
        modal, volume = cloud()
        if modal.Sandbox.from_id(old['sandbox_id']).poll() is None:
            raise ValueError('Previous worker is still active')
        if any(volume_json(volume,f"{old['run_id']}/{name}.json") for name in ('finished','fatal')):
            raise ValueError('Terminal worker output needs review; this is not an interrupted run')
        config = json.loads((directory/'configuration.json').read_text())
        states = [volume_json(volume,f"{old['run_id']}/memories/{r['history_sha256']}.json") for r in config['payload']['histories']]
        validate_resume([s for s in states if s is not None])
        baseline = sum(a.get('accounted_usd',a['reserved_usd']) for a in json.loads(
            (ROOT/'work/qwen_beam_baseline/modal_attempts.json').read_text()))
        charged = sum(r.get('accounted_usd',r['reserved_usd']) for r in
            [json.loads(p.read_text()) for p in (ROOT/'work').glob('*/cloud.json')] if r.get('runner')=='qwen_vllm')
        if baseline+charged+budget > 10:
            raise ValueError('Resume would exceed remaining baseline allocation')
        timeout = min(7200,int((budget-.5)/RATE))
        if timeout < 300:
            raise ValueError('Insufficient allocation to restart')
        previous = old.get('previous_attempts',[]) + [{k:v for k,v in old.items() if k!='previous_attempts'}]
        record = {k:v for k,v in old.items() if k not in ('accounted_usd','termination','finished_at','sandbox_id')}
        record.update(status='creating', gpu_started_at=now(), previous_attempts=previous,
            prior_run_accounted_usd=old['accounted_usd'], reserved_usd=old['accounted_usd']+budget,
            timeout_seconds=timeout)
        save(path,record)
        app=modal.App.lookup('adaption-qwen-vllm',create_if_missing=True)
        cache=modal.Volume.from_name(CACHE,create_if_missing=True,version=2)
        sb=modal.Sandbox.create('python','-u','/app/qwen_vllm_worker.py',f"/state/{old['run_id']}/payload.json",
            app=app,name=old['run_id']+f'-resume-{len(previous)}',image=modal.Image.from_id(old['image_id']),
            gpu='L40S',cpu=(4,4),memory=(32768,32768),volumes={'/state':volume,'/cache':cache},timeout=timeout)
        record.update(status='running',sandbox_id=sb.object_id)
        save(path,record)
        print('Resumed exact frozen worker image and committed state; all previous costs retained.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',required=True,type=Path)
    parser.add_argument('--budget-usd',required=True,type=float)
    args=parser.parse_args()
    resume(args.directory,args.budget_usd)
