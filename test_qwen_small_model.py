import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from adaption_memory.execution import modal
from adaption_memory.execution.vllm_worker import extract
from adaption_memory.inference.adapters import adapter_spec
from adaption_memory.inference.models import model_spec
from adaption_memory.inference.vllm import normalize_messages, request_model, server_command
from adaption_memory.presets import load_preset


class SmallModelTests(unittest.IsolatedAsyncioTestCase):
    def test_finetuned_model_is_a_pinned_configuration(self):
        preset = load_preset(Path("experiment_specs/locomo-qwen-08b-finetuned-final50.json"))
        payload, grouped = modal.build_payload(preset, smoke_histories=2, smoke_updates=2)

        self.assertEqual(payload["model"], "Qwen/Qwen3.5-0.8B")
        self.assertEqual(payload["revision"], "2fc06364715b967f1860aea9cf38778875588b17")
        self.assertEqual(payload["adapter"]["revision"], "8bcb7c3e333fb1b5577330886820150c68b7860f")
        self.assertEqual(payload["gpu"], "L4")
        self.assertEqual(payload["concurrency"], 10)
        self.assertEqual(len(payload["histories"]), 2)
        self.assertEqual(set(grouped), {row["history_sha256"] for row in payload["histories"]})
        self.assertEqual(request_model(payload), "adaption-agent-memory")
        command = server_command(payload, "/cache/pinned-adapter")
        self.assertEqual(command[2], "Qwen/Qwen3.5-0.8B")
        self.assertIn("adaption-agent-memory=/cache/pinned-adapter", command)

    def test_adapter_and_model_revisions_are_validated_at_their_owners(self):
        with self.assertRaises(ValueError):
            adapter_spec("huyxdang/adaption_agent_memory", "main")
        with self.assertRaises(ValueError):
            model_spec("unpublished/model")
        adapter = adapter_spec("huyxdang/adaption_agent_memory", "c" * 40)
        self.assertEqual(adapter.base_model, "Qwen/Qwen3.5-0.8B")

    def test_gemma_profile_merges_extractor_user_blocks(self):
        model = model_spec("google/gemma-3-4b-it")
        payload = {"merge_user_messages": model.merge_user_messages}
        original = [
            {"role": "system", "content": "rules"},
            {"role": "user", "content": "memory"},
            {"role": "user", "content": "session"},
        ]
        self.assertEqual(normalize_messages(payload, original), [
            {"role": "system", "content": "rules"},
            {"role": "user", "content": "memory\n\nsession"},
        ])

    async def test_small_model_runs_ten_ordered_streams(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {
                "fingerprint": "test",
                "concurrency": 10,
                "context_window": 65536,
                "structured_output": True,
                "merge_user_messages": False,
                "sampling": {"temperature": 0},
                "histories": [
                    {
                        "history_sha256": str(index),
                        "subject": "user",
                        "history": [{"timestamp": "today", "messages": [{"role": "user", "content": "Tea"}]}],
                    }
                    for index in range(10)
                ],
            }
            active = peak = 0
            ready = asyncio.Event()

            async def infer(ids):
                nonlocal active, peak
                active += 1
                peak = max(peak, active)
                if active == 10:
                    ready.set()
                await asyncio.wait_for(ready.wait(), 5)
                active -= 1
                return {"content": '{"narrative":[],"atomic":[]}', "finish_reason": "stop", "output_tokens": 5}

            async def commit():
                return None

            result = await extract(payload, root, infer, lambda _: [1], commit)
            self.assertEqual(peak, 10)
            self.assertEqual(result["completed_updates"], 10)

    def test_stopped_sandbox_marks_inflight_call_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "memories/history.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"status": "running", "sessions_done": 1, "calls": [{"status": "in_flight"}]}))
            self.assertEqual(modal.reconcile_stopped_states(root, {"histories": [{"history_sha256": "history"}]}), ["history"])
            self.assertEqual(json.loads(path.read_text())["status"], "unknown_outcome")



class RequestModelTests(unittest.TestCase):
    def test_explicit_null_adapter_routes_to_the_base_model(self):
        """A prepared payload always carries an `adapter` key, null when there is no LoRA.

        `dict.get(key, default)` returns the stored None rather than the default,
        so a non-adapter run must not chain another `.get` onto it. This crashed
        every base-model Modal run at startup.
        """
        self.assertEqual(request_model({"adapter": None, "model": "google/gemma-3-4b-it"}), "google/gemma-3-4b-it")

    def test_adapter_payload_routes_to_the_adapter_name(self):
        self.assertEqual(request_model({"adapter": {"name": "ft-08b"}, "model": "Qwen/Qwen3.5-0.8B"}), "ft-08b")

    def test_missing_adapter_key_routes_to_the_base_model(self):
        self.assertEqual(request_model({"model": "Qwen/Qwen3.5-0.8B"}), "Qwen/Qwen3.5-0.8B")

if __name__ == "__main__":
    unittest.main()
