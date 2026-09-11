import asyncio
import json
from pathlib import Path
import tempfile
import unittest

from checkpoint_io import save
from qwen_vllm_worker import extract, server_command, output_allowance


class CloudExtractionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = dict(fingerprint='f', model='qwen', revision='pinned', concurrency=2,
            max_output_tokens='remaining_context', context_window=1000, histories=[dict(history_sha256=key,subject='user',
                history=[dict(timestamp='2026-01-01',messages=[dict(role='user',content='I like tea.')]) for _ in range(2)]) for key in ['a','b']])
        self.commits = 0
    async def commit(self):
        self.commits += 1
    async def infer(self, ids):
        await asyncio.sleep(.005)
        return dict(content='{"narrative":["The user likes tea."],"atomic":[]}',finish_reason='stop',output_tokens=10)

    async def test_concurrent_histories_order_and_exactly_once(self):
        active=0; peak=0
        async def infer(ids):
            nonlocal active,peak
            active+=1;peak=max(peak,active)
            result=await self.infer(ids)
            active-=1
            return result
        summary=await extract(self.payload,self.root,infer,lambda _: [1],self.commit)
        self.assertEqual(peak,2)
        self.assertEqual(summary['completed_updates'],4)
        for path in (self.root/'memories').glob('*.json'):
            state=json.loads(path.read_text())
            self.assertEqual([c['session'] for c in state['calls']],[1,2])
        async def forbidden(_):
            self.fail('Completed inference replayed')
        await extract(self.payload,self.root,forbidden,lambda _: [1],self.commit)
        self.assertTrue((self.root/'progress/a.json').exists())

    async def test_context_limit_never_calls_model(self):
        self.payload['context_window']=1
        async def forbidden(_):self.fail('Overflow inference')
        r=await extract(self.payload,self.root,forbidden,lambda _: [1],self.commit)
        self.assertEqual(r['completed_updates'],0)
        self.assertEqual(set(r['histories'].values()),{'context_limit'})

    async def test_invalid_json_is_retained_and_stops_history(self):
        async def invalid(_):return dict(content='{"narrature":[]}',finish_reason='stop',output_tokens=4)
        r=await extract(self.payload,self.root,invalid,lambda _: [1],self.commit)
        self.assertEqual(set(r['histories'].values()),{'invalid_output'})
        self.assertEqual(r['completed_updates'],0)

    async def test_response_saved_recovers_without_inference(self):
        self.payload['histories']=self.payload['histories'][:1]
        self.payload['histories'][0]['history']=self.payload['histories'][0]['history'][:1]
        await extract(self.payload,self.root,self.infer,lambda _: [1],self.commit)
        path=self.root/'memories/a.json';s=json.loads(path.read_text())
        s.update(status='running',sessions_done=0,lines=[])
        s['calls'][0]['status']='response_saved';save(path,s)
        async def forbidden(_):self.fail('Saved response regenerated')
        r=await extract(self.payload,self.root,forbidden,lambda _: [1],self.commit)
        self.assertEqual(r['completed_updates'],1)

    async def test_unknown_call_blocks_and_other_histories_continue(self):
        async def failed(_):raise TimeoutError()
        await extract(self.payload,self.root,failed,lambda _: [1],self.commit)
        async def forbidden(_):self.fail('Unknown call replayed')
        r=await extract(self.payload,self.root,forbidden,lambda _: [1],self.commit)
        self.assertEqual(set(r['histories'].values()),{'unknown_outcome'})

    def test_engine_configuration(self):
        command=server_command(self.payload)
        self.assertIn('--enable-prefix-caching',command)
        self.assertIn('--enable-chunked-prefill',command)
        self.assertEqual(command[command.index('--host')+1],'127.0.0.1')
        self.assertEqual(command[command.index('--max-num-seqs')+1],'2')

    def test_full_remaining_output_allowance(self):
        self.assertEqual(output_allowance({'context_window':65536},15000),50536)
        self.assertEqual(output_allowance({'context_window':65536},65535),1)

    def test_frozen_payload_rejects_changed_file_or_stale_fingerprint(self):
        from modal_pilot_core import digest
        from qwen_vllm import validate_payload
        payload=dict(model='qwen',histories=[])
        payload['fingerprint']=digest(payload)
        save(self.root/'payload.json',payload)
        validate_payload(self.root,payload)
        changed={**payload,'model':'different'}
        save(self.root/'payload.json',changed)
        with self.assertRaises(ValueError):validate_payload(self.root,payload)
        with self.assertRaises(ValueError):validate_payload(self.root,changed)

    def test_output_continuation_preserves_failed_attempt_and_prefix(self):
        from continue_qwen_output import reconcile_state
        old=dict(status='invalid_output',sessions_done=1,payload_sha256='old',
            calls=[dict(status='complete',session=1),dict(status='response_saved',session=2,finish_reason='length',content='partial')])
        new=reconcile_state(old,'new')
        self.assertEqual(len(new['calls']),1)
        self.assertEqual(new['abandoned_attempts'][0]['content'],'partial')
        self.assertEqual(len(old['calls']),2)
        self.assertEqual(new['payload_sha256'],'new')
        old['calls'][-1]['finish_reason']='stop'
        with self.assertRaises(ValueError): reconcile_state(old,'new')

    def test_resume_rejects_unknown_and_accepts_saved_response(self):
        from resume_qwen_vllm import validate_resume
        validate_resume([dict(status='running',calls=[dict(status='response_saved')])])
        with self.assertRaises(ValueError):
            validate_resume([dict(status='running',calls=[dict(status='in_flight')])])
        with self.assertRaises(ValueError):
            validate_resume([dict(status='invalid_output',calls=[])])

    async def test_timeout_reconciliation_retries_only_unfinished_update(self):
        from continue_qwen_output import reconcile_state
        old=dict(history_sha256='a',status='unknown_outcome',sessions_done=1,
            payload_sha256='old',lines=[],warnings=[],calls=[dict(status='complete',session=1),
            dict(status='unknown_outcome',session=2,error_type='APITimeoutError')])
        with self.assertRaises(ValueError):reconcile_state(old,'f')
        fixed=reconcile_state(old,'f',retry_timeouts=True)
        self.assertEqual(fixed['abandoned_attempts'],[old['calls'][-1]])
        self.assertEqual(len(old['calls']),2)
        self.payload['histories']=self.payload['histories'][:1]
        save(self.root/'memories/a.json',fixed)
        result=await extract(self.payload,self.root,self.infer,lambda _: [1],self.commit)
        self.assertEqual(result['new_completed_updates'],1)
        state=json.loads((self.root/'memories/a.json').read_text())
        self.assertEqual([c['session'] for c in state['calls']],[1,2])
        self.assertEqual(state['status'],'complete')
        old['calls'][-1]['response_id']='saved'
        with self.assertRaises(ValueError):reconcile_state(old,'f',retry_timeouts=True)
        old['calls'][-1].pop('response_id')
        old['calls'][-1]['error_type']='ValueError'
        with self.assertRaises(ValueError):reconcile_state(old,'f',retry_timeouts=True)


if __name__=='__main__':unittest.main()
