from __future__ import annotations

import copy
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from adaption_memory import memory
from adaption_memory.domain import CallState, ExperimentSpec, sha256_json
from adaption_memory.evaluation.answering import (
    ANSWER_SYSTEM_PROMPTS,
    MEM0_ANSWER_SYSTEM_PROMPT,
    build_full_history_prompt,
    build_mem0_answer_prompt,
    fit_check,
    token_count,
    tokenizer,
)
from adaption_memory.evaluation.extractors import AppendOnlyMemoryExtractor
from adaption_memory.evaluation.judges import judge_requests, parse_judge
from adaption_memory.execution.local import CompletionBackend
from adaption_memory.history import history_sha256
from adaption_memory.presets import ExperimentPreset, resolve, selected_items
from adaption_memory.run_store import RunIndex, RunManifest, RunStatus, RunStore
from adaption_memory.source_manifest import source_hashes


class Coordinator:
    def __init__(self, runs: Path):
        self.store = RunStore(runs)
        self.index = RunIndex(runs / "index-v2.jsonl")

    def prepare(self, run_id: str, preset: ExperimentPreset, retry_of: str | None = None) -> RunManifest:
        spec = resolve(preset)
        items = selected_items(preset)
        question_ids = tuple(item.question_id for item in items)
        manifest = RunManifest.new(run_id, spec.sha256(), question_ids, retry_of=retry_of)
        specification = self.store.put_artifact(
            run_id, "experiment_spec", spec.to_dict(), (), spec.implementation_revision
        )
        dataset = self.store.put_artifact(
            run_id,
            "dataset_snapshot",
            {"benchmark": preset.benchmark, "items": [item.to_record() for item in items]},
            (specification.sha256,),
            spec.implementation_revision,
        )
        manifest = manifest.with_artifacts((specification, dataset))
        results = [
            {
                "question_id": item.question_id,
                "question_type": item.question_type,
                "status": "prepared",
                "dataset_sha256": dataset.sha256,
                "history_sha256": history_sha256(item.to_record()),
            }
            for item in items
        ]
        self.store.checkpoint(manifest, results)
        self.index.append(
            {
                "schema_version": 1,
                "run_id": run_id,
                "spec_sha256": spec.sha256(),
                "benchmark": spec.benchmark,
                "split": spec.split,
                "retry_of": retry_of,
            }
        )
        return manifest

    def check_configuration(self, run_id: str, spec: ExperimentSpec) -> RunManifest:
        """The run must have been prepared for this experiment configuration; code may differ."""
        loaded = self.store.load(run_id)
        recorded_ref = next(artifact for artifact in loaded.manifest.artifacts if artifact.kind == "experiment_spec")
        recorded = self.store.read_artifact(run_id, recorded_ref)
        recorded_configuration = {key: value for key, value in recorded.items() if key != "implementation_revision"}
        if sha256_json(recorded_configuration) != spec.configuration_sha256():
            raise RuntimeError(f"Run {run_id} was prepared for a different experiment configuration")
        return loaded.manifest

    def open(self, run_id: str, spec: ExperimentSpec) -> tuple[RunManifest, list[dict[str, Any]]]:
        """Load a run for continuation. A changed implementation is recorded in the graph, not refused.

        Every artifact already carries the implementation revision that produced it. Refusing to
        continue after any source edit froze runs out of their own bug fixes, so the gate is the
        configuration hash (data, prompts, models, parameters) and a code change becomes an
        `implementation_change` artifact plus a new manifest identity.
        """
        manifest = self.check_configuration(run_id, spec)
        loaded = self.store.load(run_id)
        results = copy.deepcopy(loaded.results)
        if manifest.spec_sha256 != spec.sha256():
            if manifest.status.terminal:
                raise RuntimeError(f"Run {run_id} is terminal; create a retry with a new run ID")
            spec_ref = next(artifact for artifact in manifest.artifacts if artifact.kind == "experiment_spec")
            change = self.store.put_artifact(
                run_id,
                "implementation_change",
                {
                    "previous_spec_sha256": manifest.spec_sha256,
                    "spec_sha256": spec.sha256(),
                    "previous_implementation_revision": manifest.artifacts[-1].implementation_revision,
                    "implementation_revision": spec.implementation_revision,
                    "source_sha256": source_hashes(),
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                    "results_generation": loaded.generation,
                },
                (spec_ref.sha256,),
                spec.implementation_revision,
            )
            manifest = replace(manifest, spec_sha256=spec.sha256(), artifacts=(*manifest.artifacts, change))
            self.store.checkpoint(manifest, results)
        return manifest, results

    def run(
        self,
        run_id: str,
        preset: ExperimentPreset,
        backend: CompletionBackend,
        *,
        allow_paid: bool,
    ) -> RunManifest:
        spec = resolve(preset)
        if spec.executor != "fixture" and not allow_paid:
            raise PermissionError("Paid execution requires --allow-paid on this command")
        manifest, results = self.open(run_id, spec)
        if manifest.status.terminal:
            raise RuntimeError(f"Run {run_id} is terminal; create a retry with a new run ID")
        refs = {artifact.sha256: artifact for artifact in manifest.artifacts}
        lock = threading.RLock()
        dataset_ref = next(artifact for artifact in manifest.artifacts if artifact.kind == "dataset_snapshot")
        dataset = self.store.read_artifact(run_id, dataset_ref)
        items = {item["question_id"]: item for item in dataset["items"]}
        parameters = dict(spec.parameters)
        extractor = AppendOnlyMemoryExtractor()

        def checkpoint() -> None:
            with lock:
                self.store.checkpoint(manifest, results)

        def put(kind: str, payload: Any, parents: tuple[str, ...]) -> Any:
            nonlocal manifest
            with lock:
                ref = self.store.put_artifact(run_id, kind, payload, parents, spec.implementation_revision)
                if ref.sha256 not in refs:
                    refs[ref.sha256] = ref
                    manifest = manifest.with_artifacts((*manifest.artifacts, ref))
                return ref

        def update(row: dict[str, Any], **fields: Any) -> None:
            with lock:
                row.update(fields)

        def artifact_payload(sha256: str) -> Any:
            return self.store.read_artifact(run_id, refs[sha256])

        def interrupted(row: dict[str, Any]) -> bool:
            if row.get("last_call_state") == CallState.UNKNOWN_OUTCOME.value:
                return True
            if row.get("last_call_state") != CallState.IN_FLIGHT.value:
                return False
            previous = row["last_call_sha256"]
            call = artifact_payload(previous)
            call = {
                **call,
                "state": CallState.UNKNOWN_OUTCOME.value,
                "ok": False,
                "error_type": "InterruptedAfterDispatch",
                "error": "The process ended after dispatch and before a durable response was saved",
            }
            ref = put("call_state", call, (previous,))
            update(row, status="unknown_outcome", last_call_state=call["state"], last_call_sha256=ref.sha256)
            checkpoint()
            return True

        def dispatch(
            row: dict[str, Any],
            parent_sha256: str,
            stage: str,
            model: str,
            system: str,
            user_messages: tuple[dict[str, Any], ...],
            max_output_tokens: int,
            reasoning_effort: str | None,
            response_format: dict[str, Any] | None,
            validate: Callable[[str], Any],
            item: dict[str, Any],
            operation: str | None = None,
        ) -> tuple[dict[str, Any], Any | None]:
            parent = parent_sha256
            label = operation or stage
            previous_state = row.get("last_call_state")
            same_stage = row.get("status") == f"{label}_{previous_state}"
            previous_call = None
            if same_stage and row.get("last_call_sha256"):
                previous_call = artifact_payload(row["last_call_sha256"])
                parent = row["last_call_sha256"]

            def saved_value(call: dict[str, Any]) -> tuple[dict[str, Any], Any | None]:
                nonlocal parent
                try:
                    value = validate(call["content"])
                except Exception as error:
                    invalid = {
                        **call,
                        "state": CallState.INVALID_OUTPUT.value,
                        "ok": False,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                    observe(invalid)
                    return invalid, None
                if call.get("state") == CallState.RESPONSE_SAVED.value:
                    call = {**call, "state": CallState.COMPLETE.value, "ok": True}
                    observe(call)
                return call, value

            last_ref = None

            def observe(call: dict[str, Any]) -> None:
                nonlocal last_ref, parent
                last_ref = put("call_state", call, (parent,))
                parent = last_ref.sha256
                update(row, 
                    status=f"{label}_{call['state']}",
                    last_call_state=call["state"],
                    last_call_sha256=last_ref.sha256,
                )
                checkpoint()

            if previous_call and previous_state in {CallState.RESPONSE_SAVED.value, CallState.COMPLETE.value}:
                recovered, value = saved_value(previous_call)
                if value is not None:
                    return recovered, value
                previous_call = recovered
                previous_state = recovered["state"]
            if previous_call and previous_state in {CallState.IN_FLIGHT.value, CallState.UNKNOWN_OUTCOME.value}:
                return previous_call, None

            start_attempt = 1
            if previous_call:
                try:
                    previous_attempt = int(str(previous_call["call_id"]).rsplit(":", 1)[1])
                except (KeyError, TypeError, ValueError):
                    previous_attempt = 1
                start_attempt = previous_attempt if previous_state == CallState.NOT_DISPATCHED.value else previous_attempt + 1
            if start_attempt > 2:
                return previous_call or {}, None

            operation_id = parent_sha256[:12]
            for attempt in range(start_attempt, 3):
                last_ref = None
                call_id = f"{run_id}:{label}:{row['question_id']}:{operation_id}:{attempt}"
                try:
                    call = backend.complete(
                        call_id=call_id,
                        stage=stage,
                        model=model,
                        system=system,
                        user_messages=user_messages,
                        max_output_tokens=max_output_tokens,
                        reasoning_effort=reasoning_effort,
                        response_format=response_format,
                        observe=observe,
                        item=item,
                    )
                except Exception as error:
                    observed = artifact_payload(last_ref.sha256) if last_ref is not None else {}
                    call = {
                        **observed,
                        "call_id": call_id,
                        "state": CallState.UNKNOWN_OUTCOME.value,
                        "ok": False,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                    observe(call)
                if call.get("state") == CallState.RESPONSE_SAVED.value:
                    call, value = saved_value(call)
                    if value is not None:
                        return call, value
                if call.get("state") not in {CallState.NOT_DISPATCHED.value, CallState.INVALID_OUTPUT.value} or attempt == 2:
                    return call, None
            raise AssertionError("unreachable")

        rows_by_history: dict[str, list[dict[str, Any]]] = {}
        for row in results:
            if row.get("status") == "blocked_memory" or interrupted(row):
                continue
            rows_by_history.setdefault(row["history_sha256"], []).append(row)

        memory_refs: dict[str, Any] = {}
        for history_id, members in rows_by_history.items():
            existing = next((row.get("memory_sha256") for row in members if row.get("memory_sha256")), None)
            if existing:
                memory_refs[history_id] = refs[existing]
                continue
            owner = members[0]
            item = items[owner["question_id"]]
            if spec.extractor == "full-history":
                ref = put("memory", {"mode": "full-history", "history": item["haystack_sessions"]}, (dataset_ref.sha256,))
            elif spec.extractor == "mem0":
                raise RuntimeError("Mem0 memories are built by the mem0 executor and imported before answering")
            else:
                progress_sha = owner.get("memory_progress_sha256")
                progress = artifact_payload(progress_sha) if progress_sha else {"sessions_done": 0, "lines": [], "failures": []}
                lines = progress["lines"]
                sessions = [
                    {"timestamp": timestamp, "messages": messages}
                    for timestamp, messages in zip(item["haystack_dates"], item["haystack_sessions"], strict=True)
                ]
                parent = progress_sha or dataset_ref.sha256
                for index in range(progress["sessions_done"], len(sessions)):
                    session = sessions[index]
                    call, parsed = dispatch(
                        owner,
                        parent,
                        "extract",
                        spec.extractor_model_name,
                        extractor.system_prompt(item["subject"]),
                        extractor.user_messages(lines, index + 1, len(sessions), session["timestamp"], session["messages"]),
                        int(parameters["extraction_max_tokens"]),
                        None if parameters.get("extractor_reasoning_effort", "provider-default") == "provider-default" else str(parameters["extractor_reasoning_effort"]),
                        extractor.response_format,
                        memory.parse_extraction,
                        item,
                        operation=f"extract:{index + 1}",
                    )
                    if call.get("state") != CallState.COMPLETE.value:
                        break
                    new_lines, failures = memory.apply_extraction(
                        lines,
                        parsed,
                        index + 1,
                        session["timestamp"],
                        memory.session_text(session["messages"]),
                    )
                    progress = {"sessions_done": index + 1, "lines": lines, "failures": [*progress["failures"], *failures]}
                    progress_ref = put("memory_progress", progress, (owner["last_call_sha256"],))
                    owner["memory_progress_sha256"] = progress_ref.sha256
                    owner["status"] = "memory_in_progress"
                    parent = progress_ref.sha256
                    checkpoint()
                if progress["sessions_done"] != len(sessions):
                    for row in members:
                        if row is not owner:
                            update(row, status="blocked_memory", last_call_state=owner.get("last_call_state"))
                    checkpoint()
                    continue
                ref = put("memory", progress, (parent,))
            memory_refs[history_id] = ref
            for row in members:
                update(row, status="memory_complete", memory_sha256=ref.sha256)
            checkpoint()

        def grade(row: dict[str, Any]) -> None:
            if row.get("last_call_state") in {CallState.IN_FLIGHT.value, CallState.UNKNOWN_OUTCOME.value} or row.get("status") == "blocked_memory":
                return
            item = items[row["question_id"]]
            memory_ref = memory_refs.get(row["history_sha256"])
            if memory_ref is None:
                return
            if not row.get("answer_sha256"):
                if spec.extractor == "full-history":
                    prompt, _ = build_full_history_prompt(item)
                    system = ANSWER_SYSTEM_PROMPTS[str(parameters["answer_prompt"])]
                elif spec.extractor == "mem0":
                    payload = self.store.read_artifact(run_id, memory_ref)
                    prompt = build_mem0_answer_prompt(
                        payload["lines"], len(item["haystack_sessions"]), item["question_date"], item["question"]
                    )
                    system = MEM0_ANSWER_SYSTEM_PROMPT
                else:
                    payload = self.store.read_artifact(run_id, memory_ref)
                    prompt = memory.build_answer_prompt(
                        payload["lines"], len(item["haystack_sessions"]), item["question_date"], item["question"]
                    )
                    system = memory.ANSWER_SYSTEM_PROMPTS[str(parameters["answer_prompt"])]
                fit = fit_check(
                    token_count(tokenizer("o200k_base"), system, prompt),
                    int(parameters["answer_max_tokens"]),
                    int(parameters["answer_context_window"]),
                )
                if not fit["fits"]:
                    failure_ref = put("preflight_failure", {"stage": "answer", **fit}, (memory_ref.sha256,))
                    update(row, status="answer_context_limit", answer_preflight_sha256=failure_ref.sha256)
                    checkpoint()
                    return
                call, answer = dispatch(
                    row,
                    memory_ref.sha256,
                    "answer",
                    spec.answerer,
                    system,
                    ({"role": "user", "content": prompt},),
                    int(parameters["answer_max_tokens"]),
                    None if parameters["answer_reasoning_effort"] == "provider-default" else str(parameters["answer_reasoning_effort"]),
                    None,
                    lambda content: content.strip() or (_ for _ in ()).throw(ValueError("Empty answer")),
                    item,
                )
                if call.get("state") != CallState.COMPLETE.value:
                    return
                answer_ref = put("answer", {"answer": answer, "call_sha256": row["last_call_sha256"]}, (row["last_call_sha256"], memory_ref.sha256))
                update(row, status="answer_complete", answer=answer, answer_sha256=answer_ref.sha256)
                checkpoint()
            if not row.get("judge_sha256"):
                def validate_judge(content: str) -> tuple[str, float | None]:
                    verdict, score = parse_judge(item.get("judge", "longmemeval"), content)
                    if verdict == "invalid":
                        raise ValueError("Judge output has no valid verdict")
                    return verdict, score

                parts = list(row.get("judge_parts", ()))
                requests = judge_requests(item, row["answer"])
                parent = parts[-1]["artifact_sha256"] if parts else row["answer_sha256"]
                for index in range(len(parts), len(requests)):
                    judge_system, prompt = requests[index]
                    call, judged = dispatch(
                        row,
                        parent,
                        "judge",
                        spec.judge,
                        judge_system,
                        ({"role": "user", "content": prompt},),
                        int(parameters["judge_max_tokens"]),
                        None if parameters["judge_reasoning_effort"] == "provider-default" else str(parameters["judge_reasoning_effort"]),
                        None,
                        validate_judge,
                        item,
                        operation=f"judge:{index + 1}",
                    )
                    if call.get("state") != CallState.COMPLETE.value:
                        break
                    verdict, score = judged
                    part_ref = put(
                        "judge_part",
                        {"index": index + 1, "verdict": verdict, "score": score, "call_sha256": row["last_call_sha256"]},
                        (row["last_call_sha256"], parent),
                    )
                    parts.append({"index": index + 1, "verdict": verdict, "score": score, "artifact_sha256": part_ref.sha256})
                    parent = part_ref.sha256
                    update(row, status="judge_in_progress", judge_parts=parts)
                    checkpoint()
                if len(parts) != len(requests):
                    return
                scores = [part["score"] for part in parts if isinstance(part.get("score"), (int, float))]
                if len(scores) != len(parts):
                    raise RuntimeError("Completed judge part has no numeric score")
                score = sum(scores) / len(scores)
                verdict = parts[0]["verdict"] if len(parts) == 1 else "yes" if score == 1.0 else "partial" if score > 0 else "no"
                judge_ref = put(
                    "judge",
                    {"verdict": verdict, "score": score, "parts": parts},
                    tuple(part["artifact_sha256"] for part in parts),
                )
                update(row, status="success", verdict=verdict, score=score, judge_sha256=judge_ref.sha256)
                checkpoint()


        with ThreadPoolExecutor(max_workers=max(1, spec.concurrency)) as pool:
            for future in [pool.submit(grade, row) for row in results]:
                future.result()

        terminal = RunStatus.COMPLETE
        if any(row.get("last_call_state") in {CallState.IN_FLIGHT.value, CallState.UNKNOWN_OUTCOME.value} for row in results):
            terminal = RunStatus.BLOCKED
        elif any(row["status"] != "success" for row in results):
            terminal = RunStatus.COMPLETE_WITH_FAILURES
        parents = tuple(
            row.get("judge_sha256") or row.get("answer_sha256") or row.get("memory_sha256") or dataset_ref.sha256
            for row in results
        )
        report = put(
            "report",
            {
                "questions": len(results),
                "successful": sum(row["status"] == "success" for row in results),
                "status": terminal.value,
            },
            parents,
        )
        for row in results:
            row["report_sha256"] = report.sha256
        manifest = manifest.with_status(terminal)
        self.store.checkpoint(manifest, results)
        return manifest

    def import_memories(
        self,
        run_id: str,
        preset: ExperimentPreset,
        directory: Path,
        executor: dict[str, Any],
    ) -> RunManifest:
        """Record memories an executor built outside the pipeline (Modal vLLM, Mem0) and their cost."""
        spec = resolve(preset)
        manifest, results = self.open(run_id, spec)
        if manifest.status.terminal:
            raise RuntimeError("Cannot import into a terminal run")
        config = json.loads((directory / "configuration.json").read_text())
        if config.get("configuration_sha256") != spec.configuration_sha256():
            raise ValueError("Executor configuration does not match the experiment configuration")
        refs = {artifact.sha256: artifact for artifact in manifest.artifacts}
        dataset_ref = next(artifact for artifact in manifest.artifacts if artifact.kind == "dataset_snapshot")

        def put(kind: str, payload: Any, parents: tuple[str, ...]):
            nonlocal manifest
            ref = self.store.put_artifact(run_id, kind, payload, parents, spec.implementation_revision)
            if ref.sha256 not in refs:
                refs[ref.sha256] = ref
                manifest = manifest.with_artifacts((*manifest.artifacts, ref))
            return ref

        if not isinstance(executor.get("cost_usd"), (int, float)):
            raise ValueError("Executor record has no final accounted cost")
        executor_ref = put(
            "executor_call_state",
            {
                "call_id": f"{run_id}:{executor['name']}",
                "state": CallState.COMPLETE.value,
                "ok": True,
                "usage": {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                **{key: value for key, value in executor.items() if key != "name"},
                "reserved_usd": float(executor["reserved_usd"]),
                "cost_usd": float(executor["cost_usd"]),
            },
            (dataset_ref.sha256,),
        )

        by_history: dict[str, list[dict[str, Any]]] = {}
        for row in results:
            by_history.setdefault(row["history_sha256"], []).append(row)
        for history_id, members in by_history.items():
            path = directory / "memories" / f"{history_id}.json"
            if not path.is_file():
                for row in members:
                    row.update(status="blocked_memory", last_call_state="missing_checkpoint")
                continue
            state = json.loads(path.read_text())
            if (state.get("history_sha256") != history_id
                or state.get("payload_sha256") != config["payload"]["fingerprint"]):
                raise ValueError("Memory checkpoint identity mismatch")
            parent = executor_ref.sha256
            for index, call in enumerate(state.get("calls", ()), start=1):
                normalized = dict(call)
                normalized.setdefault("call_id", f"{run_id}:extract:{history_id}:{index}")
                normalized["state"] = normalized.pop("status", CallState.UNKNOWN_OUTCOME.value)
                normalized["ok"] = normalized["state"] == CallState.COMPLETE.value
                normalized.setdefault("reserved_usd", 0.0)
                normalized.setdefault("cost_usd", 0.0)
                ref = put("call_state", normalized, (parent,))
                parent = ref.sha256
            if state.get("status") == "complete":
                expected = next(row for row in config["payload"]["histories"]
                    if row["history_sha256"] == history_id)
                if (state.get("sessions_done") != len(expected["history"])
                    or any(call.get("status") != "complete" for call in state.get("calls", ()))):
                    raise ValueError("Complete memory has unfinished extraction calls or sessions")
                memory_ref = put(
                    "memory",
                    {
                        "sessions_done": state["sessions_done"],
                        "lines": state["lines"],
                        "failures": state.get("warnings", ()),
                        "executor_payload_sha256": config["payload"]["fingerprint"],
                    },
                    (parent,),
                )
                for row in members:
                    row.update(status="memory_complete", memory_sha256=memory_ref.sha256)
            else:
                for row in members:
                    row.update(
                        status="blocked_memory",
                        last_call_state=state.get("status", CallState.UNKNOWN_OUTCOME.value),
                        last_call_sha256=parent,
                    )
        self.store.checkpoint(manifest, results)
        return manifest

    def retry(self, parent_run_id: str, run_id: str, preset: ExperimentPreset) -> RunManifest:
        self.check_configuration(parent_run_id, resolve(preset))
        parent = self.store.load(parent_run_id)
        if not parent.manifest.status.terminal:
            raise RuntimeError("Only terminal runs can be retried")
        unresolved = [
            row["question_id"]
            for row in parent.results
            if row.get("last_call_state") in {CallState.IN_FLIGHT.value, CallState.UNKNOWN_OUTCOME.value}
        ]
        if unresolved:
            raise RuntimeError(
                f"Run has unresolved external-call outcomes and cannot be retried: {unresolved}"
            )
        return self.prepare(run_id, preset, retry_of=parent_run_id)
