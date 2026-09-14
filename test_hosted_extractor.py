import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.cli import _backend
from adaption_memory.evaluation.pipeline import Coordinator
from adaption_memory.execution.local import FixtureBackend
from adaption_memory.presets import ExperimentPreset, hosted_extractor, load_preset, resolve


class HostedExtractorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        items = LongMemEvalAdapter().load()[:2]
        self.selection = self.root / "selection.json"
        self.selection.write_text(json.dumps({"questions": [
            {"question_id": item.question_id, "question_type": item.question_type} for item in items]}))
        self.preset = ExperimentPreset(
            name="hosted", benchmark="longmemeval", selections=(self.selection,), system="memory",
            extractor_model="gpt-5.6-luna", executor="fixture", answerer="fixture-answerer", judge="fixture-judge",
            answer_reasoning_effort="none", judge_reasoning_effort=None, concurrency=2, answer_prompt="v2",
            answer_context_window=1_050_000, extraction_max_tokens=16_384, answer_max_tokens=128, judge_max_tokens=128,
            answer_input_cost=0.2, answer_cached_input_cost=0.02, answer_output_cost=1.2,
            judge_input_cost=1.25, judge_cached_input_cost=0.125, judge_output_cost=10.0,
            extractor_reasoning_effort="low", extractor_input_cost=0.2, extractor_cached_input_cost=0.02, extractor_output_cost=1.2,
        )

    def test_hosted_model_resolves_without_a_vllm_spec_and_carries_its_settings(self):
        self.assertTrue(hosted_extractor(self.preset))
        spec = resolve(self.preset)
        self.assertIsNone(spec.extractor_model)
        self.assertEqual(spec.extractor_model_name, "gpt-5.6-luna")
        parameters = dict(spec.parameters)
        self.assertEqual(parameters["extractor_reasoning_effort"], "low")
        self.assertEqual(parameters["extractor_output_cost"], 1.2)
        self.assertEqual(spec.configuration_dict()["extractor_model_name"], "gpt-5.6-luna")
        with self.assertRaisesRegex(ValueError, "extractor prices"):
            resolve(replace(self.preset, extractor_output_cost=None))
        with self.assertRaisesRegex(ValueError, "local executor"):
            resolve(replace(self.preset, executor="modal"))
        with self.assertRaisesRegex(ValueError, "no extractor model"):
            resolve(replace(self.preset, system="full-history"))
        served = replace(self.preset, extractor_model="Qwen/Qwen3.5-9B", executor="modal", gpu="L40S")
        self.assertFalse(hosted_extractor(served))
        self.assertEqual(resolve(served).extractor_model.name, "Qwen/Qwen3.5-9B")

    def test_extraction_is_dispatched_to_the_hosted_model_with_its_reasoning_effort(self):
        coordinator = Coordinator(self.root / "runs")
        coordinator.prepare("hosted", self.preset)
        fixture = FixtureBackend()
        seen = []

        class Backend:
            def complete(inner, **kwargs):
                if kwargs["stage"] == "extract":
                    seen.append((kwargs["model"], kwargs["reasoning_effort"], kwargs["response_format"] is not None))
                return fixture.complete(**kwargs)

        manifest = coordinator.run("hosted", self.preset, Backend(), allow_paid=True)
        self.assertEqual(manifest.status.value, "complete")
        self.assertTrue(seen)
        self.assertEqual(set(seen), {("gpt-5.6-luna", "low", True)})

    def test_cli_backend_prices_the_hosted_extractor_on_the_shared_ledger(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            os.environ.pop("EXTRACTOR_BASE_URL", None)
            routed = _backend(replace(self.preset, executor="local"), 5.0)
        self.assertEqual(routed.extractor.extractor_price.output_per_million, 1.2)
        self.assertIs(routed.extractor.transport, routed.evaluator.transport)

    def test_every_published_spec_names_one_cell_of_the_table(self):
        names = sorted(path.name for path in Path("experiment_specs").glob("*.json"))
        splits = ("longmemeval-100", "locomo-50", "beam-100k-50", "beam-500k-40")
        systems = ("luna", "mem0", "full-history", "qwen9b")
        self.assertEqual(names, sorted(f"{split}-{system}.json" for split in splits for system in systems))
        expected = {
            "luna": ("memory", "local", "gpt-5.6-luna"),
            "mem0": ("mem0", "mem0", "gpt-5.6-luna"),
            "full-history": ("full-history", "local", None),
            "qwen9b": ("memory", "modal", "Qwen/Qwen3.5-9B"),
        }
        for name in names:
            preset = load_preset(Path("experiment_specs") / name)
            system = next(key for key in expected if name.endswith(f"-{key}.json"))
            self.assertEqual((preset.system, preset.executor, preset.extractor_model), expected[system], name)


if __name__ == "__main__":
    unittest.main()
