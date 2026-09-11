import unittest
from check_split_feasibility import purge, measure


class SplitFeasibilityTests(unittest.TestCase):
    def test_removing_bridge_allows_connected_graph_split(self):
        rows = [{"history_sha256": "a", "session_hashes": ["x"], "updates": 1},
                {"history_sha256": "b", "session_hashes": ["x", "y"], "updates": 2},
                {"history_sha256": "c", "session_hashes": ["y"], "updates": 1}]
        split = purge(rows, ["a"])
        self.assertEqual(split, {"train": ["c"], "dev": ["a"], "removed": ["b"]})
        self.assertEqual(measure(rows, split)["removed_updates"], 2)

    def test_disjoint_histories_are_preserved(self):
        rows = [{"history_sha256": str(i), "session_hashes": [str(i)], "updates": 4} for i in range(5)]
        split = purge(rows, ["0", "1"])
        self.assertEqual(len(split["train"]), 3)
        self.assertEqual(split["removed"], [])


if __name__ == "__main__":
    unittest.main()
