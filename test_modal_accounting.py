import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from adaption_memory.execution import modal as runner
from adaption_memory.execution.files import save


class ModalAccountingTests(unittest.TestCase):
    def test_stopped_partial_collect_preserves_cost_and_historical_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            payload = {"histories": [{"history_sha256": "missing"}],
                "code_sha256": {"obsolete-source.py": "historical-source-hash"}}
            payload["fingerprint"] = runner.digest(payload)
            save(directory / "payload.json", payload)
            save(directory / "configuration.json", {"payload": payload})
            record = dict(sandbox_id="sb-test", run_id="historical", status="stopped",
                termination="confirmed", accounted_usd=.56)
            save(directory / "cloud.json", record)
            modal = Mock()
            modal.Sandbox.from_id.return_value.poll.return_value = 137
            with patch.object(runner, "cloud", return_value=(modal, Mock())), \
                 patch.object(runner, "volume_json", return_value=None):
                summary = runner.collect(directory)
            self.assertTrue(summary["stopped"])
            self.assertFalse(summary["complete"])
            self.assertEqual(summary["missing"], ["missing"])
            self.assertEqual(json.loads((directory / "cloud.json").read_text()), record)
            # Collection tolerates changed local code; launching must not.
            with self.assertRaises((ValueError, FileNotFoundError)):
                runner.validate_payload(directory, payload)
            corrupted = dict(payload, fingerprint="wrong")
            with self.assertRaises(ValueError):
                runner.validate_payload(directory, corrupted, verify_runtime=False)

    def test_stop_waits_and_records_cost_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            save(directory / "cloud.json", dict(sandbox_id="sb-test", status="running",
                gpu_started_at="2026-01-01T00:00:00+00:00", reserved_usd=2, rate_usd_s=.001))
            save(directory / "configuration.json", {"payload": {"histories": []}})
            modal = Mock()
            with patch.object(runner, "cloud", return_value=(modal, Mock())), \
                 patch.object(runner, "now", return_value="2026-01-01T00:01:00+00:00"):
                runner.stop(directory)
            modal.Sandbox.from_id.return_value.terminate.assert_called_once_with(wait=True)
            first = (directory / "cloud.json").read_bytes()
            record = json.loads(first)
            self.assertEqual(record["status"], "stopped")
            self.assertAlmostEqual(record["accounted_usd"], .56)
            with patch.object(runner, "now", side_effect=AssertionError("Already reconciled")):
                runner.record_stopped(directory, record)
            self.assertEqual((directory / "cloud.json").read_bytes(), first)

    def test_failed_termination_does_not_claim_stopped(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            save(directory / "cloud.json", {"sandbox_id": "sb-test", "status": "running"})
            modal = Mock()
            modal.Sandbox.from_id.return_value.terminate.side_effect = RuntimeError("unconfirmed")
            with patch.object(runner, "cloud", return_value=(modal, Mock())):
                with self.assertRaises(RuntimeError):
                    runner.stop(directory)
            self.assertEqual(json.loads((directory / "cloud.json").read_text())["status"], "running")
