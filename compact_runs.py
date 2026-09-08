#!/usr/bin/env python3
"""Drop reconstructible memory messages from extraction calls in run records.

Each extraction call used to store every user message of its prompt. The memory
messages are a deterministic rendering of lines already in the store, so only the
session message needs keeping. Before dropping anything, the full prompt is rebuilt
from the store and its SHA-256 must equal the recorded prompt_sha256. Runs that fail
that check are left untouched and reported.

Usage: compact_runs.py [RUN_ID ...]   (default: every run under runs/)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import memory as memory_system

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compact_record(record: dict) -> tuple[int, int]:
    store = record.get("memory")
    if not store:
        return 0, 0
    lines = store.get("lines", [])
    converted = mismatched = 0
    for call in store.get("extraction_calls", []):
        parts = call.get("prompt_messages")
        if parts is None:
            if "prompt" in call and "session_message" not in call:  # earliest single-message format
                call["session_message"] = call.pop("prompt")
                call["memory_message_count"] = 0
                converted += 1
            continue
        session = call["session"]
        prior = [line for line in lines if line["session"] < session]
        rebuilt = memory_system.extraction_parts(prior, session, 0, "", [])[:-1] + [parts[-1]]
        if sha("\n\n".join(rebuilt)) != call.get("prompt_sha256"):
            mismatched += 1
            continue
        call["session_message"] = parts[-1]
        call["memory_message_count"] = len(parts) - 1
        del call["prompt_messages"]
        converted += 1
    return converted, mismatched


def compact_run(run_dir: Path) -> None:
    path = run_dir / "results.jsonl"
    if not path.exists():
        return
    before = path.stat().st_size
    records = [json.loads(line) for line in path.read_text().split("\n") if line.strip()]
    converted = mismatched = 0
    for record in records:
        c, m = compact_record(record)
        converted += c
        mismatched += m
    if converted:
        temporary = path.with_suffix(".jsonl.tmp")
        temporary.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
        temporary.replace(path)
    after = path.stat().st_size
    print(f"{run_dir.name}: {converted} calls compacted, {mismatched} hash mismatches left untouched, {before/1e6:.1f} MB -> {after/1e6:.1f} MB")


def main() -> int:
    targets = [RUNS / r for r in sys.argv[1:]] or sorted(p for p in RUNS.iterdir() if p.is_dir())
    for run_dir in targets:
        compact_run(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
