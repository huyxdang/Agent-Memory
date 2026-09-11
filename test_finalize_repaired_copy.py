import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import finalize_repaired_copy as finish
import longmemeval_eval as ev


class FinalizeRepairTests(unittest.TestCase):
    def test_duplicate_review_is_an_error(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            finish.unique_rows([{'example_id':'a'}, {'example_id':'a'}])

    def test_string_target_and_missing_fields_rejected(self):
        for target in ('{}', {'narrative':[]}, {'narrative':[], 'atomic':[{'key':'x','value':''}]}):
            with self.assertRaises(ValueError):
                finish.validate_target(target)
        finish.validate_target({'narrative':['A fact'], 'atomic':[]})

    def test_replay_uses_corrected_memory_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            manifest=root/'runs/r/manifest.json'; manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'metadata':{'prompts':{'extraction_message_formats':{
                'memory':'Memory {session_number} ({timestamp}):\n{lines}', 'empty_memory':'empty'}}}}))
            target=json.dumps({'narrative':['old'], 'atomic':[]})
            rows=[]
            for n in (1,2):
                rows.append({'example_id':str(n),'history_sha256':'h','session':n,'source':{'run_id':'r'},
                    'messages':[{'role':'system','content':'system'},
                        {'role':'user','content':f'New session {n} of 2, dated 2023/01/01 (Sun) 00:00. Turns (JSON):\n[]'},
                        {'role':'assistant','content':target}]})
            proposal={'1':{'original_target_sha256':ev.sha256_text(target),
                'replacement_target':{'narrative':['corrected'], 'atomic':[]}}}
            with patch.object(finish,'ROOT',root):
                output=list(finish.replay(rows,proposal))
                self.assertIn('corrected',output[1]['messages'][1]['content'])
                self.assertEqual(output[1]['messages'][-2:], rows[1]['messages'][-2:])
                self.assertEqual(rows[0]['messages'][-1]['content'],target)
                proposal['1']['original_target_sha256']='wrong'
                with self.assertRaisesRegex(ValueError,'hash mismatch'):
                    list(finish.replay(rows,proposal))

    def test_missing_queue_reviews_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'agents').mkdir()
            (root/'dependency_review_queue.jsonl').write_text('{"example_id":"a"}\n')
            with patch.object(finish,'PILOT',root), patch.object(finish,'AGENTS',root/'agents'):
                with self.assertRaisesRegex(ValueError,'1 missing'):
                    finish.collect()

    def test_cannot_seal_with_missing_or_wrong_context_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            manifest={'status':'awaiting_final_context_review','reviewed_histories':['h'],
                'history_sha256':{'h':'expected'},'artifacts':{}}
            (root/'manifest.json').write_text(json.dumps(manifest))
            attestations=root/'input.jsonl'; attestations.write_text('')
            with patch.object(finish,'OUTPUT',root), patch.object(finish,'verify'):
                with self.assertRaisesRegex(ValueError,'Missing'):
                    finish.seal(attestations)
                attestations.write_text(json.dumps({'history_sha256':'h','exported_history_sha256':'wrong',
                    'status':'checked','reviewer':'reviewer','rationale':'checked'})+'\n')
                with self.assertRaisesRegex(ValueError,'Invalid'):
                    finish.seal(attestations)
            self.assertEqual(json.loads((root/'manifest.json').read_text()),manifest)


if __name__=='__main__':
    unittest.main()
