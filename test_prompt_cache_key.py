"""The provider's prompt cache only hits when calls sharing a long prefix route together."""
import unittest
from unittest.mock import Mock

from adaption_memory.execution.local import OpenAIBackend
from adaption_memory.inference.openai import BudgetLedger, ChatRequest, OpenAITransport, Price


def transport_with(capture):
    client = Mock()
    client.chat.completions.create.side_effect = lambda **kwargs: capture.append(kwargs) or Mock(
        id="r", model="m", system_fingerprint=None,
        choices=[Mock(message=Mock(content="ok"), finish_reason="stop")],
        usage=Mock(prompt_tokens=10, completion_tokens=1, total_tokens=11,
                   prompt_tokens_details=None, completion_tokens_details=None),
    )
    return OpenAITransport(client, BudgetLedger(10.0))


class CacheKeyTest(unittest.TestCase):
    def test_key_is_sent_when_set_and_omitted_when_not(self):
        for key, expected in (("locomo-abc123", "locomo-abc123"), (None, None)):
            capture = []
            transport_with(capture).chat(ChatRequest(
                call_id="c", model="gpt-5.6-luna", system="s", user_messages=({"role": "user", "content": "u"},),
                max_output_tokens=16, price=Price(0.2, 0.02, 1.2), cache_key=key))
            self.assertEqual(capture[0].get("prompt_cache_key"), expected)

    def test_backend_forwards_the_key(self):
        capture = []
        price = Price(0.2, 0.02, 1.2)
        backend = OpenAIBackend(transport_with(capture), price, price, price)
        backend.complete(call_id="c", stage="answer", model="gpt-5.6-luna", system="s",
                         user_messages=({"role": "user", "content": "u"},), max_output_tokens=16,
                         reasoning_effort=None, response_format=None, observe=lambda call: None,
                         item={}, cache_key="beam-h1")
        self.assertEqual(capture[0]["prompt_cache_key"], "beam-h1")


class MemoryReimportTest(unittest.TestCase):
    def test_same_memory_content_keeps_graded_rows_across_a_code_revision(self):
        """An artifact's name encodes the code revision; the memory's content does not."""
        content = "c0ffee"
        rows = [
            {"question_id": "a", "status": "success", "memory_sha256": "old", "memory_content_sha256": content},
            {"question_id": "b", "status": "memory_complete", "memory_sha256": "old", "memory_content_sha256": "other"},
        ]
        for row in rows:
            if row.get("memory_content_sha256") != content:
                row.update(status="memory_complete", memory_sha256="new", memory_content_sha256=content)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["memory_sha256"], "old")
        self.assertEqual(rows[1]["memory_sha256"], "new")


if __name__ == "__main__":
    unittest.main()


class ExecutorCostTest(unittest.TestCase):
    def test_reimport_reuses_the_existing_executor_record(self):
        """A resumed Modal run re-imports its checkpoints; the GPU must be charged once, not once per resume."""
        artifacts = [("executor_call_state", {"call_id": "run:modal", "cost_usd": 1.04})]
        call_id = "run:modal"
        already = next((a for a in artifacts if a[0] == "executor_call_state" and a[1]["call_id"] == call_id), None)
        self.assertIsNotNone(already)
        self.assertEqual(sum(a[1]["cost_usd"] for a in artifacts), 1.04)


class ExtractionConcurrencyTest(unittest.TestCase):
    """Sessions of one history must stay ordered; independent histories must not wait for each other."""

    def test_histories_extract_side_by_side_and_sessions_stay_ordered(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor

        lock = threading.Lock()
        in_flight = concurrent_peak = 0
        order = {}

        def build(history, sessions):
            nonlocal in_flight, concurrent_peak
            for index in range(sessions):
                with lock:
                    in_flight += 1
                    concurrent_peak = max(concurrent_peak, in_flight)
                    order.setdefault(history, []).append(index)
                time.sleep(0.01)
                with lock:
                    in_flight -= 1

        import time
        with ThreadPoolExecutor(max_workers=max(1, min(8, 3))) as pool:
            for future in [pool.submit(build, h, 4) for h in ("a", "b", "c")]:
                future.result()
        self.assertGreater(concurrent_peak, 1, "histories did not overlap")
        for history, indexes in order.items():
            self.assertEqual(indexes, sorted(indexes), f"{history} ran its sessions out of order")
