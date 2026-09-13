"""Package five exact matched saved extraction calls for local human review."""
import hashlib
import html
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent / 'diagnostics/extractor-eval-20260913'
RUNS = Path('/private/tmp/gemma-beam-dev-20260912/runs')
CASES = [
    ('dev_beam100K_10', 1, 's0m6', 'Meeting a friend', 'Does the update retain when and where the user met Michael?', 'The source reports a meeting. Check the person, festival and date; do not treat Michael as the user just because his name appears.'),
    ('dev_beam100K_19', 1, 's0m8', 'Parents living nearby', 'Does the update retain how far away the user’s parents live?', 'Check the distance and its relationship to the user and parents. Other numbers in the message are ages, not distance.'),
    ('dev_beam500K_22', 1, 's0m6', 'Profession and age', 'Does the update retain both the user’s profession and age?', 'Check both attributes. Preserving just one is partial. The annual income is a separate attribute.'),
    ('dev_beam500K_33', 2, 's1m8', 'A practice goal', 'Does the update distinguish the starting free-throw percentage from the target?', 'A desired target is not an achieved result. Check the two values and whether their roles are preserved.'),
    ('dev_beam500K_33', 3, 's2m10', 'An improvement already made', 'Does the update retain the change in three-point accuracy?', 'The user reports an improvement already made, not just a plan. Check old and new values, the sport statistic and the status of the change.'),
]


def read(path):
    return json.loads(path.read_text())


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def render_update(raw):
    update = json.loads(raw)
    assert set(update) == {'narrative', 'atomic'}
    out = ['<h4>Narrative</h4><ul>']
    out += ['<li>' + html.escape(x) + '</li>' for x in update['narrative']]
    out += ['</ul><h4>Facts</h4><ul>']
    out += ['<li><b>' + html.escape(x['key']) + '</b>: ' + html.escape(x['value']) + '</li>' for x in update['atomic']]
    return ''.join(out) + '</ul>'


def main():
    selection = read(AUDIT / 'selection.json')
    cfg = read(RUNS / 'gemma3-base-beam-dev80-001/modal/configuration.json')
    tasks = []; mapping = {}; provenance = []
    for n, (gid, session, source_id, title, question, ai_note) in enumerate(CASES, 1):
        group = next(g for g in selection['groups'] if g['id'] == gid)
        tier, cid = gid.removeprefix('dev_').split('_')
        history = next(h for h, qs in cfg['questions'].items() if qs[0]['conversation'] == int(cid) and qs[0]['question_id'].startswith(tier + '_'))
        calls = {}
        for model, run in [('base', 'gemma3-base-beam-dev80-001'), ('finetuned', 'gemma3-finetuned-beam-dev80-001')]:
            path = RUNS / run / 'modal/memories' / f'{history}.json'
            call = next(c for c in read(path)['calls'] if c['session'] == session)
            assert call['status'] == 'complete' and call['finish_reason'] == 'stop'
            calls[model] = call
            provenance.append({'case': n, 'model': model, 'run': run, 'history_sha256': history,
                               'session': session, 'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                               'prompt_sha256': call['prompt_sha256'], 'messages_sha256': sha(call['messages']),
                               'output_sha256': sha(call['content'])})
        assert calls['base']['messages'] == calls['finetuned']['messages'], 'Only exact matched message inputs qualify'
        source = next(m for m in group['source'] if m['id'] == source_id)
        assert source['text'] in calls['base']['messages'][-1]['content'] or source['text'] in json.loads(calls['base']['messages'][-1]['content'].split('Turns (JSON):\n')[-1])[int(source_id.split('m')[1])]['content']
        mi = group['source'].index(source)
        neighbors = group['source'][max(0,mi-2):mi+3]
        order = ['base', 'finetuned']; random.Random(f'review-20260913-{n}').shuffle(order)
        case_id = f'BEAM-UPDATE-{n:02d}'
        data = {'case_id': case_id, 'title': f'{n}/5 · {title}', 'question': question,
                'scope': f'Real saved dev extraction · update {session} · identical complete input for both candidates. This card evaluates only the stated fact, not the entire memory.',
                'source_html': '<p><b>' + html.escape(source['role'].upper() + ' · ' + source['date'] + ' · ' + source_id) + '</b></p><p style="font-size:18px;line-height:1.65">' + html.escape(source['text']) + '</p>',
                'neighbors': '\n\n'.join(f"{m['id']} | {m['date']} | {m['role']}\n{m['text']}" for m in neighbors),
                'full_input': '\n\n'.join(f"MESSAGE {i+1} · {m['role']}\n{m['content']}" for i,m in enumerate(calls['base']['messages'])),
                'ai_note': 'AI first-pass guidance, not a human-approved grade: ' + ai_note,
                'a_html': render_update(calls[order[0]]['content']), 'b_html': render_update(calls[order[1]]['content']),
                'a_raw': calls[order[0]]['content'], 'b_raw': calls[order[1]]['content']}
        mapping[case_id] = {'A': order[0], 'B': order[1]}
        tasks.append({'data': data})
    assert len(tasks) == len({t['data']['case_id'] for t in tasks}) == 5
    write_json(ROOT / 'private/tasks.json', tasks)
    write_json(ROOT / 'private/model-map.json', mapping)
    write_json(ROOT / 'private/provenance.json', provenance)
    print('Prepared 5 tasks / 10 original outputs. Complete message inputs match in every pair. No inference calls.')


if __name__ == '__main__':
    main()
