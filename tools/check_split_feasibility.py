"""Offline LongMemEval dev reservation with overlapping train histories removed."""
import json
import random
from pathlib import Path

from adaption_memory import integrity as ev
from adaption_memory.provenance import git_metadata

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "work/training_trace_audit"
OUTPUT = ROOT / "work/longmemeval_split_feasibility"
SEED = 20260910


def purge(histories, dev_ids):
    dev_ids = set(dev_ids)
    sessions = {s for r in histories if r["history_sha256"] in dev_ids for s in r["session_hashes"]}
    train, dev, removed = [], [], []
    for row in histories:
        h = row["history_sha256"]
        if h in dev_ids:
            dev.append(h)
        elif sessions.intersection(row["session_hashes"]):
            removed.append(h)
        else:
            train.append(h)
    return {"train": train, "dev": dev, "removed": removed}


def measure(histories, split):
    by_id = {r["history_sha256"]: r for r in histories}
    return {**{f"{s}_histories": len(ids) for s, ids in split.items()},
            **{f"{s}_updates": sum(by_id[h]["updates"] for h in ids) for s, ids in split.items()}}


def main():
    paths = [AUDIT / n for n in ("histories.jsonl", "train_updates.jsonl", "dev_updates.jsonl")]
    histories = sorted([json.loads(l) for l in paths[0].read_text().splitlines()
                        if json.loads(l)["stratum"] == "longmemeval"], key=lambda r: r["history_sha256"])
    ids = [r["history_sha256"] for r in histories]
    assert len(ids) == len(set(ids)) and len(ids) >= 20
    fixed = purge(histories, random.Random(SEED).sample(ids, 20))
    sensitivity = []
    for k in (20, 10, 5, 2, 1):
        trials = []
        for seed in range(1000):
            split = purge(histories, random.Random(seed).sample(ids, k))
            trials.append(measure(histories, split)["train_updates"])
        sensitivity.append({"dev_histories": k, "trials": len(trials), "train_updates_min": min(trials),
            "train_updates_median": (sorted(trials)[499] + sorted(trials)[500]) / 2,
            "train_updates_max": max(trials), "trials_with_at_least_1000_updates": sum(n >= 1000 for n in trials)})
    updates = [json.loads(l) for p in paths[1:] for l in p.read_text().splitlines()]
    selected = {s: [r for r in updates if r["history_sha256"] in set(fixed[s])] for s in ("train", "dev")}
    metrics = measure(histories, fixed)
    smaller = purge(histories, random.Random(SEED).sample(ids, 10))
    smaller_metrics = measure(histories, smaller)
    for s, rows in selected.items():
        assert len(rows) == metrics[f"{s}_updates"]
        assert len({r["example_id"] for r in rows}) == len(rows)
    train_sessions = {s for r in histories if r["history_sha256"] in fixed["train"] for s in r["session_hashes"]}
    dev_sessions = {s for r in histories if r["history_sha256"] in fixed["dev"] for s in r["session_hashes"]}
    assert train_sessions.isdisjoint(dev_sessions)
    assert set(fixed["train"]) | set(fixed["dev"]) | set(fixed["removed"]) == set(ids)
    all_ids = [h for values in fixed.values() for h in values]
    assert len(all_ids) == len(set(all_ids))
    quality = {s: {"no_target_flags": sum(not r["quality_flags"] for r in rows),
        "no_target_or_prior_flags": sum(not r["quality_flags"] and not r["prior_memory_has_flags"] for r in rows)} for s, rows in selected.items()}
    report = {"status": "candidate_only_not_adopted", "seed": SEED, "fixed_candidate": metrics,
        "fixed_10_dev_candidate": {"metrics": smaller_metrics, "assignments": smaller},
        "input_sha256": {str(p.relative_to(ROOT)): ev.sha256_file(p) for p in paths},
        "script_sha256": ev.sha256_file(Path(__file__)), "code": git_metadata(Path(__file__)),
        "assignments": fixed, "quality": quality, "sensitivity": sensitivity,
        "cross_split_exact_session_overlap": len(train_sessions & dev_sessions),
        "notes": ["Fixed candidate uses the predeclared seed, not the best sensitivity-search result.",
                  "Sensitivity seeds 0..999 are diagnostics, not exhaustive bounds or accuracy-based selection.",
                  "Whole histories are retained or removed; no partial-session extraction chains are spliced.",
                  "Session hashes ignore dates; semantic near-duplicates and factual quality remain unreviewed.",
                  "Existing saved train/dev split is unchanged. No final evaluation set is reserved here.",
                  "Removed histories may overlap dev and must not be silently reused for training or final evaluation."]}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ev.atomic_json(OUTPUT / "report.json", report)
    for split, rows in selected.items():
        ev.atomic_jsonl(OUTPUT / f"candidate_{split}_updates.jsonl", rows)
        small_rows = [r for r in updates if r["history_sha256"] in set(smaller[split])]
        assert len(small_rows) == smaller_metrics[f"{split}_updates"]
        ev.atomic_jsonl(OUTPUT / f"candidate_10dev_{split}_updates.jsonl", small_rows)
    small_train_sessions = {s for r in histories if r["history_sha256"] in smaller["train"] for s in r["session_hashes"]}
    small_dev_sessions = {s for r in histories if r["history_sha256"] in smaller["dev"] for s in r["session_hashes"]}
    assert small_train_sessions.isdisjoint(small_dev_sessions)
    lines = ["# LongMemEval split feasibility", "", "Offline check; existing split unchanged. No paid calls.", "",
        f"Fixed seed: `{SEED}`. Reserve 20 dev histories, then remove every overlapping training history.", "",
        "| Assignment | Whole histories | Reconstructible updates |", "|---|---:|---:|"]
    for s in ("train", "dev", "removed"):
        lines.append(f"| {s} | {metrics[s + '_histories']} | {metrics[s + '_updates']} |")
    lines += ["", "Cross-split exact source-session overlap: **0**.", "",
              f"With the same fixed seed and 10 dev histories: {smaller_metrics['train_histories']} train histories / {smaller_metrics['train_updates']} updates; 10 dev histories / {smaller_metrics['dev_updates']} updates; {smaller_metrics['removed_histories']} histories removed. Exact session overlap is also zero.", "",
              "## Sensitivity, 1,000 seeds per dev size", "",
              "| Dev histories | Train updates min | Median | Max | Trials with at least 1,000 updates |",
              "|---:|---:|---:|---:|---:|"]
    for r in sensitivity:
        lines.append("| " + " | ".join(str(r[k]) for k in ("dev_histories", "train_updates_min", "train_updates_median", "train_updates_max", "trials_with_at_least_1000_updates")) + " |")
    lines += ["", "## Quality and limits", ""]
    for s, q in quality.items():
        lines.append(f"- {s}: {q['no_target_flags']} updates without target flags; {q['no_target_or_prior_flags']} without target or prior-memory flags. These are heuristic warnings, not factual labels.")
    lines += [f"- {n}" for n in report["notes"]]
    lines += ["", "A connected overlap graph does not forbid splitting if bridge histories can be discarded.",
        "The earlier train-only assignment preserved all histories; this candidate deliberately sacrifices some.", "",
        "Local candidate IDs and trace pointers: `work/longmemeval_split_feasibility/`.",
        "Reproduce: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python check_split_feasibility.py`.", ""]
    ev.atomic_text(OUTPUT / "summary.md", "\n".join(lines))
    print(json.dumps({"fixed": metrics, "fixed_10_dev": smaller_metrics, "quality": quality, "sensitivity": sensitivity}, indent=2))


if __name__ == "__main__":
    main()
