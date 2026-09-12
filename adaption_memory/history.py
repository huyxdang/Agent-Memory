from __future__ import annotations

import json
from typing import Any

from adaption_memory.benchmarks.base import BenchmarkItem
from adaption_memory.integrity import sha256_text


def sanitize_history(item: BenchmarkItem | dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(item, BenchmarkItem):
        return [
            {
                "timestamp": session.timestamp,
                "messages": [{"role": message.role, "content": message.content} for message in session.messages],
            }
            for session in item.sessions
        ]
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    session_ids = item["haystack_session_ids"]
    if not (len(dates) == len(sessions) == len(session_ids)):
        raise RuntimeError(f"History arrays have different lengths for {item['question_id']}.")
    clean = []
    for timestamp, session in zip(dates, sessions, strict=True):
        messages = []
        for message in session:
            role = message.get("role")
            content = message.get("content")
            if role not in {"user", "assistant"} or not isinstance(content, str):
                raise RuntimeError(f"Invalid history message in {item['question_id']}.")
            messages.append({"role": role, "content": content})
        clean.append({"timestamp": timestamp, "messages": messages})
    return clean


def history_sha256(item: BenchmarkItem | dict[str, Any]) -> str:
    history = sanitize_history(item)
    value = json.dumps(history, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256_text(value)
