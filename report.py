#!/usr/bin/env python3
"""Compare runs: per-type accuracy, tokens, cost. Usage: report.py RUN_ID [RUN_ID ...]"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"
TYPES = [
    "single-session-user", "single-session-assistant", "single-session-preference",
    "multi-session", "temporal-reasoning", "knowledge-update",
]
BENCHMARK_WEIGHTS = {  # LongMemEval-S question counts per type
    "single-session-user": 70, "single-session-assistant": 56, "single-session-preference": 30,
    "multi-session": 133, "temporal-reasoning": 133, "knowledge-update": 78,
}


def load(run_id: str) -> tuple[dict, list[dict]]:
    manifest = json.loads((RUNS / run_id / "manifest.json").read_text())
    records = [json.loads(line) for line in (RUNS / run_id / "results.jsonl").read_text().split("\n") if line.strip()]
    return manifest, records


def summarize(run_id: str) -> dict:
    manifest, records = load(run_id)
    by_type: dict[str, list[bool]] = defaultdict(list)
    for record in records:
        by_type[record["question_type"]].append(record["judge_verdict"] == "yes")
    per_type = {t: (sum(v), len(v)) for t, v in by_type.items()}
    weighted_num = sum(BENCHMARK_WEIGHTS[t] * (c / n) for t, (c, n) in per_type.items() if n)
    weighted_den = sum(BENCHMARK_WEIGHTS[t] for t, (c, n) in per_type.items() if n)
    costs = manifest["costs"]
    metrics = manifest["metrics"]
    return {
        "run_id": run_id,
        "system": manifest["system"],
        "status": manifest["status"],
        "correct": sum(r["judge_verdict"] == "yes" for r in records),
        "total": len(records),
        "per_type": per_type,
        "weighted": weighted_num / weighted_den if weighted_den else None,
        "context_tokens": metrics["context_tokens"]["total_across_questions"],
        "memory_writing_usd": costs["memory_writing_usd"],
        "answering_usd": costs["answering_usd"],
        "total_usd": costs["total_api_spend_usd"],
        "failures": [f for f in manifest["accounting_audit"]["failures"] if f["status"] != "success"],
        "misses": [r["question_id"] for r in records if r["judge_verdict"] != "yes"],
    }


def main() -> int:
    summaries = [summarize(run_id) for run_id in sys.argv[1:]]
    if not summaries:
        print(__doc__)
        return 1
    width = max(len(s["run_id"]) for s in summaries)
    print(f"{'run':{width}}  system        score    mean   weighted  ctx tokens  write$   answer$  total$")
    for s in summaries:
        mean = s["correct"] / s["total"] if s["total"] else 0
        weighted = f"{s['weighted']:.3f}" if s["weighted"] is not None else "-"
        print(
            f"{s['run_id']:{width}}  {s['system']:12}  {s['correct']:2d}/{s['total']:<3d}  {mean:.3f}  {weighted:>8}  "
            f"{s['context_tokens']:>10,}  {s['memory_writing_usd']:6.3f}  {s['answering_usd']:7.3f}  {s['total_usd']:6.3f}"
        )
    print()
    print(f"{'type':28}" + "".join(f"{s['system'][:12]:>14}" for s in summaries))
    for t in TYPES:
        cells = []
        for s in summaries:
            c, n = s["per_type"].get(t, (0, 0))
            cells.append(f"{c}/{n} ({c/n:.2f})" if n else "-")
        print(f"{t:28}" + "".join(f"{cell:>14}" for cell in cells))
    for s in summaries:
        if s["failures"]:
            print(f"\n{s['run_id']} non-success records: {[(f['question_id'], f['status']) for f in s['failures']]}")
        print(f"{s['run_id']} misses: {s['misses']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
