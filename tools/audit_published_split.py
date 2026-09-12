"""Offline audit of pinned public split sources and LongMemEval session connectivity."""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from adaption_memory import integrity as ev
from adaption_memory.benchmarks.longmemeval import DATASET_REVISION
from adaption_memory.history import sanitize_history

ROOT = Path(__file__).resolve().parent.parent
DATASET_SHA256 = 'd6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442'
PUBLIC_REVISIONS = {
    'budgetmem': '91c17435f3b7634711a22fe9cb303ec15069a7aa',
    'lazymem': 'af4109960aacb90d6dba994e9103a36a165cc380',
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def session_components(session_sets):
    """Connected components, not a claim that every pair shares a session."""
    parents = list(range(len(session_sets)))

    def root(i):
        while i != parents[i]:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    owners, occurrences = {}, Counter()
    for i, sessions in enumerate(session_sets):
        for session in set(sessions):
            occurrences[session] += 1
            if session in owners:
                parents[root(i)] = root(owners[session])
            else:
                owners[session] = i
    return {
        'histories': len(session_sets),
        'component_sizes': sorted(Counter(root(i) for i in range(len(session_sets))).values(), reverse=True),
        'unique_sessions': len(owners),
        'sessions_in_multiple_histories': sum(n > 1 for n in occurrences.values()),
        'max_histories_sharing_one_session': max(occurrences.values(), default=0),
    }


def validate_indices(split, count):
    if set(split) != {'train', 'val', 'test'}:
        raise ValueError('Expected train/val/test lists')
    indices = []
    for values in split.values():
        if not isinstance(values, list) or any(type(i) is not int for i in values):
            raise ValueError('Split indices must be integer lists')
        indices.extend(values)
    if len(indices) != count or set(indices) != set(range(count)):
        raise ValueError('Indices must cover every row exactly once')
    return {name: len(values) for name, values in split.items()}


def snapshot(path, expected_revision):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != expected_revision or git('status', '--porcelain'):
        raise ValueError(f'Expected a clean pinned source checkout: {path}')
    files = git('ls-files').splitlines()
    return {
        'revision': expected_revision,
        'tracked_file_sha256': {name: ev.sha256_file(path / name) for name in files},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budgetmem', type=Path, required=True)
    parser.add_argument('--lazymem', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = {name: snapshot(getattr(args, name), revision)
               for name, revision in PUBLIC_REVISIONS.items()}
    dataset = ROOT / 'work/longmemeval_s_cleaned.json'
    if ev.sha256_file(dataset) != DATASET_SHA256:
        raise ValueError('Dataset differs from the pinned cleaned LongMemEval-S revision')
    items = json.loads(dataset.read_text())
    if len(items) != 500 or len({item['question_id'] for item in items}) != 500:
        raise ValueError('Expected 500 unique question records')
    split = json.loads((args.budgetmem / 'data/longmemeval_s_splits.json').read_text())
    counts = validate_indices(split, len(items))
    text_graph = session_components([
        {digest(session['messages']) for session in sanitize_history(item)} for item in items
    ])
    id_graph = session_components([set(item['haystack_session_ids']) for item in items])
    copy = ROOT / 'work/training_copies_v2/copy_2_repaired'
    report = {
        'status': 'audit_only_no_split_adopted',
        'dataset_revision': DATASET_REVISION,
        'dataset_sha256': DATASET_SHA256,
        'local_code_revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'local_code_sha256': {name: ev.sha256_file(ROOT / name) for name in
                              ('audit_published_split.py', 'adaption_memory/benchmarks/longmemeval.py')},
        'current_copy_2_sha256': {s: ev.sha256_file(copy / f'{s}.jsonl') for s in ('train', 'dev')},
        'public_sources': sources,
        'budgetmem': {
            'declared_index_counts': counts,
            'indices_cover_0_through_499_exactly_once': True,
            'processed_dataset_in_checkout': (args.budgetmem / 'data/longmemeval_s.json').exists(),
            'question_id_mapping_verified': False,
            'measured_cross_split_session_counts': None,
            'source_review': 'load_train_data combines train and val indices before loading samples.',
        },
        'lazymem': {
            'readme_question_counts': {'train': 360, 'val': 40, 'test': 100},
            'split_files_present': {name: (args.lazymem / f'data/splits/{name}.txt').exists()
                                    for name in ('train', 'val', 'test')},
            'question_id_mapping_verified': False,
            'measured_cross_split_session_counts': None,
        },
        'exact_role_content_graph': text_graph,
        'session_id_graph': id_graph,
        'all_500_form_one_text_component': text_graph['component_sizes'] == [500],
        'conclusion': 'If all 500 complete histories are used, a nonempty train/test partition cannot be exact-session-disjoint when the graph has one component. This does not measure either authors actual processed split.',
        'limitations': [
            'Role/content hashing ignores timestamps and evaluation annotations; it does not normalize wording or whitespace.',
            'Connected does not mean every pair of histories shares a session.',
            'Missing mapping/IDs prevent per-partition counts or claims about authors actual training exposure.',
            'No model fitting, uploads, paid calls, or changes to existing splits.',
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ev.atomic_json(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k != 'public_sources'}, indent=2))


if __name__ == '__main__':
    main()
