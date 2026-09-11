import unittest

from experiment_preflight import classify


class SplitPreflightTests(unittest.TestCase):
    def test_distinct_questions_do_not_make_shared_sessions_independent(self):
        rows = [{'history_sha256': 'train', 'session_hashes': ['s1']},
                {'history_sha256': 'new', 'session_hashes': ['s1', 's2']},
                {'history_sha256': 'heldout', 'session_hashes': ['s3']}]
        result = classify(rows, {'train'}, {'s1'})
        self.assertEqual([len(result[k]) for k in result], [1, 1, 1])
        self.assertEqual(result['eligible'][0]['history_sha256'], 'heldout')
