"""Resumable, question-blind teacher extraction from a frozen BEAM train manifest."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import threading
import time

from dotenv import load_dotenv
from openai import OpenAI
import benchmarks
import longmemeval_eval as ev
import memory
from modal_pilot_core import output_valid
from prepare_beam_split import hashes
from checkpoint_io import save, exclusive

ROOT = Path(__file__).resolve().parent


def now():
    return datetime.now(timezone.utc).isoformat()


def usage_cost_upper_bound(usage):
    """Published Luna rates; assume every uncached token incurs cache-write uplift."""
    inputs, outputs = usage['input_tokens'], usage['output_tokens']
    cached = usage.get('cached_input_tokens') or 0
    if not 0 <= cached <= inputs or outputs < 0:
        raise ValueError('Invalid API usage counts')
    long_context = inputs > 272000
    return ((inputs-cached)*.25*(2 if long_context else 1)
            + cached*.02*(2 if long_context else 1)
            + outputs*1.20*(1.5 if long_context else 1))/1e6


def reconcile_accounting(directory, configuration):
    previous = json.loads((directory/'configuration.json').read_text())
    if previous == configuration:
        return
    old = json.loads(json.dumps(previous))
    old['code_sha256']['teacher_traces.py'] = configuration['code_sha256']['teacher_traces.py']
    if old != configuration:
        raise ValueError('Accounting reconciliation cannot change other settings or source code')
    states = [(p, json.loads(p.read_text())) for p in (directory/'histories').glob('*.json')]
    audit_path = directory/'accounting_reconciliation.json'
    if not audit_path.exists():
        save(audit_path, dict(at=now(), previous_configuration=previous,
            reason='User authorized usage-based accounting correction, same $10 cap; retain all unknown reservations.',
            pricing='https://developers.openai.com/api/docs/models/gpt-5.6-luna',
            previous_accounting={p.stem:[c.get('accounted_usd',c['reserved_usd']) for c in s['calls']] for p,s in states}))
    for path, state in states:
        for call in state['calls']:
            usage = call.get('response', {}).get('usage', {})
            if usage.get('input_tokens') is not None and usage.get('output_tokens') is not None:
                call['accounted_usd'] = usage_cost_upper_bound(usage)
        save(path, state)
    save(directory/'configuration.json', configuration)


class Journal:
    def __init__(self, directory, configuration, limit):
        self.directory, self.limit = directory, limit
        self.lock = threading.RLock()
        path = directory / 'configuration.json'
        if path.exists() and json.loads(path.read_text()) != configuration:
            raise ValueError('Resume configuration changed; use the original code, sources and settings')
        save(path, configuration)
        self.states = {p.stem: json.loads(p.read_text()) for p in directory.glob('histories/*.json')}

    def used(self):
        return sum(c.get('accounted_usd', c['reserved_usd'])
                   for s in self.states.values() for c in s['calls'])

    def checkpoint(self, identity):
        save(self.directory / 'histories' / f'{identity}.json', self.states[identity])

    def build(self, item, configuration, invoke):
        history = ev.sanitize_history(item)
        identity = hashes(item)[0]
        with self.lock:
            state = self.states.setdefault(identity, dict(history_sha256=identity, sessions_done=0,
                sessions=len(history), lines=[], warnings=[], calls=[], status='pending'))
            if state['status'] == 'complete':
                return
            if state['calls'] and state['calls'][-1]['status'] != 'complete':
                # The saved response can be applied after a crash without another API call.
                if state['calls'][-1]['status'] not in ('response_saved', 'abandoned_unknown'):
                    state['status'] = 'needs_reconciliation'
                    self.checkpoint(identity)
                    return
        for index in range(state['sessions_done'], len(history)):
            session = history[index]
            parts = memory.extraction_parts(state['lines'], index + 1, len(history),
                                            session['timestamp'], session['messages'])
            system = memory.extraction_system_prompt(item.get('subject'))
            messages = [{'role': 'system', 'content': system}] + memory.extraction_messages(parts)
            # Plain-text training copy has the same contents without API cache-control wrappers.
            training_input = [{'role': 'system', 'content': system}] + [{'role': 'user', 'content': p} for p in parts]
            input_bound = len(json.dumps(messages, ensure_ascii=False).encode()) + len(json.dumps(memory.EXTRACTION_RESPONSE_FORMAT).encode()) + 1024
            if input_bound + configuration['max_output_tokens'] > configuration['context_window']:
                with self.lock:
                    state['status'] = 'context_limit'
                    self.checkpoint(identity)
                return
            with self.lock:
                if state['calls'] and state['calls'][-1]['status'] == 'response_saved':
                    call = state['calls'][-1]
                    if call['session'] != index + 1 or call['messages'] != messages:
                        raise ValueError('Saved response does not match resumed input')
                else:
                    # Conservative Luna envelope: applies long-context multipliers plus cache-write
                    # uplift to every call, regardless of whether those charges actually apply.
                    reserve = (input_bound * .50 + configuration['max_output_tokens'] * 1.80) / 1e6
                    if self.used() + reserve > self.limit:
                        state['status'] = 'budget_blocked'
                        self.checkpoint(identity)
                        return
                    call = dict(session=index + 1, status='in_flight', started_at=now(),
                                reserved_usd=reserve, messages=messages, training_input=training_input)
                    state['calls'].append(call)
                    state['status'] = 'running'
                    self.checkpoint(identity)
            if call['status'] == 'in_flight':
                started = time.monotonic()
                try:
                    response = invoke(messages)
                    with self.lock:
                        call.update(response=response, status='response_saved', finished_at=now(),
                                    elapsed_seconds=time.monotonic() - started)
                        usage = response.get('usage', {})
                        if usage.get('input_tokens') is not None and usage.get('output_tokens') is not None:
                            # Upper-bound accounting, not a claim about the provider invoice.
                            call['accounted_usd'] = usage_cost_upper_bound(usage)
                        self.checkpoint(identity)
                except Exception as error:
                    with self.lock:
                        call.update(status='unknown_outcome', error_type=type(error).__name__,
                                    error_code=getattr(error, 'code', None), http_status=getattr(error, 'status_code', None),
                                    elapsed_seconds=time.monotonic() - started, finished_at=now())
                        state['status'] = 'needs_reconciliation'
                        self.checkpoint(identity)
                    return
            response = call['response']
            if response.get('finish_reason') != 'stop' or not output_valid(response.get('content', '')):
                with self.lock:
                    call['status'] = state['status'] = 'invalid_output'
                    self.checkpoint(identity)
                return
            with self.lock:
                _, warnings = memory.apply_extraction(state['lines'], memory.parse_extraction(response['content']),
                    index + 1, session['timestamp'], memory.session_text(session['messages']))
                state['warnings'].extend(warnings)
                state['sessions_done'] = index + 1
                call['status'] = 'complete'
                state['status'] = 'complete' if index + 1 == len(history) else 'running'
                self.checkpoint(identity)
                print(f"teacher {sum(s['sessions_done'] for s in self.states.values())} updates saved", flush=True)


def load_training(manifest_path):
    manifest = json.loads(manifest_path.read_text())
    if manifest['split'] != 'train':
        raise ValueError('Teacher training job accepts only the train manifest')
    audit = json.loads((manifest_path.parent / 'source_manifest.json').read_text())
    if manifest['source_revision'] != audit['revision']:
        raise ValueError('Source revision mismatch')
    for relative, sha in audit['sha256'].items():
        if ev.sha256_file(manifest_path.parent / 'source' / relative.removeprefix('chats/')) != sha:
            raise ValueError('Source integrity mismatch')
    original = benchmarks.BEAM_DIR
    benchmarks.BEAM_DIR = manifest_path.parent / 'source'
    try:
        items = []
        for row in manifest['histories']:
            item = benchmarks.beam_items(row['scale'], [row['chat_id']])[0]
            if hashes(item)[0] != row['history_sha256']:
                raise ValueError('History integrity mismatch')
            items.append(item)
    finally:
        benchmarks.BEAM_DIR = original
    if len({hashes(x)[0] for x in items}) != len(items):
        raise ValueError('Duplicate training history')
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'work/beam_split_v2/train.json')
    parser.add_argument('--directory', type=Path, default=ROOT / 'work/beam_teacher_traces')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--budget-usd', type=float)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--reconcile-accounting', action='store_true')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env', override=False)
    items = load_training(args.manifest)
    config = dict(model=os.getenv('EXTRACTION_MODEL'), reasoning=os.getenv('EXTRACTION_REASONING_EFFORT'),
                  max_output_tokens=int(os.getenv('EXTRACTION_MAX_TOKENS', '128000')),
                  context_window=int(os.getenv('ANSWER_CONTEXT_WINDOW', '1050000')),
                  base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
                  manifest_sha256=ev.sha256_file(args.manifest),
                  code_sha256={p: ev.sha256_file(ROOT / p) for p in ('teacher_traces.py', 'checkpoint_io.py', 'memory.py', 'benchmarks.py', 'prepare_beam_split.py')})
    if config['model'] != 'gpt-5.6-luna':
        raise ValueError('This teacher accounting is configured for gpt-5.6-luna only')
    if not args.run:
        print(json.dumps(dict(status='preflight_only', histories=len(items), updates=sum(len(ev.sanitize_history(x)) for x in items),
                              model=config['model'], resume='Repeat identical command and directory; completed updates are skipped',
                              unknown_attempts='Block for reconciliation; never automatically resend'), indent=2))
        return
    if args.budget_usd is None or not math.isfinite(args.budget_usd) or args.budget_usd <= 0 or not 1 <= args.workers <= 4:
        raise ValueError('Explicit finite positive budget and 1-4 workers required')
    cap = float(os.environ['SPENDING_LIMIT_USD'])
    if not math.isfinite(cap) or args.budget_usd > cap:
        raise ValueError('Teacher allocation exceeds configured OpenAI spending cap')
    client = OpenAI(base_url=config['base_url'], max_retries=0, timeout=180)
    def invoke(messages):
        response = client.chat.completions.create(model=config['model'], messages=messages,
            reasoning_effort=config['reasoning'], max_completion_tokens=config['max_output_tokens'],
            response_format=memory.EXTRACTION_RESPONSE_FORMAT)
        return dict(content=response.choices[0].message.content or '', finish_reason=response.choices[0].finish_reason,
                    resolved_model=response.model, response_id=response.id, usage=ev.usage_dict(response.usage))
    with exclusive(args.directory):
        if args.reconcile_accounting:
            reconcile_accounting(args.directory, config)
        journal = Journal(args.directory, config, args.budget_usd)
        start = time.monotonic()
        attempt_path = args.directory / 'invocations.json'
        attempts = json.loads(attempt_path.read_text()) if attempt_path.exists() else []
        attempt = dict(started_at=now(), status='running', budget_usd=args.budget_usd)
        attempts.append(attempt)
        save(attempt_path, attempts)
        try:
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                list(pool.map(lambda item: journal.build(item, config, invoke), items))
            attempt['status'] = 'finished'
        finally:
            attempt.update(finished_at=now(), elapsed_seconds=time.monotonic()-start)
            save(attempt_path, attempts)
        summary = dict(histories=len(items), completed_histories=sum(s['status'] == 'complete' for s in journal.states.values()),
                       updates=sum(s['sessions_done'] for s in journal.states.values()),
                       accounted_upper_bound_usd=journal.used(), budget_usd=args.budget_usd,
                       invocation_seconds=time.monotonic()-start,
                       statuses={k:s['status'] for k,s in journal.states.items()})
        save(args.directory / 'summary.json', summary)
        print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
