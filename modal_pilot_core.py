"""Provider-independent pilot selection, validation and spending estimates."""
import hashlib
import json
import math

MODEL = 'Qwen/Qwen3.5-9B'
GPU = 'A100-80GB'
CONTEXT = 65536
MAX_OUTPUT = 2048
SECONDS = 1200
RATE = 0.000694 + 2 * 0.00003942 + 32 * 0.00000667
RESERVE_USD = 0.50


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def budget_plan(limit, seconds=SECONDS):
    if not math.isfinite(limit) or not 0 < limit <= 2 or not 0 < seconds <= SECONDS:
        raise ValueError('Pilot authorization is at most $2 and 1200 seconds')
    estimate = seconds * RATE + RESERVE_USD
    if estimate > limit:
        raise ValueError(f'Budget too small: resource envelope plus reserve is ${estimate:.4f}')
    return {'limit_usd':limit,'sandbox_timeout_s':seconds,'resource_rate_usd_s':RATE,
            'resource_envelope_usd':seconds*RATE,'overhead_reserve_usd':RESERVE_USD,
            'estimated_envelope_usd':estimate,'pricing_checked':'2026-09-10',
            'actual_invoice_cost_usd':None}


def prompt_ids(tokenizer, messages):
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                         enable_thinking=False, return_dict=False)
    if not isinstance(ids, list) or not ids or any(type(token) is not int for token in ids):
        raise ValueError('Expected a nonempty flat list of token IDs')
    return ids


def select_examples(rows, tokenizer):
    ranked=[]; seen=set()
    for row in rows:
        eid=row['example_id']
        if eid in seen:
            raise ValueError(f'Duplicate source ID: {eid}')
        seen.add(eid)
        messages=row['messages']
        if messages[-1]['role']!='assistant' or any(m['role']!='user' for m in messages[1:-1]) or messages[0]['role']!='system':
            raise ValueError('Unexpected extractor training message format')
        clean=messages[:-1]
        ranked.append({'example_id':eid,'history_sha256':row['history_sha256'],'session':row['session'],
                       'messages':clean,'prompt_sha256':digest(clean),
                       'input_tokens':len(prompt_ids(tokenizer,clean))})
    if len(ranked)<2:
        raise ValueError('Need at least two distinct examples')
    ranked.sort(key=lambda r:(r['input_tokens'],r['example_id']))
    return [{**ranked[(len(ranked)-1)//2],'label':'typical'}, {**ranked[-1],'label':'longest'}],len(ranked)


def validate_payload(payload):
    if payload['model'] != MODEL or len(payload['revision'])!=40 or any(c not in '0123456789abcdef' for c in payload['revision']):
        raise ValueError('Expected selected Qwen model with pinned commit')
    if not 0 < payload['max_output_tokens'] <= MAX_OUTPUT or not 0 < payload['context_window'] <= CONTEXT:
        raise ValueError('Invalid pilot token limits')
    rows=payload['examples']
    if len(rows)!=2 or len({r['example_id'] for r in rows})!=2:
        raise ValueError('Pilot requires exactly two unique examples')
    for row in rows:
        if row['prompt_sha256']!=digest(row['messages']):
            raise ValueError('Prompt integrity mismatch')
        if any(m['role'] not in {'system','user'} for m in row['messages']):
            raise ValueError('Teacher target must not reach inference')
        if row['input_tokens']+payload['max_output_tokens'] > payload['context_window']:
            raise ValueError(f"Prompt plus output does not fit: {row['label']}; no truncation")


def output_valid(text):
    try:
        data=json.loads(text)
        return (isinstance(data,dict) and set(data)=={'narrative','atomic'}
            and isinstance(data['narrative'],list) and all(isinstance(x,str) for x in data['narrative'])
            and isinstance(data['atomic'],list) and all(isinstance(x,dict) and set(x)=={'key','value'}
                and all(isinstance(v,str) and bool(v.strip()) for v in x.values()) for x in data['atomic']))
    except (ValueError,TypeError):
        return False


def account_results(expected, results):
    ids=[r['example_id'] for r in results]
    wanted={r['example_id'] for r in expected}
    return {'missing':sorted(wanted-set(ids)),'unexpected':sorted(set(ids)-wanted),
            'duplicates':sorted({i for i in ids if ids.count(i)>1}),
            'failed':[r['example_id'] for r in results if r.get('status')!='ok']}
