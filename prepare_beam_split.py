"""Freeze and audit BEAM train/dev sources and the original final questions; no model calls."""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request

import tiktoken
import benchmarks
import longmemeval_eval as ev
import memory
from audit_published_split import digest

ROOT = Path(__file__).resolve().parent
REVISION = 'b2da22eac88bb0874c64665f13457eb99835774a'
SPLITS = {
    'train': {'100K': [7, 8, 9, 11, 14, 17, 18, 20],
              '500K': [3, 7, 21, 23, 27, 29, 32, 34]},
    'dev': {'100K': [10, 19], '500K': [22, 33]},
}
SELECTED = [(scale, number) for tiers in SPLITS.values() for scale, ids in tiers.items() for number in ids]
FINAL_FILES = ('question_ids_beam_50.json', 'question_ids_beam_500k_40.json')
FINAL_SHA256 = {
    FINAL_FILES[0]: '057f3203ea0da4941b93e627b221a83bf58e8ef3d4222f1a5ba6e018401c0c76',
    FINAL_FILES[1]: '03219aa915ff2cc573a7448bd211f19ab1062bc9937f7166a8bc4a2703604ef7',
}
REFERENCE = '20260909T064305432208Z_memory_e66fa47'
DEST = ROOT / 'work/beam_split_v2'


def validate_split(records, overlap):
    expected = {(split, scale, number) for split, tiers in SPLITS.items()
                for scale, ids in tiers.items() for number in ids}
    actual = {(r['split'], r['scale'], r['chat_id']) for r in records}
    if actual != expected or len(records) != len(expected):
        raise ValueError('Missing, duplicate or unexpected split histories')
    if len({r['history_sha256'] for r in records}) != len(records):
        raise ValueError('Duplicate source history')
    if any(r['shared_history_with_prior_eval'] or r['shared_windows_with_prior_eval']
           or r['shared_pairs_with_prior_eval'] for r in records):
        raise ValueError('Source overlaps protected evaluation pool')
    if any(r['windows'] or r['pairs'] for r in overlap):
        raise ValueError('Selected histories share source content')


