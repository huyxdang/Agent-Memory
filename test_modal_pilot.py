import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import modal_pilot_core as core
import modal_pilot


class Tokenizer:
    def apply_chat_template(self,messages,**kwargs):
        assert kwargs=={'tokenize':True,'add_generation_prompt':True,'enable_thinking':False,'return_dict':False}
        return list(range(sum(len(m['content']) for m in messages)))


def source(n):
    return {'example_id':str(n),'history_sha256':'h','session':n,'reference_answer':'SECRET',
            'messages':[{'role':'system','content':'sys'},{'role':'user','content':'x'*n},
                        {'role':'assistant','content':'TEACHER TARGET'}]}


def payload():
    examples,_=core.select_examples([source(1),source(2),source(3)],Tokenizer())
    return {'model':core.MODEL,'revision':'a'*40,'examples':examples,
            'context_window':core.CONTEXT,'max_output_tokens':core.MAX_OUTPUT}


class PilotTests(unittest.TestCase):
    def test_tokenizer_mapping_is_not_a_token_sequence(self):
        tokenizer=MagicMock()
        tokenizer.apply_chat_template.return_value={'input_ids':[1,2], 'attention_mask':[1,1]}
        with self.assertRaisesRegex(ValueError,'flat list'):
            core.prompt_ids(tokenizer,[])

    def test_selection_exact_lengths_and_no_labels(self):
        selected,count=core.select_examples([source(3),source(1),source(2)],Tokenizer())
        self.assertEqual(count,3)
        self.assertEqual([r['example_id'] for r in selected],['2','3'])
        self.assertNotIn('SECRET',json.dumps(selected))
        self.assertNotIn('TEACHER TARGET',json.dumps(selected))

    def test_duplicate_input_rejected(self):
        with self.assertRaises(ValueError): core.select_examples([source(1),source(1)],Tokenizer())

    def test_fit_and_prompt_tamper(self):
        p=payload();core.validate_payload(p)
        p['context_window']=10
        with self.assertRaisesRegex(ValueError,'no truncation'):core.validate_payload(p)
        p=payload();p['examples'][0]['messages'][1]['content']='tamper'
        with self.assertRaisesRegex(ValueError,'integrity'):core.validate_payload(p)

    def test_spend_limits(self):
        self.assertLess(core.budget_plan(2)['estimated_envelope_usd'],2)
        for amount in [0,1,2.01,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):core.budget_plan(amount)

    def test_invalid_outputs_and_accounting(self):
        self.assertTrue(core.output_valid('{"narrative":[],"atomic":[]}'))
        for text in ['[]','{}','not json','{"narrative":[],"atomic":[{"key":"x","value":0}]}']:
            self.assertFalse(core.output_valid(text))
        report=core.account_results([{'example_id':'a'},{'example_id':'b'}],[{'example_id':'a','status':'error'},{'example_id':'a','status':'ok'}])
        self.assertEqual(report,{'missing':['b'],'unexpected':[],'duplicates':['a'],'failed':['a']})

    def test_cloud_failure_terminates_and_records_missing_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);(folder/'payload.json').write_text(json.dumps(payload()))
            sb=MagicMock();sb.object_id='sb-test';sb.filesystem.copy_from_local.side_effect=RuntimeError('upload failed')
            with patch('modal.Client.from_env'),patch('modal.App.lookup'),patch('modal.Sandbox.create',return_value=sb),patch('modal.Image.debian_slim'):
                with self.assertRaisesRegex(RuntimeError,'upload failed'):modal_pilot.execute(folder,2)
            sb.terminate.assert_called_once()
            record=json.loads((folder/'run.json').read_text())
            self.assertEqual(record['status'],'failed')
            self.assertEqual(len(record['accounting']['missing']),2)
            self.assertIsNone(record['actual_invoice_cost_usd'])
            with self.assertRaisesRegex(ValueError,'already attempted'):modal_pilot.execute(folder,2)
