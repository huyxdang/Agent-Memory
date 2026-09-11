import copy
import json
from pathlib import Path
import tempfile
import unittest

from prepare_teacher_sft import LIMIT, replay
from teacher_traces import Journal


class TeacherExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.item = dict(haystack_sessions=[[{'role':'user','content':'I like tea.'}]],
            haystack_dates=['2026-01-01'], haystack_session_ids=['session1'],
            question='EVALUATION QUESTION MUST NOT LEAK',answer='REFERENCE MUST NOT LEAK')
        self.target = '{"narrative":["The user likes tea."],"atomic":[]}'
        config = dict(max_output_tokens=100,context_window=100000)
        journal = Journal(Path(self.temp.name),config,1)
        journal.build(self.item,config,lambda _:dict(content=self.target,finish_reason='stop'))

    def state(self):
        return json.loads(next((Path(self.temp.name)/'histories').glob('*.json')).read_text())

    @staticmethod
    def measure(messages,target):
        return dict(prompt_tokens=90,target_tokens=10,sequence_tokens=101)

    def test_exact_target_and_no_evaluation_labels(self):
        rows,excluded=replay(self.item,self.state(),self.measure)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['messages'][-1],dict(role='assistant',content=self.target))
        self.assertNotIn(self.item['question'],json.dumps(rows))
        self.assertNotIn(self.item['answer'],json.dumps(rows))
        self.assertEqual(excluded,[])

    def test_tampered_prompt_rejected(self):
        state=self.state();state['calls'][0]['training_input'][0]['content']='different'
        with self.assertRaisesRegex(ValueError,'input does not match'):
            replay(self.item,state,self.measure)

    def test_duplicate_completed_session_rejected(self):
        state=self.state();state['calls'].append(copy.deepcopy(state['calls'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            replay(self.item,state,self.measure)

    def test_unknown_attempt_excluded_without_losing_completed_prefix(self):
        state=self.state();state['calls'].insert(0,dict(session=1,status='abandoned_unknown'))
        rows,excluded=replay(self.item,state,self.measure)
        self.assertEqual(len(rows),1)
        self.assertEqual(excluded[0]['reason'],'abandoned_unknown')

    def test_oversized_preserved_not_truncated(self):
        rows,_=replay(self.item,self.state(),lambda *_:dict(prompt_tokens=LIMIT,target_tokens=10,sequence_tokens=LIMIT+11))
        self.assertFalse(rows[0]['fits_context'])
        self.assertEqual(rows[0]['messages'][-1]['content'],self.target)

    def test_replayed_memory_tampering_rejected(self):
        state=self.state();state['lines']=[]
        with self.assertRaisesRegex(ValueError,'Replayed'):
            replay(self.item,state,self.measure)


if __name__ == '__main__':
    unittest.main()
