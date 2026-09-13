"""Check local review integrity; keep UI test labels in a separate dummy project."""
import argparse
import copy
import json

import manage as m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-qa', action='store_true')
    args = parser.parse_args()
    project_id = m.read('project.json')['id']
    expected = {t['data']['case_id']: t['data'] for t in m.read('tasks.json')}
    rows = m.api('GET', '/api/tasks/', params={'project': project_id, 'page_size': 100}).json()['tasks']
    assert len(rows) == 5
    assert {r['data']['case_id']: r['data'] for r in rows} == expected
    for row in rows:
        task = m.api('GET', f'/api/tasks/{row["id"]}/').json()
        assert not task['annotations'], 'Real labels are now present; do not treat them as test fixtures.'
        assert not task.get('drafts'), 'A real review draft exists; leave it untouched.'
    provenance = m.read('provenance.json')
    for case in range(1, 6):
        pair = [p for p in provenance if p['case'] == case]
        assert len(pair) == 2 and pair[0]['messages_sha256'] == pair[1]['messages_sha256']
    print('PASS: five unique tasks, exact imported data, matched inputs, zero real annotations/drafts.')
    if args.prepare_qa:
        if not (m.PRIVATE / 'qa.json').exists():
            project = m.api('POST', '/api/projects/', json={
                'title': 'QA ONLY — synthetic UI test, not human review',
                'label_config': (m.ROOT / 'label-config.xml').read_text(),
                'enable_empty_annotation': False}).json()
            data = copy.deepcopy(next(iter(expected.values())))
            data.update({'case_id': 'QA-ONLY', 'title': 'QA ONLY — not experiment data',
                         'scope': 'Synthetic software test. Labels here are NOT human judgments.',
                         'question': 'Does each output preserve the stated color?',
                         'source_html': '<p>TEST USER: My bicycle is blue.</p>',
                         'neighbors': 'TEST USER: My bicycle is blue.',
                         'full_input': 'Synthetic QA input only: My bicycle is blue.',
                         'ai_note': 'Synthetic software test, not a review suggestion.',
                         'a_html': '<p>Bicycle color: blue</p>', 'b_html': '<p>Bicycle color: red</p>',
                         'a_raw': '{"color":"blue"}', 'b_raw': '{"color":"red"}'})
            m.api('POST', f'/api/projects/{project["id"]}/import', json=[{'data': data}])
            task = m.api('GET', '/api/tasks/', params={'project': project['id']}).json()['tasks'][0]
            m.save('qa.json', {'project': project['id'], 'task': task['id']})
        qa = m.read('qa.json')
        print(f'QA UI: {m.URL}/projects/{qa["project"]}/data?task={qa["task"]}')
    elif (m.PRIVATE / 'qa.json').exists():
        qa = m.read('qa.json')
        exported = m.api('GET', f'/api/projects/{qa["project"]}/export',
                         params={'exportType': 'JSON', 'download_all_tasks': 'true'}).json()
        annotations = exported[0]['annotations']
        assert len(annotations) == 1
        choices = {r['from_name']: r['value'].get('choices') for r in annotations[0]['result']}
        assert choices['source_decision'] == ['Clear']
        assert choices['grade_a'] == ['Correct'] and choices['grade_b'] == ['Wrong']
        m.save('qa-export.json', exported)
        print('PASS: submitted dummy UI choices round-trip through JSON export.')


if __name__ == '__main__':
    main()
