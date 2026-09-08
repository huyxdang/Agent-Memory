"""Mem0 OSS as a comparison system: Memory.add per turn pair, Memory.search for the answer.

Mirrors Mem0's own benchmark runner (memory-benchmarks at the pinned revision):
messages are ingested in chunks of two (one user-assistant pair) with the session
timestamp, and the answerer receives the top-k retrieved memories sorted oldest
first with their dates. Everything else, answer model, judge, run records, is our
harness, which is the article's setup: "our own evaluation of Mem0 OSS, run under
the same per-benchmark answering model and evaluation harness as our system."

Each question gets its own Memory instance with a private Qdrant directory and
history database, so questions can run concurrently. Token usage is captured by
wrapping the OpenAI clients Mem0 constructs.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("MEM0_TELEMETRY", "False")

from mem0 import Memory  # noqa: E402
# Provider modules are imported here, once, so worker threads never race the import system.
import mem0.embeddings.openai  # noqa: E402, F401
import mem0.llms.openai  # noqa: E402, F401
import mem0.vector_stores.qdrant  # noqa: E402, F401
import openai  # noqa: E402, F401

DEFAULT_TOP_K = 200  # Mem0's runner default (--top-k 200, ANSWERER_MEMORY_LIMIT 200)
DEFAULT_CHUNK_MESSAGES = 2  # Mem0's runner CHUNK_SIZE: one user-assistant pair per add
EMBEDDING_MODEL = "text-embedding-3-small"
EMBED_SAFE_CHARS = 24_000  # about 6k tokens, under text-embedding-3-small's 8,192-token input limit

ANSWER_SYSTEM_PROMPT = """Answer the question using only the retrieved memories below, which a memory system wrote from the user's earlier conversations. Each memory carries the date of the conversation it came from. Memories may repeat or partly contradict each other; when they do, prefer the more recent one.

