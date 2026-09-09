"""Matched no-retrieval report; optionally include the first LongMemEval 50 and combined 100."""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

import longmemeval_eval as e

GROUPS = {
    "LoCoMo shared 50": {
        "Full history": ["20260908T192232760084Z_full-history_8cc5c91"],
        "Ours, no retrieval": ["20260908T190559396590Z_memory_6a360f8"],
        "Mem0, no retrieval": ["20260909T121234546331Z_mem0_1f69942"],
        "Mem0, retrieval (historical)": ["20260908T222244440761Z_mem0_388f915", "20260909T005041106821Z_mem0_e2ba6d1"],
    },
    "LongMemEval second 50": {
        "Full history": ["20260909T034523377052Z_full-history_707cb39"],
        "Ours, no retrieval": ["20260909T034510538614Z_memory_707cb39"],
        "Mem0, no retrieval": ["20260909T121243562166Z_mem0_1f69942", "20260909T121716575119Z_mem0_1f69942"],
        "Mem0, retrieval (historical)": ["20260909T092328675957Z_mem0_e911e4d"],
    },
}


def rows_for(run_ids):
    runs = [e.load_run(run_id) for run_id in run_ids]
    rows = {}
    for run in runs:
        counts = Counter(r["question_id"] for r in run["results"])
        assert all(n == 1 for n in counts.values()), "Duplicate question within run"
        for record in run["results"]:
            qid = record["question_id"]
            if qid in rows and rows[qid]["status"] == "success":
                assert record["status"] != "success", "Duplicate successful source"
                continue
            rows[qid] = record
    return runs, rows


def summarize(run_ids, rows):
    records = list(rows.values())
    calls = [r["answer_call"] for r in records if r.get("answer_call")]
    measured = [c for c in calls if c.get("usage", {}).get("input_tokens") is not None]
    writing = e.aggregate_calls([c for r in records for c in r.get("memory", {}).get("extraction_calls", [])])
    answers = e.aggregate_calls(calls)
    contexts = [r["context_tokens"] for r in records if r.get("context_tokens") is not None]
    return {
        "run_ids": run_ids,
        "questions": len(records),
        "success": sum(r["status"] == "success" for r in records),
        "correct": sum(r["status"] == "success" and r["judge_verdict"] == "yes" for r in records),
        "mean_answer_input_tokens": statistics.mean(c["usage"]["input_tokens"] for c in measured) if measured else None,
        "mean_context_tokens": statistics.mean(contexts) if contexts else None,
        "mean_answer_latency_seconds": statistics.mean(c["elapsed_seconds"] for c in measured) if measured else None,
        "measured_answer_count": len(measured),
        "writing_cost_usd": writing["cost_usd"],
        "answering_cost_usd": answers["cost_usd"],
        "writing_usage": writing,
        "answering_usage": answers,
        "failures": [{"question_id": r["question_id"], "status": r["status"]} for r in records if r["status"] != "success"],
    }


