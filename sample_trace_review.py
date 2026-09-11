"""Prepare a fixed training-only diagnostic sample; no API calls or grading labels."""
import json
from collections import Counter
from pathlib import Path
import longmemeval_eval as ev

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "work/longmemeval_split_feasibility/candidate_10dev_train_updates.jsonl"
OUTPUT = ROOT / "work/trace_quality_review"
SEED = "trace-quality-review-v1-20260910"


def category(row):
    flags = row["quality_flags"]
    if any(f in ("chain_tail_mismatch", "duplicate_of_previous") for f in flags):
        return "memory_update"
    if any(f.startswith("anchor_not_in_session") for f in flags):
        return "date_number"
    return "value" if flags else "unflagged"


def main():
    rows = [json.loads(l) for l in INPUT.read_text().splitlines()]
    selected, used = [], set()
    for bucket in ("memory_update", "date_number", "value", "unflagged"):
        pool = sorted((r for r in rows if category(r) == bucket),
                      key=lambda r: ev.sha256_text(SEED + r["example_id"]))
        chosen = []
        for row in pool:
            if row["history_sha256"] not in used:
                chosen.append(row)
                used.add(row["history_sha256"])
            if len(chosen) == 2:
                break
        if len(chosen) != 2:
            raise ValueError(f"Not enough distinct histories in {bucket}")
        selected.extend({**r, "sample_category": bucket} for r in chosen)
    packets = []
    for i, pointer in enumerate(selected, 1):
        path = ROOT / "runs" / pointer["run_id"] / "results.jsonl"
        with path.open() as source:
            record = next(json.loads(line) for n, line in enumerate(source, 1) if n == pointer["results_line"])
        assert record["history_sha256"] == pointer["history_sha256"]
        call = next(c for c in record["memory"]["extraction_calls"] if c["session"] == pointer["session"])
        assert ev.sha256_text(call["content"]) == pointer["target_sha256"]
        assert call["prompt_sha256"] == pointer["prompt_sha256"]
        target = json.loads(call["content"])
        keys = {a["key"] for a in target["atomic"]}
        prior = [line for line in record["memory"]["lines"] if line["session"] < pointer["session"] and line.get("key") in keys]
        packets.append({"review_id": f"R{i:02}", "pointer": pointer, "session": call["session_message"],
                        "target": target, "prior_same_key_lines": prior})
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ev.atomic_json(OUTPUT / "sample.json", {"seed": SEED, "input_sha256": ev.sha256_file(INPUT),
        "script_sha256": ev.sha256_file(Path(__file__)), "population": dict(Counter(category(r) for r in rows)),
        "selection": "Two per warning stratum, eight different training histories; diagnostic, not prevalence estimate",
        "packets": packets})
    for packet in packets:
        ev.atomic_json(OUTPUT / f"{packet['review_id']}.json", packet)
    print(json.dumps({"population": dict(Counter(category(r) for r in rows)),
                      "selected": [(p["review_id"], p["pointer"]["sample_category"], len(p["session"])) for p in packets]}))


if __name__ == "__main__":
    main()
