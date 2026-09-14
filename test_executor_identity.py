import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adaption_memory.execution import modal
from adaption_memory.presets import load_preset


class PresetGpuTest(unittest.TestCase):
    def test_preset_gpu_reaches_payload_and_explicit_argument_wins(self):
        preset = load_preset(Path("experiment_specs/longmemeval-qwen-9b-l40s-final100.json"))
        self.assertEqual(preset.gpu, "L40S")
        payload, _ = modal.build_payload(preset, smoke_histories=1, smoke_updates=1)
        self.assertEqual(payload["gpu"], "L40S")
        payload, _ = modal.build_payload(preset, gpu="L4", smoke_histories=1, smoke_updates=1)
        self.assertEqual(payload["gpu"], "L4")
        default = load_preset(Path("experiment_specs/beam-qwen-9b-final90.json"))
        self.assertIsNone(default.gpu)
        self.assertEqual(modal.build_payload(default, smoke_histories=1, smoke_updates=1)[0]["gpu"], "L40S")


class ExecutorIdentityTest(unittest.TestCase):
    def test_fingerprint_survives_a_code_change_and_prepare_records_it(self):
        from adaption_memory.config import PROJECT_ROOT
        from adaption_memory.integrity import sha256_file
        from adaption_memory.source_manifest import source_hashes
        preset = load_preset(Path("experiment_specs/longmemeval-qwen-9b-l40s-final100.json"))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            first = modal.prepare(directory, preset, smoke_histories=1, smoke_updates=1)
            edited = {**source_hashes(), "README.md": sha256_file(PROJECT_ROOT / "README.md")}
            with patch.object(modal, "source_hashes", return_value=edited):
                second = modal.prepare(directory, preset, smoke_histories=1, smoke_updates=1)
            self.assertEqual(first["payload"]["fingerprint"], second["payload"]["fingerprint"])
            self.assertNotEqual(first["payload"]["code_sha256"], second["payload"]["code_sha256"])
            self.assertEqual(json.loads((directory / "payload.json").read_text())["code_sha256"], second["payload"]["code_sha256"])
            with self.assertRaisesRegex(ValueError, "Prepared run differs"):
                modal.prepare(directory, preset, smoke_histories=1, smoke_updates=2)


if __name__ == "__main__":
    unittest.main()
