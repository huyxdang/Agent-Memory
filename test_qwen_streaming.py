import asyncio
import copy
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from openai.types import Completion
from openai.types.completion_choice import CompletionChoice
from openai.types.completion_usage import CompletionUsage


def chunk(text='', finish=None, usage=None):
    return Completion.model_construct(id='test-response', created=0, model='qwen', object='text_completion',
        choices=[] if usage else [CompletionChoice.model_construct(index=0,text=text,finish_reason=finish,logprobs=None)],
        usage=CompletionUsage(**usage) if usage else None)


class Stream:
    def __init__(self, chunks, error=None):
        self.chunks=chunks
        self.error=error
        self.closed=False

    async def __aiter__(self):
        for item in self.chunks:yield item
        if self.error:raise self.error

    async def close(self):self.closed=True


class StreamingTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, stream, timeout=10):
        from qwen_vllm_worker import stream_infer
        self.client=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=stream)))
        self.snapshots=[]
        async def report(value):self.snapshots.append(copy.deepcopy(value))
        payload=dict(model='qwen',context_window=1000,structured_output=True,request_timeout_seconds=timeout)
        return await stream_infer(self.client,payload,[1,2],report)

    async def test_complete_stream_keeps_exact_text_and_api_usage(self):
        stream=Stream([chunk('{"narrative":'),chunk('[],"atomic":[]}', 'stop'),
            chunk(usage=dict(prompt_tokens=2,completion_tokens=12,total_tokens=14))])
        result=await self.invoke(stream)
        self.assertEqual(result['content'],'{"narrative":[],"atomic":[]}')
        self.assertEqual(result['output_tokens'],12)
        self.assertTrue(stream.closed)
        self.assertEqual(self.snapshots[0]['status'],'streaming')
        self.assertEqual(self.snapshots[-1]['status'],'complete')
        args=self.client.completions.create.call_args.kwargs
        self.assertEqual(args['max_tokens'],998)
        self.assertTrue(args['stream'])
        self.assertEqual(args['stream_options'],{'include_usage':True})

    async def test_disconnect_preserves_partial_text_but_fails(self):
        stream=Stream([chunk('{"narrative":[')],ConnectionError('interrupted'))
        with self.assertRaises(ConnectionError):await self.invoke(stream)
        self.assertTrue(stream.closed)
        last=self.snapshots[-1]
        self.assertEqual(last['status'],'failed')
        self.assertEqual(last['content'],'{"narrative":[')
        self.assertIsNone(last['usage'])

    async def test_missing_usage_and_mismatched_input_fail(self):
        for usage in (None,dict(prompt_tokens=3,completion_tokens=1,total_tokens=4)):
            chunks=[chunk('{}','stop')]
            if usage:chunks.append(chunk(usage=usage))
            with self.assertRaises(ValueError):await self.invoke(Stream(chunks))
            self.assertEqual(self.snapshots[-1]['status'],'failed')

    async def test_wall_deadline_preserves_partial_and_closes(self):
        class Slow(Stream):
            async def __aiter__(self):
                yield chunk('partial')
                await asyncio.sleep(1)
        stream=Slow([])
        with self.assertRaises(TimeoutError):await self.invoke(stream,timeout=.02)
        self.assertTrue(stream.closed)
        self.assertEqual(self.snapshots[-1]['content'],'partial')
        self.assertEqual(self.snapshots[-1]['status'],'failed')


if __name__=='__main__':unittest.main()