- For advice or recommendation questions, tailor the answer to the user's stored preferences, interests, possessions, and past choices, and name the memories you are using. Do not decline over missing incidental details such as the user's location; make reasonable suggestions from what is known.
- For questions that count things or compute dates or durations, first list the relevant memories with their dates, then do the arithmetic, then give the answer.
- For questions about what the assistant said or recommended earlier, look for memories that record the assistant's suggestions.
- Otherwise be direct and concise. If the memories truly do not contain the information, say so."""

ANSWER_PROMPT_FORMAT = (
    "Question date: {question_date}\n\n"
    "Retrieved memories ({count} retrieved from {session_count} earlier sessions, oldest first; date | memory):\n{memories}\n\n"
    "Question: {question}"
)

_DATE_FORMATS = (
    "%Y/%m/%d (%a) %H:%M",  # LongMemEval
    "%I:%M %p on %d %B, %Y",  # LoCoMo
    "%I:%M %p on %d %b, %Y",
    "%B-%d-%Y",  # BEAM time anchors
    "%Y-%m-%d",
)


def parse_timestamp(text: str) -> int | None:
    text = (text or "").strip()
    for fmt in _DATE_FORMATS:
        try:
            return int(datetime.strptime(text, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return None


def _human_date(created_at: str | None) -> str:
    if not created_at:
        return "unknown date"
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return created_at[:10]


class Mem0Store:
    """One Mem0 memory for one question, with usage capture."""

    def __init__(self, question_id: str, llm_model: str, reasoning_effort: str | None, workdir: Path | None = None) -> None:
        self.user_id = f"q_{question_id}"
        self.workdir = Path(workdir or tempfile.mkdtemp(prefix=f"mem0_{question_id}_"))
        llm_config: dict[str, Any] = {"model": llm_model, "is_reasoning_model": True}
        if reasoning_effort and reasoning_effort != "none":
            llm_config["reasoning_effort"] = reasoning_effort
        self.config = {
            "llm": {"provider": "openai", "config": llm_config},
            "embedder": {"provider": "openai", "config": {"model": EMBEDDING_MODEL}},
            "vector_store": {
                "provider": "qdrant",
                "config": {"collection_name": "mem0", "path": str(self.workdir / "qdrant"), "embedding_model_dims": 1536},
            },
            "history_db_path": str(self.workdir / "history.db"),
        }
        self.memory = Memory.from_config(self.config)
        self.calls: list[dict[str, Any]] = []
        self._wrap_clients()

    def _wrap_clients(self) -> None:
        completions = self.memory.llm.client.chat.completions
        original_create = completions.create

        def create_with_usage(**kwargs: Any) -> Any:
            start = time.perf_counter()
            response = original_create(**kwargs)
            usage = getattr(response, "usage", None)
            details_in = getattr(usage, "prompt_tokens_details", None)
            details_out = getattr(usage, "completion_tokens_details", None)
            self.calls.append(
                {
                    "kind": "llm",
                    "model": getattr(response, "model", kwargs.get("model")),
                    "input_tokens": getattr(usage, "prompt_tokens", 0) or 0,
                    "cached_input_tokens": (getattr(details_in, "cached_tokens", 0) or 0) if details_in else 0,
                    "output_tokens": getattr(usage, "completion_tokens", 0) or 0,
                    "reasoning_output_tokens": (getattr(details_out, "reasoning_tokens", 0) or 0) if details_out else 0,
                    "elapsed_seconds": time.perf_counter() - start,
                }
            )
            return response

        completions.create = create_with_usage  # type: ignore[method-assign]

        embeddings = self.memory.embedding_model.client.embeddings
        original_embed = embeddings.create

        def embed_with_usage(**kwargs: Any) -> Any:
            start = time.perf_counter()
            response = original_embed(**kwargs)
            usage = getattr(response, "usage", None)
            self.calls.append(
                {
                    "kind": "embedding",
                    "model": getattr(response, "model", kwargs.get("model")),
                    "input_tokens": getattr(usage, "prompt_tokens", 0) or 0,
                    "cached_input_tokens": 0,
                    "output_tokens": 0,
                    "reasoning_output_tokens": 0,
                    "elapsed_seconds": time.perf_counter() - start,
                }
            )
            return response

        embeddings.create = embed_with_usage  # type: ignore[method-assign]

    def _add_with_retries(self, chunk: list[dict[str, str]], timestamp: str) -> dict[str, Any]:
        """Mem0's own client retries rate limits only briefly; tokens-per-minute limits need longer waits.

        Also handles a turn longer than the embedding model's 8,192-token input limit by retrying
        once with each message cut to EMBED_SAFE_CHARS; the result is marked so the caller can count it.
        """
        truncated = False
        for attempt in range(8):
            try:
                result = self.memory.add(messages=chunk, user_id=self.user_id, metadata={"session_date": timestamp}, infer=True) or {}
                return {**result, "_truncated": truncated}
            except Exception as exc:
                text = str(exc)
                if "maximum input length" in text and not truncated:
                    chunk = [{**m, "content": m["content"][:EMBED_SAFE_CHARS]} for m in chunk]
                    truncated = True
                    continue
                if ("429" in text or "Rate limit" in text or "rate_limit" in text) and attempt < 7:
                    time.sleep(min(60.0, 5.0 * 2 ** attempt))
                    continue
                raise
        raise RuntimeError("unreachable")

    def add_session(self, messages: list[dict[str, str]], timestamp: str, chunk_messages: int = DEFAULT_CHUNK_MESSAGES) -> dict[str, Any]:
        """Ingest one session in chunks. Returns the session's usage and Mem0 events."""
        first_call = len(self.calls)
        start = time.perf_counter()
        events: dict[str, int] = {}
        adds = 0
        # The OSS SDK rejects Mem0's `timestamp` parameter (platform only), so the session date
        # travels as metadata and as a leading line of each chunk, which is what every other
        # system in this harness sees too.
        truncated = 0
        for index in range(0, len(messages), chunk_messages):
            chunk = [{"role": m["role"], "content": m["content"]} for m in messages[index:index + chunk_messages]]
            chunk[0] = {**chunk[0], "content": f"Session date: {timestamp}\n{chunk[0]['content']}"}
            result = self._add_with_retries(chunk, timestamp)
            if result.get("_truncated"):
                truncated += 1
            adds += 1
            for entry in (result or {}).get("results", []):
                events[entry.get("event", "?")] = events.get(entry.get("event", "?"), 0) + 1
        session_calls = self.calls[first_call:]
        llm = [c for c in session_calls if c["kind"] == "llm"]
        embed = [c for c in session_calls if c["kind"] == "embedding"]
        return {
            "adds": adds,
            "truncated_chunks": truncated,
            "events": events,
            "llm_calls": len(llm),
            "embedding_calls": len(embed),
            "usage": {
                "input_tokens": sum(c["input_tokens"] for c in llm),
                "cached_input_tokens": sum(c["cached_input_tokens"] for c in llm),
                "output_tokens": sum(c["output_tokens"] for c in llm),
                "reasoning_output_tokens": sum(c["reasoning_output_tokens"] for c in llm),
                "total_tokens": sum(c["input_tokens"] + c["output_tokens"] for c in llm),
            },
            "embedding_tokens": sum(c["input_tokens"] for c in embed),
            "resolved_model": next((c["model"] for c in llm if c.get("model")), None),
            "elapsed_seconds": round(time.perf_counter() - start, 4),
        }

    def search(self, question: str, top_k: int = DEFAULT_TOP_K) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        first_call = len(self.calls)
        start = time.perf_counter()
        response = self.memory.search(question, filters={"user_id": self.user_id}, top_k=top_k)
        results = response.get("results", []) if isinstance(response, dict) else list(response)
        hits = [
            {
                "memory": r.get("memory", ""),
                "session_date": (r.get("metadata") or {}).get("session_date"),
                "created_at": r.get("created_at"),
                "score": r.get("score"),
                "id": r.get("id"),
            }
            for r in results
        ]
        hits.sort(key=lambda r: (parse_timestamp(r.get("session_date") or "") or 0, r.get("created_at") or ""))
        embed = [c for c in self.calls[first_call:] if c["kind"] == "embedding"]
        return hits, {"embedding_tokens": sum(c["input_tokens"] for c in embed), "elapsed_seconds": round(time.perf_counter() - start, 4)}

    def all_memories(self) -> list[dict[str, Any]]:
        response = self.memory.get_all(filters={"user_id": self.user_id}, top_k=100_000)  # default page is 20
        results = response.get("results", []) if isinstance(response, dict) else list(response)
        return [
            {"memory": r.get("memory", ""), "session_date": (r.get("metadata") or {}).get("session_date"), "created_at": r.get("created_at"), "id": r.get("id")}
            for r in results
        ]

    def close(self) -> None:
        try:
            self.memory.db.close() if hasattr(self.memory.db, "close") else None
        except Exception:
            pass
        shutil.rmtree(self.workdir, ignore_errors=True)


def memory_date(entry: dict[str, Any]) -> str:
    return entry.get("session_date") or _human_date(entry.get("created_at"))


def render_retrieved(hits: list[dict[str, Any]]) -> str:
    return "\n".join(f"{memory_date(h)} | {h['memory']}" for h in hits) if hits else "(none retrieved)"


def build_answer_prompt(hits: list[dict[str, Any]], session_count: int, question_date: str, question: str) -> str:
    return ANSWER_PROMPT_FORMAT.format(
        question_date=question_date,
        count=len(hits),
        session_count=session_count,
        memories=render_retrieved(hits),
        question=question,
    )


def memory_lines(memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Final Mem0 memories in the run record's line shape so summaries and the bridge can show them."""
    return [{"kind": "mem0", "session": 0, "date": memory_date(m), "text": m["memory"], "id": m.get("id")} for m in memories]
