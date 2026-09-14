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
        sources, sampling and limits. It deliberately excludes
        `implementation_revision`, which hashes every package file and therefore
        changes on any edit. Full run identity is asserted separately below.
        """
        expected = {
            "beam-100k-50-full-history.json": (50, "19d6663a715215045aa1face30a64954bfb8628a4506d3d5a33841d5c5033afb", "3c96ba760b69330131affcd1fc09d988431f8680afdfd713e8148a08813e1a87"),
            "beam-100k-50-luna.json": (50, "19d6663a715215045aa1face30a64954bfb8628a4506d3d5a33841d5c5033afb", "4a4cd7853670d8f9909fb94d74a91fbdadefa7eb78592ca9cd63e0fdcf032ebb"),
            "beam-100k-50-mem0.json": (50, "19d6663a715215045aa1face30a64954bfb8628a4506d3d5a33841d5c5033afb", "cc3cca1bb66236350baadf6159c4fd8ea73cea10695e622c2898636ba7827fda"),
            "beam-100k-50-qwen9b.json": (50, "19d6663a715215045aa1face30a64954bfb8628a4506d3d5a33841d5c5033afb", "47246a55580fdb8745ac0d27e796471687b2b2ab37906765262e427fccefbb75"),
            "beam-500k-40-full-history.json": (40, "f837a0769ce941f6e53e98689e5bd3f03cc92398da015d67965551177e79675a", "b60211df78b5a2cf104b4df95dfa727c81b6323a47ac7a6acebe5c2f1f74a645"),
            "beam-500k-40-luna.json": (40, "f837a0769ce941f6e53e98689e5bd3f03cc92398da015d67965551177e79675a", "ac0b34b278ce623afc4b0eed0962dcd3dec42d81b7e29d21df4a9495a693e9f5"),
            "beam-500k-40-mem0.json": (40, "f837a0769ce941f6e53e98689e5bd3f03cc92398da015d67965551177e79675a", "eb424b57612160f794fb18e714a6e720f8abe490ec6be3483dc610be46e3f79a"),
            "beam-500k-40-qwen9b.json": (40, "f837a0769ce941f6e53e98689e5bd3f03cc92398da015d67965551177e79675a", "8d7287cd9e8c220ba69fcb70d4262df7af43ec8eaf5c2ef4913d92fa4a7c1eab"),
            "locomo-50-full-history.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "c83d794eabcc5d521b8b3ef988d768508559a318a4ab1015b70a5a177f49b652"),
            "locomo-50-luna.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "0feb7bb3333886a6180b8da1a2f851abab2617773428ed61d309fd0c062d1b28"),
            "locomo-50-mem0.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "8eee1d220c43e305788f04233a34a5ad3600dd199a9fa0a35f356795fba8cad8"),
            "locomo-50-qwen9b.json": (50, "6d1104a6f8c5378e42fd0bca44caefe509726e624eb6ccee27003779e35da9a5", "f854454d394d301be72ddfaad8667f412e631cef5b83c13ec4d217b9c418310b"),
            "longmemeval-100-full-history.json": (100, "6d722d3fa6590e07f0aaffab288f9fde14b633b12eed1cbbe39f6adefb4e94cc", "bdafa9595161659b456a5b6a87450a09e2df598b5533342a36ca1bcafee02b2f"),
            "longmemeval-100-luna.json": (100, "6d722d3fa6590e07f0aaffab288f9fde14b633b12eed1cbbe39f6adefb4e94cc", "b527fcd71a444f5d91b8043dc83a7322168e07a069ebe1454fc12ba444c93b66"),
            "longmemeval-100-mem0.json": (100, "6d722d3fa6590e07f0aaffab288f9fde14b633b12eed1cbbe39f6adefb4e94cc", "11399ef5dc2f1581494dda75cedddb16ec1f21a1f9d6808e0eb62c495e7c05f0"),
            "longmemeval-100-qwen9b.json": (100, "6d722d3fa6590e07f0aaffab288f9fde14b633b12eed1cbbe39f6adefb4e94cc", "b36842247c131677d00c3fdfe188cbf42e090acc4e4747332bd535a2e80a88ef"),
        }
        for name, (count, question_hash, configuration_hash) in expected.items():
            with self.subTest(name=name):
                preset = load_preset(Path("experiment_specs") / name)
                items = selected_items(preset)
                self.assertEqual(len(items), count)
                self.assertEqual(question_set_sha256(item.question_id for item in items), question_hash)
                self.assertEqual(resolve(preset).configuration_sha256(), configuration_hash)

    def test_configuration_hash_ignores_code_but_not_the_experiment(self):
        spec = resolve(load_preset(Path("experiment_specs") / "beam-100k-50-qwen9b.json"))
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
        spec = resolve(load_preset(Path("experiment_specs") / "beam-100k-50-qwen9b.json"))
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
