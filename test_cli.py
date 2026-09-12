import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.cli import main


class CliTests(unittest.TestCase):
    def test_stopped_partial_modal_run_reaches_import_and_grading(self):
        coordinator = Mock()
        coordinator.store.load.return_value.manifest.status.terminal = False
        coordinator.run.return_value.status.value = "failed"
        coordinator.run.return_value.to_dict.return_value = {"status": "failed"}
        preset = Mock(executor="modal")
        with patch("adaption_memory.cli.Coordinator", return_value=coordinator), \
             patch("adaption_memory.cli.load_preset", return_value=preset), \
             patch("adaption_memory.cli.resolve"), \
             patch("adaption_memory.cli._backend", return_value=Mock()), \
             patch("adaption_memory.execution.modal.collect", return_value={"complete": False, "stopped": True}), \
             redirect_stdout(StringIO()):
            code = main(["resume", "--spec", "unused.json", "--run-id", "partial", "--allow-paid", "--budget-usd", "1"])
        self.assertEqual(code, 2)
        coordinator.import_modal_memories.assert_called_once()
        coordinator.run.assert_called_once()

    def test_running_modal_run_does_not_import_changing_memories(self):
        coordinator = Mock()
        coordinator.store.load.return_value.manifest.status.terminal = False
        with patch("adaption_memory.cli.Coordinator", return_value=coordinator), \
             patch("adaption_memory.cli.load_preset", return_value=Mock(executor="modal")), \
             patch("adaption_memory.cli.resolve"), \
             patch("adaption_memory.execution.modal.collect", return_value={"complete": False, "stopped": False}), \
             redirect_stdout(StringIO()):
            self.assertEqual(main(["resume", "--spec", "unused.json", "--run-id", "active"]), 2)
        coordinator.import_modal_memories.assert_not_called()
        coordinator.run.assert_not_called()

    def test_prepare_run_resume_report_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = LongMemEvalAdapter().load()[0]
            selection = root / "selection.json"
            selection.write_text(json.dumps({"questions": [{"question_id": item.question_id, "question_type": item.question_type}]}))
            spec = root / "fixture.json"
            spec.write_text(json.dumps({
                "schema_version": 1,
                "name": "fixture",
                "benchmark": "longmemeval",
                "selections": [str(selection)],
                "system": "full-history",
                "extractor_model": "Qwen/Qwen3.5-0.8B",
                "executor": "fixture",
                "answerer": "fixture-answerer",
                "judge": "fixture-judge",
                "answer_reasoning_effort": "none",
                "judge_reasoning_effort": None,
                "concurrency": 1,
                "answer_prompt": "v2",
                "answer_context_window": 1050000,
                "extraction_max_tokens": 128,
                "answer_max_tokens": 128,
                "judge_max_tokens": 128,
                "prices_usd_per_million_tokens": {
                    "answer_input": 0, "answer_cached_input": 0, "answer_output": 0,
                    "judge_input": 0, "judge_cached_input": 0, "judge_output": 0
                }
            }))
            runs = root / "runs"
            output = root / "report"
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["--runs", str(runs), "preflight", "--spec", str(spec)]), 0)
                self.assertEqual(main(["--runs", str(runs), "prepare", "--spec", str(spec), "--run-id", "one"]), 0)
                self.assertEqual(main(["--runs", str(runs), "run", "--spec", str(spec), "--run-id", "one"]), 0)
                self.assertEqual(main(["--runs", str(runs), "report", "--run-id", "one", "--output", str(output)]), 0)
                self.assertEqual(main(["--runs", str(runs), "resume", "--spec", str(spec), "--run-id", "one", "--retry-as", "two"]), 0)
            self.assertTrue((output / "report.md").is_file())
            self.assertEqual(json.loads((runs / "two" / "current.json").read_text())["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
