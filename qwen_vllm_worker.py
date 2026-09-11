"""Cloud-owned histories, concurrent vLLM requests, and durable per-history checkpoints."""
import asyncio
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time

from checkpoint_io import save, exclusive
from modal_pilot_core import digest, output_valid, prompt_ids
import memory


def output_allowance(payload, input_tokens):
    return payload['context_window'] - input_tokens


async def stream_infer(client, payload, ids, report):
    started=time.monotonic()
    last_saved=None
    parts=[]
    stream=None
    diagnostic=dict(status='streaming',input_tokens=len(ids),usage=None,
        output_tokens=None,finish_reason=None,response_id=None,resolved_model=None,
        chunks_received=0,time_to_first_token_seconds=None)

    async def snapshot():
        diagnostic.update(content=''.join(parts),elapsed_seconds=time.monotonic()-started,
            saved_at_unix=time.time())
        await report(diagnostic)

    try:
        async with asyncio.timeout(payload.get('request_timeout_seconds',600)):
            extra={'structured_outputs':{'json':memory.EXTRACTION_RESPONSE_FORMAT['json_schema']['schema']}} if payload['structured_output'] else {}
            stream=await client.completions.create(model=payload['model'],prompt=ids,temperature=0,
                max_tokens=output_allowance(payload,len(ids)),seed=0,extra_body=extra,
                stream=True,stream_options={'include_usage':True})
            async for chunk in stream:
                diagnostic.update(response_id=chunk.id,resolved_model=chunk.model)
                diagnostic['chunks_received']+=1
                if chunk.usage is not None:
                    diagnostic['usage']=chunk.usage.model_dump()
                    diagnostic['output_tokens']=chunk.usage.completion_tokens
                for choice in chunk.choices:
                    if choice.index!=0:raise ValueError('Unexpected streamed choice')
                    parts.append(choice.text)
                    if choice.text and diagnostic['time_to_first_token_seconds'] is None:
                        diagnostic['time_to_first_token_seconds']=time.monotonic()-started
                    if choice.finish_reason is not None:
                        diagnostic['finish_reason']=choice.finish_reason
                if last_saved is None or time.monotonic()-last_saved>=10:
                    await snapshot()
                    last_saved=time.monotonic()
            if diagnostic['finish_reason'] is None or diagnostic['usage'] is None:
                raise ValueError('Stream ended without final finish reason and API usage')
            if diagnostic['usage']['prompt_tokens']!=len(ids):
                raise ValueError('Server input count mismatch; refusing truncation')
        diagnostic['status']='complete'
        await snapshot()
        return {key:diagnostic[key] for key in ('content','finish_reason','output_tokens',
            'response_id','usage','resolved_model')}
    except BaseException as error:
        diagnostic.update(status='failed',error_type=type(error).__name__)
        await snapshot()
        raise
    finally:
        if stream is not None:await stream.close()


