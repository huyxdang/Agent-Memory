"""Concurrent, checkpointed answering and Mem0 BEAM judging for finished memories."""
import json
from pathlib import Path
import threading
import time

import longmemeval_eval as ev
import memory
from checkpoint_io import save
from third_party.mem0 import beam_prompts


class Answers:
    def __init__(self, directory, client, settings, limit=20):
        self.directory, self.client, self.settings, self.limit = directory, client, settings, limit
        self.lock = threading.RLock()
        self.calls = {p.stem:json.loads(p.read_text()) for p in (directory/'api_calls').glob('*.json')}

    def request(self, identity, messages, judge=False):
        settings = self.settings
        model = settings['judge_model'] if judge else settings['answer_model']
        cap = settings['judge_max_tokens'] if judge else settings['answer_max_tokens']
        kwargs = dict(model=model, messages=messages, max_completion_tokens=cap)
        if not judge:
            kwargs['reasoning_effort'] = settings['answer_reasoning_effort']
        path = self.directory/'api_calls'/f'{identity}.json'
        with self.lock:
            if identity in self.calls:
                call = self.calls[identity]
                if call['request'] != kwargs:
                    raise ValueError('Saved answer/judge request changed')
                if call['status'] != 'complete':
                    raise RuntimeError('Uncertain API outcome requires reconciliation')
                return call['response']
            bound = len(json.dumps(messages,ensure_ascii=False).encode())+1024
            if not judge and bound + cap > settings['answer_context_window']:
                raise ValueError('Answer prompt cannot be certified to fit; no truncation')
            reserve = (bound*(settings['judge_input_rate']*1.25 if judge else .50)
                       + cap*(settings['judge_output_rate'] if judge else 1.80))/1e6
            used = sum(c.get('accounted_usd',c['reserved_usd']) for c in self.calls.values())
            if used + reserve > self.limit:
                raise RuntimeError('Baseline OpenAI allocation exhausted')
            call = dict(status='in_flight',request=kwargs,reserved_usd=reserve)
            self.calls[identity] = call
            save(path,call)
        started = time.monotonic()
        try:
            response = self.client.chat.completions.create(**kwargs)
            usage = ev.usage_dict(response.usage)
            result = dict(content=response.choices[0].message.content or '',finish_reason=response.choices[0].finish_reason,
                          response_id=response.id,resolved_model=response.model,usage=usage,
                          elapsed_seconds=time.monotonic()-started)
            with self.lock:
                call.update(status='complete',response=result)
                if usage.get('input_tokens') is not None and usage.get('output_tokens') is not None:
                    call['accounted_usd'] = (usage['input_tokens']*(settings['judge_input_rate']*1.25 if judge else .50)
                        + usage['output_tokens']*(settings['judge_output_rate'] if judge else 1.80))/1e6
                save(path,call)
            return result
        except Exception as error:
            with self.lock:
                call.update(status='unknown_outcome',error_type=type(error).__name__,
                            error_code=getattr(error,'code',None),elapsed_seconds=time.monotonic()-started)
                save(path,call)
            raise

    def evaluate(self, item, state):
        qid = item['question_id']
        path = self.directory/'results'/f'{qid}.json'
        if path.exists() and json.loads(path.read_text()).get('status') == 'success':
            return
        result = dict(question_id=qid,question=item['question'],reference_answer=item['answer'],
                      history_sha256=state['history_sha256'],status='running')
        try:
            prompt = memory.build_answer_prompt(state['lines'],state['sessions_done'],item['question_date'],item['question'])
            context = memory.render_for_answer(state['lines'])
            result['context_tokens'] = len(ev.tokenizer('o200k_base').encode(context,disallowed_special=()))
            answer = self.request('answer_'+qid,[{'role':'system','content':memory.ANSWER_SYSTEM_PROMPTS['v2']},
                                                {'role':'user','content':prompt}])
            result['answer_call'] = answer
            if answer['finish_reason'] != 'stop' or not answer['content']:
                raise ValueError('Invalid or truncated answer')
            result['generated_answer'] = answer['content']
            scores, calls = [], []
            for n,nugget in enumerate(item['rubric']):
                call = self.request(f'judge_{qid}_{n}',[{'role':'system','content':beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT},
                    {'role':'user','content':beam_prompts.get_beam_nugget_judge_prompt(item['question'],nugget,answer['content'])}],judge=True)
                score = ev.parse_beam_score(call['content'])
                calls.append(call)
                if call['finish_reason'] != 'stop' or score is None:
                    raise ValueError('Invalid judge response')
                scores.append(score)
            if not scores:
                raise ValueError('Missing BEAM rubric')
            result.update(status='success',judge_calls=calls,judge_score=sum(scores)/len(scores),
                          judge_verdict='yes' if sum(scores)/len(scores)>=.5 else 'no')
        except Exception as error:
            result.update(status='failed',error_type=type(error).__name__)
        save(path,result)
