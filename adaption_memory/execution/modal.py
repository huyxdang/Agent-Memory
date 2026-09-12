"""Modal lifecycle for one resolved vLLM extraction experiment."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import time

from adaption_memory.config import PROJECT_ROOT as ROOT
from adaption_memory.execution.files import save
from adaption_memory.history import history_sha256, sanitize_history
from adaption_memory.inference.vllm import GPU_RATES, digest, resource_rate
from adaption_memory.integrity import sha256_file
from adaption_memory.presets import ExperimentPreset, resolve, selected_items
from adaption_memory.source_manifest import RUNTIME_SOURCE_PATHS, source_hashes


VOLUME = "adaption-qwen-experiments-v3"
CACHE = "adaption-qwen-cache-v2"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_payload(
    preset: ExperimentPreset,
    *,
    gpu: str | None = None,
    smoke_histories: int | None = None,
    smoke_updates: int | None = None,
) -> tuple[dict, dict[str, list[dict]]]:
    spec = resolve(preset)
    items = selected_items(preset)
    grouped: dict[str, list[dict]] = {}
    histories: list[dict] = []
    for item in items:
        record = item.to_record()
        identity = history_sha256(record)
        if identity not in grouped:
            histories.append(
                {
                    "history_sha256": identity,
                    "subject": item.subject,
                    "history": sanitize_history(record),
                }
            )
            grouped[identity] = []
        grouped[identity].append(record)
    if smoke_histories is not None:
        if smoke_histories < 1 or smoke_histories > len(histories):
            raise ValueError("Invalid smoke history count")
        histories = histories[:smoke_histories]
        grouped = {row["history_sha256"]: grouped[row["history_sha256"]] for row in histories}
    model = spec.extractor_model
    selected_gpu = gpu or model.default_gpu
    if selected_gpu not in GPU_RATES:
        raise ValueError(f"Unsupported GPU: {selected_gpu}")
    payload = {
        "schema_version": 1,
        "benchmark": spec.benchmark,
        "spec_sha256": spec.sha256(),
        "model": model.name,
        "revision": model.revision,
        "adapter": None if spec.adapter is None else {
            "repo": spec.adapter.repo,
            "revision": spec.adapter.revision,
            "name": spec.adapter.name,
            "rank": spec.adapter.rank,
        },
        "context_window": model.context_window,
        "extraction_max_tokens": preset.extraction_max_tokens,
        "histories": histories,
        "gpu": selected_gpu,
        "concurrency": spec.concurrency,
        "structured_output": True,
        "sampling": model.sampling_dict(),
        "engine": model.engine_dict(),
        "gated_model": model.gated,
        "merge_user_messages": model.merge_user_messages,
        "updates_per_history": smoke_updates,
        "precision": model.dtype,
        "code_sha256": source_hashes(ROOT),
    }
    payload["fingerprint"] = digest(payload)
    return payload, grouped


def validate_payload(directory: Path, payload: dict) -> None:
    saved = json.loads((directory / "payload.json").read_text())
    expected = digest({key: value for key, value in payload.items() if key != "fingerprint"})
    if saved != payload or payload.get("fingerprint") != expected:
        raise ValueError("Payload differs from frozen configuration or has a stale fingerprint")
    for name, expected_hash in payload["code_sha256"].items():
        if sha256_file(ROOT / name) != expected_hash:
            raise ValueError(f"Runtime source changed after preparation: {name}")


def prepare(
    directory: Path,
    preset: ExperimentPreset,
    *,
    gpu: str | None = None,
    smoke_histories: int | None = None,
    smoke_updates: int | None = None,
) -> dict:
    payload, grouped = build_payload(
        preset,
        gpu=gpu,
        smoke_histories=smoke_histories,
        smoke_updates=smoke_updates,
    )
    config = {
        "schema_version": 1,
        "preset": preset.name,
        "benchmark": preset.benchmark,
        "spec_sha256": resolve(preset).sha256(),
        "payload": payload,
        "questions": grouped,
        "scope": "smoke" if smoke_histories is not None else "final",
    }
    path = directory / "configuration.json"
    if path.exists() and json.loads(path.read_text()) != config:
        raise ValueError("Prepared run differs; use a new directory")
    if not path.exists():
        save(path, config)
        save(directory / "payload.json", payload)
    validate_payload(directory, payload)
    return config


def cloud():
    import certifi

    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    import modal

    return modal, modal.Volume.from_name(VOLUME, create_if_missing=True, version=2)


def launch(directory: Path, budget_usd: float) -> dict:
    if not math.isfinite(budget_usd) or not 0 < budget_usd <= 10:
        raise ValueError("Explicit Modal budget must be in (0, 10]")
    config = json.loads((directory / "configuration.json").read_text())
    payload = config["payload"]
    validate_payload(directory, payload)
    ledger = directory / "cloud.json"
    if ledger.exists():
        raise ValueError("Run already launched; resume or stop it")
    rate = resource_rate(payload["gpu"])
    timeout = min(7200, int((budget_usd - 0.50) / rate))
    if timeout < 300:
        raise ValueError("Budget is insufficient for startup and validation")
    modal, volume = cloud()
    run_id = "vllm-" + payload["fingerprint"][:16]
    record = {
        "schema_version": 1,
        "runner": "adaption_memory.execution.modal",
        "run_id": run_id,
        "status": "building",
        "started_at": now(),
        "reserved_usd": budget_usd,
        "timeout_seconds": timeout,
        "rate_usd_s": rate,
        "gpu": payload["gpu"],
        "actual_invoice_cost_usd": None,
    }
    save(ledger, record)
    app = modal.App.lookup("adaption-memory-vllm", create_if_missing=True)
    image = (
        modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
        .entrypoint([])
        .uv_pip_install("vllm==0.21.0")
        .env({"HF_HOME": "/cache/huggingface", "VLLM_CACHE_ROOT": "/cache/vllm", "PYTHONPATH": "/app"})
    )
    for name in RUNTIME_SOURCE_PATHS:
        image = image.add_local_file(ROOT / name, "/app/" + name, copy=True)
    try:
        image = image.build(app)
        record["image_id"] = image.object_id
        with volume.batch_upload() as batch:
            batch.put_file(directory / "payload.json", f"/{run_id}/payload.json")
        cache = modal.Volume.from_name(CACHE, create_if_missing=True, version=2)
        record.update(status="creating", gpu_started_at=now())
        save(ledger, record)
        secrets = []
        if payload.get("gated_model"):
            from huggingface_hub import get_token

            token = get_token()
            if not token:
                raise ValueError("Gated model requires local Hugging Face authentication")
            secrets.append(modal.Secret.from_dict({"HF_TOKEN": token}))
        sandbox = modal.Sandbox.create(
            "python", "-u", "-m", "adaption_memory.execution.vllm_worker",
            f"/state/{run_id}/payload.json",
            app=app,
            name=run_id,
            image=image,
            gpu=payload["gpu"],
            cpu=(4, 4),
            memory=(32768, 32768),
            volumes={"/state": volume, "/cache": cache},
            secrets=secrets,
            timeout=timeout,
        )
        record.update(status="running", sandbox_id=sandbox.object_id)
        save(ledger, record)
        return record
    except BaseException as error:
        record.update(status="launch_failed", error_type=type(error).__name__)
        save(ledger, record)
        raise


def volume_json(volume, path: str):
    for attempt in range(3):
        try:
            return json.loads(b"".join(volume.read_file(path)).decode())
        except FileNotFoundError:
            return None
        except (UnicodeError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise AssertionError("unreachable")


def reconcile_stopped_states(directory: Path, payload: dict) -> list[str]:
    changed = []
    for row in payload["histories"]:
        key = row["history_sha256"]
        path = directory / "memories" / f"{key}.json"
        if not path.exists():
            continue
        state = json.loads(path.read_text())
        if state.get("calls") and state["calls"][-1].get("status") == "in_flight":
            state["calls"][-1].update(status="unknown_outcome", error_type="SandboxStopped")
            state["status"] = "unknown_outcome"
            save(path, state)
            changed.append(key)
    return changed


def summarize(directory: Path, payload: dict) -> dict:
    states = {
        path.stem: json.loads(path.read_text())
        for path in (directory / "memories").glob("*.json")
    }
    expected = [row["history_sha256"] for row in payload["histories"]]
    missing = sorted(set(expected) - states.keys())
    failed = sorted(key for key, state in states.items() if state.get("status") != "complete")
    result = {
        "schema_version": 1,
        "histories": len(expected),
        "complete_histories": sum(state.get("status") == "complete" for state in states.values()),
        "missing": missing,
        "failed": failed,
        "complete": not missing and not failed,
    }
    save(directory / "summary.json", result)
    return result


def collect(directory: Path, watch: bool = False) -> dict:
    modal, volume = cloud()
    config = json.loads((directory / "configuration.json").read_text())
    payload = config["payload"]
    validate_payload(directory, payload)
    ledger_path = directory / "cloud.json"
    record = json.loads(ledger_path.read_text())
    if not record.get("sandbox_id"):
        raise ValueError("Launch outcome is unresolved")
    seen = {}
    while True:
        sandbox = modal.Sandbox.from_id(record["sandbox_id"])
        stopped = sandbox.poll() is not None
        for row in payload["histories"]:
            key = row["history_sha256"]
            progress = volume_json(volume, f"{record['run_id']}/progress/{key}.json")
            if progress is not None and progress != seen.get(key):
                state = volume_json(volume, f"{record['run_id']}/memories/{key}.json")
                if state["payload_sha256"] != payload["fingerprint"]:
                    raise ValueError("Cloud checkpoint fingerprint mismatch")
                save(directory / "memories" / f"{key}.json", state)
                seen[key] = progress
        for name in ("loaded", "finished", "fatal"):
            value = volume_json(volume, f"{record['run_id']}/{name}.json")
            if value is not None:
                save(directory / f"{name}.json", value)
        if stopped:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(record["gpu_started_at"])).total_seconds()
            record.update(
                status="stopped",
                termination="confirmed",
                finished_at=now(),
                accounted_usd=min(record["reserved_usd"], elapsed * record["rate_usd_s"] + 0.50),
            )
            save(ledger_path, record)
            reconcile_stopped_states(directory, payload)
        if stopped or not watch:
            break
        time.sleep(15)
    return summarize(directory, payload)


def stop(directory: Path) -> None:
    modal, _ = cloud()
    record = json.loads((directory / "cloud.json").read_text())
    modal.Sandbox.from_id(record["sandbox_id"]).terminate()