def comparison_groups(first_run=None):
    groups = dict(GROUPS)
    if first_run:
        first = {
            "Full history": ["20260908T192233799242Z_full-history_8cc5c91"],
            "Ours, no retrieval": ["20260908T182110999548Z_memory_b5424ef"],
            "Mem0, no retrieval": [first_run],
            "Mem0, retrieval (historical)": ["20260908T194854510380Z_mem0_ae03430", "20260908T222249129132Z_mem0_388f915", "20260908T222250256294Z_mem0_388f915"],
        }
        groups["LongMemEval first 50"] = first
        groups["LongMemEval combined 100"] = {label: ids + GROUPS["LongMemEval second 50"][label] for label, ids in first.items()}
    return groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--longmemeval-first-run", metavar="RUN_ID")
    args = parser.parse_args()
    groups = comparison_groups(args.longmemeval_first_run)
    output = {}
    text = ["# No-retrieval comparison", "", "All comparisons use the same question IDs and history hashes within each named cohort. First-50, second-50 and combined-100 results are separately labeled; do not add their costs together.", "",
            "Input = API-reported answering input, including instructions and question. Context = supplied history/memory block, counted with o200k_base. Latency = mean answer-call wall time, excluding writing and judging. Costs are totals for the named cohort, not per-question averages. Writing cost includes the original reused writing; it is not charged again. Judge costs are excluded from system costs.", ""]
    incremental = 0.0
    counted_runs = set()
    for name, group in groups.items():
        count = 100 if name == "LongMemEval combined 100" else 50
        output[name] = {}
        reference = None
        text += [f"## {name}", "", f"| System | Correct / {count} | Valid outputs | Avg answer input | Avg context | Answer latency | Writing cost | Answer cost |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for label, ids in group.items():
            runs, rows = rows_for(ids)
            if label == "Mem0, no retrieval":
                assert all(r["run_status"] in {"complete", "complete_with_failures"} for r in runs), "No final report while a rerun is still running"
            if reference is None:
                reference = rows
            assert len(rows) == count and set(rows) == set(reference), f"Unmatched IDs: {label}"
            assert all(rows[q]["history_sha256"] == reference[q]["history_sha256"] for q in rows), f"History mismatch: {label}"
            assert all(rows[q]["reference_answer"] == reference[q]["reference_answer"] for q in rows), f"Reference mismatch: {label}"
            result = summarize(ids, rows)
            output[name][label] = result
            text.append(f"| {label} | {result['correct']}/{count} | {result['success']}/{count} | {result['mean_answer_input_tokens']:,.0f} | {result['mean_context_tokens']:,.0f} | {result['mean_answer_latency_seconds']:.2f}s | ${result['writing_cost_usd']:.4f} | ${result['answering_cost_usd']:.4f} |")
            if label == "Mem0, no retrieval":
                assert all(r["metadata"]["mem0"]["context_policy"] == "all" for r in runs)
                for row in rows.values():
                    if row.get("answer_prompt"):
                        assert row["memory"]["retrieved"] is None
                        assert row["memory"]["supplied_memory_count"] == len(row["memory"]["lines"])
                for run in runs:
                    run_id = run["run"]["run_id"]
                    if run_id not in counted_runs:
                        incremental += run["costs"]["total_api_spend_usd"]
                        counted_runs.add(run_id)
                result["incremental_costs"] = [r["costs"] for r in runs]
                result["judge_controls"] = [[{key: case[key] for key in ("case_id", "expected", "actual", "agreement", "status")} for case in r["judge_validation"]] for r in runs]
            result["models"] = [r["metadata"]["models"] for r in runs]
        text += ["", "Historical retrieval is a separate ablation, not part of the no-retrieval comparison. Failures count as non-correct in the full cohort denominator; token and latency means use calls with measured usage.", ""]
        for label, result in output[name].items():
            if result["failures"]:
                text += [f"Failures for {label}: `{json.dumps(result['failures'])}`", ""]
    text += [f"New API spend across unique no-retrieval runs, including judges: **${incremental:.4f}**. Authorized ceiling: $15.", "", "## Provenance", ""]
    for name, group in groups.items():
        for label, ids in group.items():
            text.append(f"- {name}, {label}: " + ", ".join(f"`{i}`" for i in ids))
    text += ["", "Writing costs cover the retained stores; discarded failed ingestion attempts are not included in those cohort figures. Latencies are observed call times from different runs and concurrency settings, not a controlled speed benchmark. LoCoMo and second-50 cohort reruns use concurrency 3; the one-question recovery uses 1; the first-50 extension uses 8.", "", "The JSON companion contains usage details, model configuration, failures and judge-control outcomes. API billing for timed-out calls with no usage is unknown, not proven zero. Stored-memory token size does not include hidden reasoning; output usage does.", ""]
    destination = Path(__file__).resolve().parent / "docs"
    stem = "longmemeval-100-no-retrieval" if args.longmemeval_first_run else "no-retrieval-comparison"
    (destination / f"{stem}.json").write_text(json.dumps(output, indent=2) + "\n")
    (destination / f"{stem}.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
