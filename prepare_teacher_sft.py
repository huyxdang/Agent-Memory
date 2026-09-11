"""Export immutable, question-blind BEAM teacher SFT candidates; no network calls."""
import argparse
from collections import Counter
import importlib.metadata
import json
from pathlib import Path
import subprocess

import benchmarks
from checkpoint_io import exclusive, save
import longmemeval_eval as ev
import memory
from modal_pilot_core import MODEL, digest, output_valid
from prepare_beam_split import FINAL_SHA256, hashes
from teacher_traces import load_training

ROOT = Path(__file__).resolve().parent
REVISION = 'c202236235762e1c871ad0ccb60c8ee5ba337b9a'
LIMIT = 65536


def replay(item, state, measure):
    """Reconstruct every input from source plus earlier targets before exporting."""
    history = ev.sanitize_history(item)
    identity = hashes(item)[0]
    if state['history_sha256'] != identity or state['sessions'] != len(history):
        raise ValueError('Trace source identity mismatch')
    lines, warnings, rows, excluded = [], [], [], []
    for attempt, call in enumerate(state['calls']):
        if call['status'] != 'complete':
            excluded.append(dict(history_sha256=identity, attempt=attempt, session=call['session'],
                                 reason=call['status'], error_type=call.get('error_type')))
            continue
        index = len(rows)
        if call['session'] != index+1 or index >= len(history):
            raise ValueError('Duplicate or non-contiguous completed session')
        session = history[index]
        parts = memory.extraction_parts(lines, index+1, len(history), session['timestamp'], session['messages'])
        system = {'role':'system', 'content':memory.extraction_system_prompt(item.get('subject'))}
        messages = [system] + [{'role':'user', 'content':p} for p in parts]
        if messages != call['training_input'] or [system]+memory.extraction_messages(parts) != call['messages']:
            raise ValueError('Teacher input does not match source and prior memory')
        response = call['response']
        target = response['content']
        if response.get('finish_reason') != 'stop' or not output_valid(target):
            raise ValueError('Completed target is invalid or truncated')
        _, issues = memory.apply_extraction(lines, memory.parse_extraction(target), index+1,
            session['timestamp'], memory.session_text(session['messages']))
        warnings.extend(issues)
        counts = measure(messages, target)
        rows.append(dict(example_id=f'{identity}:{index+1}', history_sha256=identity, session=index+1,
            source_attempt=attempt, messages=messages+[{'role':'assistant','content':target}],
            prompt_sha256=digest(messages), target_sha256=digest(target),
            resolved_teacher_model=response.get('resolved_model'), response_id=response.get('response_id'),
            usage=response.get('usage'), elapsed_seconds=call.get('elapsed_seconds'),
            warnings=issues, quality_status='not_semantically_reviewed',
            fits_context=counts['sequence_tokens'] <= LIMIT, **counts))
    if len(rows) != state['sessions_done'] or lines != state['lines'] or warnings != state['warnings']:
        raise ValueError('Replayed teacher state does not match saved checkpoint')
    return rows, excluded


def verify_splits(items, split):
    dev = json.loads((split/'dev.json').read_text())
    final = json.loads((split/'final.json').read_text())
    for name, sha in {**FINAL_SHA256, **final['source_files_sha256']}.items():
        if ev.sha256_file(ROOT/name) != sha:
            raise ValueError('Protected final source changed')
    original = benchmarks.BEAM_DIR
    try:
        benchmarks.BEAM_DIR = split/'source'
        dev_items = [benchmarks.beam_items(r['scale'],[r['chat_id']])[0] for r in dev['histories']]
    finally:
        benchmarks.BEAM_DIR = original
    if [hashes(i)[0] for i in dev_items] != [r['history_sha256'] for r in dev['histories']]:
        raise ValueError('Dev history integrity mismatch')
    wanted = {q['history_sha256'] for q in final['questions']}
    wanted_questions = {q['question_id'] for q in final['questions']}
    unique = {}
    for item in benchmarks.load_items('beam'):
        if item['question_id'] in wanted_questions:
            unique.setdefault((item['question_id'].split('_')[0],item['conversation']),item)
    final_items = {hashes(i)[0]:i for i in unique.values()}
    if set(final_items) != wanted:
        raise ValueError('Missing final history')
    groups = {'train':items, 'dev':dev_items, 'final':list(final_items.values())}
    signatures = {name:[hashes(i) for i in group] for name,group in groups.items()}
    for a,b in [('train','dev'),('train','final'),('dev','final')]:
        for field in range(3):
            left = set().union(*(set([h[0]]) if field==0 else h[field] for h in signatures[a]))
            right = set().union(*(set([h[0]]) if field==0 else h[field] for h in signatures[b]))
            if left & right:
                raise ValueError(f'{a}/{b} overlap at history/window/pair field {field}')
    return {name:sorted(h[0] for h in hs) for name,hs in signatures.items()}


