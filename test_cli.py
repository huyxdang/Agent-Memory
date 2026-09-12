import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from adaption_memory.benchmarks.longmemeval import LongMemEvalAdapter
from adaption_memory.cli import main


class CliTests(unittest.TestCase):
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
