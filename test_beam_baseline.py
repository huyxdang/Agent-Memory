import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from beam_baseline_answers import Answers


class BaselineResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        self.settings=dict(answer_model='gpt-5.6-luna',judge_model='gpt-5',answer_max_tokens=100,
            judge_max_tokens=100,answer_reasoning_effort='none',answer_context_window=100000,
            judge_input_rate=1.25,judge_output_rate=10)
        self.client=Mock()
        self.client.chat.completions.create.return_value=SimpleNamespace(id='id',model='resolved',
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"score":1}'),finish_reason='stop')],
            usage=SimpleNamespace(prompt_tokens=20,completion_tokens=10,total_tokens=30,
                prompt_tokens_details=None,completion_tokens_details=None))

    def test_saved_call_is_not_repeated(self):
        a=Answers(self.path,self.client,self.settings)
        messages=[{'role':'user','content':'question'}]
        expected=a.request('answer_x',messages)
        b=Answers(self.path,self.client,self.settings)
        self.assertEqual(b.request('answer_x',messages),expected)
        self.assertEqual(self.client.chat.completions.create.call_count,1)

    def test_unknown_outcome_blocks_resume(self):
        self.client.chat.completions.create.side_effect=TimeoutError()
        with self.assertRaises(TimeoutError):
            Answers(self.path,self.client,self.settings).request('answer_x',[])
        with self.assertRaises(RuntimeError):
            Answers(self.path,self.client,self.settings).request('answer_x',[])
        self.assertEqual(self.client.chat.completions.create.call_count,1)

    def test_budget_and_changed_prompt_rejected(self):
        with self.assertRaises(RuntimeError):
            Answers(self.path,self.client,self.settings,limit=0).request('answer_x',[])
        a=Answers(self.path,self.client,self.settings)
        a.request('answer_x',[])
        with self.assertRaises(ValueError):
            a.request('answer_x',[{'role':'user','content':'different'}])

    def test_end_to_end_judge_and_resume(self):
        item=dict(question_id='beam100K_test',question='Preference?',answer='tea',question_date='2026-01-01',rubric=['mentions tea'])
        state=dict(history_sha256='h',sessions_done=1,lines=[])
        a=Answers(self.path,self.client,self.settings)
        a.evaluate(item,state)
        result=json.loads((self.path/'results/beam100K_test.json').read_text())
        self.assertEqual(result['status'],'success')
        self.assertEqual(result['judge_verdict'],'yes')
        self.assertEqual(self.client.chat.completions.create.call_count,2)
        a.evaluate(item,state)
        self.assertEqual(self.client.chat.completions.create.call_count,2)


if __name__=='__main__':
    unittest.main()
