"""Mem0 OSS as a comparison memory system: one shared store per history, every memory to the answerer.

The retired runner built a separate Mem0 store per question, so a history was ingested once per
question. In no-retrieval mode the answerer receives every stored memory and nothing is searched
per question, so the store is question-independent: this executor builds it once per history and
the pipeline shares it across that history's questions, exactly as it shares extractor memories.

Mem0 constructs its own OpenAI clients. They are wrapped so every LLM and embedding call reserves
an upper bound on the shared budget ledger before dispatch and settles the measured cost after.
Checkpoints use the same per-history layout the Modal executor writes, so the pipeline's importer
records the calls and memories without a second code path.
"""
from __future__ import annotations

import importlib.metadata
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adaption_memory.execution.files import save
from adaption_memory.inference.openai import BudgetLedger, Price, cost_usd
from adaption_memory.inference.usage import usage_dict
from adaption_memory.execution.modal import fingerprint, same_work
from adaption_memory.presets import ExperimentPreset, grouped_histories, resolve
from adaption_memory.source_manifest import source_hashes

os.environ.setdefault("MEM0_TELEMETRY", "False")

LLM_REASONING_EFFORT = "low"  # as in every recorded Mem0 run
CHUNK_MESSAGES = 4  # one Mem0 add per four messages, as in the completed LongMemEval Mem0 runs
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PRICE_PER_MILLION = 0.02
TERMINAL_STATES = ("complete", "smoke_complete", "unknown_outcome", "failed")