async def extract(payload, root, infer, tokenize, commit):
    keys = [r['history_sha256'] for r in payload['histories']]
    if len(keys) != len(set(keys)) or not keys or payload['concurrency'] < 1:
        raise ValueError('Require unique histories and positive concurrency')
    semaphore = asyncio.Semaphore(payload['concurrency'])
    new_updates = 0
    async def persist(path, state):
        await asyncio.to_thread(save, path, state)
        if path.parent.name == 'memories':
            await asyncio.to_thread(save, root/'progress'/path.name,
                dict(sessions_done=state['sessions_done'], status=state['status'],
                     calls=len(state['calls']), last_call_status=state['calls'][-1]['status'] if state['calls'] else None))
        await commit()

    async def history(row):
        nonlocal new_updates
        key = row['history_sha256']
        path = root/'memories'/f'{key}.json'
        state = json.loads(path.read_text()) if path.exists() else dict(history_sha256=key,
            sessions_done=0, lines=[], calls=[], warnings=[], status='pending', payload_sha256=payload['fingerprint'])
        if state['payload_sha256'] != payload['fingerprint']:
            raise ValueError('Checkpoint configuration mismatch')
        if state['status'] in ('complete', 'invalid_output', 'context_limit', 'unknown_outcome'):
            return state
        if state['calls'] and state['calls'][-1]['status'] == 'in_flight':
            state['status'] = 'unknown_outcome'
            await persist(path, state)
            return state
        sessions = row['history']
        limit = min(len(sessions), payload.get('updates_per_history') or len(sessions))
        for index in range(state['sessions_done'], limit):
            session = sessions[index]
            parts = memory.extraction_parts(state['lines'], index+1, len(sessions), session['timestamp'], session['messages'])
            messages = [{'role':'system','content':memory.extraction_system_prompt(row['subject'])}] + [
                {'role':'user','content':part} for part in parts]
            ids = await asyncio.to_thread(tokenize, messages)
            allowance = output_allowance(payload, len(ids))
            if allowance <= 0:
                state.update(status='context_limit', failed_session=index+1, input_tokens=len(ids))
                await persist(path, state)
                return state
            if state['calls'] and state['calls'][-1]['status'] == 'response_saved':
                call = state['calls'][-1]
                if call['prompt_sha256'] != digest(messages) or call['session'] != index+1:
                    raise ValueError('Saved response input mismatch')
            else:
                if state['calls'] and state['calls'][-1]['status'] == 'queued':
                    call = state['calls'][-1]
                    if call['prompt_sha256'] != digest(messages) or call['session'] != index+1:
                        raise ValueError('Queued input mismatch')
                else:
                    call = dict(session=index+1, messages=messages, prompt_sha256=digest(messages),
                                input_tokens=len(ids), max_output_tokens=allowance, status='queued',
                                stream_key=digest(ids))
                    state['calls'].append(call)
                state['status'] = 'running'
                await persist(path, state)
                queued = time.monotonic()
                try:
                    async with semaphore:
                        call['queue_seconds'] = time.monotonic()-queued
                        call['status'] = 'in_flight'
                        await persist(path, state)
                        started = time.monotonic()
                        response = await infer(ids)
                        call.update(response, elapsed_seconds=time.monotonic()-started, status='response_saved')
                    await persist(path, state)
                except Exception as error:
                    call.update(status='unknown_outcome', error_type=type(error).__name__)
                    state['status'] = 'unknown_outcome'
                    await persist(path, state)
                    return state
            if call['finish_reason'] != 'stop' or not output_valid(call['content']):
                state['status'] = 'invalid_output'
                await persist(path, state)
                return state
            _, warnings = memory.apply_extraction(state['lines'], memory.parse_extraction(call['content']), index+1,
                session['timestamp'], memory.session_text(session['messages']))
            state['warnings'].extend(warnings)
            state['sessions_done'] = index+1
            new_updates += 1
            call['status'] = 'complete'
            state['status'] = 'complete' if index+1 == len(sessions) else 'running'
            if index+1 == limit and limit < len(sessions):
                state['status'] = 'smoke_complete'
            await persist(path, state)
        return state

    started = time.monotonic()
    states = await asyncio.gather(*(history(row) for row in payload['histories']))
    elapsed = time.monotonic()-started
    summary = dict(status='complete' if all(s['status'] in ('complete','smoke_complete') for s in states) else 'incomplete',
        extraction_wall_seconds=elapsed, new_completed_updates=new_updates,
        new_updates_per_second=new_updates/elapsed if elapsed else None, concurrency=payload['concurrency'],
        completed_updates=sum(s['sessions_done'] for s in states),
        histories={s['history_sha256']:s['status'] for s in states})
    await persist(root/'finished.json', summary)
    return summary


def server_command(payload):
    return ['vllm', 'serve', payload['model'], '--revision', payload['revision'],
            '--host', '127.0.0.1', '--port', '8000', '--dtype', 'bfloat16',
            '--max-model-len', str(payload['context_window']), '--max-num-seqs', str(payload['concurrency']),
            '--max-num-batched-tokens', '8192', '--gpu-memory-utilization', '0.85',
            '--enable-chunked-prefill', '--enable-prefix-caching', '--language-model-only',
            '--generation-config', 'vllm', '--seed', '0']


async def run(path):
    from openai import AsyncOpenAI
    from transformers import AutoTokenizer
    payload = json.loads(path.read_text())
    root = path.parent
    commit_lock = asyncio.Lock()
    async def commit():
        async with commit_lock:
            process = await asyncio.create_subprocess_exec('sync', '/state')
            if await process.wait() != 0:
                raise RuntimeError('Cloud checkpoint commit failed')
    tokenizer = AutoTokenizer.from_pretrained(payload['model'], revision=payload['revision'])
    client = AsyncOpenAI(base_url='http://127.0.0.1:8000/v1', api_key='local-only', max_retries=0,
        timeout=payload.get('request_timeout_seconds',600))
    started = time.monotonic()
    with (root/'server.log').open('a') as log:
        server = subprocess.Popen(server_command(payload), stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(300):
                if server.poll() is not None:
                    raise RuntimeError('vLLM exited during startup; see server.log')
                try:
                    await client.models.list(timeout=2)
                    break
                except Exception:
                    await asyncio.sleep(2)
            else:
                raise TimeoutError('vLLM startup exceeded ten minutes')
            save(root/'loaded.json', dict(startup_seconds=time.monotonic()-started,
                versions={p:importlib.metadata.version(p) for p in ('vllm','torch','transformers')},
                command=server_command(payload), gpu='L40S', thinking=False))
            await commit()
            async def infer(ids):
                async def report(diagnostic):
                    await asyncio.to_thread(save,root/'streams'/f'{digest(ids)}.json',diagnostic)
                    await commit()
                return await stream_infer(client,payload,ids,report)
            return await extract(payload, root, infer, lambda messages:prompt_ids(tokenizer,messages), commit)
        finally:
            await client.close()
            if server.poll() is None:
                server.terminate()
                try:
                    await asyncio.to_thread(server.wait, 20)
                except subprocess.TimeoutExpired:
                    server.kill()
                    await asyncio.to_thread(server.wait)


if __name__ == '__main__':
    path = Path(sys.argv[1])
    with exclusive(path.parent):
        try:
            asyncio.run(run(path))
        except BaseException as error:
            save(path.parent/'fatal.json', dict(error_type=type(error).__name__, message=str(error)[:500]))
            subprocess.run(['sync','/state'], check=True)
            raise
