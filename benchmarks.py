"""Adapters that turn LoCoMo and BEAM into the runner's item format.

An item has the LongMemEval shape the runner already understands:
    question_id, question_type, question, answer, question_date,
    haystack_dates, haystack_sessions ([{role, content}, ...] per session),
    haystack_session_ids, answer_session_ids
plus:
    benchmark   "locomo" | "beam"
    judge       which judge to apply: "locomo" (Mem0 CORRECT/WRONG) or "beam" (rubric nuggets)
    rubric      BEAM only, list of nugget strings
    subject     who the memory is about, spliced into the extractor prompt
    evidence_ids  LoCoMo only, dialogue ids of the evidence turns

Turn dicts may carry extra keys (dia_id) used only for evidence labels; the
runner keeps role and content only.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LOCOMO_PATH = ROOT / "work" / "locomo10.json"
BEAM_DIR = ROOT / "work" / "beam"

USER_SUBJECT = "one user, built from their past conversations with an assistant"

LOCOMO_CATEGORY_NAMES = {1: "multi-hop", 2: "temporal", 3: "open-domain", 4: "single-hop"}
# Question counts per category in LoCoMo, categories 1 to 4 (Mem0 excludes 5, adversarial).
LOCOMO_WEIGHTS = {"multi-hop": 282, "temporal": 321, "open-domain": 96, "single-hop": 841}

BEAM_TYPES = [
    "abstention", "contradiction_resolution", "event_ordering", "information_extraction",
    "instruction_following", "knowledge_update", "multi_session_reasoning",
    "preference_following", "summarization", "temporal_reasoning",
]
BEAM_WEIGHTS = {t: 1 for t in BEAM_TYPES}
BEAM_WINDOW_PAIRS = 8  # user+assistant pairs per extraction chunk; BEAM has no sessions


def _parse_locomo_date(text: str) -> datetime | None:
    for fmt in ("%I:%M %p on %d %B, %Y", "%I:%M %p on %d %b, %Y"):
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None


def _locomo_sessions(conversation: dict[str, Any]) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """Sessions sorted chronologically, as Mem0's get_sorted_sessions does."""
    keys = [k for k in conversation if re.fullmatch(r"session_\d+", k)]
    paired = [(k, conversation.get(f"{k}_date_time", ""), conversation[k]) for k in keys]

    def sort_key(entry: tuple[str, str, list[dict[str, Any]]]) -> tuple[int, datetime]:
        parsed = _parse_locomo_date(entry[1])
        if parsed:
            return (0, parsed)
        return (1, datetime(2000, 1, int(re.search(r"\d+", entry[0]).group())))

    return sorted(paired, key=sort_key)


def _locomo_turn(turn: dict[str, Any], speaker_a: str) -> dict[str, Any] | None:
    """Mem0's rendering: role by speaker, speaker name in the text, image captions as a tag."""
    text = turn.get("text", "") or ""
    blip = turn.get("blip_caption", "") or ""
    query = turn.get("query", "") or ""
    if query and blip:
        tag = f"[Sharing image - query: {query}. The image shows: {blip}]"
    elif query:
        tag = f"[Sharing image - query for: {query}]"
    elif blip:
        tag = f"[Sharing image that shows: {blip}]"
    else:
        tag = ""
    if tag:
        text = f"{text} {tag}" if text else tag
    if not text:
        return None
    speaker = turn.get("speaker", "")
    return {"role": "user" if speaker == speaker_a else "assistant", "content": f"{speaker}: {text}", "dia_id": turn.get("dia_id")}


