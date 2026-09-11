"""Run the authorized LoCoMo -> LongMemEval sequence, stopping on any failed gate."""
import json
from pathlib import Path
import subprocess
import sys
import time

from checkpoint_io import exclusive, save
from qwen_vllm import ROOT, now

DIRECTORY=ROOT/'work/qwen_final_sequence'
STAGES=[('locomo','pilot',2),('locomo','final',4),('longmemeval','pilot',2),('longmemeval','final',8)]


def stage_path(benchmark,kind):
    return ROOT/f'work/qwen_{benchmark}_{kind}_c8'


def available_modal():
    old=json.loads((ROOT/'work/qwen_beam_baseline/modal_attempts.json').read_text())
    spent=6+sum(r.get('accounted_usd',r['reserved_usd']) for r in old)
    for path in (ROOT/'work').glob('*/cloud.json'):
        row=json.loads(path.read_text())
        if row.get('runner')=='qwen_vllm':spent+=row.get('accounted_usd',row['reserved_usd'])
    return 30-spent-.5


def verify_stage(directory):
    config=json.loads((directory/'configuration.json').read_text())
    summary=json.loads((directory/'summary.json').read_text())
    cloud=json.loads((directory/'cloud.json').read_text())
    if not summary['complete'] or cloud.get('termination')!='confirmed':
        raise ValueError(f'{directory.name}: incomplete results or unconfirmed GPU shutdown')
    for row in config['payload']['histories']:
        state=json.loads((directory/'memories'/f"{row['history_sha256']}.json").read_text())
        if state['status']!='complete' or state['sessions_done']!=len(row['history']):
            raise ValueError('Incomplete extraction; cannot advance')
    for path in (directory/'api_calls').glob('*.json'):
        if json.loads(path.read_text())['status']!='complete':
            raise ValueError('Unknown API outcome; cannot advance')
    # A low accuracy is not an operational failure and is never a retry trigger.
    return summary


def main():
    with exclusive(DIRECTORY):
        state=dict(status='running',started_at=now(),stages=[],modal_cap_usd=30,
            gpu='L40S',concurrency=8,stop_on_failed_gate=True)
        save(DIRECTORY/'status.json',state)
        def command(args):
            with (DIRECTORY/'runner.log').open('a') as log:
                subprocess.run([sys.executable,'-u',str(ROOT/'qwen_vllm.py'),*args],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        try:
            # The first pilot was launched interactively. Do not compete with its collector.
            first=stage_path('locomo','pilot')
            deadline=time.monotonic()+2400
            while not (first/'summary.json').exists():
                if time.monotonic()>deadline:raise TimeoutError('Initial pilot collector did not finish')
                state['active_stage']='waiting_for_locomo_pilot'
                save(DIRECTORY/'status.json',state)
                time.sleep(15)
            for benchmark,kind,desired in STAGES:
                directory=stage_path(benchmark,kind)
                state['active_stage']=f'{benchmark}_{kind}'
                save(DIRECTORY/'status.json',state)
                if not (directory/'summary.json').exists():
                    if not (directory/'configuration.json').exists():
                        args=['prepare','--benchmark',benchmark,'--concurrency','8','--directory',str(directory)]
                        args+=['--pilot-histories','2'] if kind=='pilot' else ['--reuse-from',str(stage_path(benchmark,'pilot'))]
                        command(args)
                    if not (directory/'cloud.json').exists():
                        budget=min(desired,available_modal())
                        if budget<.8:raise ValueError('Insufficient remaining Modal budget for startup')
                        command(['launch','--directory',str(directory),'--budget-usd',str(budget)])
                    command(['collect','--directory',str(directory),'--watch','--evaluate'])
                summary=verify_stage(directory)
                state['stages'].append(dict(benchmark=benchmark,kind=kind,directory=str(directory),
                    completed_at=now(),valid=summary['valid'],expected=summary['expected']))
                save(DIRECTORY/'status.json',state)
            state.update(status='complete',finished_at=now())
        except Exception as error:
            state.update(status='needs_attention',error_type=type(error).__name__,error=str(error),finished_at=now())
            raise
        finally:
            save(DIRECTORY/'status.json',state)


if __name__=='__main__':main()
