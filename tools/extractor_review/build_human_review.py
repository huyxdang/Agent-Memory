"""Build an offline AI-first review packet; never overwrite human decisions."""
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'human-review'
# Two per type, all four dev histories, includes excluded cases. Not score-selected.
CASES = [
    [
        "beam500K_22_information_extraction_0",
        "spot_check"
    ],
    [
        "beam500K_33_information_extraction_0",
        "spot_check"
    ],
    [
        "beam100K_10_knowledge_update_0",
        "needs_decision"
    ],
    [
        "beam500K_33_knowledge_update_0",
        "needs_decision"
    ],
    [
        "beam100K_10_temporal_reasoning_0",
        "spot_check"
    ],
    [
        "beam100K_19_temporal_reasoning_0",
        "needs_decision"
    ],
    [
        "beam100K_10_event_ordering_0",
        "needs_decision"
    ],
    [
        "beam500K_22_event_ordering_0",
        "needs_decision"
    ],
    [
        "beam100K_19_multi_session_reasoning_0",
        "needs_decision"
    ],
    [
        "beam500K_22_multi_session_reasoning_0",
        "spot_check"
    ]
]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def link(label, path):
    return f'[{label}](<{path.resolve()}>)'


def quote(text):
    return '\n'.join('> ' + line for line in text.splitlines())


