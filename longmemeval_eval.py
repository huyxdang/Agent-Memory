#!/usr/bin/env python3
"""Minimal full-history LongMemEval-S answer-and-judge evaluation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from contextlib import nullcontext
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
# Imported once here, before any worker thread starts: importing OpenAI submodules concurrently from
# several threads raced in the import system and crashed a run with KeyError: 'openai.resources'.
from openai import OpenAI, RateLimitError  # noqa: F401

import benchmarks
import memory as memory_system
from third_party.mem0 import beam_prompts, locomo_prompts


ROOT = Path(__file__).resolve().parent
SYSTEMS = ("full-history", "memory", "mem0")
MEM0_EXTRACTION_PROMPT_TOKENS = 7_000  # Mem0's fact-extraction prompt, observed per add call; mostly served from cache
BENCHMARKS = ("longmemeval", "locomo", "beam")
MEM0_LOCOMO_PROMPTS_SHA256 = "8ebac1ef60e9ab5caf99079fdaac038b85472e81491ed35e2d2655f3927c76c2"
MEM0_BEAM_PROMPTS_SHA256 = "a1c2a4822898411f90ab2915a72d2b2031f97437bdcc1b3ac2008fe93653267b"
# Guards every mutation of the shared report and every checkpoint. API calls run outside it.
REPORT_LOCK = threading.RLock()
PAID_BUDGET = None
API_SLOTS = None


class PaidBudget:
    """Reserve uncached upper-bound cost before dispatch; retain reservations on unknown failures."""

    def __init__(self, args):
        self.args = args
        self.used = 0.0
        self.lock = threading.Lock()
        self.checkpoint = None

    def call(self, create, kwargs, embedding=False):
        judge = kwargs.get("model") == self.args.judge_model and not embedding
        input_rate = self.args.embedding_cost if embedding else (self.args.judge_input_cost if judge else self.args.answer_input_cost)
        output_rate = 0 if embedding else (self.args.judge_output_cost if judge else self.args.answer_output_cost)
        payload = kwargs.get("input") if embedding else kwargs.get("messages")
        # UTF-8 bytes exceed BPE tokens; JSON plus 512 covers message framing overhead.
        input_bound = len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) + 512
        output_bound = 0 if embedding else kwargs.get("max_completion_tokens", kwargs.get("max_tokens"))
        if output_bound is None:
            raise RuntimeError("Paid call has no explicit output cap.")
        reserve = (input_bound * input_rate + output_bound * output_rate) / 1_000_000
        with self.lock:
            if self.used + reserve > self.args.spending_limit:
                raise RuntimeError("Spending limit: cannot reserve the next call safely.")
            self.used += reserve
        if self.checkpoint:
            self.checkpoint()
        response = create(**kwargs)
        usage = response.usage
        details = getattr(usage, "prompt_tokens_details", None)
        cached = (getattr(details, "cached_tokens", 0) or 0) if details and not embedding else 0
        cached_rate = (self.args.judge_cached_input_cost if judge else self.args.answer_cached_input_cost) if cached else input_rate
        actual = (((usage.prompt_tokens or 0) - cached) * input_rate + cached * cached_rate
                  + (getattr(usage, "completion_tokens", 0) or 0) * output_rate) / 1_000_000
        with self.lock:
            self.used += max(actual, 0) - reserve
        return response
# Upper bound on memory size assumed when projecting extraction cost before any call is made.
MEMORY_PROJECTION_TOKENS = 16_000
DATASET_PATH = ROOT / "work" / "longmemeval_s_cleaned.json"
IDS_PATH = ROOT / "question_ids.json"
RUNS_DIR = ROOT / "runs"
RUN_INDEX_PATH = RUNS_DIR / "index.jsonl"
RUN_SCHEMA_VERSION = 1
TERMINAL_RUN_STATUSES = {
    "preflight_only",
    "blocked_prompt_too_large",
    "blocked_missing_paid_config",
    "blocked_spending_limit",
    "complete",
    "complete_with_failures",
    "memory_ready",
}
DATASET_REVISION = "98d7416c24c778c2fee6e6f3006e7a073259d48f"
DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
DATASET_URL = (
    "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/"
    f"{DATASET_REVISION}/longmemeval_s_cleaned.json"
)
LONGMEMEVAL_CODE_REVISION = "9e0b455f4ef0e2ab8f2e582289761153549043fc"
MEM0_CODE_REVISION = "4b61c5d31b9c668a12b4f5e78064248a02c82d2b"
MEM0_PROMPTS_SHA256 = "ba8cf60d26f1390ecbef0f07b3e950556fe3bc5a37ba4b5343f28217f18c144f"
MEM0_LLM_CLIENT_SHA256 = "b0dc8f4172ed11f7f4161df47c77ca83dd5996b075494cc39bd6a4d0a1f93701"
JUDGE_PROMPT_TEXT_SHA256 = "c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515"

ANSWER_SYSTEM_PROMPT_V1 = (
    "Answer the question using only the complete timestamped conversation history. "
    "Be direct and concise. If the history does not contain enough information, say so."
)
# The same three rules as the memory system's v2 answer prompt, worded for raw turns.
ANSWER_SYSTEM_PROMPT_V2 = """Answer the question using only the complete timestamped conversation history. Each session carries its timestamp; assistant turns record what the assistant itself recommended, listed, or wrote for the user.

- For advice or recommendation questions, tailor the answer to the user's stated preferences, interests, possessions, and past choices, and name the parts of the history you are using. Do not decline over missing incidental details such as the user's location; make reasonable suggestions from what is known.
- For questions that count things or compute dates or durations, first list the relevant turns with their session dates, then do the arithmetic, then give the answer.
- For questions about what the assistant said or recommended earlier, use the assistant turns.
- Otherwise be direct and concise. If the history truly does not contain the information, say so."""
ANSWER_SYSTEM_PROMPTS = {"v1": ANSWER_SYSTEM_PROMPT_V1, "v2": ANSWER_SYSTEM_PROMPT_V2}
ANSWER_SYSTEM_PROMPT = ANSWER_SYSTEM_PROMPT_V1  # used only for token projection before args are parsed
ANSWER_PROMPT_FORMAT = (
    "Question date: {question_date}\n\n"
    "Conversation history (chronological JSON):\n{history}\n\n"
    "Question: {question}"
)

# Copied without modification from mem0ai/memory-benchmarks at MEM0_CODE_REVISION.
JUDGE_PROMPT = """I will give you a question, a correct answer (or rubric), and a model response. Decide whether the model response is correct.

CORE PRINCIPLE — Semantic equivalence: Judge by MEANING, not exact words. Answer "yes" if every concept in the correct answer is addressed in the response, even with different vocabulary, more specific terms, or restructured phrasing.

IMPORTANT BIAS CHECK: You have a tendency to say "no" too quickly. Before concluding "no", you MUST verify the answer is truly wrong, not just differently worded. When in doubt, lean toward "yes".

Rules:

**Equivalence & Supersets**
- Equivalent or superset responses are correct. Extra details are fine unless proven to be factually wrong. Extra qualifiers are fine unless proven to be wrong. E.g., "a blue dress and a matching necklace" is correct when the answer is "a blue dress."
- If a response captures the most specific part (exact item/place/name) but omits a broader container, it's correct.
- Same factual meaning with different phrasing = correct (e.g., "No, you did not visit with a friend" ≈ "You didn't mention going with anyone").
- Adding scope qualifiers like "regular-season" or "excluding X" is fine as long as the core value is correct. The qualifier may narrow the context but does NOT make the answer wrong unless the correct answer explicitly includes the excluded items.

**Lists & Compound Terms**
- For list answers, match each item by semantic meaning. A concept is covered if restated via synonyms, sub-concepts, or related terms. Adding methodological detail or rewording verbs to near-synonyms is acceptable.
- A broad term like "A and B significance" is covered if the response addresses the topic area through related specific terms, even without naming each component literally.
- If some items as listed as "or"s, "maybe"s and potential answers, it's okay if the answer does not include those.
- If two items in a list achieve the same purpose, listing just one of them is fine.

IMPORTANT: The "anti-preference" items are very specific!
Eg. Someone "not interested in general AI topics" could be very interested in specific AI topics in general AI *conferences*; those are not the same thing and should be accepted! topics != conferences

**Numbers & Precision**
- Hedging ("at least 3", "approximately") is fine if the core number matches. A range that includes the correct answer is correct.
Generally, if the user themself would be satisfied by the response, it is acceptable. Ie. If the answer is conditional on information they would have (eg. their birthday, some hidden dependent information), and would be correct with that information, that is acceptable.
- More precise answers are correct: "22 days" matches "3 weeks"; "over $270" matches "$270."; "9 1/2 months" matches "9 months";

- Rough answers are correct: "about nine months" ≈ "9 months; "8 months and 20 days" matches "9 months";

- Off-by-one errors on days/weeks/months are acceptable.
- Approximate unit conversions are equivalent: "14 weeks" ≈ "3 months", "6 months" ≈ "half a year."
- Round time ranges generously: 7 months and 16 days ≈ 8 months.
- Notes instead of chords are acceptable when justified
- A correct number with added context (e.g., "about 5 months ago (around December 2022)") is correct — the parenthetical date is supplementary, not a contradiction.

**Dates & Temporal**
- Date format variations are equivalent: "February 1st" = "Feb 1, 2023" = "on February 1."
- Same-day event ordering swaps are acceptable.
- Outdated info alongside the correct updated answer is acceptable if the current value is identified.
- "recent" is upto 6 years ago, which means 2017+
- References like "last weekend", "last Wednesday", etc. are imprecise - people sometimes mean the weekend/Wednesday before the latest one if they're near it. "Last 3 months" can include boundary days of the 4th month back. "Last month" includes the current month so far. Be flexible with such timestamps

**Counting Edge Cases**
- If correct answer is "0" or "nothing found," model saying "not enough information" is also correct.
- Similarly, If correct answer is "not enough information", model saying "0" or "nothing found," is also correct.

**Preference/Personalization Rubrics** (apply in order):
1. Correct if the response demonstrates awareness of user's personal context (preferences, habits, interests). Need not satisfy every rubric point.
2. Primary criterion: do main suggestions align with what the user WANTS?
3. Anti-preferences: evaluate the OVERALL thrust, not keyword scanning. If the response largely suggests correct options, minor incidental references to "not-preferred" things are fine.
4. Mentioning a phone app as a MEANS to a preferred activity (e.g., meditation app for sleep) is not "suggesting phone use." Judge by the activity, not delivery mechanism.
5. "May not prefer" = mild preference, not hard prohibition. Secondary/context-dependent inclusion is fine.
6. Explicit acknowledgment of anti-preferences (e.g., "keep screens off") strengthens correctness.
7. Context-dependent suggestions are acceptable (reading is fine on a bus even if rubric flags visual attention activities). Adjacent genres alongside preferred ones are additive, not contradictory.
8. If the rubric mentions specific user resources/tools (e.g., "Suica card", "TripIt app"), the response is correct if it demonstrates awareness of the user's MAIN personal context even if it does not name every specific tool. The rubric is a guide, not a checklist.

**Abstention Matching**
- If correct answer = unanswerable/abstention, ANY phrasing that conveys "I don't have this information" is correct, regardless of what partial context is mentioned or omitted.
- Saying "not enough information" while mentioning partial related context = correct abstention.
- Saying "no record of X" or "only have plans for X, not actual dates" = correct abstention.
- The key test: does the response REFUSE to answer the question? If yes, it matches an abstention ground truth, period.

FINAL CHECK: Before answering "no," you MUST reason through these steps:
1. What is the core factual claim or intent of the correct answer?
2. Does the model response address that same claim, even in different words?
3. Is the response a superset (correct answer + extra details)?
4. For numbers: does the core number match, ignoring hedging/qualifiers?
5. For abstentions: does the response effectively decline to answer?
Only answer "no" if, after this analysis, a core concept is entirely unaddressed or contradicted.

Question: {question}

Correct Answer: {answer}

Model Response: {response}

