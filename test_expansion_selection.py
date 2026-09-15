import json
import unittest
from pathlib import Path

from adaption_memory.benchmarks.beam import BeamAdapter
from adaption_memory.benchmarks.locomo import LoCoMoAdapter
from tools import convert_beam_500k, select_expansion


class LoCoMoSelectionTest(unittest.TestCase):
    def test_rule_reproduces_the_frozen_50(self):
        items = LoCoMoAdapter().load()
        frozen = json.loads(select_expansion.LOCOMO_50.read_text())
        reproduced = [item.question_id for item in select_expansion.select_locomo(items, frozen["per_type"])]
        self.assertEqual(reproduced, select_expansion.ids(select_expansion.LOCOMO_50))

    def test_500_is_proportional_and_contains_the_50(self):
        quotas = select_expansion.proportional_quotas(500)
        self.assertEqual(sum(quotas.values()), 500)
        self.assertEqual(quotas, {"single-hop": 273, "temporal": 104, "multi-hop": 92, "open-domain": 31})
        selection = select_expansion.build_locomo_500()
        ids = [entry["question_id"] for entry in selection["questions"]]
        self.assertEqual(len(ids), 500)
        self.assertEqual(len(set(ids)), 500)
        self.assertTrue(set(select_expansion.ids(select_expansion.LOCOMO_50)) <= set(ids))
        self.assertEqual(selection["per_type"], quotas)


class BeamSelectionTest(unittest.TestCase):
    def test_100k_takes_every_question_of_the_same_five_chats(self):
        selection = select_expansion.build_beam("100K", select_expansion.BEAM_100K_CHATS, select_expansion.BEAM_100K_50, "rule")
        ids = [entry["question_id"] for entry in selection["questions"]]
        self.assertEqual(len(ids), 100)
        self.assertEqual({entry["conversation"] for entry in selection["questions"]}, set(select_expansion.BEAM_100K_CHATS))
        self.assertTrue(set(select_expansion.ids(select_expansion.BEAM_100K_50)) <= set(ids))

    def test_500k_has_five_chats_and_contains_the_40(self):
        for chat in select_expansion.BEAM_500K_CHATS:
            if not (convert_beam_500k.TARGET / str(chat) / "chat.json").is_file():
                self.skipTest(f"500K chat {chat} is not converted")
        selection = select_expansion.build_beam("500K", select_expansion.BEAM_500K_CHATS, select_expansion.BEAM_500K_40, "rule")
        ids = [entry["question_id"] for entry in selection["questions"]]
        self.assertEqual(len(ids), 100)
        self.assertEqual({entry["conversation"] for entry in selection["questions"]}, set(select_expansion.BEAM_500K_CHATS))
        self.assertTrue(set(select_expansion.ids(select_expansion.BEAM_500K_40)) <= set(ids))


class ConversionTest(unittest.TestCase):
    def test_conversion_reproduces_the_chats_already_on_disk(self):
        if not convert_beam_500k.PARQUET.is_file():
            self.skipTest("500K parquet not downloaded")
        rows = convert_beam_500k.load_rows()
        self.assertTrue(set(convert_beam_500k.verify_existing(rows)) >= {"1", "13"})

    def test_null_fields_are_dropped_and_messages_are_paired(self):
        batches = [[
            {"content": "q", "id": 0, "role": "user", "time_anchor": "January-05-2024", "index": "1,3"},
            {"content": "a", "id": 1, "role": "assistant", "time_anchor": None, "index": None},
        ]]
        self.assertEqual(convert_beam_500k.convert_chat(batches), [{
            "batch_number": 1,
            "turns": [[
                {"content": "q", "id": 0, "role": "user", "time_anchor": "January-05-2024", "index": "1,3"},
                {"content": "a", "id": 1, "role": "assistant"},
            ]],
            "time_anchor": "January-05-2024",
        }])


if __name__ == "__main__":
    unittest.main()
