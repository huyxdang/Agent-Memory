"""Read-only checks on the frozen paired dataset artifacts."""
import json
from itertools import zip_longest
from pathlib import Path
import longmemeval_eval as ev
from build_training_copies import patched_target

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'work/training_copies_v1'


def verify():
    manifest = json.loads((OUTPUT/'manifest.json').read_text())
    for f,h in manifest['artifacts'].items():
        assert ev.sha256_file(OUTPUT/f)==h, f
    for f,h in manifest['source_runs'].items():
        assert ev.sha256_file(ROOT/f)==h, f
    for f,h in manifest['source_hashes'].items():
        assert ev.sha256_file(ROOT/f)==h, f
    changes = {r['example_id']:r for r in map(json.loads,(OUTPUT/'changes.jsonl').read_text().splitlines())}
    repairs = {r['review_id']:r for r in json.loads((OUTPUT/'repair_spec.json').read_text())['repairs']}
    observed = {}; split_histories = {}; total_targets = total_inputs = 0
    for split in ('train','dev'):
        seen = set(); histories = set(); changed_ids = set()
        with (OUTPUT/f'copy_1_original/{split}.jsonl').open() as left, (OUTPUT/f'copy_2_repaired_pilot/{split}.jsonl').open() as right:
            for a,b in zip_longest(left,right):
                assert a is not None and b is not None
                old,new = json.loads(a),json.loads(b)
                eid = old['example_id']; assert eid not in seen; seen.add(eid)
                histories.add(old['history_sha256'])
                assert {k:v for k,v in old.items() if k!='messages'} == {k:v for k,v in new.items() if k!='messages'}
                assert old['messages'][0]==new['messages'][0]
                assert old['messages'][-2]==new['messages'][-2]  # unchanged source session
                original_hash = ev.sha256_text('\n\n'.join(m['content'] for m in old['messages'][1:-1]))
                assert original_hash == old['source']['original_prompt_sha256']
                assert ev.sha256_text(old['messages'][-1]['content'])==old['source']['original_target_sha256']
                tc = old['messages'][-1]!=new['messages'][-1]
                ic = old['messages'][:-1]!=new['messages'][:-1]
                if tc or ic:
                    assert split=='train'; changed_ids.add(eid)
                    change=changes[eid]; assert tc==change['target_changed'] and ic==change['input_changed']
                    assert ev.sha256_text(new['messages'][-1]['content'])==change['repaired_target_sha256']
                    if tc:
                        expected=patched_target(json.loads(old['messages'][-1]['content']),repairs[change['review_id']]['operations'])
                        assert expected==json.loads(new['messages'][-1]['content'])
                total_targets+=tc; total_inputs+=ic
        if split=='train': assert changed_ids==set(changes)
        else: assert ev.sha256_file(OUTPUT/'copy_1_original/dev.jsonl')==ev.sha256_file(OUTPUT/'copy_2_repaired_pilot/dev.jsonl')
        observed[split]={'examples':len(seen),'histories':len(histories)}
        split_histories[split]=histories
    assert split_histories['train'].isdisjoint(split_histories['dev'])
    assert total_targets==manifest['target_repairs']==6
    assert total_inputs==manifest['rebuilt_inputs']
    queue=[json.loads(l) for l in (OUTPUT/'dependency_review_queue.jsonl').read_text().splitlines()]
    assert {r['example_id'] for r in queue}=={k for k,v in changes.items() if v['input_changed']}
    print(json.dumps({'verified':observed,'target_repairs':total_targets,'changed_inputs':total_inputs,
                      'dev_identical':True,'sources_unchanged':True},indent=2))


if __name__=='__main__':
    verify()
