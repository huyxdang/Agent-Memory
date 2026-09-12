from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from adaption_memory.benchmarks.beam import WEIGHTS as BEAM_WEIGHTS
from adaption_memory.benchmarks.locomo import WEIGHTS as LOCOMO_WEIGHTS
from adaption_memory.integrity import atomic_json, atomic_text

from .accounting import aggregate_call_dicts
from .checkpoints import RunStore


def report_data(store: RunStore, run_id: str) -> dict[str, Any]:
    loaded = store.load(run_id)
    statuses = Counter(str(row.get("status", "unknown")) for row in loaded.results)
    scores = [row.get("score") for row in loaded.results if isinstance(row.get("score"), (int, float))]
    by_type: dict[str, list[float]] = {}
    for row in loaded.results:
        if isinstance(row.get("score"), (int, float)):
            by_type.setdefault(str(row.get("question_type", "unknown")), []).append(float(row["score"]))
    type_scores = {
        name: {"questions": len(values), "mean_score": sum(values) / len(values)}
        for name, values in sorted(by_type.items())
    }

    specification = next(artifact for artifact in loaded.manifest.artifacts if artifact.kind == "experiment_spec")
    benchmark = str(store.read_artifact(run_id, specification)["benchmark"])
    weights = {"locomo": LOCOMO_WEIGHTS, "beam": BEAM_WEIGHTS}.get(benchmark)
    weighted_score = None
    if weights and type_scores:
        represented = {name: weight for name, weight in weights.items() if name in type_scores}
        if represented:
            weighted_score = sum(type_scores[name]["mean_score"] * weight for name, weight in represented.items()) / sum(represented.values())

    latest_calls: dict[str, dict[str, Any]] = {}
    for artifact in loaded.manifest.artifacts:
        if artifact.kind not in {"call_state", "executor_call_state"}:
            continue
        call = store.read_artifact(run_id, artifact)
        call_id = call.get("call_id")
        if call_id:
            latest_calls[str(call_id)] = call
    accounting = aggregate_call_dicts(latest_calls.values())
    return {
        "schema_version": 1,
        "run_id": run_id,
        "generation": loaded.generation,
        "status": loaded.manifest.status.value,
        "benchmark": benchmark,
        "questions": len(loaded.manifest.question_ids),
        "result_statuses": dict(sorted(statuses.items())),
        "mean_score": sum(scores) / len(scores) if scores else None,
        "weighted_score": weighted_score,
        "scores_by_question_type": type_scores,
        "scored_questions": len(scores),
        "coverage": len(scores) / len(loaded.manifest.question_ids) if loaded.manifest.question_ids else 0.0,
        "score_scope": "full_selection" if len(scores) == len(loaded.manifest.question_ids) else "scored_subset_only",
        "accounting": accounting,
        "cost_bases": sorted({str(call["accounting_basis"]) for call in latest_calls.values()
            if call.get("accounting_basis")}),
        "artifact_sha256": [artifact.sha256 for artifact in loaded.manifest.artifacts],
    }


def write_report(store: RunStore, run_id: str, destination: Path) -> dict[str, Any]:
    data = report_data(store, run_id)
    destination.mkdir(parents=True, exist_ok=True)
    atomic_json(destination / "report.json", data)
    mean = "unavailable" if data["mean_score"] is None else f"{data['mean_score']:.4f}"
    weighted = "unavailable" if data["weighted_score"] is None else f"{data['weighted_score']:.4f}"
    accounting = data["accounting"]
    lines = [
        f"# Experiment {run_id}",
        "",
        f"- Status: `{data['status']}`",
        f"- Benchmark: `{data['benchmark']}`",
        f"- Questions: {data['questions']}",
        f"- Scored questions: {data['scored_questions']}",
        f"- Coverage: {data['coverage']:.1%}; score scope: {data['score_scope']}",
        f"- Mean score: {mean}",
        f"- Benchmark-weighted score: {weighted}",
        f"- Accounted spend (may include conservative bounds): ${accounting['known_spend_usd']:.8f}",
        f"- Recorded cost bases: {', '.join(data['cost_bases']) or 'not specified'}",
        f"- Unknown or reserved exposure: ${accounting['unknown_or_reserved_exposure_usd']:.8f}",
        f"- Validated generation: `{data['generation']}`",
        "",
        "Result statuses:",
        "",
        *[f"- `{name}`: {count}" for name, count in data["result_statuses"].items()],
        "",
        "Scores by question type:",
        "",
        *[
            f"- `{name}`: {summary['mean_score']:.4f} ({summary['questions']} scored)"
            for name, summary in data["scores_by_question_type"].items()
        ],
    ]
    atomic_text(destination / "report.md", "\n".join(lines) + "\n")
    return data
