"""Original LongMemEval 100, with question-free, independently scheduled histories."""
import json

from beam_final_inputs import ROOT, answer_settings
import longmemeval_eval as ev
import memory
from modal_pilot_core import MODEL, CONTEXT, digest

SELECTIONS = {
    'question_ids_50.json': 'df1452a82e47db9bd7284de58303d6a8f3c789dd40201f9808475858e2c759b7',
    'question_ids_50b.json': 'e462c38f89a98082b2b39ebb59cf9da7d37a41fbbaf67efbce9f9eb4205c3b11',
}
REVISION = 'c202236235762e1c871ad0ccb60c8ee5ba337b9a'


def inputs():
    ids = []
    for name, sha in SELECTIONS.items():
        if ev.sha256_file(ROOT/name) != sha:
            raise ValueError('Original LongMemEval selection changed')
        ids.extend(q['question_id'] for q in json.loads((ROOT/name).read_text())['questions'])
    if len(ids) != 100 or len(set(ids)) != 100:
        raise ValueError('Expected exactly 100 distinct LongMemEval questions')
    source = ROOT/'work/longmemeval_s_cleaned.json'
    if not source.is_file():
        raise FileNotFoundError('Download the pinned LongMemEval dataset before preparation')
    items = {r['question_id']: r for r in ev.load_dataset(source)}
    grouped, histories = {}, []
    for qid in ids:
        row = items[qid]
        history = ev.sanitize_history(row)
        key = digest(history)
        if key not in grouped:
            histories.append(dict(history_sha256=key, subject=memory.USER_SUBJECT, history=history))
            grouped[key] = []
        # Labels remain local. Only sanitized histories go to the GPU payload.
        grouped[key].append({k: row[k] for k in
            ('question_id', 'question', 'question_date', 'question_type', 'answer')})
    payload = dict(model=MODEL, revision=REVISION, context_window=CONTEXT,
        max_output_tokens='remaining_context', histories=histories,
        dataset_revision=ev.DATASET_REVISION, dataset_sha256=ev.DATASET_SHA256,
        selection_sha256=SELECTIONS, benchmark='longmemeval')
    return payload, grouped, answer_settings()
