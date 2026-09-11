import asyncio
import copy
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from beam_baseline_answers import Answers
from checkpoint_io import save
import longmemeval_eval as ev
import qwen_vllm as runner
from qwen_vllm_worker import extract, server_command


class LongMemEvalBatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_100_histories_bounded_batch_order_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = dict(fingerprint='test', concurrency=8, context_window=65536,
                histories=[dict(history_sha256=str(i), subject='user', history=[
                    dict(timestamp='2026-01-01', messages=[dict(role='user', content='I like tea.')])
                    for _ in range(2)]) for i in range(100)])
            active = peak = calls = 0
            async def infer(ids):
                nonlocal active, peak, calls
                active += 1
                peak = max(peak, active)
                calls += 1
                await asyncio.sleep(.005)
                active -= 1
                return dict(content='{"narrative":["The user likes tea."],"atomic":[]}',
                    finish_reason='stop', output_tokens=12)
            async def commit():
                pass
            summary = await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(peak, 8)
            self.assertEqual(calls, 200)
            self.assertEqual(summary['new_completed_updates'], 200)
            for path in (root/'memories').glob('*.json'):
                state = json.loads(path.read_text())
                self.assertEqual([c['session'] for c in state['calls']], [1,2])
                self.assertIn('The user likes tea.', str(state['calls'][1]['messages']))
            resumed = await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(calls, 200)
            self.assertEqual(resumed['new_completed_updates'], 0)
            self.assertEqual(resumed['completed_updates'], 200)

    async def test_queued_not_sent_can_resume_without_duplicate_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = dict(fingerprint='f', concurrency=4, context_window=65536,
                histories=[dict(history_sha256='h', subject='user', history=[
                    dict(timestamp='today', messages=[dict(role='user',content='Tea')])])])
            async def infer(ids):
                return dict(content='{"narrative":[],"atomic":[]}',finish_reason='stop',output_tokens=9)
            async def commit():
                pass
            await extract(payload, root, infer, lambda _: [1], commit)
            path = root/'memories/h.json'
            state = json.loads(path.read_text())
            state.update(status='running', sessions_done=0, lines=[])
            state['calls'][0]['status'] = 'queued'
            save(path, state)
            await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(len(json.loads(path.read_text())['calls']), 1)

    async def test_duplicate_history_rejected_before_inference(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,'unique'):
                await extract(dict(concurrency=8,histories=[dict(history_sha256='a')]*2),
                    Path(temp), Mock(), Mock(), Mock())


class LongMemEvalRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.settings = dict(answer_model='gpt-5.6-luna',judge_model='gpt-5',answer_max_tokens=100,
            judge_max_tokens=100,answer_reasoning_effort='none',answer_context_window=100000,
            judge_input_rate=1.25,judge_output_rate=10)
        self.item = dict(question_id='q',question='What do I like?',question_date='today',
            question_type='single-session-user',answer='REFERENCE_ONLY_TEA')

    def response(self, content):
        return SimpleNamespace(id='id',model='resolved',
            choices=[SimpleNamespace(message=SimpleNamespace(content=content),finish_reason='stop')],
            usage=SimpleNamespace(prompt_tokens=20,completion_tokens=10,total_tokens=30,
                prompt_tokens_details=None,completion_tokens_details=None))

    def test_longmemeval_judge_prompt_and_answer_label_isolation(self):
        client = Mock()
        client.chat.completions.create.side_effect = [self.response('tea'),
            self.response('<judge_thinking>Matches.</judge_thinking>\nyes')]
        answers = Answers(self.root, client, self.settings, benchmark='longmemeval')
        state = dict(history_sha256='h',sessions_done=1,lines=[],status='complete')
        answers.evaluate(self.item, state)
        result = json.loads((self.root/'results/q.json').read_text())
        self.assertEqual(result['judge_verdict'],'yes')
        self.assertEqual(result['judge_explanation'],'Matches.')
        requests = client.chat.completions.create.call_args_list
        self.assertNotIn('REFERENCE_ONLY_TEA',str(requests[0]))
        self.assertEqual(requests[1].kwargs['messages'],[dict(role='user', content=ev.JUDGE_PROMPT.format(
            question=self.item['question'],answer=self.item['answer'],response='tea'))])
        answers.evaluate(self.item,state)
        self.assertEqual(client.chat.completions.create.call_count,2)

    def test_invalid_judge_is_explicit(self):
        client = Mock()
        client.chat.completions.create.side_effect = [self.response('tea'),self.response('uncertain')]
        Answers(self.root,client,self.settings,benchmark='longmemeval').evaluate(
            self.item,dict(history_sha256='h',sessions_done=1,lines=[],status='complete'))
        result = json.loads((self.root/'results/q.json').read_text())
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['judge_verdict'],'invalid')
        self.assertIn('Invalid LongMemEval judge',result['error'])

    def test_preparation_and_engine_concurrency(self):
        payload = dict(model='qwen',revision='pinned',context_window=65536,
            histories=[dict(history_sha256=str(i),history=[]) for i in range(100)])
        grouped = {str(i):[{**self.item,'question_id':str(i)}] for i in range(100)}
        with patch.object(runner,'longmemeval_inputs',return_value=(payload,grouped,self.settings)):
            config = runner.prepare(self.root,False,8,True,'longmemeval')
        self.assertEqual(config['scope'],'LongMemEval final 100')
        self.assertEqual(len(config['questions']),100)
        self.assertNotIn('REFERENCE_ONLY_TEA',json.dumps(config['payload']))
        command = server_command(config['payload'])
        self.assertEqual(command[command.index('--max-num-seqs')+1],'8')
        with patch.object(runner,'longmemeval_inputs',return_value=(copy.deepcopy(payload),grouped,self.settings)):
            with self.assertRaisesRegex(ValueError,'differs'):
                runner.prepare(self.root,False,4,True,'longmemeval')

    def test_exact_question_accounting(self):
        grouped = {'h':[self.item]}
        self.assertEqual(runner.summarize(self.root,grouped,'test')['missing'],['q'])
        save(self.root/'results/q.json',dict(question_id='q',status='success'))
        self.assertTrue(runner.summarize(self.root,grouped,'test')['complete'])
        save(self.root/'results/extra.json',dict(question_id='other',status='success'))
        self.assertFalse(runner.summarize(self.root,grouped,'test')['complete'])
        save(self.root/'results/duplicate.json',dict(question_id='q',status='success'))
        self.assertEqual(runner.summarize(self.root,grouped,'test')['duplicates'],['q'])

    def test_smoke_workload_does_not_change_with_concurrency(self):
        selected = []
        for concurrency in (1,8,16):
            payload = dict(histories=[dict(history_sha256=str(i),history=[]) for i in range(100)])
            grouped = {str(i):[{**self.item,'question_id':str(i)}] for i in range(100)}
            with patch.object(runner,'longmemeval_inputs',return_value=(payload,grouped,self.settings)):
                config=runner.prepare(self.root/str(concurrency),True,concurrency,True,'longmemeval')
            self.assertEqual(config['scope'],'smoke')
            self.assertEqual(len(config['payload']['histories']),16)
            selected.append(config['payload']['histories'])
        self.assertEqual(selected[0],selected[1])
        self.assertEqual(selected[1],selected[2])

    def test_answering_starts_before_other_history_finishes(self):
        payload = dict(fingerprint='f',histories=[dict(history_sha256=k) for k in ('a','b')])
        grouped = {k:[{**self.item,'question_id':k}] for k in ('a','b')}
        save(self.root/'configuration.json',dict(benchmark='longmemeval', questions=grouped,
            payload=payload, settings=self.settings, scope='LongMemEval final 100'))
        save(self.root/'cloud.json',dict(sandbox_id='fake',run_id='fake',reserved_usd=1,
            gpu_started_at=runner.now(),rate_usd_s=.001))
        modal = Mock()
        modal.Sandbox.from_id.return_value.poll.side_effect = [None,0]
        graded_first = threading.Event()
        second_complete = False
        def evaluate(item,state):
            self.assertEqual(state['status'],'complete')
            if item['question_id']=='a':
                self.assertFalse(second_complete)
                graded_first.set()
            save(self.root/'results'/f"{item['question_id']}.json",dict(question_id=item['question_id'],status='success'))
        def cloud_json(volume,path):
            if '/progress/' in path:
                return dict(status='complete' if '/a.json' in path or second_complete else 'running')
            if '/memories/' in path:
                key=Path(path).stem
                return dict(payload_sha256='f',history_sha256=key,
                    calls=[],
                    status='complete' if key=='a' or second_complete else 'running')
            return None
        def next_poll(_):
            nonlocal second_complete
            self.assertTrue(graded_first.wait(2),'Collector waited for all extraction before answering')
            second_complete=True
        with patch.object(runner,'cloud',return_value=(modal,Mock())), \
             patch.object(runner,'volume_json',side_effect=cloud_json), \
             patch.object(runner,'Answers') as answer_cls, \
             patch('openai.OpenAI'), patch.object(runner.time,'sleep',side_effect=next_poll), \
             patch.dict(runner.os.environ,{'SPENDING_LIMIT_USD':'30'}):
            answer_cls.return_value.evaluate.side_effect=evaluate
            runner.collect(self.root,True,True)
        self.assertTrue(json.loads((self.root/'summary.json').read_text())['complete'])


if __name__ == '__main__':
    unittest.main()
