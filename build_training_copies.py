"""Export paired original/repaired pilot datasets offline, with immutable snapshots."""
import copy
import json
import re
from collections import defaultdict
from pathlib import Path
import longmemeval_eval as ev
import memory

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "work/longmemeval_split_feasibility"
REVIEW = ROOT / "work/trace_quality_review"
OUTPUT = ROOT / "work/training_copies_v1"


def patched_target(target, operations):
    result = copy.deepcopy(target)
    for op in operations:
        parent = result
        for key in op['path'][:-1]:
            parent = parent[key]
        key = op['path'][-1]
        if parent[key] != op['old']:
            raise ValueError('Repair precondition mismatch')
        if op.get('remove'):
            del parent[key]
        else:
            parent[key] = op['value']
    return result


def input_parts(lines, session, formats):
    groups = defaultdict(list)
    for line in lines:
        groups[line['session']].append(line)
    parts = [formats['memory'].format(session_number=n, timestamp=group[0]['date'],
              lines='\n'.join(memory.line_text(line) for line in group)) for n, group in sorted(groups.items())]
    return (parts or [formats['empty_memory']]) + [session]


def main():
    if OUTPUT.exists():
        raise RuntimeError(f'Immutable snapshot already exists: {OUTPUT}. Do not overwrite it.')
    sample = json.loads((REVIEW / 'sample.json').read_text())
    packets = {p['review_id']: p for p in sample['packets']}
    spec = json.loads((REVIEW / 'repairs_v1.json').read_text())
    repairs = {packets[r['review_id']]['pointer']['example_id']: r for r in spec['repairs']}
    inputs = [SOURCE / f'candidate_10dev_{s}_updates.jsonl' for s in ('train','dev')]
    inputs += [REVIEW / n for n in ('sample.json','repairs_v1.json','review_annotations.json')]
    inputs += [SOURCE / 'report.json']
    source_hashes = {str(p.relative_to(ROOT)): ev.sha256_file(p) for p in inputs}
    source_hashes.update({p.name: ev.sha256_file(p) for p in [Path(__file__), ROOT / 'memory.py']})
    streams = {}; changes = []; pending = []; snapshots = {}; used_repairs = set()
    OUTPUT.mkdir(parents=True)
    for name in ('copy_1_original','copy_2_repaired_pilot'):
        (OUTPUT / name).mkdir()
    try:
        for split in ('train','dev'):
            pointers = [json.loads(l) for l in (SOURCE / f'candidate_10dev_{split}_updates.jsonl').read_text().splitlines()]
            groups = defaultdict(list)
            for pointer in pointers:
                groups[(pointer['run_id'],pointer['results_line'])].append(pointer)
            for name in ('copy_1_original','copy_2_repaired_pilot'):
                streams[name] = (OUTPUT / name / f'{split}.jsonl').open('w')
            for (rid, line_number), group in sorted(groups.items()):
                path = ROOT / 'runs' / rid
                meta = json.loads((path / 'manifest.json').read_text())['metadata']
                for filename in ('manifest.json','results.jsonl'):
                    key = str((path / filename).relative_to(ROOT))
                    if key not in snapshots:
                        snapshots[key] = ev.sha256_file(path / filename)
                with (path / 'results.jsonl').open() as source:
                    record = next(json.loads(l) for n,l in enumerate(source,1) if n == line_number)
                group.sort(key=lambda p:p['session'])
                assert [p['session'] for p in group] == list(range(1,record['history']['sessions']+1))
                prompts = meta['prompts']; formats = prompts['extraction_message_formats']
                system = prompts.get('extraction_system') or prompts['extraction_system_template'].format(
                    subject=record['memory'].get('subject') or memory.USER_SUBJECT)
                state = []; changed_keys = set()
                for pointer in group:
                    n = pointer['session']; call = record['memory']['extraction_calls'][n-1]
                    assert call['session'] == n and call['ok'] and call['finish_reason'] == 'stop'
                    assert record['history_sha256'] == pointer['history_sha256']
                    assert ev.sha256_text(call['content']) == pointer['target_sha256']
                    original_parts = input_parts([l for l in record['memory']['lines'] if l['session'] < n],call['session_message'],formats)
                    assert ev.sha256_text('\n\n'.join(original_parts)) == pointer['prompt_sha256'] == call['prompt_sha256']
                    repaired_parts = input_parts(state,call['session_message'],formats)
                    original = json.loads(call['content']); replacement = repairs.get(pointer['example_id']) if split == 'train' else None
                    if replacement:
                        packet = packets[replacement['review_id']]
                        assert packet['pointer']['target_sha256'] == pointer['target_sha256']
                        data = patched_target(original,replacement['operations'])
                        content = json.dumps(data,ensure_ascii=False,separators=(',',':'))
                        used_repairs.add(pointer['example_id'])
                    else:
                        data = original; content = call['content']
                    changed_input = repaired_parts != original_parts
                    dependent_keys = sorted({a['key'] for a in data['atomic']} & changed_keys)
                    if changed_input:
                        pending.append({'example_id':pointer['example_id'],'history_sha256':pointer['history_sha256'],
                                        'session':n,'status':'pending_semantic_dependency_review','uses_changed_atomic_keys':dependent_keys})
                    for name, parts, target in [('copy_1_original',original_parts,call['content']),('copy_2_repaired_pilot',repaired_parts,content)]:
                        row = {'example_id':pointer['example_id'],'history_sha256':pointer['history_sha256'],'session':n,
                            'messages':[{'role':'system','content':system}]+[{'role':'user','content':p} for p in parts]+[{'role':'assistant','content':target}],
                            'source':{'run_id':rid,'question_id':pointer['question_id'],'results_line':line_number,
                                      'original_prompt_sha256':call['prompt_sha256'],'original_target_sha256':pointer['target_sha256']}}
                        streams[name].write(json.dumps(row,ensure_ascii=False)+'\n')
                    if replacement or changed_input:
                        changes.append({'example_id':pointer['example_id'],'history_sha256':pointer['history_sha256'],'session':n,
                            'target_changed':bool(replacement),'input_changed':changed_input,
                            'review_id':replacement['review_id'] if replacement else None,
                            'reason':replacement['reason'] if replacement else 'Rebuilt prior-memory input after earlier target repair',
                            'original_target_sha256':pointer['target_sha256'],'repaired_target_sha256':ev.sha256_text(content),
                            'original_prompt_sha256':call['prompt_sha256'],'repaired_prompt_sha256':ev.sha256_text('\n\n'.join(repaired_parts))})
                    if replacement:
                        old = {a['key']:a['value'] for a in original['atomic']}; new = {a['key']:a['value'] for a in data['atomic']}
                        changed_keys.update(k for k in old.keys()|new.keys() if old.get(k)!=new.get(k))
                    match = re.fullmatch(r'New session (\d+) of (\d+), dated (.*?)\. Turns \(JSON\):\n(.*)',call['session_message'],re.S)
                    assert match
                    memory.apply_extraction(state,data,n,match[3],memory.session_text(json.loads(match[4])))
            for stream in streams.values(): stream.close()
        assert used_repairs == set(repairs)
        assert ev.sha256_file(OUTPUT/'copy_1_original/dev.jsonl') == ev.sha256_file(OUTPUT/'copy_2_repaired_pilot/dev.jsonl')
        for f,h in snapshots.items(): assert ev.sha256_file(ROOT/f)==h
        ev.atomic_json(OUTPUT/'repair_spec.json',spec)
        ev.atomic_jsonl(OUTPUT/'changes.jsonl',changes)
        ev.atomic_jsonl(OUTPUT/'dependency_review_queue.jsonl',pending)
        ev.atomic_json(OUTPUT/'frozen_split.json',json.loads((SOURCE/'report.json').read_text())['fixed_10_dev_candidate'])
        artifacts = {str(p.relative_to(OUTPUT)):ev.sha256_file(p) for p in sorted(OUTPUT.rglob('*.json*'))}
        manifest = {'status':'paired_pilot_exported_not_training_ready','scope':'six reviewed targets; remaining training data not quality approved',
            'source_hashes':source_hashes,'source_runs':snapshots,'artifacts':artifacts,
            'target_repairs':len(used_repairs),'rebuilt_inputs':len(pending),'dependency_review_pending':len(pending),
            'dev_identical':True,'code':ev.git_metadata(),
            'notes':['Both arms preserve identical example IDs, ordering, source sessions, split and extractor system prompts.',
                     'Only corrected target text and its downstream memory inputs differ. No row filtering.',
                     'Provider cache hints are transport-only and omitted from both exports; text and message boundaries retained.',
                     'No hidden reasoning text is included. No benchmark question, reference answer or judge verdict is added to messages.',
                     'Dev teacher targets are unchanged and not gold labels. Final downstream accuracy requires a separately frozen evaluation.',
                     'Downstream inputs have been rebuilt, not semantically approved. Do not train either arm yet.',
                     'Compare using the same student checkpoint, prompt, hyperparameters, seed/order, training budget and answerer/judge. Record differing token lengths.']}
        ev.atomic_json(OUTPUT/'manifest.json',manifest)
        print(json.dumps({k:manifest[k] for k in ('status','target_repairs','rebuilt_inputs','dev_identical')},indent=2))
    finally:
        for stream in streams.values(): stream.close()


if __name__ == '__main__':
    main()
