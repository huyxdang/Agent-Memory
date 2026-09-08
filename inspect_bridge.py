#!/usr/bin/env python3
"""Convert immutable run records under runs/ into Inspect AI eval logs under logs/.

The runner never imports Inspect. This bridge reads a finished run directory and
writes one .eval file that `inspect view` can display: every answer prompt, the
reference answer, the generated answer, the judge prompt and reasoning, the
verdict, and per-call token usage and cost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from inspect_ai.event import InfoEvent, ModelEvent, ScoreEvent, SpanBeginEvent, SpanEndEvent
from inspect_ai.log import (
    EvalConfig,
    EvalDataset,
    EvalError,
    EvalLog,
    EvalMetric,
    EvalPlan,
    EvalPlanStep,
    EvalResults,
    EvalRevision,
    EvalSample,
    EvalScore,
    EvalSpec,
    EvalStats,
    write_eval_log,
)
from inspect_ai.model import (
    ChatCompletionChoice,
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageUser,
    GenerateConfig,
    ModelOutput,
    ModelUsage,
)
from inspect_ai.scorer import CORRECT, INCORRECT, NOANSWER, Score

ROOT = Path(__file__).resolve().parent
RUNS_DIR = ROOT / "runs"
LOGS_DIR = ROOT / "logs"
SCORER = "mem0_judge"
STOP_REASONS = {"stop": "stop", "length": "max_tokens", "content_filter": "content_filter"}
RUN_STATUS = {
    "running": "started",
    "complete": "success",
    "complete_with_failures": "success",
    "preflight_only": "success",
}


def model_name(call: dict[str, Any]) -> str:
    return "openai/" + (call.get("resolved_model") or call.get("requested_model") or "unknown")


def usage(call: dict[str, Any] | None) -> ModelUsage | None:
    if not call or not call.get("usage") or call["usage"].get("input_tokens") is None:
        return None
    raw = call["usage"]
    return ModelUsage(
        input_tokens=raw["input_tokens"],
        output_tokens=raw["output_tokens"],
        total_tokens=raw["total_tokens"],
        input_tokens_cache_read=raw.get("cached_input_tokens"),
        reasoning_tokens=raw.get("reasoning_output_tokens"),
        total_cost=call.get("cost_usd"),
    )


def add_usage(totals: dict[str, ModelUsage], key: str, item: ModelUsage | None) -> None:
    if item is None:
        return
    current = totals.get(key)
    if current is None:
        totals[key] = item.model_copy()
        return
    totals[key] = ModelUsage(
        input_tokens=current.input_tokens + item.input_tokens,
        output_tokens=current.output_tokens + item.output_tokens,
        total_tokens=current.total_tokens + item.total_tokens,
        input_tokens_cache_read=(current.input_tokens_cache_read or 0) + (item.input_tokens_cache_read or 0),
        reasoning_tokens=(current.reasoning_tokens or 0) + (item.reasoning_tokens or 0),
        total_cost=(current.total_cost or 0.0) + (item.total_cost or 0.0),
    )


def output(call: dict[str, Any] | None) -> ModelOutput:
    if not call:
        return ModelOutput()
    content = call.get("content") or ""
    return ModelOutput(
        model=model_name(call),
        choices=[
            ChatCompletionChoice(
                message=ChatMessageAssistant(content=content, model=model_name(call), source="generate"),
                stop_reason=STOP_REASONS.get(call.get("finish_reason") or "", "unknown"),
            )
        ],
        completion=content,
        usage=usage(call),
        time=call.get("elapsed_seconds"),
        error=call.get("error"),
        metadata={"reasoning_effort": call.get("reasoning_effort"), "system_fingerprint": call.get("system_fingerprint")},
    )


def model_event(role: str, messages: list[Any], call: dict[str, Any], metadata: dict[str, Any] | None = None) -> ModelEvent:
    return ModelEvent(
        model=model_name(call),
        role=role,
        input=messages,
        tools=[],
        tool_choice="none",
        config=GenerateConfig(max_tokens=call.get("max_output_tokens"), reasoning_effort=call.get("reasoning_effort")),
        output=output(call),
        error=call.get("error"),
        working_time=call.get("elapsed_seconds"),
        metadata=metadata,
    )


HISTORY_PREFIX = "Conversation history (chronological JSON):\n"
QUESTION_PREFIX = "\n\nQuestion: "


_DATASET: dict[str, dict[str, Any]] = {}


def dataset_item(file_name: str, question_id: str) -> dict[str, Any]:
    if not _DATASET:
        for item in json.loads((ROOT / "work" / file_name).read_text()):
            _DATASET[item["question_id"]] = item
    return _DATASET[question_id]


def evidence_labels(item: dict[str, Any]) -> dict[str, Any]:
    """Ground-truth evidence from the dataset: labeled sessions and has_answer turns.

    These labels are stripped from the answer prompt by the runner. They are
    shown in the viewer only, so a reader can find where the answer lives.
    """
    session_ids = item["haystack_session_ids"]
    sessions = {session_ids.index(s) + 1 for s in item["answer_session_ids"] if s in session_ids}
    turns = []
    for index, (timestamp, session) in enumerate(zip(item["haystack_dates"], item["haystack_sessions"]), start=1):
        for turn, message in enumerate(session, start=1):
            if message.get("has_answer"):
                sessions.add(index)
                turns.append({"session": index, "turn": turn, "timestamp": timestamp, "role": message["role"], "text": message["content"]})
    return {
        "sessions": [{"session": index, "timestamp": item["haystack_dates"][index - 1]} for index in sorted(sessions)],
        "turns": turns,
    }


def turn_id(session: int, turn: int) -> str:
    return f"s{session}-t{turn}"


def evidence_event(evidence: dict[str, Any], log_name: str, sample_id: str, linkable: bool) -> InfoEvent:
    """Markdown summary of the dataset evidence. Links focus each history bubble when the sample has them."""

    def link(session: int, turn: int) -> str:
        return f"#/tasks/{log_name}/samples/sample/{sample_id}/1/messages?message={turn_id(session, turn)}"

    lines = ["**Answer evidence** (dataset labels; the model never saw these)", ""]
    lines.append("Sessions: " + ", ".join(f"{e['session']} ({e['timestamp']})" for e in evidence["sessions"]))
    lines.append("")
    for entry in evidence["turns"]:
        preview = " ".join(entry["text"].split())
        if len(preview) > 240:
            preview = preview[:240] + "…"
        label = f"Session {entry['session']}, turn {entry['turn']} ({entry['role']})"
        if linkable:
            label = f"[{label}]({link(entry['session'], entry['turn'])})"
        lines.append(f"- {label}: {preview}")
    return InfoEvent(source="evidence", data="\n".join(lines))


def memory_events(store: dict[str, Any], extraction_system: str) -> list[Any]:
    """One model event per extraction call inside a memory-writing span, then the final store as markdown."""
    calls = []
    for call in store.get("extraction_calls", []):
        parts = call.get("prompt_messages") or [call.get("prompt") or ""]
        calls.append(
            model_event(
                "memory_writer",
                [ChatMessageSystem(content=extraction_system, source="input")] + [ChatMessageUser(content=part, source="input") for part in parts],
                call,
                {"session": call.get("session"), "new_lines": call.get("new_lines"), "prompt_sha256": call.get("prompt_sha256")},
            )
        )
    lines = store.get("lines", [])
    rendered = "\n".join(
        f"{l['kind']} | s{l['session']} | {l['date']} | " + (f"{l['key']}: {l['value']}" if l["kind"] == "atomic" else l["text"])
        for l in lines
    ) or "(empty)"
    text = [f"**Memory store** after {store.get('sessions_done', 0)} session(s): {len(lines)} lines, {len(store.get('failures', []))} flagged", "", "```text", rendered, "```"]
    if store.get("failures"):
        text += ["", "**Flagged lines**", ""] + [f"- s{f['session']} `{f['key']}: {f['value']}` → {', '.join(f['codes'])}" for f in store["failures"]]
    return span("memory-writing", calls) + [InfoEvent(source="memory", data="\n".join(text))]


def answer_messages(system: str, answer_prompt: str, evidence: dict[str, Any]) -> list[Any]:
    """Expand the single JSON-history user message into one chat message per turn.

    The API call sent the history as compact JSON inside one user message. The
    content shown here is identical; only the framing differs so the viewer can
    render bubbles and stays under its per-block size cap. Evidence flags come
    from the dataset labels and were never part of the prompt.
    """
    header, rest = answer_prompt.split(HISTORY_PREFIX, 1)
    history_json, question = rest.rsplit(QUESTION_PREFIX, 1)
    sessions = json.loads(history_json)
    return history_messages(system, sessions, header, question, evidence)


def history_messages(system: str, sessions: list[dict[str, Any]], header: str, question: str, evidence: dict[str, Any]) -> list[Any]:
    evidence_sessions = {entry["session"] for entry in evidence["sessions"]}
    evidence_turns = {(entry["session"], entry["turn"]) for entry in evidence["turns"]}
    messages: list[Any] = [ChatMessageSystem(content=system, source="input")]
    for index, session in enumerate(sessions, start=1):
        for turn, message in enumerate(session["messages"], start=1):
            cls = ChatMessageUser if message["role"] == "user" else ChatMessageAssistant
            metadata: dict[str, Any] = {"session": f"{index} of {len(sessions)}", "timestamp": session["timestamp"], "turn": turn}
            if (index, turn) in evidence_turns:
                metadata["evidence"] = "ANSWER EVIDENCE TURN (dataset label, not shown to model)"
            elif index in evidence_sessions:
                metadata["evidence"] = "evidence session (dataset label, not shown to model)"
            messages.append(cls(id=turn_id(index, turn), content=message["content"], source="input", metadata=metadata))
    messages.append(
        ChatMessageUser(
            content=f"{header.strip()}\n\nQuestion: {question}",
            source="input",
            metadata={"evidence_sessions": [entry["session"] for entry in evidence["sessions"]]},
        )
    )
    return messages


def span(name: str, events: list[Any]) -> list[Any]:
    return [SpanBeginEvent(id=name, name=name, type=name), *events, SpanEndEvent(id=name)]


def verdict_score(verdict: str | None, answer: str | None, explanation: str | None, meta: dict[str, Any]) -> Score:
    value = {"yes": CORRECT, "no": INCORRECT}.get(verdict or "", NOANSWER)
    return Score(value=value, answer=answer, explanation=explanation, metadata=meta)


def benchmark_sample(record: dict[str, Any], manifest: dict[str, Any], log_name: str) -> EvalSample:
    prompts = manifest["metadata"]["prompts"]
    answer_call = record.get("answer_call")
    judge_call = record.get("judge_call")
    evidence = evidence_labels(dataset_item(manifest["metadata"]["dataset"]["file"], record["question_id"]))
    store = record.get("memory")
    full_history = store is None and bool(record.get("answer_prompt"))
    if full_history:
        input_messages = answer_messages(prompts["answer_system"], record["answer_prompt"], evidence)
    else:
        input_messages = [ChatMessageSystem(content=prompts["answer_system"], source="input")]
        if record.get("answer_prompt"):
            input_messages.append(ChatMessageUser(content=record["answer_prompt"], source="input"))
    messages: list[Any] = list(input_messages)
    events: list[Any] = [evidence_event(evidence, log_name, record["question_id"], linkable=full_history)]
    model_usage: dict[str, ModelUsage] = {}
    role_usage: dict[str, ModelUsage] = {}
    if store is not None:
        events += memory_events(store, prompts.get("extraction_system") or "")
        for call in store.get("extraction_calls", []):
            add_usage(model_usage, model_name(call), usage(call))
            add_usage(role_usage, "memory_writer", usage(call))
    if answer_call:
        api_note = {
            "api_serialization": "History sent as compact JSON inside one user message; shown here as one message per turn.",
            "answer_prompt_sha256": record["answer_prompt_sha256"],
            "answer_prompt_chars": len(record["answer_prompt"]),
        }
        events += span("answer", [model_event("answerer", input_messages, answer_call, api_note)])
        add_usage(model_usage, model_name(answer_call), usage(answer_call))
        add_usage(role_usage, "answerer", usage(answer_call))
        if answer_call.get("ok"):
            messages.append(ChatMessageAssistant(content=answer_call["content"], model=model_name(answer_call), source="generate"))
    scores = None
    if judge_call:
        raw = judge_call.get("content")
        score = verdict_score(
            record.get("judge_verdict"),
            record.get("generated_answer"),
            record.get("judge_explanation") or raw,
            {
                "verdict": record.get("judge_verdict"),
                "judge_prompt": record.get("judge_prompt"),
                "judge_raw_response": raw,
                "judge_model": judge_call.get("resolved_model"),
                "judge_cost_usd": judge_call.get("cost_usd"),
                "judge_error": judge_call.get("error"),
            },
        )
        scores = {SCORER: score}
        events += span(
            "judge",
            [
                model_event("judge", [ChatMessageUser(content=record["judge_prompt"], source="input")], judge_call),
                ScoreEvent(score=score, target=record["reference_answer"], scorer=SCORER, model_usage={model_name(judge_call): u} if (u := usage(judge_call)) else None),
            ],
        )
        add_usage(model_usage, model_name(judge_call), usage(judge_call))
        add_usage(role_usage, "judge", usage(judge_call))
    error = None
    for call in [*((store or {}).get("extraction_calls", [])), answer_call, judge_call]:
        if call and call.get("error"):
            error = EvalError(message=f"{call.get('error_type')}: {call['error']}", traceback="", traceback_ansi="")
            break
    elapsed = sum((call or {}).get("elapsed_seconds") or 0.0 for call in (answer_call, judge_call))
    return EvalSample(
        id=record["question_id"],
        epoch=1,
        input=input_messages,
        target=record["reference_answer"],
        messages=messages,
        output=output(answer_call),
        scores=scores,
        metadata={
            "kind": "benchmark",
            "question_type": record["question_type"],
            "question": record["question"],
            "status": record["status"],
            "evidence": evidence,
            "memory": {
                "sessions_done": store.get("sessions_done"),
                "lines": len(store.get("lines", [])),
                "flagged": len(store.get("failures", [])),
                "extraction_calls": len(store.get("extraction_calls", [])),
            } if store is not None else None,
            "history": record.get("history"),
            "context_tokens": record.get("context_tokens"),
            "prompt_fit": record.get("prompt_fit"),
            "answer_cost_usd": (answer_call or {}).get("cost_usd"),
        },
        events=events,
        model_usage=model_usage,
        role_usage=role_usage,
        total_time=elapsed or None,
        error=error,
    )


def control_sample(item: dict[str, Any]) -> EvalSample:
    call = item.get("judge_call")
    judge_prompt = item.get("judge_prompt") or ""
    scores = None
    events: list[Any] = []
    model_usage: dict[str, ModelUsage] = {}
    if call:
        agreement = item.get("agreement")
        score = Score(
            value=NOANSWER if item.get("actual") in (None, "invalid") else (CORRECT if agreement else INCORRECT),
            answer=item.get("actual"),
            explanation=item.get("judge_explanation") or call.get("content"),
            metadata={
                "expected": item["expected"],
                "actual": item.get("actual"),
                "agreement": agreement,
                "judge_prompt": judge_prompt,
                "judge_raw_response": call.get("content"),
                "judge_cost_usd": call.get("cost_usd"),
                "judge_error": call.get("error"),
            },
        )
        scores = {SCORER: score}
        events = span("judge", [model_event("judge", [ChatMessageUser(content=judge_prompt, source="input")], call), ScoreEvent(score=score, target=item["expected"], scorer=SCORER)])
        add_usage(model_usage, model_name(call), usage(call))
    return EvalSample(
        id="control:" + item["case_id"],
        epoch=1,
        input=[ChatMessageUser(content=judge_prompt, source="input")] if judge_prompt else item["supplied_answer"],
        target=item["expected"],
        messages=[ChatMessageUser(content=judge_prompt, source="input")] if judge_prompt else [],
        output=output(call),
        scores=scores,
        metadata={
            "kind": "judge_control",
            "question": item["question"],
            "reference_answer": item["reference_answer"],
            "supplied_answer": item["supplied_answer"],
            "status": item["status"],
        },
        events=events,
        model_usage=model_usage,
        role_usage={"judge": model_usage[next(iter(model_usage))]} if model_usage else {},
        total_time=(call or {}).get("elapsed_seconds"),
        error=EvalError(message=f"{call.get('error_type')}: {call['error']}", traceback="", traceback_ansi="") if call and call.get("error") else None,
    )


def convert_run(run_dir: Path) -> Path:
    manifest = json.loads((run_dir / "manifest.json").read_text())
    records = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines() if line.strip()]
    meta = manifest["metadata"]
    models = meta["models"]
    log_name = f"{manifest['run_id']}.eval"
    samples = [benchmark_sample(record, manifest, log_name) for record in records]
    samples += [control_sample(item) for item in manifest.get("judge_validation", [])]

    model_usage: dict[str, ModelUsage] = {}
    role_usage: dict[str, ModelUsage] = {}
    for sample in samples:
        for key, item in sample.model_usage.items():
            add_usage(model_usage, key, item)
        for key, item in sample.role_usage.items():
            add_usage(role_usage, key, item)

    graded = [s for s in samples if s.metadata["kind"] == "benchmark" and s.scores and s.scores[SCORER].value in (CORRECT, INCORRECT)]
    correct = sum(s.scores[SCORER].value == CORRECT for s in graded)
    controls = [s for s in samples if s.metadata["kind"] == "judge_control" and s.scores]
    metrics = {}
    if graded:
        metrics["accuracy"] = EvalMetric(name="accuracy", value=round(correct / len(graded), 6))
    if controls:
        metrics["judge_control_agreement"] = EvalMetric(
            name="judge_control_agreement", value=round(sum(s.scores[SCORER].value == CORRECT for s in controls) / len(controls), 6)
        )

    status = manifest["status"]
    local = meta["local_code"]
    log = EvalLog(
        status=RUN_STATUS.get(status, "error"),
        eval=EvalSpec(
            eval_id=manifest["run_id"],
            run_id=manifest["run_id"],
            created=manifest["started_at"],
            task=f"longmemeval/{manifest['system']}",
            task_display_name=f"LongMemEval {manifest['system']}",
            task_args={"question_ids": manifest["question_ids"], "retry_of": manifest.get("retry_of")},
            solver=manifest["system"],
            dataset=EvalDataset(
                name=meta["dataset"]["repository"],
                location=meta["dataset"]["file"],
                samples=len(records),
                sample_ids=manifest["question_ids"],
            ),
            model="openai/" + (models["answer_requested"] or "unconfigured"),
            model_generate_config=GenerateConfig(max_tokens=models.get("answer_max_tokens"), reasoning_effort=models["answer_reasoning_effort"]),
            model_roles=None,
            config=EvalConfig(),
            revision=EvalRevision(type="git", origin="local", commit=local["git_head"] or local["script_sha256"], dirty=local.get("git_dirty")),
            packages=meta["runtime"]["packages"],
            metadata={
                "run_status": status,
                "judge": {"model": models["judge_requested"], "max_tokens": models.get("judge_max_tokens"), "prompt": meta["prompts"]["judge"]},
                "retry_of": manifest.get("retry_of"),
                "script_sha256": local["script_sha256"],
                "dataset_revision": meta["dataset"]["revision"],
                "dataset_sha256": meta["dataset"]["sha256"],
                "upstream_code": meta["upstream_code"],
                "prices_usd_per_million_tokens": meta["prices_usd_per_million_tokens"],
                "spending_limit_usd": meta["spending_limit_usd"],
                "tokenizer": models["tokenizer"],
                "costs": manifest.get("costs"),
                "metrics": manifest.get("metrics"),
                "local_checks": manifest.get("local_checks"),
                "accounting_audit": manifest.get("accounting_audit"),
                "experiment_fingerprint_sha256": manifest.get("experiment_fingerprint_sha256"),
                "python": meta["runtime"]["python"],
            },
        ),
        plan=EvalPlan(name=manifest["system"], steps=[EvalPlanStep(solver=manifest["system"], params={"answer_system_prompt": meta["prompts"]["answer_system"], "answer_user_format": meta["prompts"]["answer_user_format"]})]),
        results=EvalResults(
            total_samples=len(samples),
            completed_samples=sum(s.metadata["status"] == "success" for s in samples),
            scores=[EvalScore(name=SCORER, scorer=SCORER, scored_samples=len(graded), metrics=metrics)],
        ),
        stats=EvalStats(started_at=manifest["started_at"], completed_at=manifest.get("finished_at") or "", model_usage=model_usage, role_usage=role_usage),
        error=EvalError(message=f"Run status: {status}", traceback="", traceback_ansi="") if RUN_STATUS.get(status, "error") == "error" else None,
        samples=samples,
    )
    LOGS_DIR.mkdir(exist_ok=True)
    location = LOGS_DIR / log_name
    write_eval_log(log, location)
    return location


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_ids", nargs="*", help="Run IDs under runs/. Default: every run directory.")
    args = parser.parse_args()
    run_dirs = [RUNS_DIR / run_id for run_id in args.run_ids] or sorted(
        path for path in RUNS_DIR.iterdir() if (path / "manifest.json").exists()
    )
    for run_dir in run_dirs:
        if not (run_dir / "manifest.json").exists():
            print(f"No manifest in {run_dir}", file=sys.stderr)
            return 1
        print(f"{run_dir.name} -> {convert_run(run_dir).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
