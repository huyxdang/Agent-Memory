import copy
import unittest

from adaption_memory import integrity as ev
from adaption_memory import memory
from tools import audit_training_traces as audit


class TrainingAuditTests(unittest.TestCase):
    def test_shared_sessions_and_scale_families_never_cross_split(self):
        catalog = {
            "a": {"family": "a", "stratum": "LME", "session_hashes": ["x"]},
            "b": {"family": "b", "stratum": "LME", "session_hashes": ["x", "y"]},
            "c": {"family": "c", "stratum": "LME", "session_hashes": ["y"]},
            "d": {"family": "beam:1", "stratum": "100K", "session_hashes": ["d"]},
            "e": {"family": "beam:1", "stratum": "500K", "session_hashes": ["e"]},
        }
        split, _ = audit.split_histories(catalog, catalog, "test")
        self.assertEqual(split["a"], split["b"])
        self.assertEqual(split["b"], split["c"])
        self.assertEqual(split["d"], split["e"])
        self.assertEqual(split["a"][0], "train")

    def test_ten_independent_histories_split_eight_two_deterministically(self):
        catalog = {str(i): {"family": str(i), "stratum": "locomo", "session_hashes": [str(i)]} for i in range(10)}
        first = audit.split_histories(catalog, catalog, "test")
        second = audit.split_histories(dict(reversed(list(catalog.items()))), catalog, "test")
        self.assertEqual(first, second)
        self.assertEqual(sum(s == "dev" for s, _ in first[0].values()), 2)

    def record(self):
        messages = [{"role": "user", "content": "I live in Paris."}]
        parts = memory.extraction_parts([], 1, 1, "2026/01/01", messages)
        target = '{"narrative": ["User lives in Paris."], "atomic": []}'
        lines = [{"kind": "narrative", "session": 1, "date": "2026/01/01", "text": "User lives in Paris."}]
        record = {"history": {"sessions": 1}, "history_sha256": audit.digest([{"timestamp": "2026/01/01", "messages": messages}]),
                  "memory": {"sessions_done": 1, "lines": lines, "failures": [], "extraction_calls": [{
                      "session": 1, "ok": True, "finish_reason": "stop", "session_message": parts[-1],
                      "memory_message_count": 1, "prompt_sha256": ev.sha256_text("\n\n".join(parts)), "content": target, "new_lines": 1}]}}
        prompts = {"extraction_system": "Extract memory.", "extraction_message_formats": {
            "memory": memory.MEMORY_MESSAGE_FORMAT, "empty_memory": memory.EMPTY_MEMORY_MESSAGE,
            "session": memory.SESSION_MESSAGE_FORMAT}}
        return record, prompts

    def test_reconstruction_verifies_original_prompt_and_target(self):
        record, prompts = self.record()
        updates, _ = audit.reconstruct(record, prompts)
        self.assertEqual(len(updates), 1)
        broken = copy.deepcopy(record)
        broken["memory"]["extraction_calls"][0]["prompt_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "prompt_hash_mismatch"):
            audit.reconstruct(broken, prompts)
        broken = copy.deepcopy(record)
        broken["memory"]["lines"][0]["text"] = "Different target"
        with self.assertRaisesRegex(ValueError, "target_store_mismatch"):
            audit.reconstruct(broken, prompts)

    def test_partial_history_is_not_training_ready(self):
        record, prompts = self.record()
        record["memory"]["sessions_done"] = 0
        with self.assertRaisesRegex(ValueError, "incomplete_history"):
            audit.reconstruct(record, prompts)


if __name__ == "__main__":
    unittest.main()
