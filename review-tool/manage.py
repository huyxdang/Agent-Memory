"""Local-only Label Studio lifecycle and non-destructive pilot import."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import time

import requests

ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / 'private'
URL = 'http://127.0.0.1:8085'
TITLE = 'Memory updates — five-card human review'


def read(name):
    return json.loads((PRIVATE / name).read_text())


def save(name, value):
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    path = PRIVATE / name
    with open(path, 'w', opener=lambda p, flags: os.open(p, flags, 0o600)) as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    path.chmod(0o600)


def credentials():
    if not (PRIVATE / 'credentials.json').exists():
        save('credentials.json', {'email': 'reviewer@localhost.test',
                                 'password': secrets.token_urlsafe(24),
                                 'token': secrets.token_hex(20)})
    return read('credentials.json')


def api(method, path, **kwargs):
    response = requests.request(method, URL + path, timeout=30,
                                headers={'Authorization': 'Token ' + credentials()['token']}, **kwargs)
    response.raise_for_status()
    return response


def start():
    try:
        api('GET', '/api/current-user/whoami')
        print('Label Studio is already running at ' + URL)
        return
    except requests.ConnectionError:
        pass
    creds = credentials()
    env = os.environ.copy()
    env.update({'BASE_DATA_DIR': str(ROOT / 'data'),
                'LABEL_STUDIO_USERNAME': creds['email'],
                'LABEL_STUDIO_PASSWORD': creds['password'],
                'LABEL_STUDIO_USER_TOKEN': creds['token'],
                'COLLECT_ANALYTICS': 'False', 'LATEST_VERSION_CHECK': 'False',
                'SENTRY_DSN': '', 'FRONTEND_SENTRY_DSN': '',
                'DISABLE_SIGNUP_WITHOUT_LINK': 'True',
                'LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED': 'False'})
    log = PRIVATE / 'server.log'
    with open(log, 'a', opener=lambda p, flags: os.open(p, flags, 0o600)) as out:
        process = subprocess.Popen([str(ROOT.parent / '.label-studio-venv/bin/label-studio'),
            'start', '--data-dir', str(ROOT / 'data'), '--internal-host', '127.0.0.1',
            '--port', '8085', '--no-browser', '--enable-legacy-api-token'],
            env=env, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, start_new_session=True, umask=0o077)
    save('server.json', {'pid': process.pid, 'url': URL})
    print(f'Started local server PID {process.pid}. Log: {log}')


def provision():
    tasks = read('tasks.json')
    config = (ROOT / 'label-config.xml').read_text()
    digest = hashlib.sha256((config + json.dumps(tasks, sort_keys=True)).encode()).hexdigest()
    state_path = PRIVATE / 'project.json'
    if state_path.exists():
        state = read('project.json')
        if state['digest'] != digest:
            raise RuntimeError('Pilot content changed; do not overwrite existing human labels. Create a new version explicitly.')
        project_id = state['id']
    else:
        projects = api('GET', '/api/projects/', params={'page_size': 100}).json()
        matches = [p for p in projects['results'] if p['title'] == TITLE]
        if matches:
            raise RuntimeError('An existing project has this title but no local identity record. Inspect it before proceeding.')
        project = api('POST', '/api/projects/', json={
            'title': TITLE, 'label_config': config,
            'description': 'Five focused real BEAM dev updates. Anonymous base/FT outputs. Human labels only; not a benchmark score.',
            'show_skip_button': True, 'enable_empty_annotation': False}).json()
        project_id = project['id']
        save('project.json', {'id': project_id, 'digest': digest})
    existing = api('GET', '/api/tasks/', params={'project': project_id, 'page_size': 100}).json()['tasks']
    if not existing:
        api('POST', f'/api/projects/{project_id}/import', json=tasks)
        existing = api('GET', '/api/tasks/', params={'project': project_id, 'page_size': 100}).json()['tasks']
    expected = {t['data']['case_id'] for t in tasks}
    actual = [t['data']['case_id'] for t in existing]
    if len(actual) != 5 or set(actual) != expected:
        raise RuntimeError(f'Unexpected task inventory: {actual}; no data was overwritten.')
    print(f'Five tasks verified. Review: {URL}/projects/{project_id}/data')


def export():
    project_id = read('project.json')['id']
    rows = api('GET', f'/api/projects/{project_id}/export', params={'exportType': 'JSON', 'download_all_tasks': 'true'}).json()
    name = 'review-export-' + time.strftime('%Y%m%d-%H%M%S') + '.json'
    save(name, rows)
    print(PRIVATE / name)


def stop():
    pid = read('server.json')['pid']
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True)
    if not result.stdout.strip():
        print('Recorded server is not running.')
        return
    if str(ROOT.parent / '.label-studio-venv/bin/label-studio') not in result.stdout or '--port 8085' not in result.stdout:
        raise RuntimeError('Recorded PID no longer matches this Label Studio server; refusing to stop it.')
    os.kill(pid, signal.SIGTERM)
    print('Stopped local server; database and labels retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['start', 'provision', 'export', 'stop', 'status'])
    args = parser.parse_args()
    if args.command == 'status':
        api('GET', '/api/current-user/whoami')
        print('Local server responding at ' + URL)
    else:
        globals()[args.command]()
