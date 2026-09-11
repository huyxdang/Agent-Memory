"""Prepare an auditable continuation for explicitly authorized failed calls."""
import argparse
import copy
import json
from pathlib import Path
import shutil

from checkpoint_io import exclusive, save
import longmemeval_eval as ev
from modal_pilot_core import digest
from qwen_vllm import cloud, prepare, volume_json


def reconcile_state(original, fingerprint, retry_timeouts=False):
    state = copy.deepcopy(original)
    if state['status']=='unknown_outcome' and retry_timeouts:
        call=state['calls'][-1]
        if (call.get('error_type')!='APITimeoutError' or call['status']!='unknown_outcome'
                or call.get('content') is not None or call.get('response_id') is not None
                or call['session']!=state['sessions_done']+1):
            raise ValueError('Only a reconciled timeout without a saved response may be retried')
        state.setdefault('abandoned_attempts',[]).append(state['calls'].pop())
        state['status']='running'
    if state['status']=='invalid_output':
        call=state['calls'][-1]
        if call.get('finish_reason')!='length' or call['status']!='response_saved':
            raise ValueError('Only explicitly authorized length-truncated responses may be replaced')
        state.setdefault('abandoned_attempts',[]).append(state['calls'].pop())
        state['status']='running'
    if state['status'] not in ('complete','running'):
        raise ValueError('Unknown/failed state cannot be replayed')
    if any(c['status']!='complete' for c in state['calls']):
        raise ValueError('Unresolved call cannot be replayed')
    if len(state['calls']) != state['sessions_done']:
        raise ValueError('Completed prefix mismatch')
    state['inherited_payload_sha256']=state['payload_sha256']
    state['payload_sha256']=fingerprint
    return state


def main():
    from dotenv import load_dotenv
    from qwen_vllm import ROOT
    load_dotenv(ROOT/'.env',override=False)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'work/qwen_beam_vllm')
    parser.add_argument('--destination',type=Path,default=ROOT/'work/qwen_beam_vllm_max')
    parser.add_argument('--retry-timeouts',action='store_true')
    parser.add_argument('--request-timeout-seconds',type=int,default=600)
    args=parser.parse_args()
    if not 600 <= args.request_timeout_seconds <= 1800:
        raise ValueError('Request timeout must be between 600 and 1800 seconds')
    if args.destination.exists():
        raise ValueError('Use a fresh destination; do not overwrite a continuation')
    with exclusive(args.source):
        old=json.loads((args.source/'configuration.json').read_text())
        ledger=json.loads((args.source/'cloud.json').read_text())
        if ledger.get('termination')!='confirmed' or ledger['status']!='stopped':
            raise ValueError('Stop and collect source run first')
        modal,volume=cloud()
        if modal.Sandbox.from_id(ledger['sandbox_id']).poll() is None:
            raise ValueError('Source GPU is still running')
        config=prepare(args.destination,False,old['payload']['concurrency'],old['payload']['structured_output'],
            benchmark=old.get('benchmark','beam'))
        skip={'code_sha256','fingerprint','request_timeout_seconds'}
        if not args.retry_timeouts:skip.add('max_output_tokens')
        if {k:v for k,v in old['payload'].items() if k not in skip} != {
                k:v for k,v in config['payload'].items() if k not in skip} or old['settings']!=config['settings']:
            raise ValueError('Source histories or inference settings changed')
        payload=config['payload']
        payload['request_timeout_seconds']=args.request_timeout_seconds
        payload['parent_run_id']=ledger['run_id']
        payload['fingerprint']=digest({k:v for k,v in payload.items() if k!='fingerprint'})
        imports={};complete=set();replaced=0;source_states={}
        for row in payload['histories']:
            key=row['history_sha256']
            original=volume_json(volume,f"{ledger['run_id']}/memories/{key}.json")
            if original is None or original['payload_sha256']!=old['payload']['fingerprint']:
                raise ValueError('Missing or mismatched source checkpoint')
            source_states[key]=original
            state=reconcile_state(original,payload['fingerprint'],args.retry_timeouts)
            state['inherited_run_id']=ledger['run_id']
            replaced+=len(state.get('abandoned_attempts',[]))
            if state['status']=='complete': complete.add(key)
            path=args.destination/'memories'/f'{key}.json';save(path,state)
            imports[key]=ev.sha256_file(path)
            save(args.destination/'progress'/f'{key}.json',dict(sessions_done=state['sessions_done'],
                status=state['status'],calls=len(state['calls']),last_call_status='complete'))
        for folder in ('api_calls','results'):
            for path in (args.source/folder).glob('*.json'):
                if folder=='results':
                    result=json.loads(path.read_text())
                    key=result['history_sha256']
                    if key not in complete or result['memory_sha256']!=digest(source_states[key]):
                        raise ValueError('Answer is not tied to the complete source memory')
                destination=args.destination/folder/path.name
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,destination)
        config.update(no_checkpoint_import=False,checkpoint_import=dict(source=str(args.source),
            source_run_id=ledger['run_id'],source_configuration_sha256=ev.sha256_file(args.source/'configuration.json'),
            state_sha256=imports,reason='User authorized retry of reconciled timeout without a saved response.' if args.retry_timeouts
                else 'User authorized maximum remaining-context output and replacement of length failures.',
            replaced_calls=replaced,source_accounted_usd=ledger['accounted_usd'],
            source_memory_sha256={k:digest(v) for k,v in source_states.items()},
            note='Checkpoint continuation, not a fresh controlled run. Reused answers retain their source memory hashes; source cost remains charged separately.'))
        save(args.destination/'configuration.json',config)
        save(args.destination/'payload.json',payload)
        print(f'Prepared continuation: {len(complete)} completed histories reused; {replaced} failed calls retained for explicit replacement.')


if __name__=='__main__':main()
