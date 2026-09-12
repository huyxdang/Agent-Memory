"""Offline trace inventory and leakage-aware whole-history split. Never calls an API."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from adaption_memory.benchmarks.base import USER_SUBJECT
from adaption_memory.benchmarks.registry import load_records, source_files
from adaption_memory import integrity as ev
from adaption_memory import memory
from adaption_memory.history import sanitize_history
from adaption_memory.provenance import git_metadata

ROOT = Path(__file__).resolve().parent.parent


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def source_catalog():
    catalog = {}
    files = [ROOT / "work/longmemeval_s_cleaned.json"] + source_files("locomo") + source_files("beam")
    datasets = [("longmemeval", json.loads(files[0].read_text())),
                ("locomo", load_records("locomo")), ("beam", load_records("beam"))]
    for benchmark, items in datasets:
        for item in items:
            history = sanitize_history(item)
            h = digest(history)
            if benchmark == "beam":
                scale = re.match(r"beam([^_]+)_", item["question_id"])[1]
                stratum = f"BEAM {scale}"
                family = f"beam:{item['conversation']}"  # keep scale variants together
            else:
                stratum = benchmark
                family = f"locomo:{item['conversation']}" if benchmark == "locomo" else h
            entry = catalog.setdefault(h, {"stratum": stratum, "family": family, "question_ids": [],
                "sessions": len(history), "session_hashes": sorted({digest(s["messages"]) for s in history})})
            entry["question_ids"].append(item["question_id"])
    return catalog, {str(f.relative_to(ROOT)): ev.sha256_file(f) for f in sorted(set(files))}


def reconstruct(record, prompts):
    """Validate every saved update against its original prompt hash and appended lines."""
    store = record["memory"]
    count = record["history"]["sessions"]
    if store.get("sessions_done") != count:
        raise ValueError("incomplete_history")
    calls = store.get("extraction_calls", [])
    if len(calls) != count:
        raise ValueError("missing_or_retried_calls")
    formats = prompts.get("extraction_message_formats")
    if not formats:
        raise ValueError("missing_message_formats")
    system = prompts.get("extraction_system")
    if not system:
        system = prompts["extraction_system_template"].format(subject=store.get("subject") or USER_SUBJECT)
    lines = store["lines"]
    history, updates = [], []
    flags = defaultdict(list)
    for failure in store.get("failures", []):
        flags[failure["session"]].extend(failure.get("codes", []))
    for n, call in enumerate(calls, 1):
        if call.get("session") != n or not call.get("ok") or call.get("finish_reason") != "stop":
            raise ValueError("failed_or_incomplete_output")
        session = call.get("session_message", "")
        match = re.fullmatch(r"New session (\d+) of (\d+), dated (.*?)\. Turns \(JSON\):\n(.*)", session, re.S)
        if not match or int(match[1]) != n or int(match[2]) != count:
            raise ValueError("unrecoverable_session_message")
        timestamp, messages = match[3], json.loads(match[4])
        if formats["session"].format(session_number=n, session_count=count, timestamp=timestamp,
                                    session=json.dumps(messages, ensure_ascii=False, separators=(",", ":"))) != session:
            raise ValueError("session_format_mismatch")
        history.append({"timestamp": timestamp, "messages": messages})
        earlier = defaultdict(list)
        for line in lines:
            if line["session"] < n:
                earlier[line["session"]].append(line)
        parts = [formats["memory"].format(session_number=i, timestamp=group[0]["date"],
                    lines="\n".join(memory.line_text(line) for line in group)) for i, group in sorted(earlier.items())]
        parts = (parts or [formats["empty_memory"]]) + [session]
        if ev.sha256_text("\n\n".join(parts)) != call.get("prompt_sha256"):
            raise ValueError("prompt_hash_mismatch")
        if call.get("memory_message_count") != len(parts) - 1:
            raise ValueError("message_count_mismatch")
        data = memory.parse_extraction(call["content"])
        expected = []
        for text in data["narrative"]:
            if text.strip():
                expected.append({"kind": "narrative", "session": n, "date": timestamp, "text": text.strip()})
        for atom in data["atomic"]:
            key, value = atom["key"].strip(), atom["value"].strip()
            if key and value:
                expected.append({"kind": "atomic", "session": n, "date": timestamp, "key": key, "value": value})
        actual = [{k: v for k, v in line.items() if k != "flags"} for line in lines if line["session"] == n]
        if actual != expected or call.get("new_lines") != len(expected):
            raise ValueError("target_store_mismatch")
        updates.append({"session": n, "prompt_sha256": call["prompt_sha256"],
            "target_sha256": ev.sha256_text(call["content"]), "quality_flags": sorted(set(flags[n])),
            "prior_memory_has_flags": any(i < n and codes for i, codes in flags.items()),
            "resolved_model": call.get("resolved_model")})
    if digest(history) != record["history_sha256"]:
        raise ValueError("history_hash_mismatch")
    return updates, digest({"system": system, "formats": formats, "response_format": prompts.get("extraction_response_format")})


def split_histories(histories, catalog, seed):
    parent = {h: h for h in histories}
    def root(h):
        while parent[h] != h:
            parent[h] = parent[parent[h]]
            h = parent[h]
        return h
    seen = {}
    for h in sorted(histories):
        keys = [("family", catalog[h]["family"])] + [("session", s) for s in catalog[h]["session_hashes"]]
        for key in keys:
            if key in seen:
                a, b = sorted((root(h), root(seen[key])))
                parent[b] = a
            seen[key] = h
    groups = defaultdict(list)
    for h in sorted(histories):
        groups[root(h)].append(h)
    strata = defaultdict(list)
    for hs in groups.values():
        strata[tuple(sorted({catalog[h]["stratum"] for h in hs}))].append(hs)
    assignments, components = {}, []
    for stratum, gs in sorted(strata.items()):
        gs.sort(key=lambda hs: digest([seed, hs]))
        # With one connected component a train/dev split would leak. Keep it in train.
        dev_count = max(1, round(len(gs) * .2)) if len(gs) > 1 else 0
        for i, hs in enumerate(gs):
            split = "dev" if i < dev_count else "train"
            group_id = digest(hs)
            components.append({"group_id": group_id, "strata": list(stratum), "histories": hs, "split": split})
            for h in hs:
                assignments[h] = (split, group_id)
    return assignments, components


def audit(output, seed):
    catalog, source_hashes = source_catalog()
    occurrences, runs, issues, candidates = [], [], [], defaultdict(list)
    for path in sorted((ROOT / "runs").glob("*/manifest.json")):
        manifest = json.loads(path.read_text())
        if manifest.get("system") != "memory":
            continue
        rid = path.parent.name
        results = path.parent / "results.jsonl"
        runs.append({"run_id": rid, "status": manifest["status"], "manifest_sha256": ev.sha256_file(path),
                     "results_sha256": ev.sha256_file(results) if results.exists() else None})
        if not results.exists():
            issues.append({"run_id": rid, "reason": "missing_results"})
            continue
        for index, raw in enumerate(results.open(), 1):
            record = json.loads(raw)
            store = record.get("memory") or {}
            calls = store.get("extraction_calls", [])
            if not calls:
                continue
            h = record["history_sha256"]
            row = {"run_id": rid, "question_id": record["question_id"], "results_line": index,
                   "history_sha256": h, "calls": len(calls), "sessions_done": store.get("sessions_done"),
                   "row_sha256": ev.sha256_text(raw.rstrip("\n")), "reason": None,
                   "extraction_config": {k: v for k, v in manifest["metadata"]["models"].items() if k.startswith("extraction_")}}
            occurrences.append(row)
            if h not in catalog:
                row["reason"] = "not_full_benchmark_source_history"
                continue
            row["stratum"] = catalog[h]["stratum"]
            if store.get("reused_from_run"):
                row["reason"] = "reused_copy"
                continue
            try:
                updates, prompt_version = reconstruct(record, manifest["metadata"]["prompts"])
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                row["reason"] = str(exc)
                continue
            row.update(updates=len(updates), prompt_version=prompt_version,
                       flagged_updates=sum(bool(u["quality_flags"]) for u in updates))
            candidates[h].append((row, updates))
    # No grading/accuracy filter: latest fully reconstructible trajectory, then stable question ID.
    canonical = {}
    for h, variants in candidates.items():
        newest = max(row["run_id"] for row, _ in variants)
        canonical[h] = min((v for v in variants if v[0]["run_id"] == newest), key=lambda v: v[0]["question_id"])
    assignments, components = split_histories(canonical, catalog, seed)
    inventories, update_rows = [], {"train": [], "dev": []}
    for h in sorted(canonical):
        row, updates = canonical[h]
        split, group = assignments[h]
        source = catalog[h]
        inventories.append({**row, "split": split, "leakage_group_id": group,
            "source_family": source["family"], "source_question_ids": source["question_ids"],
            "session_hashes": source["session_hashes"], "reconstructible_variants": len(candidates[h])})
        for update in updates:
            update_rows[split].append({"example_id": digest([h, row["run_id"], row["question_id"], update["session"]]),
                "history_sha256": h, "leakage_group_id": group, "run_id": row["run_id"],
                "question_id": row["question_id"], "results_line": row["results_line"], **update})
    session_sets = {s: {k for h in canonical if assignments[h][0] == s for k in catalog[h]["session_hashes"]} for s in ("train", "dev")}
    assert not (session_sets["train"] & session_sets["dev"])
    assert len(inventories) == len({r["history_sha256"] for r in inventories})
    summary = []
    for stratum in sorted({r["stratum"] for r in inventories}):
        rs = [r for r in inventories if r["stratum"] == stratum]
        summary.append({"benchmark": stratum, "unique_histories": len(rs),
            **{f"{s}_histories": sum(r["split"] == s for r in rs) for s in ("train", "dev")},
            **{f"{s}_updates": sum(r["updates"] for r in rs if r["split"] == s) for s in ("train", "dev")},
            "flagged_updates": sum(r["flagged_updates"] for r in rs)})
    result = {"seed": seed, "policy": "80/20 by connected source-history groups; single-component strata are train-only",
        "canonical_policy": "latest fully reconstructible trajectory, then lowest question ID; never use answer grades",
        "code": git_metadata(Path(__file__)),
        "audit_script_sha256": ev.sha256_file(Path(__file__)), "source_files": source_hashes, "runs": runs,
        "summary": summary, "trace_occurrences": len(occurrences), "reconstructible_occurrences": sum(len(v) for v in candidates.values()),
        "excluded_occurrences": dict(Counter(r["reason"] for r in occurrences if r["reason"])), "issues": issues,
        "cross_split_exact_session_overlap": len(session_sets['train'] & session_sets['dev']),
        "quality_counts": {s: {"all_updates": len(rows), "no_target_flags": sum(not r["quality_flags"] for r in rows),
            "no_target_or_prior_flags": sum(not r["quality_flags"] and not r["prior_memory_has_flags"] for r in rows)}
            for s, rows in update_rows.items()},
        "leakage_components": components,
        "notes": ["Mechanically reconstructible does not imply factually correct teacher output.",
                  "Update JSONL files are trace pointers, not fine-tuning payloads. No benchmark questions or answers are training inputs.",
                  "Quality flags are preserved, not automatically treated as ground truth; prior memory may also contain flagged facts.",
                  "Exact session identity ignores timestamp and packaging. BEAM scale variants with the same chat ID stay together.",
                  "All listed histories and connected sessions are excluded from future final evaluation. No final set is selected here.",
                  "Same-history variants are inventoried but only one full trajectory is selected; no cross-trajectory splicing.",
                  "No semantic near-duplicate detection or human factual review has been performed."]}
    output.mkdir(parents=True, exist_ok=True)
    ev.atomic_json(output / "audit.json", result)
    ev.atomic_jsonl(output / "histories.jsonl", inventories)
    ev.atomic_jsonl(output / "occurrences.jsonl", occurrences)
    for split, rows in update_rows.items():
        ev.atomic_jsonl(output / f"{split}_updates.jsonl", rows)
        ev.atomic_json(output / f"{split}_histories.json", [r for r in inventories if r["split"] == split])
    lines = ["# Teacher trace audit and train/dev split", "", "Offline audit. No paid calls or model training.", "",
        "| Benchmark | Unique histories | Train histories | Dev histories | Train updates | Dev updates | Flagged updates |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for r in summary:
        lines.append("| " + " | ".join(str(r[k]) for k in ("benchmark", "unique_histories", "train_histories", "dev_histories", "train_updates", "dev_updates", "flagged_updates")) + " |")
    lines += ["", f"Seed: `{seed}`. " + result["policy"] + ".", "", result["canonical_policy"] + ".", "",
        f"Trace occurrences: {len(occurrences)}; reconstructible occurrences: {result['reconstructible_occurrences']}.",
        f"Excluded occurrences: `{json.dumps(result['excluded_occurrences'], sort_keys=True)}`.",
        "Cross-split exact session overlap: **0**.", "", "## Limits and next use", ""]
    totals = {s: sum(r[f"{s}_histories"] for r in summary) for s in ("train", "dev")}
    lines.append(f"- Actual split: {totals['train']} train histories and {totals['dev']} dev histories. BEAM scale variants share a split; connected components and small strata can prevent an 80/20 ratio.")
    for r in summary:
        if not r['dev_histories']:
            lines.append(f"- {r['benchmark']}: no leakage-safe dev component was available among the {r['unique_histories']} selected histories. This benchmark is train-only, not a complete train/dev evaluation setup.")
    used_locomo = sum(r['stratum'] == 'locomo' for r in inventories)
    available_locomo = sum(r['stratum'] == 'locomo' for r in catalog.values())
    lines.append(f"- This uses {used_locomo}/{available_locomo} local LoCoMo source conversations for train/dev. New questions on those conversations cannot be an independent final set.")
    for split, counts in result["quality_counts"].items():
        lines.append(f"- {split}: {counts['all_updates']} reconstructible updates; {counts['no_target_flags']} without target flags; {counts['no_target_or_prior_flags']} without target or prior-memory flags. These are heuristic warnings, not human labels.")
    lines += [f"- {note}" for note in result["notes"]]
    lines += ["", "Local split files and provenance: `work/training_trace_audit/`.",
              "Rerun: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python audit_training_traces.py`.", ""]
    ev.atomic_text(output / "summary.md", "\n".join(lines))
    print(json.dumps({"summary": summary, "excluded": result["excluded_occurrences"], "issues": issues}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/training_trace_audit")
    parser.add_argument("--seed", default="extractor-train-dev-v1-20260910")
    args = parser.parse_args()
    audit(args.output, args.seed)
