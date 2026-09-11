import json
from pathlib import Path
import tempfile
import unittest
from checkpoint_io import save
from finish_beam_answers import prepare


class AnswerContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.source=Path(self.temp.name)/'source';self.dest=Path(self.temp.name)/'dest'
        save(self.source/'configuration.json',dict(payload=dict(fingerprint='f',histories=[dict(history_sha256='h')]),
            settings=dict(answer_max_tokens=1024)))
        save(self.source/'memories/h.json',dict(history_sha256='h',payload_sha256='f',status='complete'))
        save(self.source/'api_calls/answer_q.json',dict(status='complete',reserved_usd=.1,response=dict(finish_reason='length')))
        save(self.source/'results/q.json',dict(question_id='q',status='failed'))

    def test_preserve_failed_cost_and_change_only_output_limit(self):
        c=prepare(self.source,self.dest)
        self.assertEqual(c['settings']['answer_max_tokens'],128000)
        self.assertTrue((self.source/'api_calls/answer_q.json').exists())
        self.assertFalse((self.dest/'api_calls/answer_q.json').exists())
        self.assertEqual(json.loads((self.dest/'api_calls/abandoned_answer_q.json').read_text())['reserved_usd'],.1)
        self.assertEqual(prepare(self.source,self.dest),c)

    def test_unknown_outcome_not_retried(self):
        save(self.source/'api_calls/answer_q.json',dict(status='in_flight'))
        with self.assertRaisesRegex(ValueError,'Unknown'):prepare(self.source,self.dest)


if __name__=='__main__':unittest.main()
