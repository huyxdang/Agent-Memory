"""Offline GPU sizing comparison; missing/OOM measurements are not successes."""
import json
from pathlib import Path
from checkpoint_io import save
import longmemeval_eval as ev

ROOT = Path(__file__).resolve().parent


def main():
    directory = ROOT / 'work/qwen_gpu_sizing_l40s'
    run = json.loads((directory / 'run.json').read_text())
    events = []
    if (directory / 'events.jsonl').exists():
        with (directory / 'events.jsonl').open() as stream:
            events = [json.loads(line) for line in stream]
    measured = [r for r in events if r['event'] == 'measurement']
    lines = ['# L40S Qwen sizing', '', f"Run status: {run['status']}. Measurements: {len(measured)}/6.", '',
             'Identical two frozen pilot prompts, 16,022 and 36,620 input tokens. BF16, SDPA, thinking off, greedy generation and 2,048-token output cap. These are teacher-forced hardware probes, not BEAM accuracy or proof that every later BEAM prompt fits.', '',
             '| Trial | Mode | Status | Updates | Seconds | Peak allocated GiB | Compute $/update |',
             '|---|---|---|---:|---:|---:|---:|']
    comparisons = []
    for row in measured:
        count = len(row.get('outputs', []))
        cost = row['inference_seconds'] * run['resource_rate_usd_s'] / count if count else None
        lines.append(f"| {row['trial']} | {row['mode']} | {row['status']} | {count} | {row['inference_seconds']:.2f} | {row['peak_allocated_bytes']/2**30:.2f} | {f'{cost:.5f}' if cost is not None else 'unavailable'} |")
    for trial in (1, 2):
        singles = [r for r in measured if r['trial'] == trial and r['mode'] == 'single' and r['status'] == 'ok']
        batches = [r for r in measured if r['trial'] == trial and r['mode'] == 'batch' and r['status'] == 'ok']
        if len(singles) != 2 or len(batches) != 1:
            continue
        sequential = sum(r['inference_seconds'] for r in singles)
        batch = batches[0]
        old = {o['example_id']: o for r in singles for o in r['outputs']}
        all_outputs = [o for r in singles + batches for o in r['outputs']]
        record = dict(trial=trial, speedup=sequential/batch['inference_seconds'],
            valid_outputs=sum(o['valid_json'] and o['finish_reason']=='stop' for o in all_outputs),
            output_count=len(all_outputs), identical_outputs=sum(o['output']==old[o['example_id']]['output'] for o in batch['outputs']))
        comparisons.append(record)
        lines.extend(['', f"Trial {trial}: batching speedup {record['speedup']:.2f}x. Valid stopped JSON outputs {record['valid_outputs']}/{record['output_count']}; identical single/batch texts {record['identical_outputs']}/2."])
    lines.extend(['', f"Total resource estimate: {run.get('resource_estimate_usd', 'pending')}. Actual invoice remains unverified.",
                  'Inference-only unit cost excludes installation/loading and host checkpoint overhead. Total run timing includes installation/loading. Peak memory is the PyTorch allocator peak, not total device utilization. No factual grading performed.'])
    save(directory/'comparison.json', dict(run=run, measurements=measured, comparisons=comparisons))
    ev.atomic_text(directory/'summary.md', '\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