def locomo_items(path: Path = LOCOMO_PATH) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    items: list[dict[str, Any]] = []
    for conv_index, entry in enumerate(data):
        conversation = entry["conversation"]
        a, b = conversation["speaker_a"], conversation["speaker_b"]
        sessions = _locomo_sessions(conversation)
        haystack_sessions, dates, ids = [], [], []
        dia_to_session: dict[str, str] = {}
        for key, date, turns in sessions:
            messages = [m for m in (_locomo_turn(t, a) for t in turns) if m]
            if not messages:
                continue
            haystack_sessions.append(messages)
            dates.append(date)
            ids.append(key)
            for m in messages:
                if m.get("dia_id"):
                    dia_to_session[m["dia_id"]] = key
        reference_date = dates[-1] if dates else ""
        subject = (
            f"two people, {a} and {b}, built from their past conversations with each other. "
            f"Record facts about each of them and start every atomic key with the person's name, "
            f"such as \"{a}'s dog's name\". Facts stated by {a} are about {a} unless they say otherwise; the same for {b}"
        )
        for q_index, qa in enumerate(entry["qa"]):
            category = qa.get("category")
            if category not in LOCOMO_CATEGORY_NAMES:
                continue
            answer = str(qa["answer"])
            if category == 3 and ";" in answer:  # Mem0's preprocess_answer for open-domain
                answer = answer.split(";")[0].strip()
            evidence = [e for e in qa.get("evidence", []) if isinstance(e, str)]
            items.append(
                {
                    "benchmark": "locomo",
                    "judge": "locomo",
                    "conversation": conv_index,
                    "question_id": f"locomo{conv_index}_q{q_index}",
                    "question_type": LOCOMO_CATEGORY_NAMES[category],
                    "question": qa["question"],
                    "answer": answer,
                    "question_date": reference_date,
                    "haystack_dates": dates,
                    "haystack_sessions": haystack_sessions,
                    "haystack_session_ids": ids,
                    "answer_session_ids": sorted({dia_to_session[e] for e in evidence if e in dia_to_session}),
                    "evidence_ids": evidence,
                    "subject": subject,
                }
            )
    return items


def beam_items(scale: str = "100K", chat_ids: list[int] | None = None, window_pairs: int = BEAM_WINDOW_PAIRS) -> list[dict[str, Any]]:
    scale_dir = BEAM_DIR / scale
    if chat_ids is None:
        chat_ids = sorted(int(p.name) for p in scale_dir.iterdir() if p.is_dir() and p.name.isdigit() and (p / "chat.json").exists())
    items: list[dict[str, Any]] = []
    for chat_id in chat_ids:
        chat_dir = scale_dir / str(chat_id)
        batches = json.loads((chat_dir / "chat.json").read_text())
        questions = json.loads((chat_dir / "probing_questions" / "probing_questions.json").read_text())
        topic = json.loads((chat_dir / "topic.json").read_text())
        haystack_sessions, dates, ids = [], [], []
        last_anchor = ""
        for batch in batches:
            number = batch.get("batch_number")
            pairs = batch.get("turns", [])
            anchor = next((m.get("time_anchor") for pair in pairs for m in pair if m.get("time_anchor")), "") or last_anchor
            last_anchor = anchor or last_anchor
            for start in range(0, len(pairs), window_pairs):
                window = pairs[start:start + window_pairs]
                messages = [
                    {"role": m["role"] if m.get("role") in ("user", "assistant") else "user", "content": m.get("content", "")}
                    for pair in window for m in pair if m.get("content")
                ]
                if not messages:
                    continue
                haystack_sessions.append(messages)
                dates.append(anchor)
                ids.append(f"batch{number}_window{start // window_pairs + 1}")
        for q_type in BEAM_TYPES:
            for q_index, q in enumerate(questions.get(q_type, [])):
                rubric = q.get("rubric", [])
                if isinstance(rubric, dict):
                    rubric = [n.get("description", str(n)) if isinstance(n, dict) else str(n) for n in rubric.get("nuggets", [])]
                items.append(
                    {
                        "benchmark": "beam",
                        "judge": "beam",
                        "conversation": chat_id,
                        "topic_category": topic.get("category"),
                        "question_id": f"beam{scale}_{chat_id}_{q_type}_{q_index}",
                        "question_type": q_type,
                        "question": q["question"],
                        "answer": q.get("ideal_response", ""),
                        "rubric": [str(n) for n in rubric],
                        "difficulty": q.get("difficulty"),
                        "question_date": last_anchor,
                        "haystack_dates": dates,
                        "haystack_sessions": haystack_sessions,
                        "haystack_session_ids": ids,
                        "answer_session_ids": [],
                        "subject": USER_SUBJECT,
                    }
                )
    return items


def beam_scales() -> list[str]:
    return sorted(p.name for p in BEAM_DIR.iterdir() if p.is_dir() and any(p.glob("*/chat.json")))


def load_items(benchmark: str) -> list[dict[str, Any]]:
    if benchmark == "locomo":
        return locomo_items()
    if benchmark == "beam":
        return [item for scale in beam_scales() for item in beam_items(scale)]
    raise ValueError(f"Unknown benchmark {benchmark!r}")


def source_files(benchmark: str) -> list[Path]:
    if benchmark == "locomo":
        return [LOCOMO_PATH]
    if benchmark == "beam":
        return sorted(BEAM_DIR.glob("*/*/chat.json")) + sorted(BEAM_DIR.glob("*/*/probing_questions/probing_questions.json"))
    return []
