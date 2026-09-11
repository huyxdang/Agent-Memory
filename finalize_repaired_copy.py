"""Offline, evidence-adjudicated repair export. Never overwrite an existing snapshot."""
import argparse
import copy
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import longmemeval_eval as ev
import memory
from build_training_copies import input_parts

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / 'work/training_copies_v1'
AGENTS = ROOT / 'work/repair_agents'
OUTPUT = ROOT / 'work/training_copies_v2'


def read_rows(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def unique_rows(rows):
    result = {}
    for row in rows:
        eid = row['example_id']
        if eid in result:
            raise ValueError(f'Duplicate example ID: {eid}')
        result[eid] = row
    return result


def validate_target(target):
    if not isinstance(target, dict) or set(target) != {'narrative', 'atomic'}:
        raise ValueError('Target must be a narrative/atomic object')
    if not isinstance(target['narrative'], list) or not all(isinstance(s, str) and s.strip() for s in target['narrative']):
        raise ValueError('Invalid narrative')
    if not isinstance(target['atomic'], list):
        raise ValueError('Invalid atomic list')
    for item in target['atomic']:
        if not isinstance(item, dict) or set(item) != {'key', 'value'} or not all(isinstance(v, str) and v.strip() for v in item.values()):
            raise ValueError('Invalid atomic item')


def history_digests(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row['history_sha256'], []).append(row)
    return {h:ev.sha256_text(json.dumps(items,ensure_ascii=False,sort_keys=True)) for h,items in grouped.items()}


def collect():
    queue = unique_rows(read_rows(PILOT / 'dependency_review_queue.jsonl'))
    reviews = unique_rows({**r, 'agent': p.parent.name} for p in sorted(AGENTS.glob('*/reviews.jsonl')) for r in read_rows(p))
    proposals = unique_rows({**r, 'agent': p.parent.name} for p in sorted(AGENTS.glob('*/proposals.jsonl')) for r in read_rows(p))
    if set(reviews) != set(queue):
        raise ValueError(f'Review accounting: {len(set(queue)-set(reviews))} missing, {len(set(reviews)-set(queue))} unexpected')
    for eid, review in reviews.items():
        if any(review[k] != queue[eid][k] for k in ('history_sha256', 'session')):
            raise ValueError(f'Review identity mismatch: {eid}')
        if review['verdict'] not in {'keep', 'repair', 'uncertain'} or not all(review.get(k) for k in ('evidence', 'rationale', 'reviewed_scope')):
            raise ValueError(f'Incomplete review: {eid}')
    if set(proposals) != {eid for eid, r in reviews.items() if r['verdict'] == 'repair'}:
        raise ValueError('Every repair review must have exactly one proposal')
    for eid, proposal in proposals.items():
        validate_target(proposal['replacement_target'])
        if not proposal.get('source_evidence') or not proposal.get('rationale') or proposal['agent'] != reviews[eid]['agent']:
            raise ValueError(f'Incomplete/misowned proposal: {eid}')
    return reviews, proposals


def replay(rows, proposals):
    state = []; previous = None; expected_session = 1; formats = None
    for original in rows:
        row = copy.deepcopy(original)
        history = row['history_sha256']
        if history != previous:
            state = []; expected_session = 1; previous = history
            meta = json.loads((ROOT / 'runs' / row['source']['run_id'] / 'manifest.json').read_text())['metadata']
            formats = meta['prompts']['extraction_message_formats']
        if row['session'] != expected_session:
            raise ValueError('Non-contiguous history/session sequence')
        expected_session += 1
        session = row['messages'][-2]['content']
        match = re.fullmatch(r'New session (\d+) of (\d+), dated (.*?)\. Turns \(JSON\):\n(.*)', session, re.S)
        if not match or int(match[1]) != row['session']:
            raise ValueError('Invalid source session')
        proposal = proposals.get(row['example_id'])
        target = row['messages'][-1]['content']
        if proposal:
            if ev.sha256_text(target) != proposal['original_target_sha256']:
                raise ValueError('Proposal original-target hash mismatch')
            target = json.dumps(proposal['replacement_target'], ensure_ascii=False, separators=(',', ':'))
        data = json.loads(target)
        validate_target(data)
        parts = input_parts(state, session, formats)
        row['messages'] = [row['messages'][0]] + [{'role':'user','content':p} for p in parts] + [{'role':'assistant','content':target}]
        memory.apply_extraction(state, data, row['session'], match[3], memory.session_text(json.loads(match[4])))
        yield row


def build(decisions_path):
    if OUTPUT.exists():
        raise ValueError(f'Snapshot exists; refusing overwrite: {OUTPUT}')
    reviews, proposals = collect()
    decisions = unique_rows(read_rows(decisions_path))
    if set(decisions) != set(proposals) | {eid for eid,r in reviews.items() if r['verdict']=='uncertain'}:
        raise ValueError('Adjudicate every proposal and uncertain review exactly once')
    for eid, decision in decisions.items():
        if decision['decision'] not in {'accept', 'retain_original'} or not decision.get('rationale') or not decision.get('source_evidence'):
            raise ValueError(f'Incomplete decision: {eid}')
        if decision['decision']=='accept' and eid not in proposals:
            raise ValueError('Cannot accept absent proposal')
        if eid in proposals and decision.get('proposal_sha256') != ev.sha256_text(json.dumps(proposals[eid],ensure_ascii=False,sort_keys=True)):
            raise ValueError(f'Proposal changed after adjudication: {eid}')
    accepted = {eid:p for eid,p in proposals.items() if decisions[eid]['decision']=='accept'}
    pilot_manifest = json.loads((PILOT / 'manifest.json').read_text())
    for name, digest in pilot_manifest['artifacts'].items():
        if ev.sha256_file(PILOT/name) != digest:
            raise ValueError(f'Pilot changed: {name}')
    folder = OUTPUT / 'copy_2_repaired'
    folder.mkdir(parents=True)
    ev.atomic_jsonl(folder/'train.jsonl', replay(read_rows(PILOT/'copy_2_repaired_pilot/train.jsonl'), accepted))
    shutil.copyfile(PILOT/'copy_1_original/dev.jsonl', folder/'dev.jsonl')
    ev.atomic_jsonl(OUTPUT/'reviews.jsonl', reviews.values())
    ev.atomic_jsonl(OUTPUT/'proposals.jsonl', proposals.values())
    ev.atomic_jsonl(OUTPUT/'decisions.jsonl', decisions.values())
    original = unique_rows(read_rows(PILOT/'copy_1_original/train.jsonl'))
    pilot = unique_rows(read_rows(PILOT/'copy_2_repaired_pilot/train.jsonl'))
    changes = []
    for row in read_rows(folder/'train.jsonl'):
        eid = row['example_id']; old = original[eid]; prior = pilot[eid]
        if old['messages'] != row['messages']:
            changes.append({'example_id':eid,'history_sha256':row['history_sha256'],'session':row['session'],
                'target_changed_from_original':old['messages'][-1]!=row['messages'][-1],
                'input_changed_from_original':old['messages'][:-1]!=row['messages'][:-1],
                'input_changed_from_pilot':prior['messages'][:-1]!=row['messages'][:-1],
                'target_sha256':ev.sha256_text(row['messages'][-1]['content']),
                'messages_sha256':ev.sha256_text(json.dumps(row['messages'],ensure_ascii=False,sort_keys=True))})
    ev.atomic_jsonl(OUTPUT/'changes.jsonl', changes)
    histories = sorted({r['history_sha256'] for r in reviews.values()})
    manifest = {'status':'awaiting_final_context_review','reviewed_rows':len(reviews),
        'review_verdicts':dict(Counter(r['verdict'] for r in reviews.values())),
        'additional_target_repairs':len(accepted),'total_target_repairs':sum(c['target_changed_from_original'] for c in changes),
        'reviewed_histories':histories,'original_copy':str(PILOT/'copy_1_original'),
        'history_sha256':{h:d for h,d in history_digests(read_rows(folder/'train.jsonl')).items() if h in histories},
        'pilot_manifest_sha256':ev.sha256_file(PILOT/'manifest.json'),
        'artifacts':{str(p.relative_to(OUTPUT)):ev.sha256_file(p) for p in OUTPUT.rglob('*.jsonl')},
        'code_sha256':ev.sha256_file(Path(__file__)),
        'quality_scope':'Six initial target fixes and 155 dependent rows reviewed. Remaining corpus not exhaustively reviewed. Dev teacher outputs unchanged, not gold labels.',
        'no_paid_calls':True,'no_training_run':True}
    ev.atomic_json(OUTPUT/'manifest.json', manifest)
    print(json.dumps({k:v for k,v in manifest.items() if k not in {'artifacts','reviewed_histories'}},indent=2))


def verify():
    manifest = json.loads((OUTPUT/'manifest.json').read_text())
    if ev.sha256_file(PILOT/'manifest.json') != manifest['pilot_manifest_sha256']:
        raise ValueError('Pilot provenance changed')
    if ev.sha256_file(Path(__file__)) != manifest['code_sha256']:
        raise ValueError('Builder changed since export')
    for name,digest in manifest['artifacts'].items():
        if ev.sha256_file(OUTPUT/name) != digest:
            raise ValueError(f'Artifact changed: {name}')
    decisions = unique_rows(read_rows(OUTPUT/'decisions.jsonl'))
    accepted = {p['example_id']:p for p in read_rows(OUTPUT/'proposals.jsonl') if decisions[p['example_id']]['decision']=='accept'}
    expected = replay(read_rows(PILOT/'copy_2_repaired_pilot/train.jsonl'), accepted)
    from itertools import zip_longest
    count = 0; ids = set(); histories = set()
    for a,b in zip_longest(expected,read_rows(OUTPUT/'copy_2_repaired/train.jsonl')):
        if a != b or b is None or b['example_id'] in ids:
            raise ValueError('Replay/accounting mismatch')
        ids.add(b['example_id']); histories.add(b['history_sha256']); count += 1
    if ev.sha256_file(OUTPUT/'copy_2_repaired/dev.jsonl') != ev.sha256_file(PILOT/'copy_1_original/dev.jsonl'):
        raise ValueError('Dev changed')
    print(json.dumps({'replay_verified':True,'training_rows':count,'histories':len(histories),'dev_identical':True,'status':manifest['status']},indent=2))


def seal(attestations_path):
    verify()
    manifest = json.loads((OUTPUT/'manifest.json').read_text())
    if manifest['status'] != 'awaiting_final_context_review':
        raise ValueError('Snapshot already sealed')
    rows = list(read_rows(attestations_path))
    observed = set()
    for row in rows:
        h = row['history_sha256']
        if h in observed or h not in manifest['reviewed_histories']:
            raise ValueError('Duplicate/unexpected context review')
        observed.add(h)
        if row['exported_history_sha256'] != manifest['history_sha256'][h] or row['status'] != 'checked' or not row.get('rationale') or not row.get('reviewer'):
            raise ValueError('Invalid final-context review')
    if observed != set(manifest['reviewed_histories']):
        raise ValueError('Missing final-context review')
    ev.atomic_jsonl(OUTPUT/'final_context_reviews.jsonl',rows)
    manifest['artifacts']['final_context_reviews.jsonl'] = ev.sha256_file(OUTPUT/'final_context_reviews.jsonl')
    manifest['status'] = 'scoped_repair_complete'
    manifest['final_context_reviewed_histories'] = len(rows)
    manifest['source_ambiguities_retained'] = sum(r['verdict']=='uncertain' for r in read_rows(OUTPUT/'reviews.jsonl'))
    ev.atomic_json(OUTPUT/'manifest.json',manifest)
    print('Scoped repair complete. This is not corpus-wide factual certification.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build','verify','seal'])
    parser.add_argument('--decisions', type=Path)
    parser.add_argument('--attestations', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        if args.decisions is None:
            parser.error('build requires --decisions')
        build(args.decisions)
    elif args.command == 'seal':
        if args.attestations is None:
            parser.error('seal requires --attestations')
        seal(args.attestations)
    else:
        verify()
