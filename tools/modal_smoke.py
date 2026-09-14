"""Extraction-only throughput smoke on Modal: prepare, launch, and collect one bounded workload.

A smoke never answers or judges questions. It measures updates per second, per-call latency,
and accounted GPU cost for a frozen preset on a chosen GPU, so a full run can be sized first.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from adaption_memory.execution import modal
from adaption_memory.presets import load_preset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.modal_smoke")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--gpu", required=True)
    parser.add_argument("--histories", type=int, required=True)
    parser.add_argument("--updates", type=int, required=True)
    parser.add_argument("--modal-budget-usd", type=float)
    parser.add_argument("--collect", action="store_true", help="Watch the launched sandbox until it stops")
    args = parser.parse_args(argv)
    preset = load_preset(args.spec)
    config = modal.prepare(
        args.directory, preset, gpu=args.gpu, smoke_histories=args.histories, smoke_updates=args.updates
    )
    payload = config["payload"]
    print(json.dumps({
        "scope": config["scope"], "gpu": payload["gpu"], "concurrency": payload["concurrency"],
        "histories": len(payload["histories"]), "updates_per_history": payload["updates_per_history"],
        "fingerprint": payload["fingerprint"],
    }, indent=2))
    if args.modal_budget_usd is not None and not (args.directory / "cloud.json").exists():
        print(json.dumps(modal.launch(args.directory, args.modal_budget_usd), indent=2))
    if args.collect:
        summary = modal.collect(args.directory, watch=True)
        states = [json.loads(p.read_text()) for p in (args.directory / "memories").glob("*.json")]
        summary["smoke_complete"] = (
            len(states) == len(payload["histories"])
            and all(s["status"] in ("complete", "smoke_complete") for s in states)
        )
        print(json.dumps(summary, indent=2))
        return 0 if summary["smoke_complete"] else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