Think step-by-step in <judge_thinking> tags, then give your final verdict as exactly "yes" or "no" on a new line after the closing tag."""

VALIDATION_CASES = [
    {
        "question_id": "e47becba",
        "question": "What degree did I graduate with?",
        "reference_answer": "Business Administration",
        "cases": [
            ("known_correct", "Business Administration", "yes"),
            ("correct_paraphrase", "I graduated with a degree in Business Administration.", "yes"),
            ("clearly_wrong", "I graduated with a Computer Science degree.", "no"),
        ],
    },
    {
        "question_id": "6a1eabeb",
        "question": "What was my personal best time in the charity 5K run?",
        "reference_answer": "25 minutes and 50 seconds (or 25:50)",
        "cases": [
            ("known_correct", "25 minutes and 50 seconds", "yes"),
            ("correct_paraphrase", "My best was 25:50.", "yes"),
            ("clearly_wrong", "My personal best was 31 minutes.", "no"),
        ],
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def atomic_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    atomic_text(path, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def download_dataset(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".download")
    print(f"Downloading {DATASET_URL}")
    with urllib.request.urlopen(DATASET_URL, timeout=60) as source, temporary.open("wb") as target:
        while chunk := source.read(1024 * 1024):
            target.write(chunk)
    digest = sha256_file(temporary)
    if digest != DATASET_SHA256:
        raise RuntimeError(f"Downloaded dataset SHA-256 mismatch: {digest}")
    temporary.replace(path)


def load_dataset(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        download_dataset(path)
    digest = sha256_file(path)
    if digest != DATASET_SHA256:
        raise RuntimeError(
            f"Dataset SHA-256 mismatch. Expected {DATASET_SHA256}, found {digest}."
        )
    data = json.loads(path.read_text())
    if not isinstance(data, list) or len(data) != 500:
        raise RuntimeError(f"Expected 500 dataset records, found {len(data) if isinstance(data, list) else 'non-list'}.")
    ids = [item.get("question_id") for item in data]
    duplicates = [key for key, count in Counter(ids).items() if count != 1]
    if duplicates:
        raise RuntimeError(f"Dataset question IDs are not unique: {duplicates}")
    return data


def load_fixture(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    required = {"question_id", "question_type", "question", "answer", "question_date", "haystack_dates", "haystack_sessions", "haystack_session_ids"}
    for item in items:
        missing = sorted(required - set(item))
        if missing:
            raise RuntimeError(f"Fixture {path} is missing fields: {missing}")
    ids = [item["question_id"] for item in items]
    if not ids or len(ids) != len(set(ids)):
        raise RuntimeError("Fixture must contain unique question IDs and at least one question.")
    return items


def load_selected(data: list[dict[str, Any]], questions_path: Path) -> list[dict[str, Any]]:
    spec = json.loads(questions_path.read_text())
    wanted = spec["questions"]
    wanted_ids = [entry["question_id"] for entry in wanted]
    if not wanted_ids or len(set(wanted_ids)) != len(wanted_ids):
        raise RuntimeError(f"{questions_path.name} must contain at least one ID and no duplicates.")
    by_id = {item["question_id"]: item for item in data}
    missing = [question_id for question_id in wanted_ids if question_id not in by_id]
    if missing:
        raise RuntimeError(f"Selected IDs missing from dataset: {missing}")
    selected = [by_id[question_id] for question_id in wanted_ids]
    mismatches = [
        item["question_id"]
        for item, expected in zip(selected, wanted, strict=True)
        if item["question_type"] != expected["question_type"]
    ]
    if mismatches:
        raise RuntimeError(f"Selected question type mismatches: {mismatches}")
    return selected


def sanitize_history(item: dict[str, Any]) -> list[dict[str, Any]]:
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    session_ids = item["haystack_session_ids"]
    if not (len(dates) == len(sessions) == len(session_ids)):
        raise RuntimeError(f"History arrays have different lengths for {item['question_id']}.")
    clean = []
    for timestamp, session in zip(dates, sessions, strict=True):
        messages = []
        for message in session:
            role = message.get("role")
            content = message.get("content")
            if role not in {"user", "assistant"} or not isinstance(content, str):
                raise RuntimeError(f"Invalid history message in {item['question_id']}.")
            messages.append({"role": role, "content": content})
        clean.append({"timestamp": timestamp, "messages": messages})
    return clean


def build_answer_prompt(item: dict[str, Any]) -> tuple[str, dict[str, int]]:
    history = sanitize_history(item)
    history_json = json.dumps(history, ensure_ascii=False, separators=(",", ":"))
    prompt = ANSWER_PROMPT_FORMAT.format(
        question_date=item["question_date"], history=history_json, question=item["question"]
    )
    check_no_label_leak(prompt)
    source_turns = sum(len(session) for session in item["haystack_sessions"])
    clean_turns = sum(len(session["messages"]) for session in history)
    if len(history) != len(item["haystack_sessions"]) or clean_turns != source_turns:
        raise RuntimeError(f"History was not preserved completely for {item['question_id']}.")
    return prompt, {"sessions": len(history), "turns": clean_turns}


def tokenizer(name: str):
    import tiktoken

    return tiktoken.get_encoding(name)


def token_count(encoding: Any, *parts: str) -> int:
    # Twelve tokens conservatively cover Chat Completions message framing.
    return sum(len(encoding.encode(part, disallowed_special=())) for part in parts) + 12


def fit_check(input_tokens: int, max_output_tokens: int, context_window: int) -> dict[str, Any]:
    framing_margin = 256
    total = input_tokens + max_output_tokens + framing_margin
    return {
        "input_tokens_estimated": input_tokens,
        "max_output_tokens": max_output_tokens,
        "framing_margin_tokens": framing_margin,
        "context_window_tokens": context_window,
        "total_reserved_tokens": total,
        "remaining_tokens": context_window - total,
        "fits": total <= context_window,
    }


def context_text_from_prompt(prompt: str) -> str:
    """The context block of an answer prompt: the history JSON or the rendered memory."""
    suffix = "\n\nQuestion: "
    for marker in (
        "Conversation history (chronological JSON):\n",
        "earlier sessions (kind | session | date | content):\n",
        "oldest first; date | memory):\n",
    ):
        if marker in prompt:
            return prompt.split(marker, 1)[1].rsplit(suffix, 1)[0]
    raise RuntimeError("Could not isolate the context block from the answer prompt.")


def check_no_label_leak(prompt: str) -> None:
    forbidden_keys = ('"has_answer":', '"answer_session_ids":', '"question_type":', '"answer":')
    leaked = [key for key in forbidden_keys if key in prompt]
    if leaked:
        raise RuntimeError(f"Evaluation label leaked into prompt: {leaked}")


def parse_locomo_label(raw: str) -> str:
    """Mem0's LoCoMo judge returns JSON with a CORRECT or WRONG label; yes/no/invalid for our records."""
    match = re.search(r'"label"\s*:\s*"(CORRECT|WRONG)"', raw, re.I)
    if not match:
        found = re.findall(r"\b(CORRECT|WRONG)\b", raw)
        if len(set(found)) != 1:
            return "invalid"
        match_label = found[-1]
    else:
        match_label = match.group(1)
    return "yes" if match_label.upper() == "CORRECT" else "no"


def parse_beam_score(raw: str) -> float | None:
    """Mem0's BEAM nugget judge returns JSON with a score of 0, 0.5, or 1; clamp anything else to those."""
    match = re.search(r'"score"\s*:\s*([0-9.]+)', raw)
    if not match:
        return None
    try:
        score = float(match.group(1))
    except ValueError:
        return None
    return min((0.0, 0.5, 1.0), key=lambda level: abs(level - score))


def parse_yes_no(raw: str) -> str:
    """Mem0's parser behavior, except no-verdict output is explicit INVALID."""
    text = raw.strip()
    if not text:
        return "invalid"
    after_cot = re.split(r"</judge_thinking>|</thinking>", text, flags=re.IGNORECASE)
    verdict_region = after_cot[-1].strip() if after_cot else text
    verdict_lines = [line.strip().lower() for line in verdict_region.splitlines() if line.strip()]
    for line in reversed(verdict_lines):
        if line in {"yes", "no"}:
            return line
    matches = re.findall(r"\b(yes|no)\b", verdict_region.lower())
    if matches:
        return matches[-1]
    lowered = text.lower()
    if lowered.startswith("yes"):
        return "yes"
    if lowered.startswith("no"):
        return "no"
    return "invalid"


def judge_explanation(raw: str) -> str | None:
    match = re.search(r"<(?:judge_thinking|thinking)>(.*?)</(?:judge_thinking|thinking)>", raw, re.I | re.S)
    return match.group(1).strip() if match else None


def usage_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    result = {
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    prompt_details = getattr(usage, "prompt_tokens_details", None)
    completion_details = getattr(usage, "completion_tokens_details", None)
    result["cached_input_tokens"] = getattr(prompt_details, "cached_tokens", 0) or 0
    result["reasoning_output_tokens"] = getattr(completion_details, "reasoning_tokens", 0) or 0
    if result["output_tokens"] is not None:
        result["non_reasoning_output_tokens"] = max(
            result["output_tokens"] - result["reasoning_output_tokens"], 0
        )
    else:
        result["non_reasoning_output_tokens"] = None
    return result


def cost_usd(
    usage: dict[str, Any],
    input_rate: float,
    cached_input_rate: float,
    output_rate: float,
) -> float | None:
    if usage["input_tokens"] is None or usage["output_tokens"] is None:
        return None
    cached_tokens = usage.get("cached_input_tokens", 0) or 0
    uncached_tokens = max(usage["input_tokens"] - cached_tokens, 0)
    return round(
        (
            uncached_tokens * input_rate
            + cached_tokens * cached_input_rate
            + usage["output_tokens"] * output_rate
        )
        / 1_000_000,
        8,
    )


def aggregate_calls(calls: list[dict[str, Any] | None]) -> dict[str, Any]:
    total = {
        "calls": 0,
        "failed_calls": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "non_reasoning_output_tokens": 0,
        "cost_usd": 0.0,
        "elapsed_seconds": 0.0,
    }
    for call in calls:
        if not call:
            continue
        total["calls"] += 1
        total["failed_calls"] += int(not call.get("ok", False))
        usage = call.get("usage") or {}
        total["unknown_usage_calls"] = total.get("unknown_usage_calls", 0) + int(
            usage.get("input_tokens") is None or usage.get("output_tokens") is None
        )
        total["unknown_cost_calls"] = total.get("unknown_cost_calls", 0) + int(call.get("cost_usd") is None)
        output_tokens = usage.get("output_tokens") or 0
        reasoning_tokens = usage.get("reasoning_output_tokens") or 0
        non_reasoning_tokens = max(output_tokens - reasoning_tokens, 0)
        usage["non_reasoning_output_tokens"] = non_reasoning_tokens
        for key, value in [
            ("input_tokens", usage.get("input_tokens") or 0),
            ("cached_input_tokens", usage.get("cached_input_tokens") or 0),
            ("output_tokens", output_tokens),
            ("reasoning_output_tokens", reasoning_tokens),
            ("non_reasoning_output_tokens", non_reasoning_tokens),
        ]:
            total[key] += value
        total["cost_usd"] += call.get("cost_usd") or 0.0
        total["elapsed_seconds"] += call.get("elapsed_seconds") or 0.0
    total["cost_usd"] = round(total["cost_usd"], 8)
    total["elapsed_seconds"] = round(total["elapsed_seconds"], 4)
    return total


def refresh_report_metrics(report: dict[str, Any]) -> None:
    if PAID_BUDGET:
        report["budget_guard"] = {
            "limit_usd": PAID_BUDGET.args.spending_limit,
            "spent_or_reserved_usd": round(PAID_BUDGET.used, 8),
            "note": "Includes in-flight reservations and retained reservations for failures with unknown billing.",
        }
    encoding = tokenizer(report["metadata"]["models"]["tokenizer"])
    context_total = 0
    for record in report["results"]:
        if record.get("answer_prompt"):
            context_text = context_text_from_prompt(record["answer_prompt"])
            record["context_tokens"] = len(encoding.encode(context_text, disallowed_special=()))
            context_total += record["context_tokens"]
        else:
            record["context_tokens"] = None

    memory_writing = aggregate_calls(
        [
            call for record in report["results"]
            for call in (record.get("memory") or {}).get("extraction_calls", [])
            if not (record.get("memory") or {}).get("reused_from_run")
        ]
    )
    answer_calls = [call for record in report["results"] for call in record.get("prior_answer_calls", []) + [record.get("answer_call")]]
    judge_calls = [call for record in report["results"] for call in record.get("prior_judge_calls", []) + [record.get("judge_call")]]
    answering = aggregate_calls(answer_calls)
    benchmark_judging = aggregate_calls(
        judge_calls
    )
    judge_controls = aggregate_calls(
        [item.get("judge_call") for item in report["judge_validation"]]
    )
    all_judging = aggregate_calls(
        judge_calls
        + [item.get("judge_call") for item in report["judge_validation"]]
    )
    report["metrics"] = {
        "tokenizer": report["metadata"]["models"]["tokenizer"],
        "context_tokens": {
            "definition": "Tokens in the context block supplied to the answerer (history JSON for full-history, rendered memory for memory); excludes instructions and question.",
            "total_across_questions": context_total,
        },
        "memory_writing": {"applicable": report["run"]["system"] in {"memory", "mem0"}, **memory_writing},
        "answering": answering,
        "judge_internal": {
            "excluded_from_reported_system_cost": True,
            "benchmark": benchmark_judging,
            "validation_controls": judge_controls,
            "total": all_judging,
        },
    }
    projected = report.get("costs", {}).get("projected_max_usd")
    system_cost = round(answering["cost_usd"] + memory_writing["cost_usd"], 8)
    report["costs"] = {
        "projected_max_usd": projected,
        "reported_system_cost_usd": system_cost,
        "answering_usd": answering["cost_usd"],
        "memory_writing_usd": memory_writing["cost_usd"],
        "judging_internal_usd": all_judging["cost_usd"],
        "judge_controls_internal_usd": judge_controls["cost_usd"],
        "total_api_spend_usd": round(system_cost + all_judging["cost_usd"], 8),
    }


def api_call(
    client: Any,
    model: str,
    system: str,
    user: str,
    max_tokens: int,
    reasoning_effort: str | None = None,
    response_format: dict[str, Any] | None = None,
    user_messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """One chat call. `user_messages` replaces the single `user` string when the prompt is several messages."""
    start = time.perf_counter()
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else [])
        + (user_messages if user_messages is not None else [{"role": "user", "content": user}]),
    }
    if model.lower().startswith(("gpt-5", "o1", "o3", "o4")):
        kwargs["max_completion_tokens"] = max_tokens
    else:
        kwargs["max_tokens"] = max_tokens
        kwargs["temperature"] = 0
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort
    if response_format:
        kwargs["response_format"] = response_format
    rate_limit_retries = 0
    rate_limit_wait_seconds = 0.0
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        while True:
            try:
                with API_SLOTS if API_SLOTS is not None else nullcontext():
                    response = (PAID_BUDGET.call(client.chat.completions.create, kwargs)
                                if PAID_BUDGET else client.chat.completions.create(**kwargs))
                break
            except RateLimitError:
                # Tokens-per-minute limits need a longer wait than the client's built-in retries give.
                if rate_limit_retries >= 6:
                    raise
                wait_start = time.perf_counter()
                time.sleep(min(60.0, 5.0 * 2 ** rate_limit_retries))
                rate_limit_wait_seconds += time.perf_counter() - wait_start
                rate_limit_retries += 1
        elapsed = time.perf_counter() - start
        content = response.choices[0].message.content
        result = {
            "elapsed_seconds": round(elapsed, 4),
            "rate_limit_retries": rate_limit_retries,
            "rate_limit_wait_seconds": round(rate_limit_wait_seconds, 6),
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "requested_model": model,
            "reasoning_effort": reasoning_effort,
            "max_output_tokens": max_tokens,
            "resolved_model": response.model,
            "system_fingerprint": getattr(response, "system_fingerprint", None),
            "finish_reason": response.choices[0].finish_reason,
            "usage": usage_dict(response.usage),
        }
        if response.choices[0].finish_reason == "length":
            return {**result, "ok": False, "content": content or "", "error_type": "OutputTokenLimit",
                    "error": "Output reached its token cap; incomplete output is not accepted."}
        if not content:
            return {
                **result,
                "ok": False,
                "error_type": "EmptyModelResponse",
                "error": f"API returned empty content; finish_reason={response.choices[0].finish_reason}",
            }
        return {**result, "ok": True, "content": content.strip()}
    except Exception as exc:
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "rate_limit_retries": rate_limit_retries,
            "rate_limit_wait_seconds": round(rate_limit_wait_seconds, 6),
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.perf_counter() - start, 4),
            "requested_model": model,
            "reasoning_effort": reasoning_effort,
            "max_output_tokens": max_tokens,
            "resolved_model": None,
            "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
        }


