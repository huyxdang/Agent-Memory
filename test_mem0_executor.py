import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.evaluation.answering import MEM0_ANSWER_PROMPT_FORMAT, MEM0_ANSWER_SYSTEM_PROMPT, build_mem0_answer_prompt
from adaption_memory.evaluation.pipeline import Coordinator
from adaption_memory.execution import mem0
from adaption_memory.execution.local import FixtureBackend
from adaption_memory.inference.openai import BudgetLedger
from adaption_memory.integrity import sha256_text
from adaption_memory.presets import ExperimentPreset, load_preset, resolve
from adaption_memory.run_store.reporting import report_data


def fake_response(prompt_tokens, cached, completion, reasoning, finish="stop"):
    return SimpleNamespace(
        model="gpt-5.6-luna-2026",
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens, completion_tokens=completion, total_tokens=prompt_tokens + completion,
            prompt_tokens_details=SimpleNamespace(cached_tokens=cached),
            completion_tokens_details=SimpleNamespace(reasoning_tokens=reasoning),
        ),
        choices=[SimpleNamespace(finish_reason=finish)],
    )


class FakeStore:
    """Stands in for Mem0: one metered LLM call and one embedding per add, memories tagged with the session date."""

    created = []

    def __init__(self, workdir, user_id, llm_model, meter):
        self.workdir, self.user_id, self.meter = workdir, user_id, meter
        self.memories = []
        FakeStore.created.append(self)

    def add_session(self, messages, timestamp):
        adds = 0
        for index in range(0, len(messages), mem0.CHUNK_MESSAGES):
            self.meter.llm(lambda **kwargs: fake_response(8_000, 7_000, 300, 100), {"model": "gpt-5.6-luna", "messages": messages[index:index + 4]})
            self.meter.embedding(lambda **kwargs: SimpleNamespace(usage=SimpleNamespace(prompt_tokens=50)), {"input": "x"})
            self.memories.append({"memory": f"fact {len(self.memories)} from {timestamp}", "session_date": timestamp,
                                  "created_at": f"2026-01-01T00:00:{len(self.memories):02d}+00:00", "id": str(len(self.memories))})
            adds += 1
        return {"adds": adds, "ADD": adds}

    def all_memories(self):
        return list(reversed(self.memories))  # Mem0 returns newest first; lines must come back oldest first

    def close(self):
        pass


