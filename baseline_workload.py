"""Count the requested baseline and extrapolate the saved Modal pilot; no API calls."""
import json
from pathlib import Path

import benchmarks
import longmemeval_eval as ev
from modal_pilot_core import RATE
from prepare_beam_split import hashes

ROOT = Path(__file__).resolve().parent


def main():
    cohorts = {
        'longmemeval_final': ('longmemeval', ['question_ids_50.json', 'question_ids_50b.json']),
        'locomo_final': ('locomo', ['question_ids_locomo_50.json']),
        'beam_final': ('beam', ['question_ids_beam_50.json', 'question_ids_beam_500k_40.json']),
    }
    result = {}
    for name, (kind, files) in cohorts.items():
        ids = {q['question_id'] for f in files for q in json.loads((ROOT / f).read_text())['questions']}
        items = json.loads((ROOT / 'work/longmemeval_s_cleaned.json').read_text()) if kind == 'longmemeval' else benchmarks.load_items(kind)
        selected = [x for x in items if x['question_id'] in ids]
        if len(selected) != len(ids):
            raise ValueError('Missing or duplicate evaluation questions')
        histories = {hashes(x)[0]: len(ev.sanitize_history(x)) for x in selected}
        result[name] = dict(questions=len(ids), histories=len(histories), updates=sum(histories.values()),
                            history_updates=histories, selection_sha256={f:ev.sha256_file(ROOT/f) for f in files})
    dev_path = ROOT / 'work/beam_split_v2/dev.json'
    dev = json.loads(dev_path.read_text())['histories']
    result['beam_dev'] = dict(questions=sum(len(r['question_ids']) for r in dev), histories=len(dev),
                              updates=sum(r['updates'] for r in dev), manifest_sha256=ev.sha256_file(dev_path))
    pilot = ROOT / 'work/modal_qwen_pilot_new_account/events.jsonl'
    calls = [json.loads(line) for line in pilot.open()]
    seconds = [r['inference_seconds'] for r in calls if r.get('event') == 'result' and r['status'] == 'ok']
    mean = sum(seconds) / len(seconds)
    for row in result.values():
        row['projected_hours'] = row['updates'] * mean / 3600
        row['projected_modal_usd'] = row['updates'] * mean * RATE
    total = sum(r['updates'] for r in result.values())
    report = dict(status='full_baseline_over_budget_under_current_pilot_extrapolation', cohorts=result,
                  total_updates=total, mean_pilot_seconds=mean, pilot_calls=len(seconds),
                  pilot_sha256=ev.sha256_file(pilot), resource_rate_usd_s=RATE,
                  projected_hours=total*mean/3600, projected_modal_usd=total*mean*RATE, modal_total_cap_usd=30,
                  limitations=['Two teacher-forced pilot calls are not representative rollout throughput.',
                               'Excludes startup, idle time, failures, answering, judging and fresh Luna dev comparison.',
                               'No inference backend optimization or new accuracy run measured.',
                               'Historical final Luna scores are observational; dev requires a new matched Luna run.'])
    ev.atomic_json(ROOT / 'work/qwen_baseline_workload.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='cohorts'}, indent=2))


if __name__ == '__main__':
    main()
