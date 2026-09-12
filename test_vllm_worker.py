import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from adaption_memory.execution.files import save
from adaption_memory.execution.vllm_worker import extract


class VllmWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_many_histories_are_bounded_ordered_and_resumable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = {
                "fingerprint": "test",
                "concurrency": 8,
                "context_window": 65536,
                "merge_user_messages": False,
                "histories": [
                    {
                        "history_sha256": str(index),
                        "subject": "user",
                        "history": [
                            {"timestamp": "2026-01-01", "messages": [{"role": "user", "content": "I like tea."}]}
                            for _ in range(2)
                        ],
                    }
                    for index in range(100)
                ],
            }
            active = peak = calls = 0

            async def infer(ids):
                nonlocal active, peak, calls
                active += 1
                peak = max(peak, active)
                calls += 1
                await asyncio.sleep(0.005)
                active -= 1
                return {"content": '{"narrative":["The user likes tea."],"atomic":[]}', "finish_reason": "stop", "output_tokens": 12}

            async def commit():
                return None

            summary = await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(peak, 8)
            self.assertEqual(calls, 200)
            self.assertEqual(summary["new_completed_updates"], 200)
            resumed = await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(resumed["new_completed_updates"], 0)
            self.assertEqual(calls, 200)

    async def test_not_dispatched_request_can_resume_but_inflight_cannot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = {
                "fingerprint": "f",
                "concurrency": 1,
                "context_window": 65536,
                "merge_user_messages": False,
                "histories": [{"history_sha256": "h", "subject": "user", "history": [
                    {"timestamp": "today", "messages": [{"role": "user", "content": "Tea"}]}
                ]}],
            }

            async def infer(ids):
                return {"content": '{"narrative":[],"atomic":[]}', "finish_reason": "stop", "output_tokens": 9}

            async def commit():
                return None

            await extract(payload, root, infer, lambda _: [1], commit)
            path = root / "memories/h.json"
            state = json.loads(path.read_text())
            state.update(status="running", sessions_done=0, lines=[])
            state["calls"][0]["status"] = "not_dispatched"
            save(path, state)
            await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(len(json.loads(path.read_text())["calls"]), 1)
            state = json.loads(path.read_text())
            state.update(status="running", sessions_done=0, lines=[])
            state["calls"][0]["status"] = "in_flight"
            save(path, state)
            await extract(payload, root, Mock(), lambda _: [1], commit)
            self.assertEqual(json.loads(path.read_text())["status"], "unknown_outcome")

    async def test_invalid_output_is_recorded_on_the_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = {
                "fingerprint": "f",
                "concurrency": 1,
                "context_window": 65536,
                "merge_user_messages": False,
                "histories": [{"history_sha256": "h", "subject": "user", "history": [
                    {"timestamp": "today", "messages": [{"role": "user", "content": "Tea"}]}
                ]}],
            }

            async def infer(ids):
                return {"content": "not json", "finish_reason": "stop", "output_tokens": 2}

            async def commit():
                return None

            await extract(payload, root, infer, lambda _: [1], commit)
            state = json.loads((root / "memories/h.json").read_text())
            self.assertEqual(state["status"], "invalid_output")
            self.assertEqual(state["calls"][-1]["status"], "invalid_output")

    async def test_duplicate_history_is_rejected_before_inference(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unique"):
                await extract(
                    {"concurrency": 8, "histories": [{"history_sha256": "a"}] * 2},
                    Path(temp),
                    Mock(),
                    Mock(),
                    Mock(),
                )


if __name__ == "__main__":
    unittest.main()