class Mem0ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        items = LongMemEvalAdapter().load()[:2]
        self.items = items
        self.selection = self.root / "selection.json"
        self.selection.write_text(json.dumps({"questions": [
            {"question_id": item.question_id, "question_type": item.question_type} for item in items]}))
        self.preset = ExperimentPreset(
            name="mem0-offline", benchmark="longmemeval", selections=(self.selection,), system="mem0",
            extractor_model="gpt-5.6-luna", executor="mem0", answerer="fixture-answerer", judge="fixture-judge",
            answer_reasoning_effort="none", judge_reasoning_effort=None, concurrency=2, answer_prompt="v2",
            answer_context_window=1_050_000, extraction_max_tokens=16_384, answer_max_tokens=128, judge_max_tokens=128,
            answer_input_cost=0.2, answer_cached_input_cost=0.02, answer_output_cost=1.2,
            judge_input_cost=1.25, judge_cached_input_cost=0.125, judge_output_cost=10.0,
        )
        FakeStore.created = []

    def test_answer_prompt_is_the_retired_runner_no_retrieval_prompt(self):
        self.assertEqual(sha256_text(MEM0_ANSWER_SYSTEM_PROMPT), "45140fcac319071cd1932e338952cc7721835a999dfd91afc2581033971c20c1")
        self.assertEqual(sha256_text(MEM0_ANSWER_PROMPT_FORMAT), "777235ff7a57211ac6889f350980664c3ea92d48d5d5b7b02bc50b20b1f47a1c")
        prompt = build_mem0_answer_prompt(
            [{"kind": "mem0", "session": 1, "date": "2023/05/20 (Sat) 02:21", "text": "likes tea"}], 7, "2023/05/30 (Tue) 23:40", "Tea or coffee?")
        self.assertIn("All stored memories (1 stored from 7 earlier sessions, oldest first; date | memory):\n2023/05/20 (Sat) 02:21 | likes tea", prompt)

    def test_spec_resolves_without_a_vllm_model_and_pins_the_mem0_prompt(self):
        spec = resolve(self.preset)
        self.assertIsNone(spec.extractor_model)
        self.assertIn("mem0_answer", {prompt.name for prompt in spec.prompts})
        with self.assertRaises(ValueError):
            resolve(replace(self.preset, executor="local"))
        with self.assertRaises(ValueError):
            resolve(replace(self.preset, system="memory", extractor_model="Qwen/Qwen3.5-0.8B"))

    def test_shared_store_per_history_with_metered_budget_and_ordered_lines(self):
        directory = self.root / "mem0"
        mem0.prepare(directory, self.preset)
        ledger = BudgetLedger(50.0)
        record = mem0.build(directory, self.preset, ledger, store_factory=FakeStore)
        payload = json.loads((directory / "payload.json").read_text())
        self.assertEqual(len(FakeStore.created), len(payload["histories"]), "one store per unique history")
        self.assertEqual(record["complete_histories"], len(payload["histories"]))
        state = json.loads(next((directory / "memories").glob("*.json")).read_text())
        history = next(row for row in payload["histories"] if row["history_sha256"] == state["history_sha256"])
        self.assertEqual(state["status"], "complete")
        self.assertEqual(state["sessions_done"], len(history["history"]))
        self.assertTrue(all(call["status"] == "complete" and call["cost_usd"] > 0 for call in state["calls"]))
        adds = sum(call["events"]["adds"] for call in state["calls"])
        expected_cost = adds * ((1_000 * 0.2 + 7_000 * 0.02 + 300 * 1.2) / 1e6 + 50 * 0.02 / 1e6)
        self.assertAlmostEqual(sum(call["cost_usd"] for call in state["calls"]), expected_cost, places=9)
        dates = [mem0.parse_timestamp(line["date"]) for line in state["lines"]]
        self.assertEqual(dates, sorted(dates), "lines are oldest first even though Mem0 returned newest first")
        self.assertEqual(state["lines"][0]["session"], 1)
        self.assertEqual({line["kind"] for line in state["lines"]}, {"mem0"})
        self.assertAlmostEqual(record["known_spend_usd"], ledger.known_spend_usd)
        self.assertEqual(ledger.unknown_or_reserved_exposure_usd, 0.0)
        again = mem0.build(directory, self.preset, BudgetLedger(50.0), store_factory=FakeStore)
        self.assertEqual(len(FakeStore.created), len(payload["histories"]), "complete histories are not rebuilt")
        self.assertEqual(again["complete_histories"], len(payload["histories"]))
        all_calls = [c for p in (directory / "memories").glob("*.json") for c in json.loads(p.read_text())["calls"]]
        self.assertAlmostEqual(again["accounted_usd"], sum(c["cost_usd"] for c in all_calls), places=8,
                               msg="a resumed build with a fresh ledger still accounts for earlier spend")
        self.assertGreater(again["accounted_usd"], 0.0)

    def test_interrupted_session_is_unknown_outcome_and_never_re_added(self):
        directory = self.root / "mem0"
        mem0.prepare(directory, self.preset)
        payload = json.loads((directory / "payload.json").read_text())
        key = payload["histories"][0]["history_sha256"]
        (directory / "memories").mkdir()
        (directory / "memories" / f"{key}.json").write_text(json.dumps({
            "history_sha256": key, "payload_sha256": payload["fingerprint"], "status": "running", "sessions_done": 2,
            "lines": [], "warnings": [], "calls": [{"session": 3, "status": "in_flight", "reserved_usd": 0.0, "cost_usd": 0.0}]}))
        record = mem0.build(directory, self.preset, BudgetLedger(5.0), store_factory=FakeStore)
        state = json.loads((directory / "memories" / f"{key}.json").read_text())
        self.assertEqual(state["status"], "unknown_outcome")
        self.assertEqual(state["calls"][-1]["status"], "unknown_outcome")
        self.assertEqual(record["histories"][key], "unknown_outcome")
        self.assertEqual(len([s for s in FakeStore.created if s.user_id == f"h_{key[:16]}"]), 0)

    def test_budget_refusal_retains_no_reservation_and_marks_the_history(self):
        directory = self.root / "mem0"
        mem0.prepare(directory, self.preset)
        ledger = BudgetLedger(0.001)
        record = mem0.build(directory, self.preset, ledger, store_factory=FakeStore)
        self.assertEqual(record["complete_histories"], 0)
        self.assertTrue(all(status == "unknown_outcome" for status in record["histories"].values()))
        self.assertEqual(ledger.known_spend_usd, 0.0)

    def test_imported_mem0_memories_are_answered_with_the_mem0_prompt_and_no_extraction(self):
        coordinator = Coordinator(self.root / "runs")
        coordinator.prepare("mem0-run", self.preset)
        directory = self.root / "runs" / "mem0-run" / "mem0"
        mem0.prepare(directory, self.preset)
        mem0.build(directory, self.preset, BudgetLedger(50.0), store_factory=FakeStore)
        coordinator.import_memories("mem0-run", self.preset, directory, mem0.executor_record(directory))
        stages = []
        fixture = FixtureBackend()

        class Backend:
            def complete(inner, **kwargs):
                stages.append(kwargs["stage"])
                if kwargs["stage"] == "answer":
                    self.assertEqual(kwargs["system"], MEM0_ANSWER_SYSTEM_PROMPT)
                    self.assertIn("All stored memories (", kwargs["user_messages"][0]["content"])
                return fixture.complete(**kwargs)

        manifest = coordinator.run("mem0-run", self.preset, Backend(), allow_paid=True)
        self.assertEqual(manifest.status.value, "complete")
        self.assertNotIn("extract", stages)
        self.assertEqual(stages.count("answer"), len(self.items))
        report = report_data(coordinator.store, "mem0-run")
        self.assertGreater(report["accounting"]["known_spend_usd"], 0.0)

    def test_beam_mem0_preset_resolves(self):
        preset = load_preset(Path("experiment_specs/beam-mem0-final90.json"))
        spec = resolve(preset)
        self.assertEqual((preset.system, preset.executor, preset.extractor_model, preset.concurrency), ("mem0", "mem0", "gpt-5.6-luna", 7))
        self.assertIsNone(spec.extractor_model)


if __name__ == "__main__":
    unittest.main()