def distribution(values):
    values = sorted(values)
    if not values:
        return None
    return dict(min=values[0], median=values[len(values)//2], p95=values[int((len(values)-1)*.95)],
                max=values[-1], total=sum(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--traces', type=Path, default=ROOT/'work/beam_teacher_traces')
    parser.add_argument('--split', type=Path, default=ROOT/'work/beam_split_v2')
    parser.add_argument('--output', type=Path, default=ROOT/'work/beam_teacher_sft')
    args = parser.parse_args()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    def measure(messages, target):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        sequence = tokenizer.apply_chat_template(messages+[{'role':'assistant','content':target}],
            tokenize=False, add_generation_prompt=False, enable_thinking=False)
        if not sequence.startswith(prompt):
            raise ValueError('Training template changes the inference prompt')
        count = lambda text: len(tokenizer.encode(text, add_special_tokens=False))
        return dict(prompt_tokens=count(prompt), target_tokens=count(target), sequence_tokens=count(sequence))
    # Refuse to snapshot while the teacher is writing. Read bytes once under its lock.
    with exclusive(args.traces):
        config = json.loads((args.traces/'configuration.json').read_text())
        if config['manifest_sha256'] != ev.sha256_file(args.split/'train.json'):
            raise ValueError('Training manifest changed')
        for name,sha in config['code_sha256'].items():
            if ev.sha256_file(ROOT/name) != sha:
                raise ValueError('Teacher code changed; cannot certify replay')
        states = {p.stem:json.loads(p.read_text()) for p in sorted((args.traces/'histories').glob('*.json'))}
    items = load_training(args.split/'train.json')
    splits = verify_splits(items,args.split)
    if set(states)-set(splits['train']):
        raise ValueError('Unexpected trace history outside training split')
    fingerprint = digest(dict(states=states, config=config, exporter=ev.sha256_file(Path(__file__)),
                              split=splits, tokenizer=REVISION))
    destination = args.output/fingerprint[:16]
    if (destination/'report.json').exists():
        report = json.loads((destination/'report.json').read_text())
        for name,sha in report['artifact_sha256'].items():
            if ev.sha256_file(destination/name) != sha:
                raise ValueError('Existing export was modified')
        print(json.dumps(dict(directory=str(destination),report=report),indent=2))
        return
    rows, excluded, histories = [], [], []
    manifest_rows = {r['history_sha256']:r for r in json.loads((args.split/'train.json').read_text())['histories']}
    for item in items:
        key = hashes(item)[0]; state=states.get(key)
        batch, failures = replay(item,state,measure) if state else ([],[])
        rows.extend(batch); excluded.extend(failures)
        histories.append(dict(history_sha256=key, scale=manifest_rows[key]['scale'],
            chat_id=manifest_rows[key]['chat_id'], status=state['status'] if state else 'missing',
            expected=len(ev.sanitize_history(item)), completed=len(batch),
            missing_sessions=list(range(len(batch)+1,len(ev.sanitize_history(item))+1))))
        print(f"Prepared {len(histories)}/{len(items)} histories; {len(rows)} updates",flush=True)
    fit = [r for r in rows if r['fits_context']]
    destination.mkdir(parents=True,exist_ok=True)
    # Canonical chat data keeps role boundaries and unchanged visible JSON targets.
    exports = {'candidates.jsonl':rows, 'train.messages.jsonl':[{'messages':r['messages']} for r in fit],
        'train.provenance.jsonl':[{k:v for k,v in r.items() if k!='messages'} for r in fit],
        'oversize.provenance.jsonl':[{k:v for k,v in r.items() if k!='messages'} for r in rows if not r['fits_context']]}
    for name,values in exports.items():
        with (destination/name).open('w') as stream:
            for value in values:
                stream.write(json.dumps(value,ensure_ascii=False)+'\n')
    save(destination/'split_manifest.json',splits)
    save(destination/'teacher_configuration.json',config)
    save(destination/'excluded_attempts.json',excluded)
    report = dict(fingerprint=fingerprint, status='prepared_not_approved_for_training',
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        exporter_sha256=ev.sha256_file(Path(__file__)), teacher_state_sha256={k:digest(s) for k,s in states.items()},
        tokenizer=dict(model=MODEL,revision=REVISION,thinking=False,
            transformers=importlib.metadata.version('transformers'), template_sha256=digest(tokenizer.chat_template)),
        context_limit=LIMIT, expected_updates=sum(h['expected'] for h in histories),
        completed_updates=len(rows), fit_updates=len(fit), oversize_updates=len(rows)-len(fit),
        warned_updates=sum(bool(r['warnings']) for r in rows),
        warning_codes=dict(Counter(c for r in rows for w in r['warnings'] for c in w['codes'])),
        histories=histories, excluded_attempts=len(excluded),
        tokens={k:distribution([r[k] for r in rows]) for k in ('prompt_tokens','target_tokens','sequence_tokens')},
        minimum_autoscientist_rows=1000, additional_fit_rows_needed=max(0,1000-len(fit)),
        blockers=['Semantic quality review remains required; warnings are not a keep/discard classifier.',
                  'AutoScientist raw prompt/completion mapping must preserve chat roles and thinking-off template before upload.',
                  'Runtime model/credit checks required before submission.'],
        artifact_sha256={p.name:ev.sha256_file(p) for p in destination.iterdir() if p.is_file()})
    save(destination/'report.json',report)
    print(json.dumps(dict(directory=str(destination),report=report),indent=2))


if __name__ == '__main__':
    main()
