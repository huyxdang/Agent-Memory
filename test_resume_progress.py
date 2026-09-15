import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from adaption_memory.benchmarks.base import BenchmarkItem, Message, Session
from adaption_memory.evaluation.pipeline import Coordinator
from adaption_memory.execution import modal
from adaption_memory.execution.files import save
from adaption_memory.execution.local import FixtureBackend
from adaption_memory.presets import load_preset
from adaption_memory.run_store.records import RunStatus


class ResumeProgressTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        session = Session("s1", "2026-01-01", (Message("user", "I like tea."),))
        items = [BenchmarkItem("beam", key, "abstention", "What do I like?", "Tea", "2026-01-02",
                               (session,), "user", "beam", rubric=("Tea", "No coffee")) for key in ("a", "b")]
        source = self.root / "source.json"
        save(source, [item.to_record() for item in items])
        selection = self.root / "selection.json"
        save(selection, {"questions": [{"question_id": item.question_id, "question_type": item.question_type}
                                        for item in items]})
        adapter = SimpleNamespace(load=lambda: items, source_files=lambda: (source,))
        patcher = patch("adaption_memory.presets.benchmark_adapter", return_value=adapter)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.preset = replace(load_preset(Path("experiment_specs/beam-100k-50-qwen9b.json")),
                              name="resume-fixture", selections=(selection,), concurrency=1)
        self.coordinator = Coordinator(self.root / "runs")
        self.coordinator.prepare("run", self.preset)
        self.directory = self.root / "runs/run/modal"
        config = modal.prepare(self.directory, self.preset)
        history = config["payload"]["histories"][0]
        self.memory_path = self.directory / "memories" / (history["history_sha256"] + ".json")
        save(self.memory_path, {"history_sha256": history["history_sha256"],
                               "payload_sha256": config["payload"]["fingerprint"], "status": "complete",
                               "sessions_done": 1, "calls": [], "warnings": [],
                               "lines": [{"kind": "narrative", "session": 1, "date": "2026-01-01", "text": "Likes tea."}]})
        save(self.directory / "cloud.json", {"termination": "confirmed", "accounted_usd": 0.5})
        self.executor = {"name": "modal", "reserved_usd": 1.0, "cost_usd": 0.5}
        self.import_memories()

    def import_memories(self):
        return self.coordinator.import_memories("run", self.preset, self.directory, self.executor)

    def load(self):
        return self.coordinator.store.load("run")

    def run_fixture(self, backend=None):
        return self.coordinator.run("run", self.preset, backend or FixtureBackend(), allow_paid=True)

    def leave_mislabeled_results(self):
        checkpoint = self.coordinator.store.checkpoint

        def legacy_checkpoint(manifest, rows):
            if manifest.status is RunStatus.COMPLETE:
                manifest = replace(manifest, status=RunStatus.COMPLETE_WITH_FAILURES)
                rows = copy.deepcopy(rows)
                rows[0]["status"] = "memory_complete"
                for row in rows:
                    row.pop("memory_content_sha256", None)
            return checkpoint(manifest, rows)

        with patch.object(self.coordinator.store, "checkpoint", side_effect=legacy_checkpoint):
            self.run_fixture()

    def test_reimport_preserves_old_rows_without_content_digest(self):
        self.leave_mislabeled_results()
        before = self.load()
        self.import_memories()
        after = self.load()
        self.assertEqual(after.results, before.results)
        self.assertEqual(after.manifest.artifacts, before.manifest.artifacts)

    def test_resume_repairs_completed_rows_without_calls_or_rewriting_history(self):
        self.leave_mislabeled_results()
        before = self.load()
        root = self.root / "runs/run"
        original_files = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                          for directory in (root / "artifacts", root / "generations")
                          for p in directory.rglob("*.json*")}
        calls = []

        class NoCalls:
            def complete(inner, **kwargs):
                calls.append(kwargs["call_id"])
                raise AssertionError("Completed work must not call a provider")

        self.assertEqual(self.run_fixture(NoCalls()).status, RunStatus.COMPLETE)
        after = self.load()
        self.assertEqual(calls, [])
        self.assertEqual([r["status"] for r in after.results], ["success", "success"])
        for old, new in zip(before.results, after.results):
            for key in ("memory_sha256", "answer_sha256", "judge_sha256", "judge_parts", "score", "verdict"):
                self.assertEqual(old[key], new[key])
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in original_files.items()))

    def test_resume_only_finishes_remaining_judge_part_after_invalid_outputs(self):
        fixture = FixtureBackend()

        class InvalidLastPart:
            def complete(inner, **kwargs):
                if ":judge:2:b:" not in kwargs["call_id"]:
                    return fixture.complete(**kwargs)
                call = {"call_id": kwargs["call_id"], "state": "response_saved", "content": "invalid",
                        "ok": False, "reserved_usd": 0, "cost_usd": 0, "usage": {"input_tokens": 0, "output_tokens": 0}}
                kwargs["observe"](call)
                return call

        self.assertEqual(self.run_fixture(InvalidLastPart()).status, RunStatus.COMPLETE_WITH_FAILURES)
        before = self.load().results
        self.import_memories()
        calls = []

        class CountCalls:
            def complete(inner, **kwargs):
                calls.append(kwargs["call_id"])
                return fixture.complete(**kwargs)

        self.assertEqual(self.run_fixture(CountCalls()).status, RunStatus.COMPLETE)
        self.assertEqual(len(calls), 1)
        self.assertIn(":judge:2:b:", calls[0])
        self.assertTrue(calls[0].endswith(":3"))
        after = self.load().results
        self.assertEqual({k: v for k, v in before[0].items() if k != "report_sha256"},
                         {k: v for k, v in after[0].items() if k != "report_sha256"})
        self.assertEqual(before[1]["answer_sha256"], after[1]["answer_sha256"])
        self.assertEqual(before[1]["judge_parts"], after[1]["judge_parts"][:1])

    def test_changed_memory_is_rejected_without_replacing_saved_evaluation(self):
        self.leave_mislabeled_results()
        before = self.load().results
        state = json.loads(self.memory_path.read_text())
        state["lines"][0]["text"] = "Likes coffee."
        save(self.memory_path, state)
        with self.assertRaisesRegex(ValueError, "Memory content changed"):
            self.import_memories()
        self.assertEqual(self.load().results, before)

    def test_stopped_complete_local_memories_need_no_cloud_collection(self):
        with patch.object(modal, "cloud", side_effect=AssertionError("Unexpected cloud access")):
            result = modal.collect(self.directory)
        self.assertTrue(result["complete"])
        self.assertTrue(result["stopped"])

    def test_local_collection_rejects_wrong_memory_identity(self):
        state = json.loads(self.memory_path.read_text())
        state["payload_sha256"] = "wrong"
        save(self.memory_path, state)
        with patch.object(modal, "cloud", side_effect=AssertionError("Unexpected cloud access")):
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                modal.collect(self.directory)

    def test_incomplete_local_checkpoint_still_collects_from_cloud(self):
        self.memory_path.unlink()
        with patch.object(modal, "cloud", side_effect=RuntimeError("cloud collection reached")):
            with self.assertRaisesRegex(RuntimeError, "cloud collection reached"):
                modal.collect(self.directory)

    def test_unknown_judge_is_not_replayed_and_other_questions_finish(self):
        fixture = FixtureBackend()

        class UnknownJudge:
            def complete(inner, **kwargs):
                if ":judge:2:a:" not in kwargs["call_id"]:
                    return fixture.complete(**kwargs)
                call = {"call_id": kwargs["call_id"], "state": "unknown_outcome", "ok": False,
                        "reserved_usd": 0.1, "cost_usd": None, "usage": {}}
                kwargs["observe"](call)
                return call

        self.assertEqual(self.run_fixture(UnknownJudge()).status, RunStatus.BLOCKED)
        before = self.load().results
        self.import_memories()
        calls = []

        class NoCalls:
            def complete(inner, **kwargs):
                calls.append(kwargs["call_id"])
                raise AssertionError("Unresolved request must not be replayed")

        self.assertEqual(self.run_fixture(NoCalls()).status, RunStatus.BLOCKED)
        self.assertEqual(calls, [])
        after = self.load().results
        self.assertEqual(before, after)

    def test_reimport_after_code_change_retains_original_memory_and_judgments(self):
        self.leave_mislabeled_results()
        before = self.load()
        with patch("adaption_memory.presets.source_hashes", return_value={"runtime.py": "f" * 64}):
            self.import_memories()
        after = self.load()
        self.assertEqual(before.results, after.results)
        added = [ref.kind for ref in after.manifest.artifacts if ref not in before.manifest.artifacts]
        self.assertEqual(added, ["implementation_change"])

    def test_completed_checkpoint_releases_questions_blocked_on_extraction(self):
        loaded = self.load()
        for row in loaded.results:
            row.pop("memory_sha256")
            row.pop("memory_content_sha256")
            row.update(status="blocked_memory", last_call_state="unknown_outcome")
        self.coordinator.store.checkpoint(loaded.manifest, loaded.results)
        self.import_memories()
        self.assertEqual(self.run_fixture().status, RunStatus.COMPLETE)


if __name__ == "__main__":
    unittest.main()
