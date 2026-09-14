"""Extraction-only Mem0 smoke: build a bounded slice of a preset's histories and report usage and cost.

A smoke never answers or judges questions and is never imported into a run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.execution import mem0
from adaption_memory.inference.openai import BudgetLedger
from adaption_memory.presets import load_preset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.mem0_smoke")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--histories", type=int, required=True)
    parser.add_argument("--updates", type=int, required=True)
    parser.add_argument("--budget-usd", type=float, required=True)
    args = parser.parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")
    preset = load_preset(args.spec)
    config = mem0.prepare(args.directory, preset, smoke_histories=args.histories, smoke_updates=args.updates)
    ledger = BudgetLedger(args.budget_usd)
    record = mem0.build(args.directory, preset, ledger)
    states = [json.loads(path.read_text()) for path in sorted((args.directory / "memories").glob("*.json"))]
    summary = {
        "scope": config["scope"],
        "histories": {s["history_sha256"][:8]: s["status"] for s in states},
        "sessions": [
            {k: call.get(k) for k in ("session", "status", "events", "llm_calls", "embedding_calls", "usage",
                                       "embedding_tokens", "cost_usd", "elapsed_seconds", "resolved_model", "error_type", "error")}
            for s in states for call in s["calls"]
        ],
        "lines": sum(len(s["lines"]) for s in states),
        "sample_lines": [f"{line['date']} | {line['text']}" for s in states for line in s["lines"][:5]],
        "known_spend_usd": record["known_spend_usd"],
        "unknown_or_reserved_exposure_usd": record["unknown_or_reserved_exposure_usd"],
    }
    print(json.dumps(summary, indent=2))
    return 0 if all(s["status"] in ("complete", "smoke_complete") for s in states) else 2


if __name__ == "__main__":
    raise SystemExit(main())