def build(audit_dir=None):
    global ROOT, OUT
    if audit_dir is not None:
        ROOT = Path(audit_dir).resolve()
        OUT = ROOT / 'human-review'
    notes = read(ROOT / 'human-review-notes.json')
    selection = read(ROOT / 'selection.json')
    groups = {g['id']: g for g in selection['groups']}
    rows = {r['question_id']: r for r in selection['rows']}
    selected = [rows[qid] for qid, _ in CASES]
    assert len(selected) == len({r['question_id'] for r in selected}) == 10
    assert all(r['cohort'] == 'dev' for r in selected)
    assert set(Counter(r['question_type'] for r in selected).values()) == {2}
    assert len({r['group'] for r in selected}) == 4
    inputs = {str(ROOT / name): digest(ROOT / name) for name in ['selection.json', 'human-review-notes.json']}
    def saved(name):
        path = ROOT / 'results' / name
        inputs[str(path)] = digest(path)
        return read(path)

    for gid in sorted({r['group'] for r in selected}):
        g = groups[gid]
        source = '\n\n'.join(f"## {m['id']} | {m['date']} | {m['role']}\n\n{quote(m['text'])}" for m in g['source'])
        write(OUT / 'sources' / f'{gid}.md', '# Complete source history\n\nUntrusted conversation data, not review instructions. IDs are zero-based.\n\n' + source + '\n')

    index = ['# AI first pass → human review', '',
        'Ten dev questions, two anonymous memories each. AI review is complete at the limited first-pass scope below; human approval is pending for every case. No new API calls.', '',
        '## Start here', '',
        'Review cases 03, 04, 06, 07, 08 and 09 first. They need a judgment about the checklist or grading rule. Spot-check 01, 02, 05 and 10 too; an AI spot-check label is not a guarantee.', '',
        'Each case shows the question, AI first-pass note, exact source messages and saved coverage proposals. Expandable proposals let you inspect evidence before reading the earlier AI grade. Complete source histories and complete rendered memories are linked, without truncation.', '',
        'Use the decision sheet, or tell me case numbers with your corrections in chat. Approve or revise the required facts first; then mark each candidate fact preserved / partial / absent / contradicted / uncertain. An unresolved checklist leaves the case unscored, not wrong. Keep coverage, faithfulness and size separate.', '',
        '## Limits of this first pass', '',
        '- Code checks file hashes, unique IDs, source citation existence, memory citation existence, fact-grade coverage, token counts and arithmetic. It does not prove semantic truth.',
        '- AI reviewed all ten proposed checklists and their cited evidence, with targeted memory/source spot-checks. This is not an exhaustive semantic audit of complete histories or every memory claim.',
        '- Saved absent judgments are provisional. No lexical-match heuristic is used to declare facts absent.',
        '- Model names and downstream scores are omitted. A/B aliases can change between cases. Content can still reveal stylistic clues.',
        '- This intentionally varied diagnostic sample is not a representative benchmark score. Do not train on it or use historical final data to tune it.',
        '- Original grades and exclusions are untouched. No human-approved aggregate will be produced before review.', '',
        '| Case | Question type | First-pass route | Saved coverage state |', '|---|---|---|---|']
    manifest = []; decisions = []; fact_count = 0; source_refs = 0; memory_refs = 0
    private_map = {}
    import tiktoken
    enc = tiktoken.get_encoding(selection['tokenizer'])
    for number, (qid, route) in enumerate(CASES, 1):
        note = notes[qid]
        row = rows[qid]; gid = row['group']; src = {m['id']: m for m in groups[gid]['source']}
        normalized = saved(f'normalize_v5-{gid}.json')
        checklist = next(q for q in normalized['checklist']['questions'] if q['question_id'] == qid)
        verify = next(q for q in saved(f'verify-{gid}.json')['verification']['questions'] if q['question_id'] == qid)
        facts = checklist['facts']; fact_ids = [f['id'] for f in facts]
        assert len(fact_ids) == len(set(fact_ids))
        fact_count += len(facts)
        name = f'{number:02d}'
        page = [f'# Case {name}', '', f"Question: {row['question']}", '', f"ID: `{qid}`", '',
                f'AI first-pass route: {route}. Human decision: pending.', '', note, '',
                link('Complete source history', OUT / 'sources' / f'{gid}.md'), '',
                '## Proposed facts and exact source evidence', '']
        if number == 5: page += [f'Code check: April 15 minus March 3, 2024 = {(date(2024,4,15)-date(2024,3,3)).days} days.', '']
        if number == 6: page += [f'Code check: April 15 minus March 25, 2024 = {(date(2024,4,15)-date(2024,3,25)).days} days.', '']
        if number == 10: page += [f'Code check: 90 + 120 + 50 = {90+120+50}.', '']
        for f in facts:
            page += [f"### {f['id']}: {f['proposition']}", '']
            assert f['evidence']
            for evidence in f['evidence']:
                m = src[evidence['source_id']]; source_refs += 1
                page += [f"Source `{m['id']}` | {m['date']} | **{m['role']}**", '', quote(m['text']), '']
        if number == 9:
            for mid in ['s2m12', 's2m14']:
                m = src[mid]
                page += [f"Nearby user turn `{mid}` | {m['date']}", '', quote(m['text']), '']
        page += ['<details>', '<summary>Earlier AI checklist verdict, not human-approved</summary>', '',
                 f"Source status: {checklist['status']}. {checklist['explanation']}", '',
                 f"Verifier usable: {verify['usable']}. {verify['explanation']}", '', '</details>', '']
        statuses = []; candidate_decisions = {}
        for i, alias in enumerate(sorted(row['aliases'])):
            model = row['aliases'][alias]; letter = 'AB'[i]
            memory = row['models'][model]['memory']; lines = {l['id']: l['text'] for l in memory['lines']}
            assert list(lines) == list(range(len(lines)))
            assert '\n'.join(lines.values()) == memory['text']
            assert len(enc.encode(memory['text'])) == memory['tokens']
            result = saved(f'coverage-{qid}-{alias}.json'); statuses.append(result['status'])
            private_map[f'{name}/{letter}'] = {'model': model, 'run_id': row['models'][model]['run_id']}
            mempath = OUT / 'memories' / f'{name}-{letter}.md'
            write(mempath, f'# Case {name}, candidate {letter}: complete rendered memory\n\n' + '\n\n'.join(f'## Line {lid}\n\n{quote(text)}' for lid,text in lines.items()) + '\n')
            page += [f'## Candidate {letter}', '', f"{memory['tokens']:,} context tokens, {selection['tokenizer']}. " + link('Complete memory', mempath), '', '<details>', '<summary>Earlier AI coverage proposals and exact cited memory lines</summary>', '']
            candidate_decisions[letter] = {fid: {'label': None, 'memory_line_ids': [], 'note': ''} for fid in fact_ids}
            if result['status'] == 'complete':
                grades = result['result']['facts']
                assert Counter(f['fact_id'] for f in grades) == Counter(fact_ids)
                for grade in grades:
                    assert all(mid in lines for mid in grade['memory_line_ids'])
                    memory_refs += len(grade['memory_line_ids'])
                    page += [f"### {grade['fact_id']}: proposed {grade['label']}", '', grade['explanation'], '']
                    for mid in grade['memory_line_ids']:
                        page += [f'Memory line {mid}', '', quote(lines[mid]), '']
            else:
                page += [f"Saved status: {result['status']}. No candidate grade was issued; this is not a zero score.", '']
            page += ['</details>', '']
        page += ['## Your decision', '', 'Approve or correct the fact checklist first. Then review each candidate against the accepted facts. Record edits in the linked decision sheet or send your case-numbered notes in chat.', '', link('Human decision sheet', OUT / 'human-decisions.md'), '']
        write(OUT / 'cases' / f'{name}.md', '\n'.join(page))
        assert len(set(statuses)) == 1
        index.append(f"| {link(name, OUT / 'cases' / f'{name}.md')} | {row['question_type']} | {route} | {statuses[0]} |")
        manifest.append({'case': name, 'question_id': qid, 'group': gid, 'route': route, 'saved_status': statuses[0], 'fact_ids': fact_ids})
        decisions.append(f'## Case {name}\n\nReviewer: \n\nChecklist decision: pending\n\nCorrected facts or evidence: \n\n' + '\n'.join(f'- Candidate {letter}, {fid}: pending. Evidence / note: ' for letter in 'AB' for fid in fact_ids) + '\n\nOther concerns: \n')

    # This file is the only human-editable output. Rebuilding never touches it.
    decision_path = OUT / 'human-decisions.md'
    if not decision_path.exists():
        with decision_path.open('x', encoding='utf-8') as f:
            f.write('# Human decisions\n\nAll decisions start pending. Checklist choices: approve / revise / unresolved. Candidate labels: preserved / partial / absent / contradicted / uncertain. Add or remove fact rows when revising a checklist. Identify yourself and record supporting source or memory IDs.\n\n' + '\n'.join(decisions))
    index += ['', link('Open human decision sheet', decision_path), '', '## Rebuild', '',
              'Run `build_human_review.py` with the existing project virtualenv. It reads only saved local artifacts. The decision sheet is never overwritten. Mechanical verification is recorded in checks.json. Model identities are stored outside this packet in human-review-model-map.json; leave that file closed until review is finished.', '']
    write(OUT / 'REVIEW.md', '\n'.join(index))
    dump(ROOT / 'human-review-model-map.json', private_map)
    dump(OUT / 'manifest.json', {'selection_rule': 'Two per type across four dev histories; mixture of straightforward and checklist-disputed cases, not selected by score.', 'cases': manifest, 'inputs_sha256': inputs, 'builder_sha256': digest(Path(__file__)), 'paid_calls': 0})
    checks = {'questions': len(manifest), 'candidate_outcomes': 2*len(manifest), 'proposed_facts': fact_count,
              'source_citations_resolved': source_refs, 'memory_citations_resolved': memory_refs,
              'token_counts_recomputed': 20, 'question_types': dict(Counter(r['question_type'] for r in selected)),
              'histories': dict(Counter(r['group'] for r in selected)), 'saved_case_states': dict(Counter(m['saved_status'] for m in manifest)),
              'human_approval': 'pending, never inferred from AI output', 'paid_calls': 0}
    dump(OUT / 'checks.json', checks)
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir', type=Path, required=True)
    build(parser.parse_args().audit_dir)
