"""Frozen LoCoMo shared 50, with one question-free memory build per conversation."""
import json

import benchmarks
import longmemeval_eval as ev
from beam_final_inputs import ROOT, answer_settings
from longmemeval_qwen_inputs import REVISION
from modal_pilot_core import MODEL, CONTEXT, digest

SELECTION = 'question_ids_locomo_50.json'
SELECTION_SHA256 = 'd36d23a7ecebc0707064137c707699436edd65a353ec09078c6afa8687657cbe'
DATASET_SHA256 = '79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4'


def inputs():
    if ev.sha256_file(ROOT/SELECTION) != SELECTION_SHA256:
        raise ValueError('Original LoCoMo selection changed')
    source = ROOT/'work/locomo10.json'
    if ev.sha256_file(source) != DATASET_SHA256:
        raise ValueError('Frozen LoCoMo dataset changed')
    ids = [r['question_id'] for r in json.loads((ROOT/SELECTION).read_text())['questions']]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError('Expected exactly 50 distinct LoCoMo questions')
    items = {r['question_id']:r for r in benchmarks.locomo_items(source)}
    grouped, histories = {}, {}
    for qid in ids:
        row = items[qid]
        history = ev.sanitize_history(row)
        key = digest(history)
        if key not in histories:
            histories[key] = dict(history_sha256=key,subject=row['subject'],history=history)
            grouped[key] = []
        if histories[key]['subject'] != row['subject']:
            raise ValueError('Shared history has inconsistent speaker attribution')
        grouped[key].append({k:row[k] for k in
            ('question_id','question','question_date','question_type','answer','conversation')})
    if len(histories) != 10:
        raise ValueError('Expected the original ten LoCoMo histories')
    payload = dict(model=MODEL,revision=REVISION,context_window=CONTEXT,
        max_output_tokens='remaining_context',histories=list(histories.values()),
        benchmark='locomo',dataset_source='snap-research/locomo:data/locomo10.json',
        dataset_revision=None,dataset_sha256=DATASET_SHA256,
        selection_sha256={SELECTION:SELECTION_SHA256})
    return payload, grouped, answer_settings()
