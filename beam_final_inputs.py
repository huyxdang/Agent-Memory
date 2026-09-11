"""Frozen BEAM inputs shared by preparation and collection; no cloud side effects."""
import json
import os
from pathlib import Path
import benchmarks
import longmemeval_eval as ev
import memory
from modal_pilot_core import MODEL, CONTEXT
from prepare_beam_split import hashes, FINAL_SHA256
ROOT = Path(__file__).resolve().parent

def inputs():
    for name,sha in FINAL_SHA256.items():
        if ev.sha256_file(ROOT/name) != sha:
            raise ValueError('Final selection changed')
    ids = [q['question_id'] for p in FINAL_SHA256 for q in json.loads((ROOT/p).read_text())['questions']]
    items = {x['question_id']:x for x in benchmarks.load_items('beam') if x['question_id'] in set(ids)}
    if len(ids) != 90 or set(ids) != items.keys():
        raise ValueError('Expected original 90 final questions')
    grouped = {}
    for item in items.values():
        grouped.setdefault(hashes(item)[0],[]).append(item)
    pilot = json.loads((ROOT/'work/modal_qwen_pilot_new_account/payload.json').read_text())
    payload = dict(model=MODEL,revision=pilot['revision'],context_window=CONTEXT,max_output_tokens='remaining_context',
                   histories=[dict(history_sha256=key,subject=rows[0].get('subject') or memory.USER_SUBJECT,
                                   history=ev.sanitize_history(rows[0])) for key,rows in grouped.items()])
    return payload, grouped, answer_settings()


def answer_settings():
    settings = dict(answer_model=os.environ['ANSWER_MODEL'],judge_model=os.environ['JUDGE_MODEL'],
        answer_reasoning_effort=os.environ['ANSWER_REASONING_EFFORT'],answer_max_tokens=int(os.environ['ANSWER_MAX_TOKENS']),
        judge_max_tokens=int(os.environ['JUDGE_MAX_TOKENS']),answer_context_window=int(os.environ['ANSWER_CONTEXT_WINDOW']),
        judge_input_rate=float(os.environ['JUDGE_INPUT_USD_PER_MTOK']),judge_output_rate=float(os.environ['JUDGE_OUTPUT_USD_PER_MTOK']))
    if settings['answer_model'] != 'gpt-5.6-luna' or settings['judge_model'] != 'gpt-5':
        raise ValueError('Expected the original Luna answerer and GPT-5 judge')
    return settings
