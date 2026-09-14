"""Roll back a Mem0 history's interrupted session so a resume re-ingests it without duplicates.

When the process died or the provider became unreachable mid-session, some of that
session's adds may already be in the store. Deleting every memory created after the
last completed session, dropping the in-flight call record, and noting the rollback in
the checkpoint's warnings lets `run`/`resume` re-add the whole session cleanly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.execution import mem0
from adaption_memory.execution.files import save
from adaption_memory.inference.openai import BudgetLedger, Price


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.mem0_rollback_partial_session")
    parser.add_argument("--runs", type=Path, default=PROJECT_ROOT / "runs")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")  # Mem0 constructs OpenAI clients at open; nothing here calls them
    directory = args.runs / args.run_id / "mem0"
    payload = json.loads((directory / "payload.json").read_text())
    touched = 0
    for path in sorted((directory / "memories").glob("*.json")):
        state = json.loads(path.read_text())
        if state["status"] != "running" or not state["calls"] or state["calls"][-1]["status"] != "in_flight":
            continue
        key = state["history_sha256"]
        inflight = state["calls"][-1]
        complete = [c for c in state["calls"] if c["status"] == "complete"]
        cutoff = complete[-1]["finished_at"] if complete else ""
        meter = mem0.Meter(BudgetLedger(1.0), Price(0, 0, 0), 1, "rollback")
        store = mem0.Mem0Store(directory / "stores" / key, f"h_{key[:16]}", payload["llm"]["model"], meter)
        try:
            partial = [m for m in store.all_memories() if (m.get("created_at") or "") > cutoff]
            print(f"{key[:8]}: session {inflight['session']} in flight, {len(partial)} partial memories after {cutoff}")
            if args.apply:
                for memory in partial:
                    store.memory.delete(memory["id"])
                remaining = [m for m in store.all_memories() if (m.get("created_at") or "") > cutoff]
                if remaining:
                    raise RuntimeError(f"{len(remaining)} partial memories survived deletion")
        finally:
            store.close()
        if args.apply:
            state["calls"].pop()
            state["warnings"].append({
                "session": inflight["session"], "event": "partial_session_rolled_back",
                "deleted_memories": len(partial), "in_flight_started_at": inflight.get("started_at"), "reason": args.reason,
            })
            save(path, state)
            touched += 1
    print("applied to", touched, "histories" if args.apply else "histories (dry run; pass --apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
