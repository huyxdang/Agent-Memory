"""Resume BEAM answering only, replacing explicitly authorized truncated answers."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import time

from dotenv import load_dotenv
from openai import OpenAI
from checkpoint_io import exclusive, save
from beam_baseline_answers import Answers
from beam_final_inputs import ROOT, inputs
import longmemeval_eval as ev
from report_beam_baseline import main as report


def prepare(source, destination):
    old=json.loads((source/'configuration.json').read_text())
    if (destination/'configuration.json').exists():
        return json.loads((destination/'configuration.json').read_text())
    states=[json.loads(p.read_text()) for p in (source/'memories').glob('*.json')]
    expected={r['history_sha256'] for r in old['payload']['histories']}
    if {s['history_sha256'] for s in states}!=expected or any(
            s['status']!='complete' or s['payload_sha256']!=old['payload']['fingerprint'] for s in states):
        raise ValueError('Require all completed, verified source memories')
    calls={p.name:json.loads(p.read_text()) for p in (source/'api_calls').glob('*.json')}
    if any(c['status']!='complete' for c in calls.values()):
        raise ValueError('Unknown API outcome requires separate reconciliation')
    retry=[]
    for p in (source/'results').glob('*.json'):
        r=json.loads(p.read_text())
        if r['status']=='success':continue
        name='answer_'+r['question_id']+'.json'
        if calls[name]['response']['finish_reason']!='length':
            raise ValueError('Only length-truncated answers were authorized for replacement')
        retry.append(name)
    for folder in ('memories','api_calls','results'):
        (destination/folder).mkdir(parents=True,exist_ok=True)
        for p in (source/folder).glob('*.json'):
            name='abandoned_'+p.name if folder=='api_calls' and p.name in retry else p.name
            shutil.copy2(p,destination/folder/name)
    config=dict(source=str(source), source_configuration_sha256=ev.sha256_file(source/'configuration.json'),
        payload=old['payload'],settings={**old['settings'],'answer_max_tokens':128000},
        replaced_answers=retry, code_sha256={p:ev.sha256_file(ROOT/p) for p in
            ('finish_beam_answers.py','beam_baseline_answers.py','memory.py')},
        note='Answer-only continuation; successful old answers retained, truncations archived and charged. Mixed caps.')
    save(destination/'configuration.json',config)
    return config


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'work/qwen_beam_vllm_max')
    parser.add_argument('--directory',type=Path,default=ROOT/'work/qwen_beam_answers_max')
    parser.add_argument('--run',action='store_true')
    args=parser.parse_args();load_dotenv(ROOT/'.env',override=False)
    with exclusive(args.directory):
        config=prepare(args.source,args.directory)
        for name,sha in config['code_sha256'].items():
            if ev.sha256_file(ROOT/name)!=sha: raise ValueError('Answer runner changed after preparation')
        if not args.run:
            print('Prepared only; no API calls.');return
        _,grouped,_=inputs()
        prior=[json.loads(p.read_text()) for p in (ROOT/'work/qwen_beam_baseline/api_calls').glob('*.json')]
        limit=20-sum(c.get('accounted_usd',c['reserved_usd']) for c in prior)
        answers=Answers(args.directory,OpenAI(max_retries=0,timeout=180),config['settings'],limit)
        started=time.monotonic()
        save(args.directory/'execution.json',dict(status='running',source=str(args.source),started_at=time.time(),
             answer_max_tokens=128000,api_budget_usd=limit))
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[]
            for key,items in grouped.items():
                state=json.loads((args.directory/'memories'/f'{key}.json').read_text())
                futures.extend(pool.submit(answers.evaluate,item,state) for item in items)
            for f in futures:f.result()
        results=[json.loads(p.read_text()) for p in (args.directory/'results').glob('*.json')]
        wanted={i['question_id'] for items in grouped.values() for i in items}
        ids=[r['question_id'] for r in results]
        if len(ids)!=len(set(ids)) or set(ids)-wanted:raise ValueError('Duplicate/unexpected results')
        summary=dict(status='complete' if len(results)==90 and all(r['status']=='success' for r in results) else 'incomplete',
            expected=90,valid=sum(r['status']=='success' for r in results),missing=sorted(wanted-set(ids)),
            failed=[r['question_id'] for r in results if r['status']!='success'],elapsed_seconds=time.monotonic()-started,
            total_api_accounted_usd=sum(c.get('accounted_usd',c['reserved_usd']) for c in answers.calls.values()))
        save(args.directory/'summary.json',summary);save(args.directory/'execution.json',summary)
        report(args.directory);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
