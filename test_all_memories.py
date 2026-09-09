"""Offline checks: .venv/bin/python -m unittest test_all_memories -v."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import longmemeval_eval as e
import mem0_system


class AllMemoryTests(unittest.TestCase):
    def test_complete_prompt_without_search(self):
        args = SimpleNamespace(tokenizer="o200k_base", answer_max_tokens=1024, answer_context_window=1050000)
        source = e.load_run("20260908T222244440761Z_mem0_388f915")
        record = next(r for r in source["results"] if r["status"] == "success")
        lines = json.loads(json.dumps(record["memory"]["lines"]))
        report = {"metadata": {"prompts": {
            "answer_system": mem0_system.ANSWER_SYSTEM_PROMPT.replace("retrieved", "stored"),
            "answer_user_format": mem0_system.ANSWER_PROMPT_FORMAT.replace("Retrieved", "All stored").replace("retrieved", "stored"),
        }}}
        with patch.object(mem0_system.Mem0Store, "search", side_effect=AssertionError("Search forbidden")):
            e.prepare_all_memories(args, report, record, {"question": "Test question?", "question_date": "unknown"})
        self.assertEqual(lines, record["memory"]["lines"])
        self.assertEqual(len(lines), record["memory"]["supplied_memory_count"])
        self.assertIsNone(record["memory"]["retrieved"])
        for line in lines:
            self.assertIn(line["text"], record["answer_prompt"])
        self.assertTrue(record["prompt_fit"]["fits"])
        self.assertTrue(e.context_text_from_prompt(record["answer_prompt"]))
        args.answer_context_window = 1024
        e.prepare_all_memories(args, report, record, {"question": "Test question?", "question_date": "unknown"})
        self.assertEqual(record["status"], "prompt_too_large")
        self.assertEqual(lines, record["memory"]["lines"])

    def test_budget_prevents_dispatch(self):
        budget = e.PaidBudget(SimpleNamespace(judge_model="judge", judge_input_cost=1.25, judge_output_cost=10, answer_input_cost=.2, answer_output_cost=1.2, spending_limit=0))
        with self.assertRaisesRegex(RuntimeError, "Spending limit"):
            budget.call(lambda **kw: self.fail("Must not dispatch"), {"model": "answer", "messages": [], "max_completion_tokens": 1024})

    def test_budget_keeps_unknown_failure_reservation(self):
        budget = e.PaidBudget(SimpleNamespace(judge_model="judge", answer_input_cost=.2, answer_output_cost=1.2, spending_limit=5))
        def failed(**kwargs):
            raise TimeoutError("unknown billing")
        with self.assertRaises(TimeoutError):
            budget.call(failed, {"model": "answer", "messages": [], "max_completion_tokens": 1024})
        self.assertGreater(budget.used, 0)

    def test_mem0_reasoning_call_has_explicit_cap(self):
        captured = []
        def create(**kwargs):
            captured.append(kwargs)
            return SimpleNamespace(model="answer", usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5), choices=[SimpleNamespace(finish_reason="stop")])
        completions = SimpleNamespace(create=create)
        store = mem0_system.Mem0Store.__new__(mem0_system.Mem0Store)
        store.calls = []
        store.memory = SimpleNamespace(
            llm=SimpleNamespace(client=SimpleNamespace(chat=SimpleNamespace(completions=completions))),
            embedding_model=SimpleNamespace(client=SimpleNamespace(embeddings=SimpleNamespace(create=create))))
        budget = SimpleNamespace(args=SimpleNamespace(extraction_max_tokens=128000), call=lambda fn, kw, **unused: fn(**kw))
        with patch.object(mem0_system, "PAID_BUDGET", budget):
            store._wrap_clients()
            completions.create(model="answer", messages=[])
        self.assertEqual(captured[0]["max_completion_tokens"], 128000)
        self.assertEqual(store.memory.llm.client.max_retries, 0)
        self.assertEqual(store.calls[0]["output_tokens"], 5)

    def test_budget_settles_cached_input_at_configured_rate(self):
        args = SimpleNamespace(judge_model="judge", answer_input_cost=.2, answer_cached_input_cost=.02, answer_output_cost=1.2, spending_limit=5)
        budget = e.PaidBudget(args)
        usage = SimpleNamespace(prompt_tokens=1000, completion_tokens=100, prompt_tokens_details=SimpleNamespace(cached_tokens=800))
        budget.call(lambda **kw: SimpleNamespace(usage=usage), {"model": "answer", "messages": [], "max_completion_tokens": 1024})
        self.assertAlmostEqual(budget.used, (200 * .2 + 800 * .02 + 100 * 1.2) / 1e6)


if __name__ == "__main__":
    unittest.main()
