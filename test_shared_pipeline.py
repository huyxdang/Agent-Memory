"""Offline integration tests. All API calls are replaced; artifacts live in temporary directories."""
import copy
import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import longmemeval_eval as e
import shared_pipeline as p


class SharedPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patches = [patch.object(e, "RUNS_DIR", self.root), patch.object(e, "RUN_INDEX_PATH", self.root / "index.jsonl"),
                        patch.object(e, "PAID_BUDGET", None), patch.object(e, "API_SLOTS", None)]
        for context in self.patches:
            context.start()
            self.addCleanup(context.stop)
        with patch("sys.argv", ["eval", "--system", "memory", "--benchmark", "locomo"]):
            self.args = e.parse_args()
        for name, value in dict(answer_model="fake-answer", extraction_model="fake-extractor", judge_model="fake-judge",
                                answer_input_cost=.2, answer_cached_input_cost=.02, answer_output_cost=1.2,
                                judge_input_cost=1.25, judge_cached_input_cost=.125, judge_output_cost=10,
                                answer_context_window=1050000, extraction_max_tokens=1000, answer_max_tokens=100,
                                judge_max_tokens=100, spending_limit=100, concurrency=3).items():
            setattr(self.args, name, value)
        self.items = []
        for qid, history in [("a1", "A"), ("a2", "A"), ("b1", "B")]:
            self.items.append(dict(question_id=qid, question_type="single-hop", question=f"Question {qid}?",
                answer="Paris", question_date="2026/01/03", judge="locomo",
                haystack_session_ids=[f"{history}1", f"{history}2"], haystack_dates=["2026/01/01", "2026/01/02"],
                haystack_sessions=[[{"role": "user", "content": f"History {history} session {i}: I live in Paris."}] for i in (1, 2)],
                answer_session_ids=[]))
        records, projected = e.preflight(self.items, self.args)
        self.report = dict(run=e.make_run_metadata("memory", None), metadata=e.base_metadata(self.args),
                           run_status="running", results=records, judge_validation=[], local_checks=[],
                           costs={"projected_max_usd": projected})
        self.by_id = {r["question_id"]: r for r in self.items}
        self.calls = []
        self.lock = threading.Lock()

    def fake_api(self, client, model, system, user, max_tokens, reasoning_effort=None, response_format=None, user_messages=None):
        payload = json.dumps(user_messages) if user_messages else user
        with self.lock:
            self.calls.append((model, payload))
        if model == "fake-extractor":
            content = json.dumps({"narrative": ["The user lives in Paris."], "atomic": []})
        elif model == "fake-judge":
            content = '{"label":"CORRECT"}'
        else:
            content = "Paris"
        return dict(ok=True, content=content, elapsed_seconds=.01, requested_model=model, resolved_model=model,
                    finish_reason="stop", usage=dict(input_tokens=100, output_tokens=20, total_tokens=120,
                    cached_input_tokens=0, reasoning_output_tokens=5), cost_usd=0, rate_limit_retries=0)

    def execute(self, fake=None):
        with patch.object(e, "api_call", side_effect=fake or self.fake_api):
            p.execute(e, None, self.args, self.report, self.by_id, [])

    def test_build_once_artifacts_accounting_and_resume(self):
        self.execute()
        rows = self.report["results"]
        self.assertEqual([r["status"] for r in rows], ["success"] * 3)
        self.assertEqual(sum(m == "fake-extractor" for m, _ in self.calls), 4)
        self.assertEqual(rows[0]["memory_build_id"], rows[1]["memory_build_id"])
        self.assertEqual(rows[0]["memory_sha256"], rows[1]["memory_sha256"])
        self.assertEqual(rows[0]["memory"]["lines"], rows[1]["memory"]["lines"])
        self.assertEqual(self.report["metrics"]["memory_writing"]["calls"], 4)
        self.assertEqual(self.report["metrics"]["answering"]["calls"], 3)
        self.assertEqual(self.report["metrics"]["judge_internal"]["total"]["calls"], 3)
        self.assertAlmostEqual(self.report["costs"]["memory_writing_usd"], 4 * (100*.2 + 20*1.2)/1e6)
        self.assertIn("seconds_to_all_graded", self.report["timing"])
        for m, payload in self.calls:
            if m == "fake-extractor":
                self.assertNotIn("Question a", payload)
        self.report = e.load_run(self.report["run"]["run_id"])
        self.execute(lambda *a, **kw: self.fail("Completed work must not be called again"))
        self.assertEqual(self.report["metrics"]["memory_writing"]["calls"], 4)

    def test_overlap_answers_before_other_build_finishes(self):
        answered = threading.Event()
        def fake(*args, **kwargs):
            if args[1] == "fake-extractor" and "History B session 1" in json.dumps(kwargs):
                self.assertTrue(answered.wait(3), "Builder B should overlap answers for A")
            if args[1] == "fake-answer":
                answered.set()
            return self.fake_api(*args, **kwargs)
        self.execute(fake)
        self.assertTrue(answered.is_set())
        self.assertTrue(all(r["status"] == "success" for r in self.report["results"]))

    def test_barrier_answers_wait_for_all_builds(self):
        self.args.memory_schedule = "barrier"
        def fake(*args, **kwargs):
            if args[1] == "fake-answer":
                self.assertEqual(sum(m == "fake-extractor" for m, _ in self.calls), 4)
            return self.fake_api(*args, **kwargs)
        self.execute(fake)
        self.assertTrue(all(r["status"] == "success" for r in self.report["results"]))

    def test_failed_build_blocks_only_its_consumers(self):
        def fake(*args, **kwargs):
            if args[1] == "fake-extractor" and "History A" in json.dumps(kwargs):
                raise RuntimeError("simulated extraction failure")
            return self.fake_api(*args, **kwargs)
        self.execute(fake)
        self.assertEqual([r["status"] for r in self.report["results"]], ["blocked_memory_build", "blocked_memory_build", "success"])

    def test_corrupt_artifact_never_answers(self):
        self.execute()
        r = self.report["results"][0]
        path = e.validated_run_dir(self.report["run"]["run_id"]) / "memories" / (r["memory_build_id"].split(":")[-1] + ".json")
        artifact = json.loads(path.read_text()); artifact["memory"]["lines"] = []
        e.atomic_json(path, artifact)
        for row in self.report["results"][:2]:
            row["status"] = "memory_complete"
        self.execute(lambda *a, **kw: self.fail("Corrupt memory must not dispatch"))
        self.assertEqual(self.report["results"][0]["status"], "blocked_memory_build")

    def test_key_includes_subject_and_extractor_not_question(self):
        a, b = self.report["results"][:2]
        self.assertEqual(p.memory_key(e, self.report, a), p.memory_key(e, self.report, b))
        b["memory"]["subject"] = "another person"
        self.assertNotEqual(p.memory_key(e, self.report, a), p.memory_key(e, self.report, b))

    def test_build_only_then_answer_only_reuses_identical_artifacts(self):
        self.args.memory_stage = "build"
        self.execute()
        self.assertEqual([r["status"] for r in self.report["results"]], ["memory_complete"] * 3)
        self.assertEqual(len(self.calls), 4)
        self.args.memory_stage = "all"
        def no_build(*args, **kwargs):
            self.assertNotEqual(args[1], "fake-extractor")
            return self.fake_api(*args, **kwargs)
        self.execute(no_build)
        self.assertTrue(all(r["status"] == "success" for r in self.report["results"]))

    def test_retry_failed_answer_preserves_cost_without_rebuilding(self):
        def fake(*args, **kwargs):
            result = self.fake_api(*args, **kwargs)
            if args[1] == "fake-answer" and "Question a1?" in args[3]:
                result.update(ok=False, error="simulated failure", error_type="test")
            return result
        self.execute(fake)
        self.assertEqual(self.report["results"][0]["status"], "answer_api_error")
        before = self.report["costs"]["total_api_spend_usd"]
        self.args.retry_failed = True
        def no_build(*args, **kwargs):
            self.assertNotEqual(args[1], "fake-extractor")
            return self.fake_api(*args, **kwargs)
        self.execute(no_build)
        self.assertTrue(all(r["status"] == "success" for r in self.report["results"]))
        self.assertEqual(self.report["metrics"]["answering"]["calls"], 4)
        self.assertEqual(self.report["metrics"]["answering"]["failed_calls"], 1)
        self.assertGreater(self.report["costs"]["total_api_spend_usd"], before)

    def test_global_api_limit(self):
        active = 0
        peak = 0
        lock = threading.Lock()
        def create(**kwargs):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            time.sleep(.02)
            with lock:
                active -= 1
            return SimpleNamespace(model="fake", usage=None, choices=[SimpleNamespace(
                finish_reason="stop", message=SimpleNamespace(content="ok"))])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with patch.object(e, "API_SLOTS", threading.BoundedSemaphore(2)), ThreadPoolExecutor(max_workers=6) as pool:
            calls = [pool.submit(e.api_call, client, "fake", "", "hello", 10) for _ in range(6)]
            self.assertTrue(all(call.result()["ok"] for call in calls))
        self.assertEqual(peak, 2)

    def test_invalid_judge_is_reported_not_success(self):
        def invalid(*args, **kwargs):
            result = self.fake_api(*args, **kwargs)
            if args[1] == "fake-judge":
                result["content"] = "not a valid grade"
            return result
        self.execute(invalid)
        self.assertTrue(all(r["status"] == "invalid_judge_response" for r in self.report["results"]))
        self.assertEqual(len(self.report["accounting_audit"]["failures"]), 3)
        self.assertNotIn("all_graded_at", self.report["timing"])

    def test_runner_with_fake_provider_writes_terminal_timing_and_reusable_run(self):
        args = self.args
        args.test = Path("unused-fixture.json")
        args.memory_stage = "build"
        args.answer_reasoning_effort = "none"
        args.extraction_reasoning_effort = "none"
        def create(**kw):
            result = self.fake_api(None, kw['model'], '', '', kw.get('max_tokens',100), user_messages=kw['messages'])
            usage = SimpleNamespace(prompt_tokens=100, completion_tokens=20, total_tokens=120,
                                    prompt_tokens_details=SimpleNamespace(cached_tokens=0),
                                    completion_tokens_details=SimpleNamespace(reasoning_tokens=5))
            return SimpleNamespace(model=kw['model'], usage=usage, choices=[SimpleNamespace(
                finish_reason='stop', message=SimpleNamespace(content=result['content']))])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with patch.object(e, 'load_fixture', return_value=self.items), patch.object(e, 'local_checks', return_value=[]), \
             patch.object(e, 'OpenAI', return_value=client), patch.dict('os.environ', {'OPENAI_API_KEY':'fake-not-a-key'}):
            self.assertEqual(e.run(args), 0)
            manifests = list(self.root.glob('*/manifest.json'))
            built = json.loads(manifests[0].read_text())
            self.assertEqual(built['status'], 'memory_ready')
            self.assertEqual(built['metrics']['memory_writing']['calls'], 4)
            self.assertEqual(built['metrics']['answering']['calls'], 0)
            args.memory_stage = 'answer'
            args.memory_from = built['run_id']
            self.assertEqual(e.run(args), 0)
        manifests = [json.loads(x.read_text()) for x in self.root.glob('*/manifest.json')]
        answered = next(m for m in manifests if m['status']=='complete')
        self.assertEqual(answered['metrics']['memory_writing']['calls'], 0)
        self.assertEqual(answered['metrics']['answering']['calls'], 3)
        self.assertEqual(answered['metrics']['judge_internal']['total']['calls'], 3)
        end = json.loads((self.root/answered['run_id']/'execution_timing.json').read_text())
        self.assertGreater(end['invocation_elapsed_seconds'], 0)
        self.assertGreater(answered['timing']['recorded_run_elapsed_seconds'], 0)


if __name__ == "__main__":
    unittest.main()
