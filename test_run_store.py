import json
import tempfile
import unittest
from pathlib import Path

from adaption_memory.domain import CallRecord, CallState, retry_allowed
from adaption_memory.run_store.accounting import aggregate_call_dicts, summarize_calls
from adaption_memory.run_store.checkpoints import RunStore
from adaption_memory.run_store.index import RunIndex
from adaption_memory.run_store.records import ArtifactRef, RunManifest, RunStatus


class RunStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = RunStore(self.root)
        self.manifest = RunManifest.new(
            run_id="run-1",
            spec_sha256="a" * 64,
            question_ids=("q1", "q2"),
        )
        self.results = [
            {"question_id": "q1", "status": "success"},
            {"question_id": "q2", "status": "success"},
        ]

    def test_checkpoint_round_trip_and_terminal_immutability(self):
        self.store.checkpoint(self.manifest, self.results)
        terminal = self.manifest.with_status(RunStatus.COMPLETE)
        self.store.checkpoint(terminal, self.results)

        loaded = self.store.load("run-1")
        self.assertEqual(loaded.manifest, terminal)
        self.assertEqual(loaded.results, self.results)

        with self.assertRaisesRegex(RuntimeError, "terminal"):
            self.store.checkpoint(terminal, self.results)

    def test_retry_gets_a_new_identity_and_parent(self):
        terminal = self.manifest.with_status(RunStatus.COMPLETE_WITH_FAILURES)
        self.store.checkpoint(terminal, self.results)

        retry = self.store.new_retry("run-1", "run-2")

        self.assertEqual(retry.run_id, "run-2")
        self.assertEqual(retry.retry_of, "run-1")
        self.assertEqual(retry.status, RunStatus.RUNNING)
        self.assertFalse((self.root / "run-2").exists())
        self.assertEqual(self.store.load("run-1").manifest.status, RunStatus.COMPLETE_WITH_FAILURES)

    def test_tampered_results_are_rejected(self):
        self.store.checkpoint(self.manifest, self.results)
        pointer = json.loads((self.root / "run-1" / "current.json").read_text())
        path = self.root / "run-1" / "generations" / pointer["generation"] / "results.jsonl"
        path.write_text('{"question_id":"q1","status":"changed"}\n')

        with self.assertRaisesRegex(RuntimeError, "results hash"):
            self.store.load("run-1")

    def test_tampered_manifest_and_mixed_generation_are_rejected(self):
        generation = self.store.checkpoint(self.manifest, self.results)
        run = self.root / "run-1"
        manifest_path = run / "generations" / generation / "manifest.json"
        original = manifest_path.read_text()
        manifest_path.write_text(original.replace('"running"', '"complete"'))
        with self.assertRaisesRegex(RuntimeError, "manifest hash"):
            self.store.load("run-1")

        manifest_path.write_text(original)
        pointer_path = run / "current.json"
        pointer = json.loads(pointer_path.read_text())
        pointer["generation"] = "f" * 64
        pointer_path.write_text(json.dumps(pointer))
        with self.assertRaisesRegex(RuntimeError, "missing checkpoint generation"):
            self.store.load("run-1")

    def test_run_index_is_append_only(self):
        index = RunIndex(self.root / "index.jsonl")
        index.append({"run_id": "run-1", "status": "complete"})
        with self.assertRaisesRegex(RuntimeError, "already contains"):
            index.append({"run_id": "run-1", "status": "failed"})
        self.assertEqual(index.rows(), [{"run_id": "run-1", "status": "complete"}])

    def test_question_set_and_exactly_once_are_verified(self):
        bad = [
            {"question_id": "q1", "status": "success"},
            {"question_id": "q1", "status": "success"},
        ]
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.store.checkpoint(self.manifest, bad)

    def test_artifact_graph_rejects_a_missing_parent(self):
        artifact = ArtifactRef(
            kind="answer",
            sha256="b" * 64,
            path="artifacts/answer/b.json",
            parent_sha256=("c" * 64,),
            implementation_revision="answer-v1",
        )
        bad = self.manifest.with_artifacts((artifact,))
        with self.assertRaisesRegex(ValueError, "missing parent"):
            self.store.checkpoint(bad, self.results)


class CallRecordTests(unittest.TestCase):
    def test_unknown_outcome_is_not_safe_to_retry(self):
        call = CallRecord.start("call-1", "model-a", reserved_usd=0.25)
        call = call.transition(CallState.IN_FLIGHT)
        call = call.transition(CallState.UNKNOWN_OUTCOME, error_type="TimeoutError")

        self.assertFalse(retry_allowed(call.state))
        with self.assertRaisesRegex(ValueError, "transition"):
            call.transition(CallState.IN_FLIGHT)

    def test_provider_rejection_returns_to_a_retryable_state(self):
        call = CallRecord.start("call-1", "model-a", reserved_usd=0.25)
        call = call.transition(CallState.IN_FLIGHT)
        call = call.transition(CallState.NOT_DISPATCHED)

        self.assertTrue(retry_allowed(call.state))
        self.assertEqual(call.transition(CallState.IN_FLIGHT).state, CallState.IN_FLIGHT)

    def test_accounting_separates_known_spend_and_exposure(self):
        complete = CallRecord.start("known", "model-a", reserved_usd=0.50)
        complete = complete.transition(CallState.IN_FLIGHT)
        complete = complete.transition(CallState.RESPONSE_SAVED, cost_usd=0.12)
        complete = complete.transition(CallState.COMPLETE)
        unknown = CallRecord.start("unknown", "model-a", reserved_usd=0.30)
        unknown = unknown.transition(CallState.IN_FLIGHT)
        unknown = unknown.transition(CallState.UNKNOWN_OUTCOME, error_type="TimeoutError")

        summary = summarize_calls((complete, unknown))

        self.assertEqual(summary.known_spend_usd, 0.12)
        self.assertEqual(summary.unknown_or_reserved_exposure_usd, 0.30)
        self.assertEqual(summary.unknown_outcome_calls, 1)

    def test_missing_usage_is_counted_without_becoming_zero_cost(self):
        summary = aggregate_call_dicts(
            ({"ok": True, "state": "complete", "cost_usd": None, "usage": {"input_tokens": None, "output_tokens": None}},)
        )

        self.assertEqual(summary["unknown_usage_calls"], 1)
        self.assertEqual(summary["unknown_cost_calls"], 1)
        self.assertEqual(summary["known_spend_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
