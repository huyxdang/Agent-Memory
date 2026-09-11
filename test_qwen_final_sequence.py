import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from checkpoint_io import save
import run_qwen_final_sequence as sequence
from qwen_vllm import volume_json
from unittest.mock import Mock


class SequenceTests(unittest.TestCase):
    def test_checkpoint_download_retries_partial_bytes_not_inference(self):
        volume=Mock()
        volume.read_file.side_effect=[[b'\x00\x00\x00\x00{'],[b'{"status":"complete"}']]
        with patch('qwen_vllm.time.sleep'):
            self.assertEqual(volume_json(volume,'state.json'),{'status':'complete'})
        self.assertEqual(volume.read_file.call_count,2)

    def test_required_order(self):
        self.assertEqual([(b,k) for b,k,_ in sequence.STAGES],
            [('locomo','pilot'),('locomo','final'),('longmemeval','pilot'),('longmemeval','final')])

    def test_gate_accepts_low_score_but_rejects_incomplete_work(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            save(root/'configuration.json',dict(payload=dict(histories=[dict(history_sha256='a',history=[{}])])) )
            save(root/'summary.json',dict(complete=True,valid=1,expected=1,accuracy=0))
            save(root/'cloud.json',dict(termination='confirmed'))
            save(root/'memories/a.json',dict(status='complete',sessions_done=1))
            self.assertTrue(sequence.verify_stage(root)['complete'])
            save(root/'api_calls/a.json',dict(status='unknown_outcome'))
            with self.assertRaisesRegex(ValueError,'Unknown API'):sequence.verify_stage(root)

    def test_budget_counts_previous_attempts_and_outstanding_reservations(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            save(root/'work/qwen_beam_baseline/modal_attempts.json',[dict(reserved_usd=10,accounted_usd=3)])
            save(root/'work/old/cloud.json',dict(runner='qwen_vllm',reserved_usd=4,accounted_usd=2))
            save(root/'work/live/cloud.json',dict(runner='qwen_vllm',reserved_usd=5))
            with patch.object(sequence,'ROOT',root):
                self.assertEqual(sequence.available_modal(),13.5)


if __name__=='__main__':unittest.main()
