import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.benchmarks.locomo import LoCoMoAdapter, CATEGORY_NAMES
from adaption_memory.domain import CallState
from adaption_memory.evaluation.pipeline import Coordinator
from adaption_memory.execution.local import FixtureBackend
from adaption_memory.presets import ExperimentPreset, resolve
from adaption_memory.run_store.reporting import report_data


class CoordinatorTests(unittest.TestCase):
    def test_locomo_adapter_through_answering_and_judging_all_categories(self):
        by_type = {}
        for item in LoCoMoAdapter().load():
            by_type.setdefault(item.question_type, item)
        self.assertEqual(set(by_type), set(CATEGORY_NAMES.values()))
        selection = self.root / "locomo-selection.json"
        selection.write_text(json.dumps({"questions": [
            {"question_id": item.question_id, "question_type": item.question_type}
            for item in by_type.values()]}))
        preset = replace(self.preset, benchmark="locomo", selections=(selection,))
        self.coordinator.prepare("locomo-categories", preset)
        terminal = self.coordinator.run("locomo-categories", preset, FixtureBackend(), allow_paid=False)
        loaded = self.coordinator.store.load("locomo-categories")
        self.assertEqual(terminal.status.value, "complete")
        self.assertEqual(len(loaded.results), 4)
        self.assertTrue(all(row["status"] == "success" for row in loaded.results))
        self.assertTrue(all(row["verdict"] == "yes" for row in loaded.results))
        self.assertEqual(len({row["question_id"] for row in loaded.results}), 4)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        item = LongMemEvalAdapter().load()[0]
        self.selection = self.root / "selection.json"
        self.selection.write_text(json.dumps({"questions": [{"question_id": item.question_id, "question_type": item.question_type}]}))
        self.preset = ExperimentPreset(
            name="offline-contract",
            benchmark="longmemeval",
            selections=(self.selection,),
            system="full-history",
            extractor_model="Qwen/Qwen3.5-0.8B",
            executor="fixture",
            answerer="fixture-answerer",
            judge="fixture-judge",
            answer_reasoning_effort="none",
            judge_reasoning_effort=None,
            concurrency=1,
            answer_prompt="v2",
            answer_context_window=1_050_000,
            extraction_max_tokens=128,
            answer_max_tokens=128,
            judge_max_tokens=128,
            answer_input_cost=0,
            answer_cached_input_cost=0,
            answer_output_cost=0,
            judge_input_cost=0,
            judge_cached_input_cost=0,
            judge_output_cost=0,
        )
        self.coordinator = Coordinator(self.root / "runs")

    def test_no_network_end_to_end_and_strict_report(self):
        self.coordinator.prepare("run-1", self.preset)
        terminal = self.coordinator.run("run-1", self.preset, FixtureBackend(), allow_paid=False)
        loaded = self.coordinator.store.load("run-1")

        self.assertEqual(terminal.status.value, "complete")
        self.assertEqual(loaded.results[0]["status"], "success")
        self.assertEqual(loaded.results[0]["score"], 1.0)
        self.assertEqual(
            {artifact.kind for artifact in loaded.manifest.artifacts},
            {"experiment_spec", "dataset_snapshot", "memory", "call_state", "answer", "judge_part", "judge", "report"},
        )
        report = report_data(self.coordinator.store, "run-1")
        self.assertEqual(report["mean_score"], 1.0)
        self.assertEqual(report["accounting"]["known_spend_usd"], 0.0)
        self.assertEqual(report["accounting"]["unknown_or_reserved_exposure_usd"], 0.0)
        self.assertEqual(report["scores_by_question_type"][loaded.results[0]["question_type"]]["mean_score"], 1.0)

    def test_memory_extraction_runs_end_to_end_with_unique_call_ids(self):
        preset = replace(self.preset, system="memory")
        self.coordinator.prepare("run-1", preset)
        terminal = self.coordinator.run("run-1", preset, FixtureBackend(), allow_paid=False)
        loaded = self.coordinator.store.load("run-1")
        calls = [
            self.coordinator.store.read_artifact("run-1", artifact)
            for artifact in loaded.manifest.artifacts
            if artifact.kind == "call_state"
        ]
        extraction_ids = [call["call_id"] for call in calls if ":extract:" in call["call_id"] and call["state"] == "complete"]

        self.assertEqual(terminal.status.value, "complete")
        self.assertTrue(any(artifact.kind == "memory_progress" for artifact in loaded.manifest.artifacts))
        self.assertEqual(len(extraction_ids), len(set(extraction_ids)))

    def test_terminal_retry_gets_new_identity_and_lineage(self):
        self.coordinator.prepare("run-1", self.preset)
        self.coordinator.run("run-1", self.preset, FixtureBackend(), allow_paid=False)

        retry = self.coordinator.retry("run-1", "run-2", self.preset)

        self.assertEqual(retry.retry_of, "run-1")
        self.assertEqual(retry.status.value, "running")
        with self.assertRaisesRegex(RuntimeError, "terminal"):
            self.coordinator.run("run-1", self.preset, FixtureBackend(), allow_paid=False)

    def test_resume_uses_a_saved_response_without_replaying_the_call(self):
        fixture = FixtureBackend()

        class CrashAfterSaved:
            def complete(inner, **kwargs):
                if kwargs["stage"] != "answer":
                    return fixture.complete(**kwargs)
                call = {
                    "call_id": kwargs["call_id"],
                    "state": CallState.RESPONSE_SAVED.value,
                    "requested_model": kwargs["model"],
                    "resolved_model": "crash-fixture",
                    "reserved_usd": 0.0,
                    "cost_usd": 0.0,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                    "content": str(kwargs["item"]["answer"]),
                    "ok": False,
                }
                kwargs["observe"]({**call, "state": CallState.IN_FLIGHT.value})
                kwargs["observe"](call)
                raise KeyboardInterrupt("simulated process loss")

        class CountAnswers:
            answers = 0

            def complete(inner, **kwargs):
                if kwargs["stage"] == "answer":
                    inner.answers += 1
                return fixture.complete(**kwargs)

        self.coordinator.prepare("run-1", self.preset)
        with self.assertRaises(KeyboardInterrupt):
            self.coordinator.run("run-1", self.preset, CrashAfterSaved(), allow_paid=False)
        backend = CountAnswers()
        terminal = self.coordinator.run("run-1", self.preset, backend, allow_paid=False)

        self.assertEqual(terminal.status.value, "complete")
        self.assertEqual(backend.answers, 0)

    def test_unknown_outcome_blocks_without_an_automatic_replay(self):
        class UnknownBackend:
            calls = 0

            def complete(inner, **kwargs):
                inner.calls += 1
                kwargs["observe"]({
                    "call_id": kwargs["call_id"],
                    "state": CallState.IN_FLIGHT.value,
                    "requested_model": kwargs["model"],
                    "reserved_usd": 0.25,
                    "cost_usd": None,
                    "ok": False,
                })
                raise TimeoutError("outcome unknown")

        self.coordinator.prepare("run-1", self.preset)
        backend = UnknownBackend()
        terminal = self.coordinator.run("run-1", self.preset, backend, allow_paid=False)

        self.assertEqual(terminal.status.value, "blocked")
        self.assertEqual(backend.calls, 1)
        report = report_data(self.coordinator.store, "run-1")
        self.assertEqual(report["accounting"]["unknown_or_reserved_exposure_usd"], 0.25)
        with self.assertRaisesRegex(RuntimeError, "unresolved external-call outcomes"):
            self.coordinator.retry("run-1", "run-2", self.preset)

    def test_modal_import_records_executor_cost_in_the_artifact_graph(self):
        preset = replace(self.preset, executor="modal", system="memory")
        self.coordinator.prepare("run-1", preset)
        loaded = self.coordinator.store.load("run-1")
        history_id = loaded.results[0]["history_sha256"]
        item = LongMemEvalAdapter().load()[0]
        directory = self.root / "modal"
        (directory / "memories").mkdir(parents=True)
        resolved = resolve(preset)
        (directory / "configuration.json").write_text(json.dumps({
            "spec_sha256": resolved.sha256(),
            "payload": {"fingerprint": "payload", "gpu": "L4", "histories": [
                {"history_sha256": history_id, "history": [None] * len(item.sessions)}]},
        }))
        (directory / "cloud.json").write_text(json.dumps({
            "reserved_usd": 2.0,
            "accounted_usd": 1.25,
            "gpu_started_at": "2026-01-01T00:00:00+00:00",
            "finished_at": "2026-01-01T00:10:00+00:00",
        }))
        (directory / "memories" / f"{history_id}.json").write_text(json.dumps({
            "status": "complete",
            "history_sha256": history_id,
            "payload_sha256": "payload",
            "sessions_done": len(item.sessions),
            "lines": [],
            "warnings": [],
            "calls": [],
        }))

        manifest = self.coordinator.import_modal_memories("run-1", preset, directory)
        report = report_data(self.coordinator.store, "run-1")

        self.assertIn("executor_call_state", {artifact.kind for artifact in manifest.artifacts})
        self.assertEqual(report["accounting"]["known_spend_usd"], 1.25)

    def test_partial_modal_import_grades_only_complete_history(self):
        items = LongMemEvalAdapter().load()[:3]
        self.selection.write_text(json.dumps({"questions": [
            {"question_id": item.question_id, "question_type": item.question_type} for item in items]}))
        preset = replace(self.preset, executor="modal", system="memory")
        self.coordinator.prepare("partial", preset)
        loaded = self.coordinator.store.load("partial")
        ids = [row["history_sha256"] for row in loaded.results]
        self.assertEqual(len(set(ids)), 3)
        directory = self.root / "modal"
        (directory / "memories").mkdir(parents=True)
        (directory / "configuration.json").write_text(json.dumps({
            "spec_sha256": resolve(preset).sha256(), "payload": {
                "fingerprint": "payload", "gpu": "L4", "histories": [
                    {"history_sha256": key, "history": [None] * len(item.sessions)}
                    for key, item in zip(ids, items)]}}))
        (directory / "cloud.json").write_text(json.dumps({"reserved_usd": 2, "accounted_usd": 1}))
        (directory / "memories" / f"{ids[0]}.json").write_text(json.dumps({
            "history_sha256": ids[0], "payload_sha256": "payload", "status": "complete",
            "sessions_done": len(items[0].sessions), "lines": [], "calls": []}))
        (directory / "memories" / f"{ids[1]}.json").write_text(json.dumps({
            "history_sha256": ids[1], "payload_sha256": "payload", "status": "invalid_output",
            "sessions_done": 0, "lines": [], "calls": []}))
        self.coordinator.import_modal_memories("partial", preset, directory)
        fixture = FixtureBackend()
        stages = []
        class Backend:
            def complete(inner, **kwargs):
                stages.append(kwargs["stage"])
                self.assertNotEqual(kwargs["stage"], "extract")
                return fixture.complete(**kwargs)
        self.coordinator.run("partial", preset, Backend(), allow_paid=True)
        loaded = self.coordinator.store.load("partial")
        self.assertEqual([row["status"] for row in loaded.results], ["success", "blocked_memory", "blocked_memory"])
        self.assertEqual(stages.count("answer"), 1)
        report = report_data(self.coordinator.store, "partial")
        self.assertEqual(report["scored_questions"], 1)
        self.assertEqual(report["coverage"], 1 / 3)
        self.assertEqual(report["score_scope"], "scored_subset_only")


if __name__ == "__main__":
    unittest.main()