def get(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def download_sources():
    inventory = json.loads(get(f'https://api.github.com/repos/mohammadtavakoli78/BEAM/git/trees/{REVISION}?recursive=1'))
    if inventory['truncated']:
        raise ValueError('Incomplete Git source inventory')
    blobs = {x['path']: x['sha'] for x in inventory['tree'] if x['type'] == 'blob'}

    def fetch(task):
        scale, number, filename = task
        relative = f'chats/{scale}/{number}/{filename}'
        path = DEST / 'source' / scale / str(number) / filename
        data = path.read_bytes() if path.exists() else get(f'https://raw.githubusercontent.com/mohammadtavakoli78/BEAM/{REVISION}/{relative}')
        actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        if actual != blobs[relative]:
            raise ValueError(f'Source hash mismatch: {relative}')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(data)
        return relative, ev.sha256_file(path)

    tasks = [(scale, number, filename) for scale, number in SELECTED
             for filename in ('chat.json', 'topic.json', 'probing_questions/probing_questions.json')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        hashes = dict(pool.map(fetch, tasks))
    ev.atomic_json(DEST / 'source_manifest.json', {'revision': REVISION, 'sha256': hashes})


def hashes(item):
    history = ev.sanitize_history(item)
    return digest(history), {digest(s['messages']) for s in history}, {
        digest(s['messages'][i:i+2]) for s in history for i in range(0, len(s['messages']) - 1, 2)
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    if args.download:
        download_sources()
    source = json.loads((DEST / 'source_manifest.json').read_text())
    assert source['revision'] == REVISION
    expected_files = {f'chats/{scale}/{number}/{filename}' for scale, number in SELECTED
                      for filename in ('chat.json', 'topic.json', 'probing_questions/probing_questions.json')}
    assert set(source['sha256']) == expected_files
    for relative, sha in source['sha256'].items():
        assert ev.sha256_file(DEST / 'source' / relative.removeprefix('chats/')) == sha
    historical = {item['question_id']: item for item in benchmarks.load_items('beam')}
    if any(ev.sha256_file(ROOT / p) != sha for p, sha in FINAL_SHA256.items()):
        raise ValueError('Original final question selection changed')
    final_questions = [q for name in FINAL_FILES for q in json.loads((ROOT / name).read_text())['questions']]
    evaluated_ids = {q['question_id'] for q in final_questions}
    if len(final_questions) != 90 or len(evaluated_ids) != 90:
        raise ValueError('Final must contain the original 90 unique questions')
    assert evaluated_ids <= historical.keys()
    final_records = [{'question_id': q['question_id'], 'question_type': q['question_type'],
                      'conversation': q['conversation'],
                      'history_sha256': hashes(historical[q['question_id']])[0]}
                     for q in final_questions]
    historical = list(historical.values())
    protected = {h: item for item in historical for h in [hashes(item)[0]]}
    protected_windows, protected_pairs = set(), set()
    for item in protected.values():
        _, windows, pairs = hashes(item)
        protected_windows.update(windows)
        protected_pairs.update(pairs)
    enc = tiktoken.get_encoding('o200k_base')
    count = lambda text: len(enc.encode(text, disallowed_special=()))
    unique = {}
    result_path = ROOT / 'runs' / REFERENCE / 'results.jsonl'
    with result_path.open() as stream:
        for line in stream:
            r = json.loads(line)
            if r['status'] == 'ok' or r.get('memory', {}).get('sessions_done'):
                unique.setdefault(r['history_sha256'], r)
    calls = [c for r in unique.values() for c in r['memory']['extraction_calls'] if c['ok']]
    output_per_call = sum(c['usage']['output_tokens'] for c in calls) / len(calls)
    memory_tokens = 0
    for r in unique.values():
        grouped = defaultdict(list)
        for line in r['memory']['lines']:
            grouped[line['session']].append(line)
        for n, lines in grouped.items():
            memory_tokens += count(memory.MEMORY_MESSAGE_FORMAT.format(session_number=n, timestamp=lines[0]['date'], lines=memory.render_store(lines))) + 8
    growth = memory_tokens / len(calls)
    manifest = json.loads((ROOT / 'runs' / REFERENCE / 'manifest.json').read_text())
    prices = manifest['metadata']['prices_usd_per_million_tokens']
    original_dir = benchmarks.BEAM_DIR
    benchmarks.BEAM_DIR = DEST / 'source'
    records, selected_hashes = [], []
    try:
        for scale, number in SELECTED:
            items = benchmarks.beam_items(scale, [number])
            assert len(items) == 20 and len({x['question_id'] for x in items}) == 20
            item = items[0]
            split = next(s for s, tiers in SPLITS.items() if number in tiers.get(scale, []))
            history = ev.sanitize_history(item)
            h, windows, pairs = hashes(item)
            selected_hashes.append((scale, number, windows, pairs))
            topic = json.loads((benchmarks.BEAM_DIR / scale / str(number) / 'topic.json').read_text())
            static = 0
            for n, session in enumerate(history, 1):
                parts = memory.extraction_parts([], n, len(history), session['timestamp'], session['messages'])
                static += count(memory.extraction_system_prompt(item['subject'])) + count(parts[-1]) + 24
            prior = growth * len(history) * (len(history) - 1) / 2
            output = output_per_call * len(history)
            cost = lambda rate: (static * prices['answer_input'] + prior * rate + output * prices['answer_output']) / 1e6
            records.append({'split': split, 'scale': scale, 'chat_id': number, 'category': topic.get('category'), 'title': topic.get('title'),
                            'question_ids': [x['question_id'] for x in items],
                            'history_sha256': h, 'updates': len(history), 'associated_questions': 20,
                            'content_tokens': sum(count(m['content']) for s in history for m in s['messages']),
                            'static_prompt_tokens_estimate': static, 'prior_memory_tokens_estimate': round(prior),
                            'output_tokens_estimate_including_reasoning': round(output),
                            'teacher_cost_cached_prefix_usd': cost(prices['answer_cached_input']),
                            'teacher_cost_uncached_usd': cost(prices['answer_input']),
                            'shared_history_with_prior_eval': h in protected,
                            'shared_windows_with_prior_eval': len(windows & protected_windows),
                            'shared_pairs_with_prior_eval': len(pairs & protected_pairs)})
    finally:
        benchmarks.BEAM_DIR = original_dir
    overlap = [{'a': f'{a[0]}/{a[1]}', 'b': f'{b[0]}/{b[1]}', 'windows': len(a[2]&b[2]), 'pairs': len(a[3]&b[3])}
               for i,a in enumerate(selected_hashes) for b in selected_hashes[i+1:]]
    report = {'status': 'split_sources_frozen_teacher_targets_not_generated', 'source': source,
              'selection_rule': 'Eight train and two dev per tier. Mix writing and legal topics in 100K dev, with both represented in training; include coding and math in 500K training. Select using topic metadata, not scores. Exclude actual protected source content, not unrelated numeric IDs across scales. Keep original final lists unchanged.',
              'protected_local_beam_histories': len(protected), 'known_evaluation_questions': len(evaluated_ids),
              'records': records, 'pairwise_source_overlap': overlap,
              'final': {'questions': final_records, 'selection_files_sha256': FINAL_SHA256,
                        'source_files_sha256': {str(p.relative_to(ROOT)): ev.sha256_file(p)
                                                for p in benchmarks.source_files('beam')}},
              'teacher_reference': {'run_id': REFERENCE, 'histories': len(unique), 'calls': len(calls),
                                   'models': manifest['metadata']['models'], 'prices': prices,
                                   'output_tokens_per_call': output_per_call, 'added_memory_tokens_per_call': growth,
                                   'results_sha256': ev.sha256_file(result_path)},
              'totals': {'updates': sum(r['updates'] for r in records), 'content_tokens': sum(r['content_tokens'] for r in records),
                         'cost_cached_prefix_usd': sum(r['teacher_cost_cached_prefix_usd'] for r in records),
                         'cost_uncached_usd': sum(r['teacher_cost_uncached_usd'] for r in records)},
              'limits': ['Forecast uses historical model/rates, not verified current provider prices or a hard cap.',
                         'Teacher output and memory growth extrapolate two 500K histories; actual quality, fit and cost are unverified.',
                         'Source tokens exclude repeated prior memory; cost includes its estimated repeated input.',
                         'Cost is teacher writing only, excluding training, synthesis, Modal, answering and judging.',
                         'Exact windows/pairs are checked, not semantic duplicates. Identity uses scale and chat ID, not numeric ID alone.',
                         'BEAM split only; additional LongMemEval and LoCoMo evaluation manifests are not changed or certified here. Old training exports are not merged.',
                         'Update slots are not validated teacher targets; outputs may be empty or need repairs.',
                         'All update prompts and targets must fit the student training context using its tokenizer once teacher memory exists. No silent truncation.'],
              'code_sha256': {p: ev.sha256_file(ROOT / p) for p in ('prepare_beam_split.py','benchmarks.py','memory.py')}}
    validate_split(records, overlap)
    assert not any(r['shared_history_with_prior_eval'] or r['shared_windows_with_prior_eval'] or r['shared_pairs_with_prior_eval'] for r in records)
    assert not any(r['windows'] or r['pairs'] for r in overlap)
    report['by_split'] = {}
    for split in SPLITS:
        rows = [r for r in records if r['split'] == split]
        report['by_split'][split] = {'histories': len(rows), 'questions': sum(len(r['question_ids']) for r in rows),
                                    'updates': sum(r['updates'] for r in rows),
                                    'cost_cached_prefix_usd': sum(r['teacher_cost_cached_prefix_usd'] for r in rows),
                                    'cost_uncached_usd': sum(r['teacher_cost_uncached_usd'] for r in rows)}
        ev.atomic_json(DEST / f'{split}.json', {'source_revision': REVISION, 'split': split, 'histories': rows})
    ev.atomic_json(DEST / 'final.json', report['final'])
    ev.atomic_json(DEST / 'report.json', report)
    print(json.dumps({'status': report['status'], 'by_split': report['by_split'],
                      'final_questions': len(final_records), 'protected_histories': len(protected),
                      'overlap_pairs_checked': len(overlap)}, indent=2))


if __name__ == '__main__':
    main()
