"""One line per run: phase, memories built, questions graded, correct so far, spend against cap, cache share,
idle time, and failed-call counts. Reads the run store and artifact files only; never takes the run lock.

    .venv/bin/python -m tools.status            # every run with a budget.json
    .venv/bin/python -m tools.status --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.evaluation.pipeline import Coordinator

PASS = {"beam": 0.5}


def newest_mtime(directory: Path) -> float:
    """Activity time from the few files a live run rewrites, not a walk of the whole directory."""
    latest = 0.0
    for name in ("current.json", "run.log", "resume.log", "modal/summary.json", "mem0/summary.json"):
        path = directory / name
        if path.exists():
            latest = max(latest, path.stat().st_mtime)
    return latest


FIELDS = ("spend_usd", "gpu_usd", "sessions_extracted", "cached", "answer_input", "not_dispatched", "unknown_outcome")


def calls(directory: Path) -> dict[str, Any]:
    """Artifacts are content-addressed and never rewritten, so only files newer than the last
    reading need parsing. Without this every poll re-reads tens of thousands of files."""
    cache_path = directory / ".status_cache.json"
    try:
        cache = json.loads(cache_path.read_text())
    except (OSError, ValueError):
        cache = {"read_through": 0.0, **{field: 0 for field in FIELDS}}
    spend, gpu = float(cache["spend_usd"]), float(cache["gpu_usd"])
    extracted, cached_tokens = int(cache["sessions_extracted"]), int(cache["cached"])
    answer_input = int(cache["answer_input"])
    failed = {"not_dispatched": int(cache["not_dispatched"]), "unknown_outcome": int(cache["unknown_outcome"])}
    read_through = float(cache["read_through"])
    newest = read_through
    for kind in ("call_state",):
        artifacts = directory / "artifacts" / kind
        if not artifacts.is_dir():
            continue
        for entry in os.scandir(artifacts):
            if not entry.name.endswith(".json"):
                continue
            modified = entry.stat().st_mtime
            if modified <= read_through:
                continue
            newest = max(newest, modified)
            try:
                payload = json.loads(Path(entry.path).read_text()).get("payload") or {}
            except (OSError, ValueError):
                continue
            if kind != "executor_call_state":
                spend += float(payload.get("cost_usd") or 0)
            state = payload.get("state")
            if state in failed:
                failed[state] += 1
            if ":extract:" in str(payload.get("call_id", "")) and state == "complete":
                extracted += 1
            if "answer" in str(payload.get("call_id", "")):
                usage = payload.get("usage") or {}
                answer_input += int(usage.get("input_tokens") or 0)
                cached_tokens += int(usage.get("cached_input_tokens") or 0)
    totals = {"spend_usd": spend, "gpu_usd": 0.0, "sessions_extracted": extracted,
              "cached": cached_tokens, "answer_input": answer_input, **failed}
    try:
        cache_path.write_text(json.dumps({"read_through": newest, **totals}))
    except OSError:
        pass
    return {"spend_usd": spend, "sessions_extracted": extracted,
            "cached_share": cached_tokens / answer_input if answer_input else None, **failed}


def modal_phase(directory: Path) -> dict[str, Any] | None:
    if not (directory / "configuration.json").is_file():
        return None
    payload = json.loads((directory / "configuration.json").read_text())["payload"]
    histories = len(payload["histories"])
    sessions = sum(len(row["history"]) for row in payload["histories"])
    states = [json.loads(path.read_text()) for path in (directory / "memories").glob("*.json")] if (directory / "memories").is_dir() else []
    complete = sum(state.get("status") == "complete" for state in states)
    sessions_done = sum(int(state.get("sessions_done") or 0) for state in states)
    cloud = json.loads((directory / "cloud.json").read_text()) if (directory / "cloud.json").is_file() else {}
    # cloud.json carries the executor's own final figure, so a resumed run is not charged twice.
    return {
        "histories": histories,
        "complete": complete,
        "sessions": sessions,
        "sessions_done": sessions_done,
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
    sessions_path = directory / ".sessions.json"
    try:
        sessions = int(json.loads(sessions_path.read_text())["sessions"])
    except (OSError, ValueError, KeyError):
        sessions = 0
        snapshot = next((a for a in loaded.manifest.artifacts if a.kind == "dataset_snapshot"), None)
        if snapshot is not None:
            seen = set()
            for item, row in zip(Coordinator(runs).store.read_artifact(run_id, snapshot)["items"], rows):
                if row.get("history_sha256") not in seen:
                    seen.add(row.get("history_sha256"))
                    sessions += len(item.get("haystack_sessions") or item.get("sessions") or ())
        try:
            sessions_path.write_text(json.dumps({"sessions": sessions}))
        except OSError:
            pass
    blocked = sum(row.get("status") == "blocked_memory" for row in rows)
    result = {
        "run_id": run_id,
        "status": loaded.manifest.status.value,
        "questions": len(rows),
        "graded": len(graded),
        "correct": sum(score(row) >= threshold for row in graded),
        "histories": len(histories),
        "memories_built": len(built),
        "sessions": sessions,
        "blocked_histories": blocked,
        "cap_usd": budget.get("budget_usd"),
        "modal_cap_usd": budget.get("modal_budget_usd"),
        "idle_seconds": max(0, int(time.time() - newest_mtime(directory))) if directory.exists() else None,
        "gpu_usd": 0.0,
        **calls(directory),
    }
    modal = modal_phase(directory / "modal")
    if modal:
        result["modal"] = modal
        result["gpu_usd"] = float(modal.get("accounted_usd") or 0)
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
    if modal and phase.startswith("modal"):
        mem = f"mem {bar(modal['sessions_done'], modal['sessions'], 10)} {modal['sessions_done']:>3}/{modal['sessions']:<3}s"
    elif phase.startswith("extract") and row.get("sessions"):
        mem = f"mem {bar(row['sessions_extracted'], row['sessions'], 10)} {row['sessions_extracted']:>3}/{row['sessions']:<3}s"
    else:
        mem = f"mem {bar(built, row['histories'], 10)} {built:>2}/{row['histories']:<2}  "
    return (
        f"{row['run_id']:<26} {phase:<22} {mem} "
        f"graded {bar(row['graded'], row['questions'])} {row['graded']:>3}/{row['questions']:<3} "
        f"correct {row['correct'] / row['graded'] * 100 if row['graded'] else 0:5.1f}% ({row['correct']:>3})  api ${row['spend_usd']:.2f}{cap:<6}" + (f" gpu ${row['gpu_usd']:.2f}" if row["gpu_usd"] else "        ") + f" cache {cached:>4} idle {idle:>6} "
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
