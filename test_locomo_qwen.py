import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from beam_baseline_answers import Answers
from checkpoint_io import save
import qwen_vllm as runner
from third_party.mem0 import locomo_prompts


class LoCoMoTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.settings=dict(answer_model='gpt-5.6-luna',judge_model='gpt-5',answer_max_tokens=100,
            judge_max_tokens=100,answer_reasoning_effort='none',answer_context_window=100000,
            judge_input_rate=1.25,judge_output_rate=10)
        self.item=dict(question_id='locomo0_q1',question='What does Alice like?',
            answer='REFERENCE_ONLY_TEA',question_date='today')
        self.state=dict(history_sha256='a',lines=[],sessions_done=2,status='complete')

    def response(self,content,finish='stop'):
        return SimpleNamespace(id='test',model='resolved',
            choices=[SimpleNamespace(message=SimpleNamespace(content=content),finish_reason=finish)],
            usage=SimpleNamespace(prompt_tokens=20,completion_tokens=10,total_tokens=30,
                prompt_tokens_details=None,completion_tokens_details=None))

    def test_judge_labels_prompts_and_resume(self):
        for label,expected in [('CORRECT','yes'),('WRONG','no'),('UNKNOWN','invalid')]:
            with self.subTest(label=label):
                root=self.root/label
                client=Mock()
                client.chat.completions.create.side_effect=[self.response('tea'),
                    self.response(json.dumps(dict(label=label,reason='test explanation')))]
                answers=Answers(root,client,self.settings,benchmark='locomo')
                answers.evaluate(self.item,self.state)
                result=json.loads((root/'results/locomo0_q1.json').read_text())
                self.assertEqual(result['judge_verdict'],expected)
                self.assertEqual(result['status'],'failed' if expected=='invalid' else 'success')
                self.assertIn('test explanation',result['judge_explanation'])
                requests=client.chat.completions.create.call_args_list
                self.assertNotIn('REFERENCE_ONLY_TEA',str(requests[0]))
                self.assertEqual(requests[1].kwargs['messages'],[
                    dict(role='system',content=locomo_prompts.JUDGE_SYSTEM_PROMPT),
                    dict(role='user',content=locomo_prompts.JUDGE_PROMPT.format(
                        question=self.item['question'],answer=self.item['answer'],response='tea'))])
                answers.evaluate(self.item,self.state)
                self.assertEqual(client.chat.completions.create.call_count,2)

    def test_frozen_smoke_selection_across_concurrency(self):
        selected=[]
        for concurrency in (1,4,8,16):
            payload=dict(histories=[dict(history_sha256=str(i),subject='Alice and Bob',history=[]) for i in range(10)])
            grouped={str(i):[{**self.item,'question_id':f'{i}_{j}'} for j in range(5)] for i in range(10)}
            with patch.object(runner,'locomo_inputs',return_value=(payload,grouped,self.settings)):
                config=runner.prepare(self.root/str(concurrency),True,concurrency,True,'locomo')
            self.assertEqual(config['scope'],'smoke')
            self.assertEqual(config['payload']['updates_per_history'],2)
            self.assertNotIn('REFERENCE_ONLY_TEA',json.dumps(config['payload']))
            self.assertEqual(config['judge_system_prompt'],locomo_prompts.JUDGE_SYSTEM_PROMPT)
            selected.append(config['payload']['histories'])
        self.assertTrue(all(rows==selected[0] for rows in selected))

    def test_shared_memory_fanout_before_other_history_finishes(self):
        grouped={key:[{**self.item,'question_id':key+str(i)} for i in range(3)] for key in ('a','b')}
        payload=dict(fingerprint='f',histories=[dict(history_sha256=k) for k in grouped])
        save(self.root/'configuration.json',dict(benchmark='locomo',questions=grouped,payload=payload,
            settings=self.settings,scope='LoCoMo final 50'))
        save(self.root/'cloud.json',dict(sandbox_id='fake',run_id='fake',reserved_usd=1,
            gpu_started_at=runner.now(),rate_usd_s=.001))
        modal=Mock()
        modal.Sandbox.from_id.return_value.poll.side_effect=[None,0]
        second_complete=False
        first_batch=threading.Barrier(3)
        first_done=threading.Event()
        states=[]
        def evaluate(item,state):
            self.assertEqual(state['status'],'complete')
            if item['question_id'].startswith('a'):
                self.assertFalse(second_complete)
                states.append(state)
                first_batch.wait(timeout=3)
                first_done.set()
            save(self.root/'results'/f"{item['question_id']}.json",dict(question_id=item['question_id'],status='success'))
        def read(volume,path):
            key=Path(path).stem
            status='complete' if key=='a' or second_complete else 'running'
            if '/progress/' in path:return dict(status=status)
            if '/memories/' in path:return dict(payload_sha256='f',history_sha256=key,status=status,
                calls=[dict(status=status,stream_key=key)])
            if '/streams/' in path:return dict(status='complete',content='diagnostic only')
            return None
        def poll_again(_):
            nonlocal second_complete
            self.assertTrue(first_done.wait(4))
            second_complete=True
        with patch.object(runner,'cloud',return_value=(modal,Mock())), \
             patch.object(runner,'volume_json',side_effect=read), \
             patch.object(runner,'Answers') as answer_cls, patch('openai.OpenAI'), \
             patch.object(runner.time,'sleep',side_effect=poll_again), \
             patch.dict(runner.os.environ,{'SPENDING_LIMIT_USD':'30'}):
            answer_cls.return_value.evaluate.side_effect=evaluate
            runner.collect(self.root,True,True)
        self.assertEqual(len(states),3)
        self.assertTrue(all(s is states[0] for s in states))
        self.assertEqual(answer_cls.call_args.kwargs['benchmark'],'locomo')
        summary=json.loads((self.root/'summary.json').read_text())
        self.assertTrue(summary['complete'])
        self.assertEqual(summary['valid'],6)
        self.assertEqual(json.loads((self.root/'streams/a.json').read_text())['content'],'diagnostic only')

    def test_complete_pilot_import_preserves_memory_and_rejects_settings_drift(self):
        def inputs():
            return (dict(histories=[dict(history_sha256=str(i),history=[]) for i in range(10)]),
                {str(i):[{**self.item,'question_id':str(i)}] for i in range(10)},self.settings)
        source=self.root/'pilot';dest=self.root/'final'
        with patch.object(runner,'locomo_inputs',side_effect=inputs):
            pilot=runner.prepare(source,False,8,True,'locomo',pilot_histories=2)
            self.assertEqual(len(pilot['questions']),2)
            self.assertIsNone(pilot['payload']['updates_per_history'])
            for key in pilot['questions']:
                save(source/'memories'/f'{key}.json',dict(history_sha256=key,status='complete',
                    payload_sha256=pilot['payload']['fingerprint'],lines=['saved'],sessions_done=0,calls=[]))
            final=runner.prepare(dest,False,8,True,'locomo',reuse_from=source)
            self.assertEqual(len(final['questions']),10)
            self.assertEqual(len(final['checkpoint_import']['state_sha256']),2)
            self.assertEqual(json.loads((dest/'memories/0.json').read_text())['lines'],['saved'])
            with self.assertRaisesRegex(ValueError,'configuration differs'):
                runner.prepare(self.root/'bad',False,4,True,'locomo',reuse_from=source)


if __name__=='__main__':unittest.main()
