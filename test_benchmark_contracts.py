import ast
import unittest
from dataclasses import replace
from pathlib import Path

from adaption_memory.benchmarks.beam import BeamAdapter
from adaption_memory.benchmarks.locomo import LoCoMoAdapter
from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.benchmarks.registry import adapter
from adaption_memory.integrity import canonical_json, sha256_bytes
from adaption_memory.presets import load_preset, resolve, selected_items
from adaption_memory.run_store.records import question_set_sha256


class BenchmarkContractTests(unittest.TestCase):
    def test_locomo_normalization_is_unchanged(self):
        actual = [item.to_record() for item in LoCoMoAdapter().load()]
        self.assertEqual(
            sha256_bytes(canonical_json(actual)),
            "a262824df17b0ec29ec563418221de97fb3e897b394e3a9b4753e04106b5fe99",
        )

    def test_beam_normalization_is_unchanged(self):
        actual = [item.to_record() for item in BeamAdapter(scale="100K", chat_ids=(1,)).load()]
        self.assertEqual(
            sha256_bytes(canonical_json(actual)),
            "56dd37bcb100455c7228d9a7448dfdcbb89626056df66c09d8fcb6fa161748e3",
        )

    def test_longmemeval_normalization_is_unchanged(self):
        items = LongMemEvalAdapter().load()
        item = items[0]
        self.assertEqual(item.benchmark, "longmemeval")
        self.assertEqual(item.judge_id, "longmemeval")
        self.assertTrue(item.question_id)
        self.assertTrue(item.sessions)
        self.assertEqual(
            sha256_bytes(canonical_json([value.to_record() for value in items])),
            "6455c08c4487f4b20bc06a30cd6404b97fc3eb0cf9ad1c8a589bf62a4309d532",
        )

    def test_frozen_question_sets_and_experiment_fingerprints(self):
        """Freeze the configured experiment, not the code revision.

        `configuration_sha256` covers the benchmark, split, prompts, model and
        adapter revisions, sources, sampling and limits. It deliberately excludes
        `implementation_revision`, which hashes every package file and therefore
        changes on any edit. Full run identity is asserted separately below.
        """
        expected = {
            "beam-qwen-9b-final90.json": (90, "c40e1d484d7fcef85a84fbf672e68fe571ba31ee3ae4d544339434c109a686ea", "16dd4044f78d365ea73f96ef2d78efd45ad0c420aa59c6dd9ed807a29045bb82"),
            "locomo-qwen-08b-base-final50.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "e13d0e734a1d8c61a5eda435c772a15585853b42a742080a05d0a14a79e24e27"),
            "locomo-qwen-08b-finetuned-final50.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "7a8f0743c7813584ab7f1fb35df577f49b9293b01531abe1c779f367c6ff5abe"),
            "longmemeval-qwen-9b-final100.json": (100, "6d722d3fa6590e07f0aaffab288f9fde14b633b12eed1cbbe39f6adefb4e94cc", "87441ff5d08acaed527de4be49b768e0f7966aed012ac787e159531310f208f9"),
            "beam-gemma3-4b-final90.json": (90, "c40e1d484d7fcef85a84fbf672e68fe571ba31ee3ae4d544339434c109a686ea", "434807ccc95b13db2fe8b3f71fc2f70ea2cecf09254a74b9bb992ff2b064f4b3"),
            "locomo-gemma3-4b-final50.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "dd7dbd3a14408948cf48a0edd0dc06f64b1d1ae77ec04b12f653b68fcd3debf3"),
        }
        for name, (count, question_hash, configuration_hash) in expected.items():
            with self.subTest(name=name):
                preset = load_preset(Path("experiment_specs") / name)
                items = selected_items(preset)
                self.assertEqual(len(items), count)
                self.assertEqual(question_set_sha256(item.question_id for item in items), question_hash)
                self.assertEqual(resolve(preset).configuration_sha256(), configuration_hash)

    def test_configuration_hash_ignores_code_but_not_the_experiment(self):
        spec = resolve(load_preset(Path("experiment_specs") / "locomo-qwen-08b-base-final50.json"))
        frozen = spec.configuration_sha256()

        recompiled = replace(spec, implementation_revision="0" * 64)
        self.assertEqual(recompiled.configuration_sha256(), frozen)
        self.assertNotEqual(recompiled.sha256(), spec.sha256())

        changed_prompt = replace(
            spec, prompts=tuple(replace(p, sha256="0" * 64) if p.name == "extraction" else p for p in spec.prompts)
        )
        self.assertNotEqual(changed_prompt.configuration_sha256(), frozen)

        changed_model = replace(spec, extractor_model=replace(spec.extractor_model, revision="0" * 40))
        self.assertNotEqual(changed_model.configuration_sha256(), frozen)

        changed_source = replace(
            spec, sources=tuple(replace(s, sha256="0" * 64) for s in spec.sources[:1]) + spec.sources[1:]
        )
        self.assertNotEqual(changed_source.configuration_sha256(), frozen)

    def test_run_identity_still_binds_the_implementation(self):
        spec = resolve(load_preset(Path("experiment_specs") / "locomo-qwen-08b-base-final50.json"))
        self.assertNotEqual(replace(spec, implementation_revision="0" * 64).sha256(), spec.sha256())
        self.assertIn("implementation_revision", spec.to_dict())
        self.assertNotIn("implementation_revision", spec.configuration_dict())

    def test_registry_covers_all_benchmarks(self):
        self.assertEqual(
            {adapter(name).name for name in ("longmemeval", "locomo", "beam")},
            {"longmemeval", "locomo", "beam"},
        )

    def test_benchmark_modules_do_not_import_siblings_or_orchestrators(self):
        directory = Path("adaption_memory/benchmarks")
        forbidden = {
            "longmemeval_eval",
            "adaption_memory.execution.modal",
            "beam_final_inputs",
            "locomo_qwen_inputs",
            "longmemeval_qwen_inputs",
        }
        modules = {"beam", "locomo", "longmemeval"}
        for path in directory.glob("*.py"):
            if path.stem in {"__init__", "base", "registry"}:
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[-1] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[-1])
            self.assertFalse(imported & forbidden, f"{path} imports an orchestrator")
            self.assertFalse((imported & modules) - {path.stem}, f"{path} imports a sibling benchmark")


if __name__ == "__main__":
    unittest.main()
