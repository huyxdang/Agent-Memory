import unittest
from tools.sample_trace_review import category


class TraceReviewSampleTests(unittest.TestCase):
    def test_warning_categories_are_disjoint_and_prioritized(self):
        self.assertEqual(category({'quality_flags': []}), 'unflagged')
        self.assertEqual(category({'quality_flags': ['value_not_in_session']}), 'value')
        self.assertEqual(category({'quality_flags': ['value_not_in_session', 'anchor_not_in_session:2022']}), 'date_number')
        self.assertEqual(category({'quality_flags': ['chain_tail_mismatch', 'anchor_not_in_session:2022']}), 'memory_update')


if __name__ == '__main__':
    unittest.main()
