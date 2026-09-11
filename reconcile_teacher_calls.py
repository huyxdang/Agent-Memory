"""Explicitly replace unrecoverable calls while preserving their full reservations."""
import argparse
import json
from pathlib import Path

from checkpoint_io import exclusive, save
import longmemeval_eval as ev
from teacher_traces import now

ROOT = Path(__file__).resolve().parent


def reconcile(directory, reason):
    with exclusive(directory):
        config_path = directory / 'configuration.json'
        previous = json.loads(config_path.read_text())
        for name, sha in previous['code_sha256'].items():
            if name != 'teacher_traces.py' and ev.sha256_file(ROOT / name) != sha:
                raise ValueError('Unrelated code changed; reconciliation refused')
        states = [(p, json.loads(p.read_text())) for p in (directory / 'histories').glob('*.json')]
        candidates = [(p, s) for p, s in states if s['calls'] and s['calls'][-1]['status'] == 'unknown_outcome']
        if not candidates:
            raise ValueError('No unknown calls to reconcile')
        if any(s['calls'][-1].get('response') for _, s in candidates):
            raise ValueError('A saved response exists; recover it instead')
        stamp = now()
        audit_path = directory / 'reconciliations.json'
        audits = json.loads(audit_path.read_text()) if audit_path.exists() else []
        audits.append(dict(at=stamp, reason=reason, previous_configuration=previous,
            affected=[dict(history=s['history_sha256'], session=s['calls'][-1]['session'],
                           reserved_usd=s['calls'][-1]['reserved_usd']) for _, s in candidates],
            retained_unknown_cost=True, previous_responses_recoverable=False))
        save(audit_path, audits)
        for path, state in candidates:
            state['calls'][-1].update(status='abandoned_unknown', resolved_at=stamp, resolution=reason)
            state['status'] = 'pending'
            save(path, state)
        current = json.loads(json.dumps(previous))
        current['code_sha256']['teacher_traces.py'] = ev.sha256_file(ROOT / 'teacher_traces.py')
        save(config_path, current)
        print(f'Reconciled {len(candidates)} calls. All prior reservations retained; no model calls made.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--directory', type=Path, default=ROOT / 'work/beam_teacher_traces')
    args = parser.parse_args()
    reconcile(args.directory, args.reason)
