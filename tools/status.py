"""One line per run: phase, memories built, questions graded, correct so far, spend against cap, cache share,
idle time, and failed-call counts. Reads the run store and artifact files only; never takes the run lock.

    .venv/bin/python -m tools.status            # every run with a budget.json
    .venv/bin/python -m tools.status --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.evaluation.pipeline import Coordinator

PASS = {"beam": 0.5}


def newest_mtime(directory: Path) -> float:
    latest = 0.0
    for path in directory.rglob("*"):
        if path.is_file():
            latest = max(latest, path.stat().st_mtime)
    return latest


def calls(directory: Path) -> dict[str, Any]:
    spend = 0.0
    gpu = 0.0
    cached = 0
    answer_input = 0
    failed = {"not_dispatched": 0, "unknown_outcome": 0}
    for kind in ("call_state", "executor_call_state"):
        for path in (directory / "artifacts" / kind).glob("*.json"):
            try:
                payload = json.loads(path.read_text()).get("payload") or {}
            except (OSError, ValueError):
                continue
            if kind == "executor_call_state":
                gpu += float(payload.get("cost_usd") or 0)
            else:
                spend += float(payload.get("cost_usd") or 0)
            state = payload.get("state")
            if state in failed:
                failed[state] += 1
            if "answer" in str(payload.get("call_id", "")):
                usage = payload.get("usage") or {}
                answer_input += int(usage.get("input_tokens") or 0)
                cached += int(usage.get("cached_input_tokens") or 0)
    return {"spend_usd": spend, "gpu_usd": gpu, "cached_share": cached / answer_input if answer_input else None, **failed}


def modal_phase(directory: Path) -> dict[str, Any] | None:
    if not (directory / "configuration.json").is_file():
        return None
    histories = len(json.loads((directory / "configuration.json").read_text())["payload"]["histories"])
    complete = sum(
        json.loads(path.read_text()).get("status") == "complete"
        for path in (directory / "memories").glob("*.json")
    ) if (directory / "memories").is_dir() else 0
    cloud = json.loads((directory / "cloud.json").read_text()) if (directory / "cloud.json").is_file() else {}
    return {
        "histories": histories,
        "complete": complete,
        "engine_loaded": (directory / "loaded.json").is_file(),
        "sandbox": cloud.get("status"),
        "accounted_usd": cloud.get("accounted_usd"),
    }


def status(runs: Path, run_id: str) -> dict[str, Any]:
    directory = runs / run_id
    budget = json.loads((directory / "budget.json").read_text())
    benchmark = budget.get("benchmark", "")
    threshold = PASS.get(benchmark, 1.0)
    loaded = Coordinator(runs).store.load(run_id)
    rows = loaded.results
    graded = [row for row in rows if row.get("status") == "success"]
    def score(row: dict[str, Any]) -> float:
        try:
            return float(row.get("score"))
        except (TypeError, ValueError):
            return 0.0
    histories = {row.get("history_sha256") for row in rows}
    built = {row.get("history_sha256") for row in rows if row.get("memory_sha256")}
    blocked = sum(row.get("status") == "blocked_memory" for row in rows)
    result = {
        "run_id": run_id,
        "status": loaded.manifest.status.value,
        "questions": len(rows),
        "graded": len(graded),
        "correct": sum(score(row) >= threshold for row in graded),
        "histories": len(histories),
        "memories_built": len(built),
        "blocked_histories": blocked,
        "cap_usd": budget.get("budget_usd"),
        "modal_cap_usd": budget.get("modal_budget_usd"),
        "idle_seconds": int(time.time() - newest_mtime(directory)) if directory.exists() else None,
        **calls(directory),
    }
    modal = modal_phase(directory / "modal")
    if modal:
        result["modal"] = modal
    return result


def bar(done: int, total: int, width: int = 20) -> str:
    filled = int(width * done / total) if total else 0
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def line(row: dict[str, Any]) -> str:
    modal = row.get("modal")
    if row["status"] in {"complete", "complete_with_failures", "blocked"}:
        phase = row["status"]
    elif modal and modal["complete"] < modal["histories"]:
        phase = f"modal {modal['complete']}/{modal['histories']} " + ("engine up" if modal["engine_loaded"] else "booting")
    elif row["memories_built"] < row["histories"]:
        phase = f"extract {row['memories_built']}/{row['histories']}"
    else:
        phase = "grading"
    cached = "-" if row["cached_share"] is None else f"{row['cached_share'] * 100:.0f}%"
    cap = f"/{row['cap_usd']:.2f}" if row.get("cap_usd") else ""
    idle = "-" if row["idle_seconds"] is None else f"{row['idle_seconds'] // 60}m{row['idle_seconds'] % 60:02d}s"
    modal_built = modal["complete"] if modal else 0
    built = max(row["memories_built"], modal_built)
    return (
        f"{row['run_id']:<26} {phase:<22} mem {bar(built, row['histories'], 10)} {built:>2}/{row['histories']:<2} "
        f"graded {bar(row['graded'], row['questions'])} {row['graded']:>3}/{row['questions']:<3} "
        f"correct {row['correct']:>3}  api ${row['spend_usd']:.2f}{cap:<6}" + (f" gpu ${row['gpu_usd']:.2f}" if row["gpu_usd"] else "        ") + f" cache {cached:>4} idle {idle:>6} "
        f"nd {row['not_dispatched']} uo {row['unknown_outcome']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.status")
    parser.add_argument("--runs", type=Path, default=PROJECT_ROOT / "runs")
    parser.add_argument("run_ids", nargs="*")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    run_ids = args.run_ids or sorted(path.parent.name for path in args.runs.glob("*/budget.json"))
    rows = [status(args.runs, run_id) for run_id in run_ids]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        for row in rows:
            print(line(row))
        print(f"total api ${sum(row['spend_usd'] for row in rows):.2f}  gpu ${sum(row['gpu_usd'] for row in rows):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
