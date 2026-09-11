"""One immutable memory per history, with separate build/answer/judge executors."""
import copy
import json
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def digest(e, value):
    return e.sha256_text(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def memory_key(e, report, record):
    meta = report["metadata"]
    return digest(e, {
        "history": record["history_sha256"], "subject": record["memory"].get("subject"),
        "extractor": {k: v for k, v in meta["models"].items() if k.startswith("extraction_")},
        "prompts": {k: v for k, v in meta["prompts"].items() if k.startswith("extraction_")},
        "memory_code": meta.get("local_code", {}).get("memory_sha256"),
    })


def execute(e, client, args, report, by_id, validation_specs):
    if len({r["question_id"] for r in report["results"]}) != len(report["results"]):
        raise ValueError("Duplicate question IDs in shared pipeline")
    parent = report["run"]["run_id"]
    pipeline = report.setdefault("pipeline", {"memory_builds": {}, "mode": "answer-only-reuse" if args.memory_from else "build-and-answer"})
    timing = report.setdefault("timing", {})
    groups = {}
    for row in report["results"]:
        key = memory_key(e, report, row)
        groups.setdefault(key, []).append(row)
        row["memory_build_id"] = f"{parent}:memory:{key}"
        row.setdefault("stages", {})
    pipeline["unique_histories"] = len(groups)
    pipeline["questions"] = len(report["results"])
    pipeline["schedule"] = args.memory_schedule
    directory = e.validated_run_dir(parent) / "memories"
    directory.mkdir(parents=True, exist_ok=True)

    def stage(stage_id, node, operation):
        attempt = {"id": stage_id, "parent_run_id": parent, "started_at": utcnow(), "status": "running"}
        start = time.perf_counter()
        with e.REPORT_LOCK:
            attempt["attempt_id"] = f"{stage_id}:attempt:{len(node.get('attempts', [])) + 1}"
            node.setdefault("attempts", []).append(attempt)
            e.checkpoint_run(report)
        try:
            operation()
        except Exception as exc:
            with e.REPORT_LOCK:
                node["status"] = "pipeline_error"
                attempt["error_type"] = type(exc).__name__
                attempt["error"] = str(exc)
        finally:
            with e.REPORT_LOCK:
                attempt.update(finished_at=utcnow(), elapsed_seconds=round(time.perf_counter() - start, 6),
                               status=node.get("status", "finished"))
                e.checkpoint_run(report)

    def build(key, members, node):
        owner = members[0]
        path = directory / f"{key}.json"
        if path.exists():
            artifact = json.loads(path.read_text())
            if artifact["memory_build_id"] != owner["memory_build_id"] or artifact["sha256"] != digest(e, artifact["memory"]):
                raise ValueError("Memory artifact identity/hash mismatch")
            if artifact["history_sha256"] != owner["history_sha256"]:
                raise ValueError("Memory artifact history mismatch")
            store = artifact["memory"]
        else:
            store = owner["memory"]
            if store.get("reused_from_run"):
                # Old runs may contain multiple independently generated versions. Do not choose silently.
                if len({digest(e, r["memory"]["lines"]) for r in members}) != 1:
                    raise ValueError("Source has different memories for one history; select one canonical memory before reuse")
            if store["sessions_done"] != owner["history"]["sessions"]:
                if owner["status"] not in {"not_run", "memory_in_progress"} and not args.retry_failed:
                    node["status"] = owner["status"]
                    return
                if not e.write_memory(client, args, report, owner, by_id[owner["question_id"]]):
                    node["status"] = owner["status"]
                    return
            store = copy.deepcopy(owner["memory"])
            artifact = {"parent_run_id": parent, "memory_build_id": owner["memory_build_id"],
                        "history_sha256": owner["history_sha256"], "created_at": utcnow(),
                        "sha256": digest(e, store), "memory": store}
            e.atomic_json(path, artifact)
        if store["sessions_done"] != owner["history"]["sessions"]:
            raise ValueError("Incomplete memory artifact")
        with e.REPORT_LOCK:
            node.update(status="complete", artifact=str(path.relative_to(e.validated_run_dir(parent))),
                        sha256=artifact["sha256"], lines_sha256=digest(e, store["lines"]))
            for row in members:
                row["memory_sha256"] = artifact["sha256"]
                # One owner accounts for writing. Consumers refer to its ID, never duplicate its calls.
                row["memory"] = copy.deepcopy(store)
                if row is not owner:
                    row["memory"]["extraction_calls"] = []
                    row["memory"]["shared_from_question_id"] = owner["question_id"]
                if row["status"] in {"success", "answer_complete"}:
                    continue
                if row["status"] in {"judge_api_error", "invalid_judge_response"} and args.retry_failed:
                    row["status"] = "answer_complete"
                elif row["status"] in {"not_run", "memory_in_progress", "memory_complete", "blocked_memory_build"} or args.retry_failed:
                    if args.memory_stage == "build":
                        row["status"] = "memory_complete"
                    else:
                        e.prepare_memory_answer(args, report, row, by_id[row["question_id"]])

    def answer(row):
        with e.REPORT_LOCK:
            node = row["stages"].setdefault("answer", {})
            if row.get("answer_call"):
                row.setdefault("prior_answer_calls", []).append(row.pop("answer_call"))
        def operation():
            e.answer_record(client, args, report, row, by_id[row["question_id"]])
            node["status"] = row["status"]
        stage(f"{parent}:answer:{row['question_id']}", node, operation)
        if node.get("status") == "pipeline_error":
            with e.REPORT_LOCK:
                row["status"] = "pipeline_error"

    def judge(row):
        with e.REPORT_LOCK:
            node = row["stages"].setdefault("judge", {})
            if row.get("judge_call"):
                row.setdefault("prior_judge_calls", []).append(row.pop("judge_call"))
        def operation():
            e.judge_record(client, args, report, row, by_id[row["question_id"]])
            node["status"] = row["status"]
            if row["status"] == "success":
                with e.REPORT_LOCK:
                    timing.setdefault("first_graded_at", utcnow())
                    if all(r["status"] == "success" for r in report["results"]):
                        timing["all_graded_at"] = utcnow()
        stage(f"{parent}:judge:{row['question_id']}", node, operation)
        if node.get("status") == "pipeline_error":
            with e.REPORT_LOCK:
                row["status"] = "pipeline_error"

    pending = {}
    deferred = []
    with ThreadPoolExecutor(max_workers=args.build_workers) as builders, \
         ThreadPoolExecutor(max_workers=args.answer_workers) as answerers, \
         ThreadPoolExecutor(max_workers=args.judge_workers) as judges:
        for row, spec in zip(report["judge_validation"], validation_specs, strict=True):
            if row["status"] == "not_run":
                future = judges.submit(stage, f"{parent}:control:{row['case_id']}", row,
                                       lambda row=row, spec=spec: e.judge_control(client, args, report, row, spec))
                pending[future] = ("control", row)
        for key, members in groups.items():
            with e.REPORT_LOCK:
                node = pipeline["memory_builds"].setdefault(key, {"id": members[0]["memory_build_id"],
                    "owner_question_id": members[0]["question_id"], "question_ids": [r["question_id"] for r in members]})
            future = builders.submit(stage, node["id"], node, lambda key=key, members=members, node=node: build(key, members, node))
            pending[future] = ("build", (members, node))

        def enqueue(members):
            if args.memory_stage == "build":
                return
            for row in members:
                if row["status"] == "memory_complete":
                    pending[answerers.submit(answer, row)] = ("answer", row)
                elif row["status"] == "answer_complete":
                    pending[judges.submit(judge, row)] = ("judge", row)

        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                kind, value = pending.pop(future)
                future.result()
                if kind == "build":
                    members, node = value
                    if node["status"] != "complete":
                        with e.REPORT_LOCK:
                            for row in members:
                                if row["status"] not in {"success", "answer_complete"}:
                                    row["status"] = "blocked_memory_build"
                                    row["error"] = f"Memory build {node['id']} failed: {node['status']}"
                    elif args.memory_schedule == "overlap":
                        enqueue(members)
                    else:
                        deferred.extend(members)
                elif kind == "answer" and value["status"] == "answer_complete":
                    pending[judges.submit(judge, value)] = ("judge", value)
            if deferred and not any(kind == "build" for kind, _ in pending.values()):
                enqueue(deferred)
                deferred.clear()
    start = datetime.fromisoformat(report["run"]["started_at"])
    for event in ("first_graded", "all_graded"):
        if timing.get(f"{event}_at"):
            timing[f"seconds_to_{event}"] = (datetime.fromisoformat(timing[f"{event}_at"]) - start).total_seconds()
    e.checkpoint_run(report)
