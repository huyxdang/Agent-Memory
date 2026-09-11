"""Compare saved Qwen BEAM results with the original Luna runs; no API calls."""
import json
import argparse
from pathlib import Path

import longmemeval_eval as ev
from qwen_vllm import DIRECTORY

ROOT = Path(__file__).resolve().parent
REFERENCES = {'100K':'20260908T191319329343Z_memory_07ccfb9',
              '500K':'20260909T064305432208Z_memory_e66fa47'}


def main(directory=DIRECTORY):
    results = {p.stem:json.loads(p.read_text()) for p in (directory/'results').glob('*.json')}
    lines = ['# Qwen versus historical Luna: BEAM final', '',
             'Same original question sets. Luna uses historical per-question memory builds; Qwen builds one memory per history. This is an observational comparison, not an isolated model-only causal effect.', '',
             '| Tier | Questions | Qwen valid | Qwen passes | Luna passes | Qwen mean answer input | Luna mean answer input |',
             '|---|---:|---:|---:|---:|---:|---:|']
    records = []
    for tier,run_id in REFERENCES.items():
        with (ROOT/'runs'/run_id/'results.jsonl').open() as stream:
            old = [json.loads(line) for line in stream]
        ids = {r['question_id'] for r in old}
        current = [results[q] for q in ids if q in results]
        valid = [r for r in current if r['status']=='success']
        passed = sum(r['judge_verdict']=='yes' for r in valid)
        prior_passed = sum(r['judge_verdict']=='yes' for r in old)
        def mean_input(rows):
            values = [r['answer_call']['usage']['input_tokens'] for r in rows if r.get('answer_call',{}).get('usage',{}).get('input_tokens') is not None]
            return sum(values)/len(values) if values else None
        qinput, linput = mean_input(current), mean_input(old)
        lines.append(f"| {tier} | {len(ids)} | {len(valid)} | {str(passed)+'/'+str(len(ids)) if valid else 'unavailable'} | {prior_passed}/{len(ids)} | {round(qinput) if qinput is not None else 'pending'} | {round(linput)} |")
        records.append(dict(tier=tier,expected=len(ids),valid=len(valid),passed=passed,reference_run=run_id,
                            missing=sorted(ids-results.keys()),failed=[r['question_id'] for r in current if r['status']!='success'],
                            complete=len(valid)==len(ids)))
    expected_ids = {q for r in REFERENCES.values() for q in [json.loads(line)['question_id'] for line in (ROOT/'runs'/r/'results.jsonl').open()]}
    unexpected = sorted(results.keys()-expected_ids)
    lines.extend(['', 'Incomplete rows use the full expected denominator; missing and failed questions are not silently dropped.',
                  'Token means include answering calls with measured usage, including calls whose judging later failed.',
                  'No Qwen score is final until all expected questions have valid outputs.'])
    ev.atomic_json(directory/'comparison.json',dict(cohorts=records,unexpected=unexpected))
    ev.atomic_text(directory/'comparison.md','\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=DIRECTORY)
    main(parser.parse_args().directory)
