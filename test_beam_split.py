"""Offline guards for the approved BEAM split."""
import copy
import unittest

from tools.prepare_beam_split import SPLITS, validate_split


class BeamSplitTests(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(split=split, scale=scale, chat_id=n,
                          history_sha256=f'{scale}/{n}', shared_history_with_prior_eval=False,
                          shared_windows_with_prior_eval=0, shared_pairs_with_prior_eval=0)
                     for split, tiers in SPLITS.items() for scale, ids in tiers.items() for n in ids]

    def test_counts_and_valid_split(self):
        self.assertEqual([len(ids) for tiers in SPLITS.values() for ids in tiers.values()], [8, 8, 2, 2])
        validate_split(self.rows, [])

    def test_same_numeric_id_across_scales_is_not_identity(self):
        self.assertIn(('100K', 7), [(r['scale'], r['chat_id']) for r in self.rows])
        self.assertIn(('500K', 7), [(r['scale'], r['chat_id']) for r in self.rows])
        validate_split(self.rows, [])

    def test_missing_duplicate_and_wrong_assignment(self):
        wrong = copy.deepcopy(self.rows)
        wrong[0]['split'] = 'dev'
        for rows in (self.rows[:-1], self.rows + [self.rows[0]], wrong):
            with self.assertRaises(ValueError):
                validate_split(rows, [])

    def test_duplicate_history(self):
        self.rows[-1]['history_sha256'] = self.rows[0]['history_sha256']
        with self.assertRaises(ValueError):
            validate_split(self.rows, [])

    def test_final_overlap(self):
        for field in ('shared_history_with_prior_eval', 'shared_windows_with_prior_eval', 'shared_pairs_with_prior_eval'):
            rows = copy.deepcopy(self.rows)
            rows[0][field] = 1
            with self.assertRaises(ValueError):
                validate_split(rows, [])

    def test_pair_overlap_without_window_overlap(self):
        with self.assertRaises(ValueError):
            validate_split(self.rows, [{'windows': 0, 'pairs': 1}])


if __name__ == '__main__':
    unittest.main()