def mem0_answer_system_prompt() -> str:
    import mem0_system

    return mem0_system.ANSWER_SYSTEM_PROMPT


def mem0_answer_prompt_format() -> str:
    import mem0_system

    return mem0_system.ANSWER_PROMPT_FORMAT


def git_metadata() -> dict[str, Any]:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    return {"git_head": head, "git_dirty": dirty, "script_sha256": sha256_file(Path(__file__))}


def package_versions() -> dict[str, str]:
    names = ["openai", "python-dotenv", "tiktoken"]
    return {name: importlib.metadata.version(name) for name in names}


def base_metadata(args: argparse.Namespace) -> dict[str, Any]:
    if args.benchmark == "longmemeval":
        dataset = {
            "repository": "xiaowu0162/longmemeval-cleaned",
            "file": DATASET_PATH.name,
            "revision": DATASET_REVISION,
            "sha256": DATASET_SHA256,
        }
    else:
        dataset = {
            "benchmark": args.benchmark,
            "file": DATASET_PATH.name,
            "sources": {str(path.relative_to(ROOT)): sha256_file(path) for path in benchmarks.source_files(args.benchmark)},
        }
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": args.benchmark,
        "dataset": dataset,
        "upstream_code": {
            "longmemeval_revision": LONGMEMEVAL_CODE_REVISION,
            "mem0_memory_benchmarks_revision": MEM0_CODE_REVISION,
            "mem0_prompts_sha256": MEM0_PROMPTS_SHA256,
            "mem0_llm_client_sha256": MEM0_LLM_CLIENT_SHA256,
            "mem0_locomo_prompts_sha256": MEM0_LOCOMO_PROMPTS_SHA256,
            "mem0_beam_prompts_sha256": MEM0_BEAM_PROMPTS_SHA256,
        },
        "local_code": git_metadata(),
        "runtime": {"python": platform.python_version(), "packages": package_versions()},
        "models": {
            "answer_requested": args.answer_model,
            "answer_reasoning_effort": args.answer_reasoning_effort,
            "extraction_requested": args.extraction_model,
            "extraction_reasoning_effort": args.extraction_reasoning_effort,
            "extraction_max_tokens": args.extraction_max_tokens,
            "judge_requested": args.judge_model,
            "judge_reasoning_effort": "provider default (matches pinned Mem0 runner)",
            "answer_context_window": args.answer_context_window,
            "answer_max_tokens": args.answer_max_tokens,
            "judge_max_tokens": args.judge_max_tokens,
            "tokenizer": args.tokenizer,
        },
        "prices_usd_per_million_tokens": {
            "answer_input": args.answer_input_cost,
            "answer_cached_input": args.answer_cached_input_cost,
            "answer_output": args.answer_output_cost,
            "judge_input": args.judge_input_cost,
            "judge_cached_input": args.judge_cached_input_cost,
            "judge_output": args.judge_output_cost,
        },
        "spending_limit_usd": args.spending_limit,
        "mem0": {
            "package": "mem0ai " + importlib.metadata.version("mem0ai"),
            "llm": {"model": args.extraction_model, "reasoning_effort": args.extraction_reasoning_effort},
            "embedder": "text-embedding-3-small",
            "vector_store": "qdrant, local directory per question",
            "top_k": args.mem0_top_k,
            "chunk_messages": args.mem0_chunk_messages,
            "date_handling": "OSS SDK rejects the platform timestamp parameter; the session date is passed as metadata and as a leading line of each chunk.",
        } if args.system == "mem0" else None,
        "prompts": {
            "answer_prompt_version": args.answer_prompt,
            "answer_system": {
                "full-history": ANSWER_SYSTEM_PROMPTS[args.answer_prompt],
                "memory": memory_system.ANSWER_SYSTEM_PROMPTS[args.answer_prompt],
                "mem0": mem0_answer_system_prompt(),
            }[args.system],
            "answer_user_format": {
                "full-history": ANSWER_PROMPT_FORMAT,
                "memory": memory_system.ANSWER_PROMPT_FORMAT,
                "mem0": mem0_answer_prompt_format(),
            }[args.system],
            "extraction_system_template": memory_system.EXTRACTION_SYSTEM_TEMPLATE if args.system == "memory" else None,
            "extraction_message_formats": {
                "memory": memory_system.MEMORY_MESSAGE_FORMAT,
                "empty_memory": memory_system.EMPTY_MEMORY_MESSAGE,
                "session": memory_system.SESSION_MESSAGE_FORMAT,
                "cache_breakpoint_on_last_memory_message": memory_system.CACHE_BREAKPOINT,
            } if args.system == "memory" else None,
            "extraction_response_format": memory_system.EXTRACTION_RESPONSE_FORMAT if args.system == "memory" else None,
            "judge": JUDGE_PROMPT,
        },
    }


def preflight(
    selected: list[dict[str, Any]], args: argparse.Namespace
) -> tuple[list[dict[str, Any]], float | None]:
    encoding = tokenizer(args.tokenizer)
    records = []
    projected_histories = set()
    upper_cost = 0.0
    rates = [
        args.answer_input_cost, args.answer_output_cost,
        args.judge_input_cost, args.judge_output_cost,
    ]
    prices_complete = all(rate is not None for rate in rates)
    for item in selected:
        clean_history = sanitize_history(item)
        history_json = json.dumps(clean_history, ensure_ascii=False, separators=(",", ":"))
        record: dict[str, Any] = {
            "question_id": item["question_id"],
            "question_type": item["question_type"],
            "question": item["question"],
            "reference_answer": str(item["answer"]),
            "judge": item.get("judge", "longmemeval"),
            "rubric": item.get("rubric"),
            "judge_score": None,
            "history": {"sessions": len(clean_history), "turns": sum(len(s["messages"]) for s in clean_history)},
            "history_sha256": sha256_text(history_json),
            "answer_prompt_sha256": None,
            "answer_prompt": None,
            "prompt_fit": None,
            "status": "not_run",
            "generated_answer": None,
            "judge_verdict": None,
            "judge_explanation": None,
            "answer_call": None,
            "judge_call": None,
        }
        if args.system == "full-history":
            prompt, _ = build_answer_prompt(item)
            answer_input = token_count(encoding, ANSWER_SYSTEM_PROMPTS[args.answer_prompt], prompt)
            record["answer_prompt_sha256"] = sha256_text(prompt)
            record["answer_prompt"] = prompt
            record["prompt_fit"] = fit_check(answer_input, args.answer_max_tokens, args.answer_context_window)
        elif args.system == "mem0":
            # One Mem0 add per chunk, each an LLM call over the extraction prompt plus the chunk, output capped by Mem0 at 2,000.
            adds = 0
            add_input = 0
            for session in clean_history:
                chunks = [session["messages"][i:i + args.mem0_chunk_messages] for i in range(0, len(session["messages"]), args.mem0_chunk_messages)]
                for chunk in chunks:
                    adds += 1
                    add_input += MEM0_EXTRACTION_PROMPT_TOKENS + token_count(encoding, *(m["content"] for m in chunk))
            if prices_complete and not args.memory_from:
                upper_cost += (add_input * 1.02 * args.answer_input_cost + adds * 2_000 * args.answer_output_cost) / 1_000_000
            record["extraction_fit"] = {"fits": True, "remaining_tokens": None, "mem0_adds": adds, "projected_input_tokens": add_input}
            record["memory"] = {"lines": [], "extraction_calls": [], "failures": [], "sessions_done": 0, "engine": "mem0", "retrieved": None}
            answer_input = token_count(encoding, mem0_answer_system_prompt(), item["question_date"], item["question"]) + MEMORY_PROJECTION_TOKENS
        else:
            # Extraction prompts are projected with an assumed memory size; the answer prompt exists only after extraction.
            worst = None
            session_count = len(clean_history)
            extraction_system = memory_system.extraction_system_prompt(item.get("subject"))
            for index, session in enumerate(clean_history, start=1):
                parts = memory_system.extraction_parts([], index, session_count, session["timestamp"], session["messages"])
                extraction_input = token_count(encoding, extraction_system, *parts) + MEMORY_PROJECTION_TOKENS
                fit = fit_check(extraction_input, args.extraction_max_tokens, args.answer_context_window)
                if worst is None or fit["remaining_tokens"] < worst["remaining_tokens"]:
                    worst = fit
                history_key = (record["history_sha256"], item.get("subject"))
                if prices_complete and not args.memory_from and history_key not in projected_histories:
                    upper_cost += (
                        extraction_input * 1.02 * args.answer_input_cost
                        + args.extraction_max_tokens * args.answer_output_cost
                    ) / 1_000_000
            record["extraction_fit"] = {**worst, "assumed_memory_tokens": MEMORY_PROJECTION_TOKENS}
            record["memory"] = {"lines": [], "extraction_calls": [], "failures": [], "sessions_done": 0, "subject": item.get("subject") or memory_system.USER_SUBJECT}
            projected_histories.add(history_key)
            answer_input = token_count(encoding, memory_system.ANSWER_SYSTEM_PROMPT, item["question_date"], item["question"]) + MEMORY_PROJECTION_TOKENS
        judge_static = JUDGE_PROMPT.format(
            question=item["question"], answer=str(item["answer"]), response=""
        )
        judge_upper_tokens = token_count(encoding, judge_static) + args.answer_max_tokens
        if prices_complete and not (args.system == "memory" and args.memory_stage == "build"):
            upper_cost += (
                answer_input * 1.02 * args.answer_input_cost
                + args.answer_max_tokens * args.answer_output_cost
                + judge_upper_tokens * 1.02 * args.judge_input_cost
                + args.judge_max_tokens * args.judge_output_cost
            ) / 1_000_000
        records.append(record)
    controls = VALIDATION_CASES if args.benchmark == "longmemeval" and not (args.system == "memory" and args.memory_stage == "build") else []
    for validation in controls:
        for _, response, _ in validation["cases"]:
            prompt = JUDGE_PROMPT.format(
                question=validation["question"],
                answer=validation["reference_answer"],
                response=response,
            )
            if prices_complete:
                upper_cost += (
                    token_count(encoding, prompt) * 1.02 * args.judge_input_cost
                    + args.judge_max_tokens * args.judge_output_cost
                ) / 1_000_000
    return records, round(upper_cost, 8) if prices_complete else None


