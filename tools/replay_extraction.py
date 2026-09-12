"""Replay one saved extraction request in its original Modal image, without benchmark grading."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


def save(path, value):
    from adaption_memory.execution.files import save as atomic_save
    atomic_save(path, value)


def prepare(source, history, session, directory):
    from adaption_memory.inference.vllm import digest
    config = json.loads((source / "configuration.json").read_text())
    state = json.loads((source / "memories" / f"{history}.json").read_text())
    call = next(call for call in state["calls"] if call["session"] == session)
    if call["prompt_sha256"] != digest(call["messages"]):
        raise ValueError("Saved prompt digest mismatch")
    if call["status"] != "invalid_output":
        raise ValueError("This diagnostic requires a saved invalid-output call")
    ledger = json.loads((source / "cloud.json").read_text())
    fixture = dict(source=str(source.resolve()), source_image_id=ledger["image_id"],
        payload=config["payload"], call=call,
        note="Replay is isolated from benchmark results. Original concurrency setting retained; original competing traffic is not recreated.")
    if (directory / "fixture.json").exists():
        raise ValueError("Use a new diagnostic directory")
    save(directory / "fixture.json", fixture)


async def worker(path):
    from openai import AsyncOpenAI
    from transformers import AutoTokenizer
    from adaption_memory import memory
    from adaption_memory.execution.vllm_worker import stream_infer
    from adaption_memory.inference.vllm import output_valid, prompt_ids, server_command
    fixture = json.loads(path.read_text())
    payload, call = fixture["payload"], fixture["call"]
    root = path.parent
    tokenizer = AutoTokenizer.from_pretrained(payload["model"], revision=payload["revision"])
    ids = prompt_ids(tokenizer, call["messages"])
    if len(ids) != call["input_tokens"]:
        raise ValueError("Replay tokenizer count differs from original")
    command = server_command(payload)
    save(root / "request_identity.json", dict(input_tokens=len(ids),
        prompt_sha256=call["prompt_sha256"], command=command,
        schema=memory.EXTRACTION_RESPONSE_FORMAT, source_image_id=fixture["source_image_id"]))
    client = AsyncOpenAI(base_url="http://127.0.0.1:8000/v1", api_key="local-only", max_retries=0, timeout=600)
    with (root / "server.log").open("w") as log:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(240):
                if server.poll() is not None:
                    raise RuntimeError("vLLM startup failed")
                try:
                    await client.models.list(timeout=2)
                    break
                except Exception:
                    await asyncio.sleep(2)
            else:
                raise TimeoutError("Startup readiness timeout")
            sentinel_schema = {"type": "object", "properties": {"probe": {"type": "string", "enum": ["grammar-active"]}},
                "required": ["probe"], "additionalProperties": False}
            sentinel = await client.completions.create(model=payload["model"], prompt=ids,
                temperature=0, max_tokens=32, seed=0,
                extra_body={"structured_outputs": {"json": sentinel_schema}})
            save(root / "sentinel.json", sentinel.model_dump())
            async def report(value):
                save(root / "stream.json", value)
                process = await asyncio.create_subprocess_exec("sync", "/state")
                await process.wait()
            streamed = await stream_infer(client, payload, ids, report)
            save(root / "streamed_response.json", streamed)
            sampling = dict(payload["sampling"])
            extra = {"structured_outputs": {"json": memory.EXTRACTION_RESPONSE_FORMAT["json_schema"]["schema"]}}
            for key in ("top_k", "min_p", "repetition_penalty"):
                if key in sampling:
                    extra[key] = sampling.pop(key)
            unstreamed = await client.completions.create(model=payload["model"], prompt=ids,
                **sampling, max_tokens=call["max_output_tokens"], seed=0, extra_body=extra)
            save(root / "unstreamed_response.json", unstreamed.model_dump())
            try:
                enforced = json.loads(sentinel.choices[0].text) == {"probe": "grammar-active"}
            except ValueError:
                enforced = False
            save(root / "summary.json", dict(sentinel_enforced=enforced,
                streamed_valid=output_valid(streamed["content"]),
                unstreamed_valid=output_valid(unstreamed.choices[0].text),
                streamed_finish_reason=streamed["finish_reason"],
                unstreamed_finish_reason=unstreamed.choices[0].finish_reason,
                streamed_output_tokens=streamed["output_tokens"],
                unstreamed_output_tokens=unstreamed.usage.completion_tokens))
        finally:
            await client.close()
            server.terminate()
            try:
                await asyncio.to_thread(server.wait, 20)
            except subprocess.TimeoutExpired:
                server.kill()
                await asyncio.to_thread(server.wait)
            process = await asyncio.create_subprocess_exec("sync", "/state")
            await process.wait()


def launch(directory, budget):
    from huggingface_hub import get_token
    from adaption_memory.execution.modal import CACHE, cloud
    from adaption_memory.inference.vllm import digest, resource_rate
    fixture = json.loads((directory / "fixture.json").read_text())
    if not 0.7 <= budget <= 1.1:
        raise ValueError("Diagnostic budget must be $0.70 to $1.10")
    if (directory / "cloud.json").exists():
        raise ValueError("Diagnostic already launched")
    modal, volume = cloud()
    run_id = "replay-" + digest(fixture)[:16]
    rate = resource_rate(fixture["payload"]["gpu"])
    record = dict(run_id=run_id, status="building", reserved_usd=budget,
        rate_usd_s=rate, timeout_seconds=int((budget-.5)/rate),
        source_image_id=fixture["source_image_id"])
    save(directory / "cloud.json", record)
    app = modal.App.lookup("adaption-memory-vllm", create_if_missing=False)
    image = modal.Image.from_id(fixture["source_image_id"]).add_local_file(
        Path(__file__).resolve(), "/diagnostic.py", copy=True).build(app)
    with volume.batch_upload() as batch:
        batch.put_file(directory / "fixture.json", f"/{run_id}/fixture.json")
    token = get_token()
    if not token:
        raise ValueError("Existing Hugging Face authentication is required")
    record.update(gpu_started_at=datetime.now(timezone.utc).isoformat(), image_id=image.object_id)
    save(directory / "cloud.json", record)
    sandbox = modal.Sandbox.create("python", "/diagnostic.py", "worker", "--directory", f"/state/{run_id}",
        app=app, image=image, gpu=fixture["payload"]["gpu"], cpu=(4,4), memory=(32768,32768),
        volumes={"/state": volume, "/cache": modal.Volume.from_name(CACHE)},
        secrets=[modal.Secret.from_dict({"HF_TOKEN": token})], timeout=record["timeout_seconds"])
    record.update(status="running", sandbox_id=sandbox.object_id)
    save(directory / "cloud.json", record)
    print(json.dumps(record, indent=2))


def collect(directory):
    from adaption_memory.execution.modal import cloud, record_stopped, volume_json
    from adaption_memory.integrity import atomic_text
    record = json.loads((directory / "cloud.json").read_text())
    modal, volume = cloud()
    exit_code = modal.Sandbox.from_id(record["sandbox_id"]).poll()
    if exit_code is not None:
        record_stopped(directory, record)
    collected = {}
    for name in ("request_identity", "sentinel", "stream", "streamed_response",
                 "unstreamed_response", "summary", "fatal"):
        value = volume_json(volume, f"{record['run_id']}/{name}.json")
        if value is not None:
            save(directory / f"{name}.json", value)
            collected[name] = value
    try:
        log = b"".join(volume.read_file(f"{record['run_id']}/server.log")).decode()
        atomic_text(directory / "server.log", log)
    except FileNotFoundError:
        pass
    print(json.dumps(dict(exit_code=exit_code, files=list(collected),
        summary=collected.get("summary"), fatal=collected.get("fatal"),
        accounted_usd=record.get("accounted_usd")), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "launch", "worker", "collect"])
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--history")
    parser.add_argument("--session", type=int)
    parser.add_argument("--budget-usd", type=float)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.source, args.history, args.session, args.directory)
    elif args.command == "launch":
        launch(args.directory, args.budget_usd)
    elif args.command == "collect":
        collect(args.directory)
    else:
        try:
            asyncio.run(worker(args.directory / "fixture.json"))
        except BaseException as error:
            save(args.directory / "fatal.json", {"error_type": type(error).__name__, "message": str(error)[:1000]})
            subprocess.run(["sync", "/state"], check=True)
            raise
