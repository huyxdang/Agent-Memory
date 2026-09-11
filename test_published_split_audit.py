import unittest

from audit_published_split import session_components, validate_indices


class PublishedSplitTests(unittest.TestCase):
    def test_chain_is_connected_without_all_pairs_sharing(self):
        graph = session_components([{'a'}, {'a', 'b'}, {'b'}, {'c'}])
        self.assertEqual(graph['component_sizes'], [3, 1])
        self.assertEqual(graph['sessions_in_multiple_histories'], 2)

    def test_duplicate_session_within_history_does_not_add_owner(self):
        graph = session_components([['a', 'a'], ['b']])
        self.assertEqual(graph['component_sizes'], [1, 1])
        self.assertEqual(graph['sessions_in_multiple_histories'], 0)

    def test_split_must_cover_rows_exactly_once(self):
        self.assertEqual(validate_indices({'train': [0], 'val': [1], 'test': [2]}, 3),
                         {'train': 1, 'val': 1, 'test': 1})
        for split in ({'train': [0], 'val': [0], 'test': [2]},
                      {'train': [0], 'val': [1], 'test': [3]},
                      {'train': [False], 'val': [1], 'test': [2]}):
            with self.assertRaises(ValueError):
                validate_indices(split, 3)