def audit_results(expected_ids: list[str], records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(record.get("question_id") for record in records)
    missing = [question_id for question_id in expected_ids if counts[question_id] == 0]
    duplicates = [question_id for question_id in expected_ids if counts[question_id] != 1]
    unexpected = [question_id for question_id in counts if question_id not in expected_ids]
    return {
        "expected_count": len(expected_ids),
        "record_count": len(records),
        "missing_ids": missing,
        "duplicate_or_wrong_count_ids": duplicates,
        "unexpected_ids": unexpected,
        "all_selected_exactly_once": len(records) == len(expected_ids) and not missing and not duplicates and not unexpected,
        "failures": [
            {
                "question_id": record["question_id"],
                "status": record["status"],
                "detail": issue_detail(record),
            }
            for record in records
            if record["status"] != "success"
        ],
    }


def issue_detail(record: dict[str, Any]) -> str:
    if record.get("status") == "not_run":
        return "No paid API call was made."
    extraction_calls = (record.get("memory") or {}).get("extraction_calls", [])
    for call in extraction_calls:
        if call.get("error"):
            return f"Session {call.get('session')} {call.get('error_type', 'API error')}: {call['error']}"
    for key in ("answer_call", "judge_call"):
        call = record.get(key) or {}
        if call.get("error"):
            return f"{call.get('error_type', 'API error')}: {call['error']}"
    if record.get("status") == "invalid_judge_response":
        raw = (record.get("judge_call") or {}).get("content")
        return f"No valid yes/no verdict. Raw response: {raw}"
    return ""


def markdown_cell(value: Any) -> str:
    if value is None:
        return "NOT RUN"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    run_meta = report["run"]
    lines = [
        "# LongMemEval five-question results",
        "",
        f"- Run ID: `{run_meta['run_id']}`",
        f"- System: `{run_meta['system']}`",
        f"- Run status: `{report['run_status']}`",
        f"- Retry of: `{run_meta['retry_of'] or 'none'}`",
        f"- Dataset revision: `{meta['dataset'].get('revision', meta['dataset'].get('benchmark'))}`",
        f"- Dataset SHA-256: `{meta['dataset'].get('sha256', 'see sources in manifest')}`",
        f"- Mem0 revision: `{meta['upstream_code']['mem0_memory_benchmarks_revision']}`",
        f"- Answer model requested: `{meta['models']['answer_requested'] or 'NOT CONFIGURED'}`",
        f"- Judge model requested: `{meta['models']['judge_requested'] or 'NOT CONFIGURED'}`",
        "",
        "## Local checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in report["local_checks"]:
        lines.append(
            f"| {markdown_cell(check['check'])} | {markdown_cell(check['status'])} | "
            f"{markdown_cell(check['detail'])} |"
        )
    if "pipeline" in report:
        pipeline = report["pipeline"]
        timing = report.get("timing", {})
        lines += ["", "## Shared-memory pipeline", "",
                  f"- Schedule: {pipeline['schedule']}; mode: {pipeline['mode']}",
                  f"- Unique builds: {pipeline['unique_histories']}; questions: {pipeline['questions']}",
                  f"- Recorded run wall seconds: {timing.get('recorded_run_elapsed_seconds', 'running')}",
                  f"- Seconds to first graded answer: {timing.get('seconds_to_first_graded', 'not available')}",
                  f"- Seconds to all graded answers: {timing.get('seconds_to_all_graded', 'not complete')}",
                  "- Writing is counted once per build; per-stage elapsed times overlap and must not be summed as wall time."]
    lines += [
        "",
        "## Prompt fit",
        "",
        "| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for record in report["results"]:
        fit = record.get("prompt_fit")
        if fit is None:
            lines.append(f"| {record['question_id']} | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |")
            continue
        lines.append(
            f"| {record['question_id']} | {record['context_tokens']} | {fit['input_tokens_estimated']} | "
            f"{fit['max_output_tokens']} | {fit['framing_margin_tokens']} | "
            f"{fit['context_window_tokens']} | {fit['remaining_tokens']} | {fit['fits']} |"
        )
    metrics = report["metrics"]
    writing = metrics["memory_writing"]
    answering = metrics["answering"]
    judging = metrics["judge_internal"]["total"]
    lines += [
        "",
        "## Tracking summary",
        "",
        f"Fixed tokenizer: `{metrics['tokenizer']}`. Output tokens include reasoning tokens; "
        "non-reasoning output is output minus reasoning.",
        "",
        "| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Memory writing{'' if writing['applicable'] else ' (not applicable)'} | {writing['input_tokens']} | "
        f"{writing['output_tokens']} | {writing['reasoning_output_tokens']} | {writing['non_reasoning_output_tokens']} | "
        f"{writing['cost_usd']} | {writing['elapsed_seconds']} |",
        f"| Answering | {answering['input_tokens']} | {answering['output_tokens']} | "
        f"{answering['reasoning_output_tokens']} | {answering['non_reasoning_output_tokens']} | "
        f"{answering['cost_usd']} | {answering['elapsed_seconds']} |",
        f"| Judge (internal only) | {judging['input_tokens']} | {judging['output_tokens']} | "
        f"{judging['reasoning_output_tokens']} | {judging['non_reasoning_output_tokens']} | "
        f"{judging['cost_usd']} | {judging['elapsed_seconds']} |",
        "",
        f"- Reported system cost (judge excluded): `{report['costs']['reported_system_cost_usd']}`",
        f"- Total API spend (judge included): `{report['costs']['total_api_spend_usd']}`",
    ]
    if run_meta["system"] in ("memory", "mem0"):
        lines += ["", "## Memory stores", ""]
        for record in report["results"]:
            store = record.get("memory") or {}
            lines += [
                f"### {record['question_id']}",
                "",
                f"- Sessions written: {store.get('sessions_done', 0)} of {record['history']['sessions']}",
                f"- Lines: {len(store.get('lines', []))}; flagged lines: {len(store.get('failures', []))}",
                "",
                "```text",
                memory_system.render_store(store.get("lines", [])),
                "```",
                "",
            ]
            if store.get("failures"):
                lines += ["| Session | Key | Value | Flags |", "|---|---|---|---|"]
                for failure in store["failures"]:
                    lines.append(
                        f"| {failure['session']} | {markdown_cell(failure['key'])} | {markdown_cell(failure['value'])} | "
                        f"{markdown_cell(', '.join(failure['codes']))} |"
                    )
                lines.append("")
            lines += ["| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
            for call in store.get("extraction_calls", []):
                usage = call.get("usage") or {}
                lines.append(
                    f"| {call.get('session')} | {markdown_cell(usage.get('input_tokens'))} | {markdown_cell(usage.get('cached_input_tokens'))} | "
                    f"{markdown_cell(usage.get('output_tokens'))} | {markdown_cell(usage.get('reasoning_output_tokens'))} | "
                    f"{markdown_cell(call.get('new_lines'))} | {markdown_cell(call.get('cost_usd'))} | {markdown_cell(call.get('elapsed_seconds'))} |"
                )
            lines.append("")
    lines += [
        "",
        "## Answers and grades",
        "",
        "| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for record in report["results"]:
        lines.append(
            "| " + " | ".join(
                markdown_cell(record.get(key))
                for key in [
                    "question_id", "question_type", "question", "reference_answer",
                    "generated_answer", "judge_verdict", "judge_explanation", "status",
                ]
            ) + " |"
        )
    lines += [
        "",
        "## Answering usage",
        "",
        "| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for record in report["results"]:
        call = record.get("answer_call") or {}
        usage = call.get("usage") or {}
        lines.append(
            f"| {record['question_id']} | {markdown_cell(usage.get('input_tokens'))} | "
            f"{markdown_cell(usage.get('output_tokens'))} | "
            f"{markdown_cell(usage.get('reasoning_output_tokens'))} | "
            f"{markdown_cell(usage.get('non_reasoning_output_tokens'))} | "
            f"{markdown_cell(call.get('cost_usd'))} | "
            f"{markdown_cell(call.get('elapsed_seconds'))} | {markdown_cell(call.get('resolved_model'))} |"
        )
    lines += [
        "",
        "## Judging usage",
        "",
        "| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    judge_rows = [(record["question_id"], record.get("judge_call")) for record in report["results"]]
    judge_rows += [("validation:" + item["case_id"], item.get("judge_call")) for item in report["judge_validation"]]
    for label, call_or_none in judge_rows:
        call = call_or_none or {}
        usage = call.get("usage") or {}
        lines.append(
            f"| {label} | {markdown_cell(usage.get('input_tokens'))} | "
            f"{markdown_cell(usage.get('output_tokens'))} | "
            f"{markdown_cell(usage.get('reasoning_output_tokens'))} | "
            f"{markdown_cell(usage.get('non_reasoning_output_tokens'))} | "
            f"{markdown_cell(call.get('cost_usd'))} | "
            f"{markdown_cell(call.get('elapsed_seconds'))} | {markdown_cell(call.get('resolved_model'))} |"
        )
    lines += [
        "",
        "## Judge validation",
        "",
        "| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report["judge_validation"]:
        lines.append(
            "| " + " | ".join(
                markdown_cell(item.get(key))
                for key in ["case_id", "supplied_answer", "expected", "actual", "agreement", "status"]
            ) + f" | {markdown_cell(issue_detail(item))} |"
        )
    audit = report["accounting_audit"]
    lines += [
        "",
        "## Accounting and failures",
        "",
        f"- All selected questions exactly once: `{audit['all_selected_exactly_once']}`",
        f"- Missing IDs: `{audit['missing_ids']}`",
        f"- Duplicate or wrong-count IDs: `{audit['duplicate_or_wrong_count_ids']}`",
        f"- Unexpected IDs: `{audit['unexpected_ids']}`",
        f"- Failures: `{audit['failures']}`",
        f"- Projected maximum cost: `{markdown_cell(report['costs']['projected_max_usd'])}`",
        f"- Reported system cost, excluding judge: `{markdown_cell(report['costs']['reported_system_cost_usd'])}`",
        f"- Internal judging cost: `{markdown_cell(report['costs']['judging_internal_usd'])}`",
        f"- Total API spend: `{markdown_cell(report['costs']['total_api_spend_usd'])}`",
        "",
    ]
    return "\n".join(lines)


def validated_run_dir(run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id):
        raise RuntimeError(f"Invalid run ID: {run_id!r}")
    return RUNS_DIR / run_id


def question_set_sha256(report: dict[str, Any]) -> str:
    ids = [record["question_id"] for record in report["results"]]
    return sha256_text(json.dumps(ids, separators=(",", ":")))


def experiment_fingerprint(report: dict[str, Any]) -> str:
    metadata = report["metadata"]
    payload = {
        "system": report["run"]["system"],
        "dataset": metadata["dataset"],
        "upstream_code": metadata["upstream_code"],
        # The script hash is recorded in local_code for provenance but kept out of the fingerprint:
        # a bug fix must not strand every unfinished run. What changes results is listed here.
        "models": metadata["models"],
        "prices": metadata["prices_usd_per_million_tokens"],
        "spending_limit_usd": metadata["spending_limit_usd"],
        "prompts": metadata["prompts"],
        "mem0_context": metadata.get("mem0"),
        "execution": metadata.get("execution"),
        "questions": [
            {
                "question_id": record["question_id"],
                "history_sha256": record.get("history_sha256"),
                "answer_prompt_sha256": record["answer_prompt_sha256"] if report["run"]["system"] == "full-history" else None,
            }
            for record in report["results"]
        ],
    }
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def build_manifest(report: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        key: value for key, value in report.items() if key not in {"results", "run"}
    }
    manifest.update(report["run"])
    manifest["schema_version"] = RUN_SCHEMA_VERSION
    manifest["status"] = manifest.pop("run_status")
    manifest["question_ids"] = [record["question_id"] for record in report["results"]]
    manifest["question_set_sha256"] = question_set_sha256(report)
    manifest["experiment_fingerprint_sha256"] = experiment_fingerprint(report)
    return manifest


def load_run(run_id: str) -> dict[str, Any]:
    directory = validated_run_dir(run_id)
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("schema_version") != RUN_SCHEMA_VERSION:
        raise RuntimeError(f"Unsupported run schema in {directory}.")
    records = [
        json.loads(line)
        for line in (directory / "results.jsonl").read_text().split("\n")
        if line.strip()
    ]
    run_keys = {"run_id", "system", "retry_of", "started_at", "finished_at", "backfill"}
    report = {
        key: value
        for key, value in manifest.items()
        if key not in {
            "schema_version",
            "status",
            "question_ids",
            "question_set_sha256",
            "experiment_fingerprint_sha256",
        } | run_keys
    }
    report["run"] = {key: manifest.get(key) for key in run_keys if key in manifest}
    report["run_status"] = manifest["status"]
    report["results"] = records
    expected_ids = manifest["question_ids"]
    audit = audit_results(expected_ids, records)
    if not audit["all_selected_exactly_once"]:
        raise RuntimeError(f"Run {run_id} failed exactly-once validation: {audit}")
    return report


def checkpoint_run(report: dict[str, Any]) -> None:
    with REPORT_LOCK:
        expected_ids = [record["question_id"] for record in report["results"]]
        report["accounting_audit"] = audit_results(expected_ids, report["results"])
        if report["metadata"].get("execution", {}).get("stage") == "build":
            report["accounting_audit"]["failures"] = [
                row for row in report["accounting_audit"]["failures"] if row["status"] != "memory_complete"
            ]
            report["accounting_audit"]["note"] = "Build-only: answers and grades intentionally not requested; not a completed QA benchmark."
        refresh_report_metrics(report)
        directory = validated_run_dir(report["run"]["run_id"])
        manifest_path = directory / "manifest.json"
        if manifest_path.exists():
            existing = json.loads(manifest_path.read_text())
            if existing.get("status") in TERMINAL_RUN_STATUSES:
                raise RuntimeError(f"Run {report['run']['run_id']} is immutable because it is terminal.")
        directory.mkdir(parents=True, exist_ok=True)
        atomic_json(manifest_path, build_manifest(report))
        atomic_jsonl(directory / "results.jsonl", report["results"])
        atomic_text(directory / "summary.md", render_markdown(report))


def index_row(report: dict[str, Any]) -> dict[str, Any]:
    results = report["results"]
    yes_count = sum(record.get("judge_verdict") == "yes" for record in results)
    graded_count = sum(record.get("judge_verdict") in {"yes", "no"} for record in results)
    answer_models = sorted(
        {
            call["resolved_model"]
            for record in results
            if (call := record.get("answer_call")) and call.get("resolved_model")
        }
    )
    judge_calls = [record.get("judge_call") for record in results]
    judge_calls += [item.get("judge_call") for item in report["judge_validation"]]
    judge_models = sorted(
        {call["resolved_model"] for call in judge_calls if call and call.get("resolved_model")}
    )
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "run_id": report["run"]["run_id"],
        "system": report["run"]["system"],
        "status": report["run_status"],
        "retry_of": report["run"]["retry_of"],
        "started_at": report["run"]["started_at"],
        "finished_at": report["run"]["finished_at"],
        "question_set_sha256": question_set_sha256(report),
        "questions": len(results),
        "yes": yes_count,
        "graded": graded_count,
        "accuracy_all_questions": round(yes_count / len(results), 6) if results else None,
        "accuracy_graded": round(yes_count / graded_count, 6) if graded_count else None,
        "failures": len(report["accounting_audit"]["failures"]),
        "context_tokens": report["metrics"]["context_tokens"]["total_across_questions"],
        "memory_writing_input_tokens": report["metrics"]["memory_writing"]["input_tokens"],
        "memory_writing_output_tokens": report["metrics"]["memory_writing"]["output_tokens"],
        "answering_input_tokens": report["metrics"]["answering"]["input_tokens"],
        "answering_output_tokens": report["metrics"]["answering"]["output_tokens"],
        "answering_reasoning_tokens": report["metrics"]["answering"]["reasoning_output_tokens"],
        "reported_system_cost_usd": report["costs"]["reported_system_cost_usd"],
        "judging_internal_usd": report["costs"]["judging_internal_usd"],
        "total_api_spend_usd": report["costs"]["total_api_spend_usd"],
        "answer_models_resolved": answer_models,
        "judge_models_resolved": judge_models,
        "git_head": report["metadata"]["local_code"]["git_head"],
        "script_sha256": report["metadata"]["local_code"]["script_sha256"],
    }


def append_run_index(report: dict[str, Any]) -> None:
    row = index_row(report)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    existing_rows = []
    if RUN_INDEX_PATH.exists():
        existing_rows = [
            json.loads(line) for line in RUN_INDEX_PATH.read_text().split("\n") if line.strip()
        ]
    matching = [item for item in existing_rows if item.get("run_id") == row["run_id"]]
    if matching == [row]:
        return
    if matching:  # a reopened run finalizes again: replace its row
        rows = [row if item.get("run_id") == row["run_id"] else item for item in existing_rows]
        atomic_jsonl(RUN_INDEX_PATH, rows)
        return
    with RUN_INDEX_PATH.open("a") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def finalize_run(report: dict[str, Any]) -> None:
    if report["run_status"] not in TERMINAL_RUN_STATUSES:
        raise RuntimeError(f"Cannot finalize non-terminal status {report['run_status']}.")
    if report["run"]["finished_at"] is None:
        report["run"]["finished_at"] = datetime.now(timezone.utc).isoformat()
    if "timing" in report:
        report["timing"]["recorded_run_elapsed_seconds"] = (
            datetime.fromisoformat(report["run"]["finished_at"]) - datetime.fromisoformat(report["run"]["started_at"])
        ).total_seconds()
        report["timing"]["boundary"] = "Run creation through immediately before terminal checkpoint, matching historical manifest timing."
    checkpoint_run(report)
    append_run_index(report)


def make_run_metadata(system: str, retry_of: str | None) -> dict[str, Any]:
    if retry_of:
        parent_manifest = validated_run_dir(retry_of) / "manifest.json"
        if not parent_manifest.exists():
            raise RuntimeError(f"Retry parent run does not exist: {retry_of}")
    now = datetime.now(timezone.utc)
    git_head = git_metadata()["git_head"]
    code_suffix = (git_head or sha256_file(Path(__file__)))[:7]
    run_id = f"{now.strftime('%Y%m%dT%H%M%S%fZ')}_{system}_{code_suffix}"
    return {
        "run_id": run_id,
        "system": system,
        "retry_of": retry_of,
        "started_at": now.isoformat(),
        "finished_at": None,
    }


def resume_run(current_report: dict[str, Any], run_id: str, retry_failed: bool = False) -> dict[str, Any]:
    saved = load_run(run_id)
    if saved["run_status"] in TERMINAL_RUN_STATUSES:
        if not (retry_failed and saved["run_status"] == "complete_with_failures"):
            raise RuntimeError(
                f"Run {run_id} is terminal ({saved['run_status']}); start a new run with --retry-of {run_id}."
            )
    if experiment_fingerprint(saved) != experiment_fingerprint(current_report):
        raise RuntimeError(
            "Resume configuration does not match the saved experiment fingerprint. "
            "Use the original code/configuration or start a new run."
        )
    if saved["run_status"] == "complete_with_failures":
        # Reopen: the failed questions are retried, the run finalizes again, and its index row is replaced.
        saved["run_status"] = "running"
        saved["run"]["finished_at"] = None
        saved.setdefault("reopened", []).append(datetime.now(timezone.utc).isoformat())
        atomic_json(validated_run_dir(run_id) / "manifest.json", build_manifest(saved))
    return saved


def legacy_run_id(report: dict[str, Any]) -> str:
    created_at = datetime.fromisoformat(report["metadata"]["created_at"].replace("Z", "+00:00"))
    local_code = report["metadata"]["local_code"]
    code_suffix = (local_code.get("git_head") or local_code["script_sha256"])[:7]
    return f"{created_at.strftime('%Y%m%dT%H%M%S%fZ')}_full-history_{code_suffix}"


def backfill_legacy_report(path: Path) -> str:
    source_sha256 = sha256_file(path)
    report = json.loads(path.read_text())
    run_id = legacy_run_id(report)
    directory = validated_run_dir(run_id)
    if (directory / "manifest.json").exists():
        existing = json.loads((directory / "manifest.json").read_text())
        existing_backfill = existing.get("backfill", {})
        if existing_backfill.get("source_sha256") == source_sha256:
            append_run_index(load_run(run_id))
            return run_id
        raise RuntimeError(f"Backfill run ID collision for {run_id}.")

    postprocessing = report["metadata"].get("postprocessing", {})
    report["run"] = {
        "run_id": run_id,
        "system": "full-history",
        "retry_of": None,
        "started_at": report["metadata"]["created_at"],
        "finished_at": postprocessing.get("updated_at"),
        "backfill": {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "source_path": str(path),
            "source_sha256": source_sha256,
            "finished_at_note": (
                "Derived from postprocessing timestamp."
                if postprocessing.get("updated_at")
                else "Exact legacy finish time was not recorded."
            ),
        },
    }
    expected_ids = [record["question_id"] for record in report["results"]]
    report["accounting_audit"] = audit_results(expected_ids, report["results"])
    if not report["accounting_audit"]["all_selected_exactly_once"]:
        raise RuntimeError(f"Legacy report failed exactly-once validation: {path}")
    checkpoint_run(report)
    append_run_index(report)
    return run_id


def backfill_legacy_reports(paths: list[Path]) -> int:
    for path in paths:
        run_id = backfill_legacy_report(path)
        print(f"Backfilled {path} as {run_id}")
    return 0


def validation_placeholders() -> list[dict[str, Any]]:
    rows = []
    for validation in VALIDATION_CASES:
        for label, response, expected in validation["cases"]:
            rows.append(
                {
                    "case_id": f"{validation['question_id']}:{label}",
                    "question_id": validation["question_id"],
                    "question": validation["question"],
                    "reference_answer": validation["reference_answer"],
                    "supplied_answer": response,
                    "expected": expected,
                    "actual": None,
                    "agreement": None,
                    "status": "not_run",
                    "judge_explanation": None,
                    "judge_call": None,
                }
            )
    return rows


def local_checks(records: list[dict[str, Any]], dataset_path: Path, fixture: Path | None, questions: Path, benchmark: str) -> list[dict[str, str]]:
    parser_cases = {
        "<judge_thinking>x</judge_thinking>\nyes": "yes",
        "<judge_thinking>x</judge_thinking>\nno": "no",
        "analysis yes but final no": "no",
        "": "invalid",
        "maybe": "invalid",
    }
    parser_ok = all(parse_yes_no(raw) == expected for raw, expected in parser_cases.items())
    if fixture is not None:
        source_checks = [("fixture_sha256", True, f"{fixture.name} {sha256_file(fixture)}")]
    elif benchmark == "longmemeval":
        source_checks = [
            ("dataset_sha256", sha256_file(dataset_path) == DATASET_SHA256, DATASET_SHA256),
            ("dataset_500_unique_questions", True, "validated while loading"),
            ("selected_ids_unique", len({r['question_id'] for r in records}) == len(records), f"{questions.name}: {len(records)} questions"),
        ]
    else:
        vendored = {"locomo": (ROOT / "third_party" / "mem0" / "locomo_prompts.py", MEM0_LOCOMO_PROMPTS_SHA256), "beam": (ROOT / "third_party" / "mem0" / "beam_prompts.py", MEM0_BEAM_PROMPTS_SHA256)}[benchmark]
        source_checks = [
            ("source_files_recorded", True, f"{benchmark}: {len(benchmarks.source_files(benchmark))} files hashed in metadata"),
            ("selected_ids_unique", len({r['question_id'] for r in records}) == len(records), f"{questions.name}: {len(records)} questions"),
            (f"mem0_{benchmark}_judge_prompts_exact", sha256_file(vendored[0]) == vendored[1], vendored[1]),
        ]
    fits = all(r["prompt_fit"]["fits"] for r in records if r.get("prompt_fit"))
    checks = source_checks + [
        ("complete_history_and_no_labels", True, "validated while building every prompt"),
        ("mem0_judge_prompt_exact_text", sha256_text(JUDGE_PROMPT) == JUDGE_PROMPT_TEXT_SHA256, JUDGE_PROMPT_TEXT_SHA256),
        ("mem0_yes_no_parser_cases", parser_ok, "yes, no, last-token, empty, and garbage cases"),
        ("all_answer_prompts_fit", fits, "configured context window" if fixture is None else "checked when the memory prompt is built"),
    ]
    return [
        {"check": name, "status": "passed" if passed else "failed", "detail": detail}
        for name, passed, detail in checks
    ]


def missing_paid_config(args: argparse.Namespace) -> list[str]:
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    names = [
        "answer_model", "answer_reasoning_effort", "judge_model", "spending_limit", "answer_input_cost",
        "answer_cached_input_cost", "answer_output_cost", "judge_input_cost",
        "judge_cached_input_cost", "judge_output_cost",
    ]
    if args.system in ("memory", "mem0"):
        names += ["extraction_model", "extraction_reasoning_effort"]
    for name in names:
        if getattr(args, name) is None:
            missing.append("--" + name.replace("_", "-"))
    return missing


def write_memory(client: Any, args: argparse.Namespace, report: dict[str, Any], record: dict[str, Any], item: dict[str, Any]) -> bool:
    """Run extraction over every remaining session, then build the answer prompt. False when the record stopped."""
    history = sanitize_history(item)
    store = record["memory"]
    session_count = len(history)
    for index in range(store["sessions_done"], session_count):
        session = history[index]
        number = index + 1
        parts = memory_system.extraction_parts(store["lines"], number, session_count, session["timestamp"], session["messages"])
        prompt_text = "\n\n".join(parts)
        check_no_label_leak(prompt_text)
        call = api_call(
            client, args.extraction_model, memory_system.extraction_system_prompt(store.get("subject")), "",
            args.extraction_max_tokens, args.extraction_reasoning_effort, memory_system.EXTRACTION_RESPONSE_FORMAT,
            user_messages=memory_system.extraction_messages(parts),
        )
        with REPORT_LOCK:
            call["session"] = number
            call["prompt_sha256"] = sha256_text(prompt_text)
            # The memory messages are a deterministic rendering of lines already in the store, so only
            # the session message is kept; memory.extraction_parts rebuilds the rest for the same hash.
            call["session_message"] = parts[-1]
            call["memory_message_count"] = len(parts) - 1
            call["cost_usd"] = cost_usd(call["usage"], args.answer_input_cost, args.answer_cached_input_cost, args.answer_output_cost)
            store["extraction_calls"].append(call)
            if not call["ok"]:
                record["status"] = "extraction_api_error"
                checkpoint_run(report)
                return False
            try:
                data = memory_system.parse_extraction(call["content"])
            except (ValueError, json.JSONDecodeError) as exc:
                call["ok"] = False
                call["error_type"] = "InvalidExtractionOutput"
                call["error"] = str(exc)
                record["status"] = "extraction_invalid_output"
                checkpoint_run(report)
                return False
            new_lines, failures = memory_system.apply_extraction(
                store["lines"], data, number, session["timestamp"], memory_system.session_text(session["messages"])
            )
            call["new_lines"] = len(new_lines)
            store["failures"].extend(failures)
            store["sessions_done"] = number
            record["status"] = "memory_in_progress"
            checkpoint_run(report)

    return True


def prepare_memory_answer(args, report, record, item):
    store = record["memory"]
    session_count = record["history"]["sessions"]
    prompt = memory_system.build_answer_prompt(store["lines"], session_count, item["question_date"], item["question"])
    check_no_label_leak(prompt)
    encoding = tokenizer(args.tokenizer)
    fit = fit_check(
        token_count(encoding, report["metadata"]["prompts"]["answer_system"], prompt), args.answer_max_tokens, args.answer_context_window
    )
    with REPORT_LOCK:
        record["prompt_fit"] = fit
        record["answer_prompt"] = prompt
        record["answer_prompt_sha256"] = sha256_text(prompt)
        if not fit["fits"]:
            record["status"] = "prompt_too_large"
            checkpoint_run(report)
            return False
        record["status"] = "memory_complete"
        checkpoint_run(report)
    return True


def write_mem0(args: argparse.Namespace, report: dict[str, Any], record: dict[str, Any], item: dict[str, Any]) -> bool:
    """Ingest every session into a private Mem0 store, retrieve for the question, build the answer prompt.

    Any exception outside the per-session handling (store construction, retrieval) is recorded on
    the record as an extraction error rather than propagating, so one question cannot abort the run.
    """
    try:
        return _write_mem0(args, report, record, item)
    except Exception as exc:
        import traceback

        with REPORT_LOCK:
            record["memory"]["extraction_calls"].append(
                {"ok": False, "mem0": True, "session": record["memory"].get("sessions_done", 0), "error_type": type(exc).__name__, "error": str(exc)[:500], "traceback": traceback.format_exc()[-2000:], "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None}}
            )
            record["status"] = "extraction_api_error"
            checkpoint_run(report)
        return False


def _write_mem0(args: argparse.Namespace, report: dict[str, Any], record: dict[str, Any], item: dict[str, Any]) -> bool:
    import mem0_system

    history = sanitize_history(item)
    store = record["memory"]
    session_count = len(history)
    # The Mem0 store is kept under the run directory (ignored by git), so a resumed question reopens it
    # and continues from the recorded number of ingested sessions instead of re-ingesting.
    workdir = validated_run_dir(report["run"]["run_id"]) / "mem0" / record["question_id"]
    resuming = store.get("sessions_done", 0) > 0 and (workdir / "qdrant").exists()
    if not resuming:
        with REPORT_LOCK:
            store.update({"lines": [], "extraction_calls": [], "failures": [], "sessions_done": 0, "retrieved": None})
        shutil.rmtree(workdir, ignore_errors=True)
    mem0 = mem0_system.Mem0Store(record["question_id"], args.extraction_model, args.extraction_reasoning_effort, workdir=workdir, persistent=True)
    try:
        for index, session in enumerate(history, start=1):
            if index <= store["sessions_done"]:
                continue
            try:
                summary = mem0.add_session(session["messages"], session["timestamp"], args.mem0_chunk_messages)
            except Exception as exc:  # Mem0 wraps provider errors in its own exception types
                with REPORT_LOCK:
                    store["extraction_calls"].append({"ok": False, "mem0": True, "session": index, "error_type": type(exc).__name__, "error": str(exc)[:500], "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None}})
                    record["status"] = "extraction_api_error"
                    checkpoint_run(report)
                return False
            usage = summary["usage"]
            call = {
                "ok": True,
                "mem0": True,
                "session": index,
                "adds": summary["adds"],
                "events": summary["events"],
                "llm_calls": summary["llm_calls"],
                "embedding_calls": summary["embedding_calls"],
                "embedding_tokens": summary["embedding_tokens"],
                "requested_model": args.extraction_model,
                "resolved_model": summary["resolved_model"],
                "usage": usage,
                "elapsed_seconds": summary["elapsed_seconds"],
            }
            call["cost_usd"] = round(
                (cost_usd(usage, args.answer_input_cost, args.answer_cached_input_cost, args.answer_output_cost) or 0.0)
                + summary["embedding_tokens"] * args.embedding_cost / 1_000_000,
                8,
            )
            with REPORT_LOCK:
                store["extraction_calls"].append(call)
                store["sessions_done"] = index
                record["status"] = "memory_in_progress"
                checkpoint_run(report)
        memories = mem0.all_memories()
        if args.mem0_all_from:
            hits, search_info = memories, {}
        else:
            hits, search_info = mem0.search(item["question"], args.mem0_top_k)
    finally:
        mem0.close()
    prompt = mem0_system.build_answer_prompt(hits, session_count, item["question_date"], item["question"])
    check_no_label_leak(prompt)
    encoding = tokenizer(args.tokenizer)
    fit = fit_check(token_count(encoding, mem0_system.ANSWER_SYSTEM_PROMPT, prompt), args.answer_max_tokens, args.answer_context_window)
    with REPORT_LOCK:
        store["lines"] = mem0_system.memory_lines(memories)
        store["retrieved"] = {"top_k": args.mem0_top_k, "count": len(hits), "hits": hits, **search_info}
        if args.mem0_all_from:
            prepare_all_memories(args, report, record, item)
            checkpoint_run(report)
            return record["prompt_fit"]["fits"]
        record["prompt_fit"] = fit
        record["answer_prompt"] = prompt
        record["answer_prompt_sha256"] = sha256_text(prompt)
        record["status"] = "memory_complete" if fit["fits"] else "prompt_too_large"
        checkpoint_run(report)
    return fit["fits"]


def judge_control(client: Any, args: argparse.Namespace, report: dict[str, Any], row: dict[str, Any], spec: dict[str, Any]) -> None:
    _, response, _ = spec["case"]
    judge_prompt = JUDGE_PROMPT.format(question=spec["question"], answer=spec["answer"], response=response)
    call = api_call(client, args.judge_model, "", judge_prompt, args.judge_max_tokens)
    with REPORT_LOCK:
        row["judge_prompt_sha256"] = sha256_text(judge_prompt)
        row["judge_prompt"] = judge_prompt
        row["judge_call"] = call
        call["cost_usd"] = cost_usd(call["usage"], args.judge_input_cost, args.judge_cached_input_cost, args.judge_output_cost)
        if not call["ok"]:
            row["status"] = "judge_api_error"
        else:
            actual = parse_yes_no(call["content"])
            row["actual"] = actual
            row["judge_explanation"] = judge_explanation(call["content"])
            row["agreement"] = actual == row["expected"] if actual != "invalid" else False
            row["status"] = "success" if actual != "invalid" else "invalid_judge_response"
        checkpoint_run(report)


def process_record(client: Any, args: argparse.Namespace, report: dict[str, Any], record: dict[str, Any], item: dict[str, Any]) -> None:
    """Memory writing (if any), answer, judge for one question. Each stage checkpoints under the lock."""
    if record["status"] == "success":
        return
    if args.retry_failed:
        # Continue a question that stopped on an API error from the stage it reached.
        with REPORT_LOCK:
            if record["status"] in {"extraction_api_error", "extraction_invalid_output"}:
                record["status"] = "memory_in_progress" if record["memory"]["sessions_done"] else "not_run"
            elif record["status"] == "answer_api_error":
                record["status"] = "memory_complete" if args.system != "full-history" else "not_run"
            elif record["status"] in {"judge_api_error", "invalid_judge_response"}:
                record["status"] = "answer_complete"
    if args.system == "memory" and record["status"] in {"not_run", "memory_in_progress"}:
        raise RuntimeError("Our memory system must run through the shared-history pipeline.")
    if args.system == "mem0" and record["status"] in {"not_run", "memory_in_progress"}:
        if not write_mem0(args, report, record, item):
            return
    answer_record(client, args, report, record, item)
    judge_record(client, args, report, record, item)


def answer_record(client, args, report, record, item):
    answer_system_prompt = report["metadata"]["prompts"]["answer_system"]
    if record["status"] in {"not_run", "memory_complete"}:
        answer_call = api_call(
            client, args.answer_model, answer_system_prompt,
            record["answer_prompt"], args.answer_max_tokens, args.answer_reasoning_effort,
        )
        with REPORT_LOCK:
            record["answer_call"] = answer_call
            answer_call["cost_usd"] = cost_usd(
                answer_call["usage"], args.answer_input_cost, args.answer_cached_input_cost, args.answer_output_cost
            )
            if not answer_call["ok"]:
                record["status"] = "answer_api_error"
                checkpoint_run(report)
                return
            record["generated_answer"] = answer_call["content"]
            record["status"] = "answer_complete"
            checkpoint_run(report)


def judge_record(client, args, report, record, item):
    if record["status"] != "answer_complete":
        return
    judge_kind = item.get("judge", "longmemeval")
    if judge_kind == "beam":
        judge_beam(client, args, report, record, item)
        return
    if judge_kind == "locomo":
        system = locomo_prompts.JUDGE_SYSTEM_PROMPT
        judge_prompt = locomo_prompts.JUDGE_PROMPT.format(
            question=item["question"], answer=str(item["answer"]), response=record["generated_answer"]
        )
    else:
        system = ""
        judge_prompt = JUDGE_PROMPT.format(
            question=item["question"], answer=str(item["answer"]), response=record["generated_answer"]
        )
    judge_call = api_call(client, args.judge_model, system, judge_prompt, args.judge_max_tokens)
    with REPORT_LOCK:
        record["judge_prompt_sha256"] = sha256_text(judge_prompt)
        record["judge_prompt"] = judge_prompt
        record["judge_call"] = judge_call
        judge_call["cost_usd"] = cost_usd(
            judge_call["usage"], args.judge_input_cost, args.judge_cached_input_cost, args.judge_output_cost
        )
        if not judge_call["ok"]:
            record["status"] = "judge_api_error"
            checkpoint_run(report)
            return
        if judge_kind == "locomo":
            verdict = parse_locomo_label(judge_call["content"])
            record["judge_explanation"] = judge_call["content"]
        else:
            verdict = parse_yes_no(judge_call["content"])
            record["judge_explanation"] = judge_explanation(judge_call["content"])
        record["judge_verdict"] = verdict
        record["status"] = "success" if verdict != "invalid" else "invalid_judge_response"
        checkpoint_run(report)


def judge_beam(client: Any, args: argparse.Namespace, report: dict[str, Any], record: dict[str, Any], item: dict[str, Any]) -> None:
    """Mem0's BEAM scoring: one judge call per rubric nugget, 0/0.5/1 each; question score is the mean, pass at 0.5 or more."""
    nuggets = item.get("rubric") or []
    calls = []
    for nugget in nuggets:
        prompt = beam_prompts.get_beam_nugget_judge_prompt(item["question"], nugget, record["generated_answer"])
        call = api_call(client, args.judge_model, beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT, prompt, args.judge_max_tokens)
        call["nugget"] = nugget
        call["prompt_sha256"] = sha256_text(prompt)
        call["cost_usd"] = cost_usd(call["usage"], args.judge_input_cost, args.judge_cached_input_cost, args.judge_output_cost)
        call["score"] = parse_beam_score(call["content"]) if call.get("ok") else None
        calls.append(call)
    with REPORT_LOCK:
        record["judge_calls"] = calls
        usage_keys = ("input_tokens", "output_tokens", "total_tokens", "cached_input_tokens", "reasoning_output_tokens")
        merged_usage = {key: sum((c["usage"].get(key) or 0) for c in calls if c.get("usage")) for key in usage_keys}
        record["judge_call"] = {
            "ok": bool(calls) and all(c.get("ok") for c in calls),
            "nugget_count": len(calls),
            "requested_model": args.judge_model,
            "resolved_model": next((c.get("resolved_model") for c in calls if c.get("resolved_model")), None),
            "usage": merged_usage if calls else {"input_tokens": None, "output_tokens": None, "total_tokens": None},
            "cost_usd": round(sum(c.get("cost_usd") or 0.0 for c in calls), 8),
            "elapsed_seconds": round(sum(c.get("elapsed_seconds") or 0.0 for c in calls), 4),
            "content": json.dumps([{"nugget": c["nugget"], "score": c.get("score"), "reason": c.get("content")} for c in calls], ensure_ascii=False),
            "error": next((c.get("error") for c in calls if c.get("error")), None),
            "error_type": next((c.get("error_type") for c in calls if c.get("error_type")), None),
        }
        if not record["judge_call"]["ok"]:
            record["status"] = "judge_api_error"
            checkpoint_run(report)
            return
        scores = [c["score"] for c in calls]
        if any(s is None for s in scores):
            record["judge_verdict"] = "invalid"
            record["status"] = "invalid_judge_response"
            checkpoint_run(report)
            return
        record["judge_score"] = round(sum(scores) / len(scores), 4)
        record["judge_verdict"] = "yes" if record["judge_score"] >= 0.5 else "no"
        record["judge_explanation"] = "; ".join(f"{s:.1f}: {n[:80]}" for s, n in zip(scores, nuggets))
        record["status"] = "success"
        checkpoint_run(report)


def prepare_all_memories(args, report, record, item):
    import mem0_system

    store = record["memory"]
    lines = store["lines"]
    if any(not isinstance(line.get("text"), str) or not line["text"] for line in lines):
        raise RuntimeError(f"Invalid saved memory for {record['question_id']}")
    ordered = sorted(lines, key=lambda line: mem0_system.parse_timestamp(line.get("date", "")) or 0)
    prompt = report["metadata"]["prompts"]["answer_user_format"].format(
        question_date=item["question_date"], count=len(lines), session_count=record["history"]["sessions"],
        memories="\n".join(f"{line['date']} | {line['text']}" for line in ordered), question=item["question"])
    check_no_label_leak(prompt)
    store["retrieved"] = None
    store["context_policy"] = "all"
    store["supplied_memory_count"] = len(lines)
    store["lines_sha256"] = sha256_text(json.dumps(lines, sort_keys=True, ensure_ascii=False))
    record["answer_prompt"] = prompt
    record["answer_prompt_sha256"] = sha256_text(prompt)
    record["prompt_fit"] = fit_check(token_count(tokenizer(args.tokenizer), report["metadata"]["prompts"]["answer_system"], prompt), args.answer_max_tokens, args.answer_context_window)
    record["status"] = "memory_complete" if record["prompt_fit"]["fits"] else "prompt_too_large"


def all_memory_projection(args, report):
    encoding = tokenizer(args.tokenizer)
    reference_cost_per_add = None
    if args.mem0_cost_reference:
        reference = load_run(args.mem0_cost_reference)
        metadata = reference["metadata"]
        if (reference["run"]["system"] != "mem0"
                or metadata["benchmark"] != args.benchmark
                or metadata["mem0"]["chunk_messages"] != args.mem0_chunk_messages
                or metadata["models"]["extraction_requested"] != args.extraction_model
                or metadata["models"]["extraction_reasoning_effort"] != args.extraction_reasoning_effort
                or metadata["prices_usd_per_million_tokens"] != report["metadata"]["prices_usd_per_million_tokens"]):
            raise RuntimeError("Ingestion cost reference has mismatched benchmark, chunk size, model or prices.")
        calls = [c for r in reference["results"] for c in r.get("memory", {}).get("extraction_calls", []) if c.get("ok")]
        adds = sum(c.get("adds", 0) for c in calls)
        if not adds or any(c.get("cost_usd") is None for c in calls):
            raise RuntimeError("Ingestion cost reference lacks measured add costs.")
        reference_cost_per_add = sum(c["cost_usd"] for c in calls) / adds
        report["metadata"]["cost_projection"] = {
            "kind": "empirical ingestion forecast, not a guaranteed maximum",
            "reference_run": args.mem0_cost_reference,
            "reference_adds": adds,
            "reference_cost_per_add_usd": reference_cost_per_add,
            "ingestion_margin": 1.25,
            "answer_input_assumption": "complete history token count for stores not yet built",
            "runtime_budget_enforced": True,
        }
    total = 0.0
    for record in report["results"]:
        answer_input = (record.get("prompt_fit") or {}).get("input_tokens_estimated", record.get("history_tokens_estimated", args.answer_context_window))
        if not record["memory"].get("reused_from_run"):
            fit = record["extraction_fit"]
            if reference_cost_per_add is not None:
                total += fit["mem0_adds"] * reference_cost_per_add * 1.25
            else:
                total += (fit["projected_input_tokens"] * 1.02 * args.answer_input_cost + fit["mem0_adds"] * 2000 * args.answer_output_cost) / 1e6
        template = locomo_prompts.JUDGE_PROMPT if record["judge"] == "locomo" else JUDGE_PROMPT
        judge_system = locomo_prompts.JUDGE_SYSTEM_PROMPT if record["judge"] == "locomo" else ""
        judge_input = token_count(encoding, judge_system, template.format(question=record["question"], answer=record["reference_answer"], response="")) + args.answer_max_tokens
        total += (answer_input * 1.02 * args.answer_input_cost + args.answer_max_tokens * args.answer_output_cost + judge_input * 1.02 * args.judge_input_cost + args.judge_max_tokens * args.judge_output_cost) / 1e6
    for group in VALIDATION_CASES if report["judge_validation"] else []:
        for _, response, _ in group["cases"]:
            prompt = JUDGE_PROMPT.format(question=group["question"], answer=group["reference_answer"], response=response)
            total += (token_count(encoding, prompt) * 1.02 * args.judge_input_cost + args.judge_max_tokens * args.judge_output_cost) / 1e6
    return total


def run(args: argparse.Namespace) -> int:
    global PAID_BUDGET, API_SLOTS
    PAID_BUDGET = None
    API_SLOTS = None
    run_clock = time.perf_counter()
    if args.backfill_existing:
        return backfill_legacy_reports(args.backfill_existing)
    if args.resume and args.retry_of:
        raise RuntimeError("--resume and --retry-of are mutually exclusive.")
    if args.resume and args.preflight:
        raise RuntimeError("--resume cannot be combined with --preflight.")

    if args.test:
        selected = load_fixture(args.test)
    elif args.benchmark == "longmemeval":
        selected = load_selected(load_dataset(args.dataset), args.questions)
    else:
        selected = load_selected(benchmarks.load_items(args.benchmark), args.questions)
    records, projected_max = preflight(selected, args)
    fit_failures = [
        record["question_id"] for record in records
        if not (record.get("prompt_fit") or record.get("extraction_fit"))["fits"]
    ]
    # The six judge controls are LongMemEval questions and only make sense for that judge.
    validation = validation_placeholders() if args.benchmark == "longmemeval" else []
    report = {
        "run": make_run_metadata(args.system, args.retry_of),
        "metadata": base_metadata(args),
        "run_status": "running",
        "costs": {"projected_max_usd": projected_max},
        "results": records,
        "judge_validation": validation,
        "accounting_audit": audit_results([item["question_id"] for item in selected], records),
        "local_checks": local_checks(records, args.dataset, args.test, args.questions, args.benchmark),
    }
    if args.system == "memory":
        import shared_pipeline
        report["metadata"]["execution"] = {
            "pipeline": "shared-history-v1", "schedule": args.memory_schedule, "stage": args.memory_stage,
            "api_concurrency": args.concurrency, "build_workers": args.build_workers,
            "answer_workers": args.answer_workers, "judge_workers": args.judge_workers,
            "sdk_automatic_retries": 0,
        }
        report["metadata"]["local_code"]["shared_pipeline_sha256"] = sha256_file(ROOT / "shared_pipeline.py")
        report["metadata"]["local_code"]["memory_sha256"] = sha256_file(ROOT / "memory.py")
        if min(args.concurrency, args.build_workers, args.answer_workers, args.judge_workers) < 1:
            raise ValueError("Concurrency and all stage worker counts must be positive.")
        if args.memory_stage == "answer" and not args.memory_from:
            raise ValueError("--memory-stage answer requires --memory-from RUN_ID")
        if args.memory_stage == "build":
            validation = report["judge_validation"] = []
    if args.resume:
        report = resume_run(report, args.resume, args.retry_failed)
        records = report["results"]
        validation = report["judge_validation"]
    if args.memory_from:
        if args.system != "memory":
            raise RuntimeError("--memory-from requires --system memory (Mem0 stores live only in the process that built them).")
        source = load_run(args.memory_from)
        stores = {record["question_id"]: record for record in source["results"]}
        for record in records:
            prior = stores.get(record["question_id"])
            store = prior.get("memory") if prior else None
            if not store or prior["history_sha256"] != record["history_sha256"] or store["sessions_done"] != record["history"]["sessions"]:
                raise RuntimeError(f"Run {args.memory_from} has no complete memory store for {record['question_id']}.")
            record["memory"] = {**store, "reused_from_run": args.memory_from}
        report["metadata"]["memory_from"] = args.memory_from
        variants = {}
        for record in records:
            key = (record["history_sha256"], record["memory"].get("subject"))
            variants.setdefault(key, set()).add(sha256_text(json.dumps(record["memory"]["lines"], sort_keys=True)))
        if any(len(values) != 1 for values in variants.values()):
            raise ValueError("Source contains different memories for the same history; canonicalize it explicitly before reuse.")
        report["metadata"]["memory_source_models"] = source["metadata"]["models"]

    if args.mem0_all_from:
        if args.system != "mem0" or args.resume or args.memory_from:
            raise RuntimeError("--mem0-all-from requires a new Mem0 run without --memory-from.")
        sources = [load_run(run_id) for run_id in args.mem0_all_from]
        if any(s["run"]["system"] != "mem0" or s["metadata"]["benchmark"] != args.benchmark for s in sources):
            raise RuntimeError("Mem0 source system/benchmark mismatch.")
        report["metadata"]["mem0"].update(context_policy="all", top_k=None, source_runs=args.mem0_all_from)
        report["metadata"]["execution"] = {"concurrency": args.concurrency, "sdk_automatic_retries": 0}
        report["metadata"]["local_code"]["mem0_system_sha256"] = sha256_file(ROOT / "mem0_system.py")
        for key in ("answer_system", "answer_user_format"):
            report["metadata"]["prompts"][key] = report["metadata"]["prompts"][key].replace("retrieved", "stored").replace("Retrieved", "All stored")
        by_id = {item["question_id"]: item for item in selected}
        missing_stores = []
        for record in records:
            if args.mem0_cost_reference:
                history_prompt, _ = build_answer_prompt(by_id[record["question_id"]])
                record["history_tokens_estimated"] = token_count(tokenizer(args.tokenizer), history_prompt)
            candidates = [(s, r) for s in sources for r in s["results"]
                          if r["question_id"] == record["question_id"] and r["status"] == "success"]
            if len(candidates) > 1:
                raise RuntimeError(f"Duplicate source stores for {record['question_id']}")
            if not candidates:
                missing_stores.append(record["question_id"])
                continue
            source, prior = candidates[0]
            store = prior["memory"]
            if prior["history_sha256"] != record["history_sha256"] or store["sessions_done"] != record["history"]["sessions"]:
                raise RuntimeError(f"Incomplete or mismatched history for {record['question_id']}")
            # The old first-50 export retained only 20 lines. Never treat it as a complete store.
            if len(store["lines"]) < (store.get("retrieved") or {}).get("count", 0):
                raise RuntimeError(f"Truncated memory export for {record['question_id']}")
            record["memory"] = {**store, "reused_from_run": source["run"]["run_id"]}
            record["memory"]["source_history_sha256"] = prior["history_sha256"]
            record["memory"]["historical_writing"] = aggregate_calls(store["extraction_calls"])
            prepare_all_memories(args, report, record, by_id[record["question_id"]])
        if set(missing_stores) != set(args.mem0_ingest_missing):
            raise RuntimeError(f"Missing complete stores: {missing_stores}; explicitly authorize exactly these IDs with --mem0-ingest-missing.")
        report["metadata"]["mem0"]["ingest_missing"] = missing_stores
        projected_max = all_memory_projection(args, report)
        report["costs"]["projected_max_usd"] = projected_max
        fit_failures = [r["question_id"] for r in records if r.get("prompt_fit") and not r["prompt_fit"]["fits"]]

    if fit_failures:
        report["run_status"] = "blocked_prompt_too_large"
        for record in records:
            if record["question_id"] in fit_failures:
                record["status"] = "prompt_too_large"
        report["accounting_audit"] = audit_results([item["question_id"] for item in selected], records)
        finalize_run(report)
        print(
            f"Run {report['run']['run_id']} blocked: prompts do not fit for {fit_failures}. "
            "No API calls made."
        )
        return 2
    if args.preflight:
        report["run_status"] = "preflight_only"
        finalize_run(report)
        cost_text = f"${projected_max:.8f}" if projected_max is not None else "unavailable until prices are configured"
        print(
            f"Preflight run {report['run']['run_id']} passed for {len(records)} question(s). "
            f"Cost projection: {cost_text}"
        )
        return 0
    missing = missing_paid_config(args)
    if missing:
        report["run_status"] = "blocked_missing_paid_config"
        report["missing_paid_config"] = missing
        finalize_run(report)
        print(f"Run {report['run']['run_id']} blocked. Missing: " + ", ".join(missing))
        return 2
    if projected_max is None:
        raise RuntimeError("Internal error: paid configuration passed without complete prices.")
    if projected_max > args.spending_limit:
        report["run_status"] = "blocked_spending_limit"
        finalize_run(report)
        print(
            f"Run {report['run']['run_id']} blocked. Projected maximum ${projected_max:.8f} exceeds "
            f"limit ${args.spending_limit:.8f}."
        )
        return 2

    if args.system == "memory":
        PAID_BUDGET = PaidBudget(args)
        PAID_BUDGET.used = max(report.get("budget_guard", {}).get("spent_or_reserved_usd", 0),
                               report["costs"].get("total_api_spend_usd", 0))
        API_SLOTS = threading.BoundedSemaphore(args.concurrency)
        PAID_BUDGET.checkpoint = lambda: checkpoint_run(report)
    checkpoint_run(report)

    if args.system == "mem0":
        import mem0_system  # noqa: F401  (loads Mem0's provider modules in the main thread before the pool starts)
        if args.mem0_all_from:
            PAID_BUDGET = PaidBudget(args)
            mem0_system.PAID_BUDGET = PAID_BUDGET

    # Extraction calls take 3 to 9 s and full-history answers under 30 s; hung requests showed up as exactly the old 180 s.
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=args.base_url, max_retries=0 if PAID_BUDGET else 2, timeout=float(os.getenv("CLIENT_TIMEOUT_SECONDS", "60")))
    validation_specs = []
    if validation:  # judge controls exist only for LongMemEval
        for group in VALIDATION_CASES:
            for case in group["cases"]:
                validation_specs.append(
                    {"question": group["question"], "answer": group["reference_answer"], "case": case}
                )
    by_id = {item["question_id"]: item for item in selected}
    # Judge controls and questions are independent of each other; sessions within a question stay sequential.
    if args.system == "memory":
        shared_pipeline.execute(sys.modules[__name__], client, args, report, by_id, validation_specs)
    else:
        run_question_jobs(client, args, report, records, by_id, validation, validation_specs)

    report["accounting_audit"] = audit_results([item["question_id"] for item in selected], records)
    failures = report["accounting_audit"]["failures"]
    validation_failures = [row for row in validation if row["status"] != "success"]
    report["run_status"] = "complete" if not failures and not validation_failures else "complete_with_failures"
    if args.system == "memory" and args.memory_stage == "build":
        ready = all(r["status"] == "memory_complete" for r in records)
        report["run_status"] = "memory_ready" if ready else "complete_with_failures"
        report["accounting_audit"]["note"] = "Build-only run: answers and verdicts intentionally not requested; not a completed QA benchmark."
    if args.system == "memory":
        report["timing"]["invocation_elapsed_before_finalization_seconds"] = round(time.perf_counter() - run_clock, 6)
    finalize_run(report)
    if args.system == "memory":
        atomic_json(validated_run_dir(report["run"]["run_id"]) / "execution_timing.json", {
            "parent_run_id": report["run"]["run_id"], "finished_at": datetime.now(timezone.utc).isoformat(),
            "invocation_elapsed_seconds": round(time.perf_counter() - run_clock, 6),
            "boundary": "Invocation entry through terminal checkpoint and index write; excludes this timing-file write. Includes preflight; on resume covers this invocation only.",
            "historical_comparison_seconds": report["timing"]["recorded_run_elapsed_seconds"],
        })
    print(f"Run {report['run']['run_id']} status: {report['run_status']}; total API spend: ${report['costs']['total_api_spend_usd']:.8f}")
    return 0 if report["run_status"] in {"complete", "memory_ready"} else 1


def run_question_jobs(client, args, report, records, by_id, validation, validation_specs):
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = [
            pool.submit(judge_control, client, args, report, row, spec)
            for row, spec in zip(validation, validation_specs, strict=True)
            if row["status"] == "not_run"
        ]
        futures += [pool.submit(process_record, client, args, report, record, by_id[record["question_id"]]) for record in records]
        for future in futures:
            future.result()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true", help="Run all local checks without API calls.")
    parser.add_argument(
        "--backfill-existing",
        type=Path,
        nargs="+",
        metavar="LEGACY_RESULTS_JSON",
        help="Convert one or more legacy results JSON files into immutable run records.",
    )
    parser.add_argument("--resume", metavar="RUN_ID", help="Resume an interrupted non-terminal run.")
    parser.add_argument("--retry-failed", action="store_true", help="With --resume: also continue questions that stopped on an API error, from the stage they reached.")
    parser.add_argument("--retry-of", metavar="RUN_ID", help="Link a new run to an earlier terminal run.")
    parser.add_argument("--system", choices=SYSTEMS, default="full-history", help="Answer from the full history or from write-time memory.")
    parser.add_argument("--benchmark", choices=BENCHMARKS, default="longmemeval", help="Which benchmark the selection file refers to.")
    parser.add_argument("--questions", type=Path, default=IDS_PATH, help="Selection file listing question IDs and types. Default question_ids.json (five); question_ids_50.json holds fifty.")
    parser.add_argument("--test", type=Path, help="Run one dataset-shaped JSON test file, e.g. fixtures/memory_smoke_test.json, instead of the five fixed questions.")
    parser.add_argument("--answer-prompt", choices=sorted(memory_system.ANSWER_SYSTEM_PROMPTS), default="v2", help="Answer prompt version for either system: v1 is the original one-liner, v2 adds the same three reasoning rules to both.")
    parser.add_argument("--mem0-top-k", type=int, default=int(os.getenv("MEM0_TOP_K", "200")), help="Memories retrieved per question for the mem0 system (Mem0's runner default 200).")
    parser.add_argument("--mem0-chunk-messages", type=int, default=2, help="Messages per Mem0 add call (Mem0's runner uses 2, one user-assistant pair).")
    parser.add_argument("--embedding-cost", type=float, default=float(os.getenv("EMBEDDING_USD_PER_MTOK", "0.02")), help="USD per million embedding tokens, for the mem0 system.")
    parser.add_argument("--memory-from", metavar="RUN_ID", help="Reuse the memory stores of an earlier memory run and only rebuild the answer prompt, answer, and judge.")
    parser.add_argument("--mem0-all-from", nargs="+", default=[], metavar="RUN_ID", help="Use complete saved Mem0 stores with no question-based retrieval.")
    parser.add_argument("--mem0-ingest-missing", nargs="*", default=[], metavar="QUESTION_ID", help="Explicit IDs allowed to rebuild if missing from the all-memory sources.")
    parser.add_argument("--mem0-cost-reference", metavar="RUN_ID", help="Forecast ingestion from a saved run with matching settings, with a 25 percent margin. The runtime spending cap still applies.")
    parser.add_argument("--concurrency", type=int, default=int(os.getenv("CONCURRENCY", "5")), help="Our memory pipeline: global in-flight API limit. Other systems: question workers.")
    parser.add_argument("--memory-schedule", choices=("overlap", "barrier"), default="overlap", help="Our extractor: overlap stages (C), or finish all building before answering (B).")
    parser.add_argument("--memory-stage", choices=("all", "build", "answer"), default="all", help="Our extractor: run the full pipeline, only build, or answer from --memory-from.")
    parser.add_argument("--build-workers", type=int, default=2)
    parser.add_argument("--answer-workers", type=int, default=4)
    parser.add_argument("--judge-workers", type=int, default=4)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--answer-model", default=os.getenv("ANSWER_MODEL"))
    parser.add_argument("--answer-reasoning-effort", default=os.getenv("ANSWER_REASONING_EFFORT"))
    parser.add_argument("--extraction-model", default=os.getenv("EXTRACTION_MODEL"))
    parser.add_argument("--extraction-reasoning-effort", default=os.getenv("EXTRACTION_REASONING_EFFORT"))
    parser.add_argument("--extraction-max-tokens", type=int, default=int(os.getenv("EXTRACTION_MAX_TOKENS", "128000")))
    parser.add_argument("--judge-model", default=os.getenv("JUDGE_MODEL"))
    parser.add_argument("--answer-context-window", type=int, default=int(os.getenv("ANSWER_CONTEXT_WINDOW", "128000")))
    parser.add_argument("--answer-max-tokens", type=int, default=int(os.getenv("ANSWER_MAX_TOKENS", "1024")))
    parser.add_argument("--judge-max-tokens", type=int, default=int(os.getenv("JUDGE_MAX_TOKENS", "1024")))
    parser.add_argument("--tokenizer", default=os.getenv("TOKENIZER", "o200k_base"))
    parser.add_argument("--spending-limit", type=float, default=os.getenv("SPENDING_LIMIT_USD"))
    parser.add_argument("--answer-input-cost", type=float, default=os.getenv("ANSWER_INPUT_USD_PER_MTOK"))
    parser.add_argument("--answer-cached-input-cost", type=float, default=os.getenv("ANSWER_CACHED_INPUT_USD_PER_MTOK"))
    parser.add_argument("--answer-output-cost", type=float, default=os.getenv("ANSWER_OUTPUT_USD_PER_MTOK"))
    parser.add_argument("--judge-input-cost", type=float, default=os.getenv("JUDGE_INPUT_USD_PER_MTOK"))
    parser.add_argument("--judge-cached-input-cost", type=float, default=os.getenv("JUDGE_CACHED_INPUT_USD_PER_MTOK"))
    parser.add_argument("--judge-output-cost", type=float, default=os.getenv("JUDGE_OUTPUT_USD_PER_MTOK"))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv(ROOT / ".env", override=False)
    raise SystemExit(run(parse_args()))