_DATE_FORMATS = (
    "%Y/%m/%d (%a) %H:%M",  # LongMemEval
    "%I:%M %p on %d %B, %Y",  # LoCoMo
    "%I:%M %p on %d %b, %Y",
    "%B-%d-%Y",  # BEAM
    "%Y-%m-%d",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(text: str) -> int | None:
    text = (text or "").strip()
    for fmt in _DATE_FORMATS:
        try:
            return int(datetime.strptime(text, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return None


def build_payload(
    preset: ExperimentPreset, *, smoke_histories: int | None = None, smoke_updates: int | None = None
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    spec = resolve(preset)
    histories, grouped = grouped_histories(preset)
    if smoke_histories is not None:
        if smoke_histories < 1 or smoke_histories > len(histories):
            raise ValueError("Invalid smoke history count")
        histories = histories[:smoke_histories]
        grouped = {row["history_sha256"]: grouped[row["history_sha256"]] for row in histories}
    payload = {
        "schema_version": 1,
        "benchmark": spec.benchmark,
        "spec_sha256": spec.sha256(),
        "system": "mem0",
        "mem0ai_version": importlib.metadata.version("mem0ai"),
        "llm": {"model": preset.extractor_model, "reasoning_effort": LLM_REASONING_EFFORT},
        "embedder": EMBEDDING_MODEL,
        "chunk_messages": CHUNK_MESSAGES,
        "extraction_max_tokens": preset.extraction_max_tokens,
        "store_scope": "one store per history, shared by its questions",
        "context_policy": "all stored memories, oldest first, no question-based search",
        "date_handling": "OSS SDK rejects the platform timestamp parameter; the session date is passed as metadata and as a leading line of each chunk.",
        "prices_usd_per_million_tokens": {
            "llm_input": preset.answer_input_cost,
            "llm_cached_input": preset.answer_cached_input_cost,
            "llm_output": preset.answer_output_cost,
            "embedding_input": EMBEDDING_PRICE_PER_MILLION,
        },
        "histories": histories,
        "updates_per_history": smoke_updates,
        "code_sha256": source_hashes(),
    }
    payload["fingerprint"] = fingerprint(payload)
    return payload, grouped


def prepare(
    directory: Path, preset: ExperimentPreset, *, smoke_histories: int | None = None, smoke_updates: int | None = None
) -> dict[str, Any]:
    payload, grouped = build_payload(preset, smoke_histories=smoke_histories, smoke_updates=smoke_updates)
    spec = resolve(preset)
    config = {
        "schema_version": 1,
        "preset": preset.name,
        "benchmark": preset.benchmark,
        "spec_sha256": spec.sha256(),
        "configuration_sha256": spec.configuration_sha256(),
        "payload": payload,
        "questions": grouped,
        "scope": "smoke" if smoke_histories is not None else "final",
    }
    path = directory / "configuration.json"
    if path.exists():
        saved = json.loads(path.read_text())
        if not same_work(saved, config):
            raise ValueError("Prepared run differs; use a new directory")
        if saved != config:
            save(path, config)
            save(directory / "payload.json", payload)
    else:
        save(path, config)
        save(directory / "payload.json", payload)
    return config


class Meter:
    """Budget reservation and usage capture for the OpenAI clients Mem0 constructs."""

    def __init__(self, ledger: BudgetLedger, llm_price: Price, max_output_tokens: int, prefix: str):
        self.ledger = ledger
        self.llm_price = llm_price
        self.max_output_tokens = max_output_tokens
        self.prefix = prefix
        self.calls: list[dict[str, Any]] = []
        self._count = 0
        self._lock = threading.Lock()

    def _call_id(self, kind: str) -> str:
        with self._lock:
            self._count += 1
            return f"{self.prefix}:{kind}:{self._count}"

    def llm(self, create, kwargs: dict[str, Any]) -> Any:
        kwargs.setdefault("max_completion_tokens", self.max_output_tokens)  # Mem0 drops the cap for reasoning models
        call_id = self._call_id("llm")
        bound = len(json.dumps(kwargs.get("messages"), ensure_ascii=False).encode()) + 512
        reserved = (bound * self.llm_price.input_per_million + self.max_output_tokens * self.llm_price.output_per_million) / 1e6
        self.ledger.reserve(call_id, reserved)
        started = time.perf_counter()
        try:
            response = create(**kwargs)
        except Exception:
            self.calls.append({"kind": "llm", "call_id": call_id, "status": "unknown_outcome", "reserved_usd": reserved})
            raise  # the reservation stays; an unknown outcome is never assumed free
        usage = usage_dict(getattr(response, "usage", None))
        actual = cost_usd(usage, self.llm_price.input_per_million, self.llm_price.cached_input_per_million, self.llm_price.output_per_million)
        self.ledger.settle(call_id, actual)
        self.calls.append({
            "kind": "llm", "call_id": call_id, "status": "complete", "reserved_usd": reserved, "cost_usd": actual,
            "usage": usage, "resolved_model": getattr(response, "model", None), "finish_reason": response.choices[0].finish_reason,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
        })
        if response.choices[0].finish_reason == "length":
            raise RuntimeError("Mem0 extraction output reached its token cap; refusing incomplete memory")
        return response

    def embedding(self, create, kwargs: dict[str, Any]) -> Any:
        call_id = self._call_id("embed")
        bound = len(json.dumps(kwargs.get("input"), ensure_ascii=False).encode()) + 64
        reserved = bound * EMBEDDING_PRICE_PER_MILLION / 1e6
        self.ledger.reserve(call_id, reserved)
        started = time.perf_counter()
        try:
            response = create(**kwargs)
        except Exception:
            self.calls.append({"kind": "embedding", "call_id": call_id, "status": "unknown_outcome", "reserved_usd": reserved})
            raise
        tokens = getattr(getattr(response, "usage", None), "prompt_tokens", 0) or 0
        actual = tokens * EMBEDDING_PRICE_PER_MILLION / 1e6
        self.ledger.settle(call_id, actual)
        self.calls.append({"kind": "embedding", "call_id": call_id, "status": "complete", "reserved_usd": reserved,
            "cost_usd": actual, "input_tokens": tokens, "elapsed_seconds": round(time.perf_counter() - started, 4)})
        return response

    def take(self) -> list[dict[str, Any]]:
        calls, self.calls = self.calls, []
        return calls


class Mem0Store:
    """One persistent Mem0 memory for one history, with metered clients."""

    def __init__(self, workdir: Path, user_id: str, llm_model: str, meter: Meter):
        from mem0 import Memory
        import mem0.embeddings.openai  # noqa: F401  provider modules imported once, so threads never race the import system
        import mem0.llms.openai  # noqa: F401
        import mem0.vector_stores.qdrant  # noqa: F401

        self.user_id = user_id
        self.meter = meter
        workdir.mkdir(parents=True, exist_ok=True)
        # Luna is a reasoning model; without the flag Mem0's provider sends a temperature the model rejects.
        llm_config: dict[str, Any] = {"model": llm_model, "is_reasoning_model": True, "reasoning_effort": LLM_REASONING_EFFORT}
        self.memory = Memory.from_config({
            "llm": {"provider": "openai", "config": llm_config},
            "embedder": {"provider": "openai", "config": {"model": EMBEDDING_MODEL}},
            "vector_store": {"provider": "qdrant", "config": {
                "collection_name": "mem0", "path": str(workdir / "qdrant"), "embedding_model_dims": 1536}},
            "history_db_path": str(workdir / "history.db"),
        })
        self.memory.llm.client.max_retries = 0
        self.memory.embedding_model.client.max_retries = 0
        completions = self.memory.llm.client.chat.completions
        original_create = completions.create
        completions.create = lambda **kwargs: meter.llm(original_create, kwargs)  # type: ignore[method-assign]
        embeddings = self.memory.embedding_model.client.embeddings
        original_embed = embeddings.create
        embeddings.create = lambda **kwargs: meter.embedding(original_embed, kwargs)  # type: ignore[method-assign]

    def add_session(self, messages: list[dict[str, str]], timestamp: str) -> dict[str, int]:
        events: dict[str, int] = {"adds": 0}
        for index in range(0, len(messages), CHUNK_MESSAGES):
            chunk = [{"role": m["role"], "content": m["content"]} for m in messages[index:index + CHUNK_MESSAGES]]
            chunk[0] = {**chunk[0], "content": f"Session date: {timestamp}\n{chunk[0]['content']}"}
            result = self._add_with_retries(chunk, timestamp)
            events["adds"] += 1
            for entry in (result or {}).get("results", []):
                events[entry.get("event", "?")] = events.get(entry.get("event", "?"), 0) + 1
        return events

    def _add_with_retries(self, chunk: list[dict[str, str]], timestamp: str) -> dict[str, Any]:
        """Mem0's client has retries disabled for exact accounting; rate limits wait here instead."""
        for attempt in range(8):
            try:
                return self.memory.add(messages=chunk, user_id=self.user_id, metadata={"session_date": timestamp}, infer=True) or {}
            except Exception as error:
                text = str(error)
                if ("429" in text or "rate_limit" in text.lower() or "rate limit" in text.lower()) and attempt < 7:
                    time.sleep(min(60.0, 5.0 * 2 ** attempt))
                    continue
                raise
        raise RuntimeError("unreachable")

    def all_memories(self) -> list[dict[str, Any]]:
        response = self.memory.get_all(filters={"user_id": self.user_id}, top_k=100_000)  # default page is 20
        results = response.get("results", []) if isinstance(response, dict) else list(response)
        return [{"memory": r.get("memory", ""), "session_date": (r.get("metadata") or {}).get("session_date"),
                 "created_at": r.get("created_at"), "id": r.get("id")} for r in results]

    def close(self) -> None:
        for closer in (lambda: self.memory.db.close(), lambda: self.memory.vector_store.client.close()):
            try:
                closer()
            except Exception:
                pass


def memory_lines(memories: list[dict[str, Any]], timestamps: list[str]) -> list[dict[str, Any]]:
    """Every memory as a run-record line, oldest session first; equal dates keep Mem0's saved order."""
    session_of = {}
    for number, timestamp in enumerate(timestamps, start=1):
        session_of.setdefault(timestamp, number)
    ordered = sorted(memories, key=lambda m: (parse_timestamp(m.get("session_date") or "") or 0, m.get("created_at") or ""))
    return [{"kind": "mem0", "session": session_of.get(m.get("session_date"), 0), "date": m.get("session_date") or "unknown date",
             "text": m["memory"], "id": m.get("id")} for m in ordered]


def build_history(directory: Path, payload: dict[str, Any], row: dict[str, Any], ledger: BudgetLedger,
                  store_factory=Mem0Store) -> dict[str, Any]:
    key = row["history_sha256"]
    path = directory / "memories" / f"{key}.json"
    state = json.loads(path.read_text()) if path.exists() else {
        "history_sha256": key, "payload_sha256": payload["fingerprint"], "status": "pending",
        "sessions_done": 0, "lines": [], "calls": [], "warnings": []}
    if state["payload_sha256"] != payload["fingerprint"]:
        raise ValueError("Checkpoint configuration mismatch")
    if state["status"] in TERMINAL_STATES:
        return state
    if state["calls"] and state["calls"][-1]["status"] == "in_flight":
        # A session was interrupted after some adds reached the store; re-adding it would duplicate memories.
        state["calls"][-1]["status"] = "unknown_outcome"
        state["status"] = "unknown_outcome"
        save(path, state)
        return state
    prices = payload["prices_usd_per_million_tokens"]
    meter = Meter(ledger, Price(prices["llm_input"], prices["llm_cached_input"], prices["llm_output"]),
                  payload["extraction_max_tokens"], f"mem0:{key[:16]}")
    store = store_factory(directory / "stores" / key, f"h_{key[:16]}", payload["llm"]["model"], meter)
    sessions = row["history"]
    limit = min(len(sessions), payload.get("updates_per_history") or len(sessions))
    try:
        for index in range(state["sessions_done"], limit):
            session = sessions[index]
            call = {"session": index + 1, "status": "in_flight", "requested_model": payload["llm"]["model"],
                    "reserved_usd": 0.0, "cost_usd": 0.0, "started_at": now()}
            state["calls"].append(call)
            state["status"] = "running"
            save(path, state)
            started = time.perf_counter()
            try:
                events = store.add_session(session["messages"], session["timestamp"])
            except Exception as error:
                provider = meter.take()
                call.update(status="unknown_outcome", error_type=type(error).__name__, error=str(error)[:500],
                            provider_calls=provider, reserved_usd=sum(c["reserved_usd"] for c in provider),
                            cost_usd=sum(c.get("cost_usd") or 0.0 for c in provider), finished_at=now())
                state["status"] = "unknown_outcome"
                save(path, state)
                return state
            provider = meter.take()
            llm = [c for c in provider if c["kind"] == "llm"]
            call.update(
                status="complete", ok=True, events=events, llm_calls=len(llm),
                embedding_calls=sum(c["kind"] == "embedding" for c in provider),
                usage={
                    "input_tokens": sum(c["usage"]["input_tokens"] or 0 for c in llm),
                    "cached_input_tokens": sum(c["usage"]["cached_input_tokens"] or 0 for c in llm),
                    "output_tokens": sum(c["usage"]["output_tokens"] or 0 for c in llm),
                    "reasoning_output_tokens": sum(c["usage"]["reasoning_output_tokens"] or 0 for c in llm),
                    "total_tokens": sum(c["usage"]["total_tokens"] or 0 for c in llm),
                },
                embedding_tokens=sum(c.get("input_tokens", 0) for c in provider if c["kind"] == "embedding"),
                reserved_usd=sum(c["reserved_usd"] for c in provider),
                cost_usd=sum(c.get("cost_usd") or 0.0 for c in provider),
                resolved_model=next((c.get("resolved_model") for c in llm if c.get("resolved_model")), None),
                elapsed_seconds=round(time.perf_counter() - started, 4), finished_at=now(),
            )
            state["sessions_done"] = index + 1
            save(path, state)
        state["lines"] = memory_lines(store.all_memories(), [s["timestamp"] for s in sessions])
        state["status"] = "complete" if limit == len(sessions) else "smoke_complete"
        save(path, state)
        return state
    finally:
        store.close()


def build(directory: Path, preset: ExperimentPreset, ledger: BudgetLedger, store_factory=Mem0Store) -> dict[str, Any]:
    config = json.loads((directory / "configuration.json").read_text())
    payload = config["payload"]
    record_path = directory / "executor.json"
    record = json.loads(record_path.read_text()) if record_path.exists() else {
        "schema_version": 1, "runner": "adaption_memory.execution.mem0", "started_at": now(), "sessions": []}
    record.update(status="running", reserved_usd=ledger.limit_usd)
    record["sessions"].append({"started_at": now()})
    save(record_path, record)
    with ThreadPoolExecutor(max_workers=max(1, preset.concurrency)) as pool:
        states = list(pool.map(lambda row: build_history(directory, payload, row, ledger, store_factory), payload["histories"]))
    statuses = {s["history_sha256"]: s["status"] for s in states}
    # Cost is the sum over every session call ever recorded for this directory, so a build that
    # resumed after an earlier process still accounts for that process's spend.
    known = sum(call.get("cost_usd") or 0.0 for s in states for call in s["calls"] if call["status"] == "complete")
    exposure = sum(call.get("reserved_usd") or 0.0 for s in states for call in s["calls"] if call["status"] == "unknown_outcome")
    record["sessions"][-1].update(finished_at=now(), process_known_spend_usd=ledger.known_spend_usd)
    record.update(
        status="stopped", finished_at=now(), histories=statuses,
        complete_histories=sum(v in ("complete", "smoke_complete") for v in statuses.values()),
        known_spend_usd=round(known, 8),
        unknown_or_reserved_exposure_usd=round(exposure, 8),
        accounted_usd=round(known + exposure, 8),
        accounting_basis="sum_of_session_call_costs_plus_retained_unknown_reservations",
    )
    save(record_path, record)
    return record


def executor_record(directory: Path) -> dict[str, Any]:
    """The executor's cost as one artifact for the run's graph, in the shape the importer records."""
    record = json.loads((directory / "executor.json").read_text())
    payload = json.loads((directory / "payload.json").read_text())
    return {
        "name": "mem0",
        "requested_model": f"mem0/{payload['llm']['model']}",
        "resolved_model": f"mem0ai-{payload['mem0ai_version']}/{payload['llm']['model']}",
        "reserved_usd": float(record["reserved_usd"]),
        "cost_usd": float(record["accounted_usd"]),
        "accounting_basis": record.get("accounting_basis"),
        "accounting_note": "Measured Mem0 LLM and embedding usage at configured prices; unknown-outcome reservations retained.",
        "started_at": record.get("started_at"),
        "finished_at": record.get("finished_at"),
    }
