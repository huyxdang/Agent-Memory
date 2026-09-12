import unittest

from adaption_memory import memory
from adaption_memory.evaluation import answering, judges
from adaption_memory.integrity import sha256_text
from third_party.mem0 import beam_prompts, locomo_prompts


class PromptContractTests(unittest.TestCase):
    def test_frozen_prompt_hashes(self):
        expected = {
            "extraction": "0a4e4f38ddbafa571a42398e3d985ab860d6cf1208b0af16d0ad7ab2e07b9632",
            "memory_answer_v1": "587620e0dbea09f1cc518df7b8703d73ec08db0f97b4905ab2ac3f0028c45dec",
            "memory_answer_v2": "2013052e2bc14a8c820a1f1287b49710285695edcaa9cb327e7fd0f6eb40e833",
            "full_answer_v1": "49e1ed721f1f402be08e1317dcf95edf3e8df10cbc867dba7f0517e6f15a7f8c",
            "full_answer_v2": "d39c68834917ead198895649d28deb691c0cf0513df2769378ad6dddc7af6104",
            "longmemeval_judge": "c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515",
            "locomo_judge": "d248e056d993725e28fba8d16ca7081f0b59deae272ef294f3c6b00d48eac02b",
            "locomo_judge_system": "36c007917faf1ab84516cdca577fb523711a9b993706fbae8ae37806e6f9adcc",
            "beam_judge": "bb210f16d9bdf4dbf0979033be850cf5aedfd8741b7c1689dd54730d0ac0441d",
            "beam_judge_system": "88af8076015217ee2f4bb2b114d17d284d6d546e73fbb71949935fa8c3065f24",
        }
        actual = {
            "extraction": sha256_text(memory.EXTRACTION_SYSTEM_TEMPLATE),
            "memory_answer_v1": sha256_text(memory.ANSWER_SYSTEM_PROMPT_V1),
            "memory_answer_v2": sha256_text(memory.ANSWER_SYSTEM_PROMPT_V2),
            "full_answer_v1": sha256_text(answering.ANSWER_SYSTEM_PROMPT_V1),
            "full_answer_v2": sha256_text(answering.ANSWER_SYSTEM_PROMPT_V2),
            "longmemeval_judge": sha256_text(judges.LONGMEMEVAL_JUDGE_PROMPT),
            "locomo_judge": sha256_text(locomo_prompts.JUDGE_PROMPT),
            "locomo_judge_system": sha256_text(locomo_prompts.JUDGE_SYSTEM_PROMPT),
            "beam_judge": sha256_text(beam_prompts.JUDGE_PROMPT),
            "beam_judge_system": sha256_text(beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT),
        }
        self.assertEqual(actual, expected)

    def test_memory_parser_accepts_only_complete_json(self):
        valid = '{"narrative":["User moved."],"atomic":[{"key":"city","value":"Paris"}]}'
        self.assertEqual(memory.parse_extraction(valid)["atomic"][0]["value"], "Paris")
        for invalid in (
            "",
            '{"narrative":[]}',
            '{"atomic":[]}',
            '{"narrative":[],"atomic":',
            '```json\n{"narrative":[],"atomic":[]}\n```',
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises((ValueError, TypeError)):
                    memory.parse_extraction(invalid)

    def test_judge_parsers_make_invalid_output_explicit(self):
        self.assertEqual(judges.parse_yes_no("<judge_thinking>ok</judge_thinking>\nyes"), "yes")
        self.assertEqual(judges.parse_yes_no("maybe"), "invalid")
        self.assertEqual(judges.parse_locomo_label('{"label":"CORRECT"}'), "yes")
        self.assertEqual(judges.parse_locomo_label("partial response"), "invalid")
        self.assertEqual(judges.parse_beam_score('{"score":0.49}'), 0.5)
        self.assertIsNone(judges.parse_beam_score("```json\n{}\n```"))

    def test_beam_creates_one_judge_request_per_rubric_nugget(self):
        item = {"judge": "beam", "question": "What changed?", "answer": "", "rubric": ["first", "second"]}

        requests = judges.judge_requests(item, "response")

        self.assertEqual(len(requests), 2)
        self.assertTrue(all(system == beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT for system, _ in requests))
        self.assertIn("first", requests[0][1])
        self.assertIn("second", requests[1][1])


if __name__ == "__main__":
    unittest.main()


class ExtractionSchemaContractTests(unittest.TestCase):
    """The generation grammar and the output validator must agree.

    Gemma emitted five atomic facts with empty values on LoCoMo history
    b9ca8173. The JSON schema permitted them, so structured output produced
    them; output_valid then rejected the whole response, the worker recorded
    invalid_output, and the history stopped at three updates. One such history
    makes the run incomplete, which blocks grading for every question.
    """

    def test_atomic_key_and_value_are_required_non_empty_by_the_schema(self):
        from adaption_memory import memory

        properties = memory.EXTRACTION_RESPONSE_FORMAT["json_schema"]["schema"]["properties"]
        atomic = properties["atomic"]["items"]["properties"]
        self.assertEqual(atomic["key"].get("minLength"), 1)
        self.assertEqual(atomic["value"].get("minLength"), 1)

    def test_validator_rejects_exactly_what_the_schema_now_forbids(self):
        import json

        from adaption_memory.inference.vllm import output_valid

        empty_value = json.dumps({"narrative": ["a"], "atomic": [{"key": "gym membership card", "value": ""}]})
        empty_key = json.dumps({"narrative": ["a"], "atomic": [{"key": "", "value": "x"}]})
        good = json.dumps({"narrative": ["a"], "atomic": [{"key": "k", "value": "v"}]})
        self.assertFalse(output_valid(empty_value))
        self.assertFalse(output_valid(empty_key))
        self.assertTrue(output_valid(good))
