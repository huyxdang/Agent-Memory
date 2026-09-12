"""Offline experiment readiness checks. Does not select final IDs or call paid APIs."""
import json
from collections import Counter
from pathlib import Path

from tools import audit_training_traces as audit
from adaption_memory import integrity as ev
from adaption_memory.history import sanitize_history

ROOT = Path(__file__).resolve().parent.parent


def read_rows(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def classify(histories, used_history_ids, used_sessions):
    exact, session_overlap, eligible = [], [], []
    for row in histories:
        if row['history_sha256'] in used_history_ids:
            exact.append(row)
        elif used_sessions.intersection(row['session_hashes']):
            session_overlap.append(row)
        else:
            eligible.append(row)
    return {'exact_history_overlap': exact, 'session_overlap': session_overlap, 'eligible': eligible}


def main():
    copy = ROOT / 'work/training_copies_v2/copy_2_repaired'
    split_rows = {s: read_rows(copy / f'{s}.jsonl') for s in ('train', 'dev')}
    history_rows = read_rows(ROOT / 'work/training_trace_audit/histories.jsonl')
    history_index = {r['history_sha256']: r for r in history_rows}
    ids = {s: {r['history_sha256'] for r in rows} for s, rows in split_rows.items()}
    sessions = {s: {v for h in hashes for v in history_index[h]['session_hashes']}
                for s, hashes in ids.items()}
    if ids['train'] & ids['dev'] or sessions['train'] & sessions['dev']:
        raise ValueError('Frozen training/dev split overlaps')
    used = ids['train'] | ids['dev']
    used_sessions = sessions['train'] | sessions['dev']
    dataset_path = ROOT / 'work/longmemeval_s_cleaned.json'
    items = json.loads(dataset_path.read_text())
    candidates = []
    for item in items:
        history = sanitize_history(item)
        candidates.append({'question_id': item['question_id'], 'question_type': item['question_type'],
                           'history_sha256': audit.digest(history),
                           'session_hashes': sorted({audit.digest(s['messages']) for s in history}),
                           'updates': len(history)})
    groups = classify(candidates, used, used_sessions)
    historical_ids = {q['question_id'] for name in ('question_ids_50.json', 'question_ids_50b.json')
                      for q in json.loads((ROOT / name).read_text())['questions']}
    report = {'status': 'preflight_only_no_paid_jobs',
              'split': {s: {'rows': len(split_rows[s]), 'histories': len(ids[s]),
                            'strata': dict(Counter(history_index[h]['stratum'] for h in ids[s]))}
                        for s in ids},
              'train_dev_exact_session_overlap': 0,
              'longmemeval': {
                  'total_records': len(candidates),
                  'counts': {k: len(v) for k, v in groups.items()},
                  'eligible_by_type': dict(Counter(r['question_type'] for r in groups['eligible'])),
                  'eligible_nonabstention_by_type': dict(Counter(r['question_type'] for r in groups['eligible']
                                                                if not r['question_id'].endswith('_abs'))),
                  'historical_100_counts': {k: sum(r['question_id'] in historical_ids for r in v)
                                             for k, v in groups.items()},
                  'eligible_question_ids': [r['question_id'] for r in groups['eligible']]},
              'historical_other_benchmarks': {
                  s: {k: len(v) for k, v in classify([r for r in history_rows if r['stratum'] == s],
                                                    used, used_sessions).items()}
                  for s in ('locomo', 'BEAM 500K')},
              'input_sha256': {str(p.relative_to(ROOT)): ev.sha256_file(p) for p in
                               [copy/'train.jsonl', copy/'dev.jsonl', dataset_path,
                                ROOT/'work/training_trace_audit/histories.jsonl']},
              'code_sha256': ev.sha256_file(Path(__file__)),
              'limitations': ['Exact normalized session comparison only; near-duplicates not certified.',
                              'No final IDs frozen and no external credit balances verified.',
                              'Historical exposure is not the same as training overlap.']}
    destination = ROOT/'work/qwen_experiment_preflight'
    destination.mkdir(parents=True, exist_ok=True)
    ev.atomic_json(destination/'report.json', report)
    summary = {**report, 'longmemeval': {k: v for k, v in report['longmemeval'].items()
                                      if k != 'eligible_question_ids'}}
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
