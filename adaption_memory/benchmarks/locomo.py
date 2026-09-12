from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import BenchmarkItem, Message, Session


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "work" / "locomo10.json"
CATEGORY_NAMES = {1: "multi-hop", 2: "temporal", 3: "open-domain", 4: "single-hop"}
WEIGHTS = {"multi-hop": 282, "temporal": 321, "open-domain": 96, "single-hop": 841}


def _parse_date(text: str) -> datetime | None:
    for format_string in ("%I:%M %p on %d %B, %Y", "%I:%M %p on %d %b, %Y"):
        try:
            return datetime.strptime(text.strip(), format_string)
        except ValueError:
            continue
    return None


def _sessions(conversation: dict[str, Any]) -> list[tuple[str, str, list[dict[str, Any]]]]:
    keys = [key for key in conversation if re.fullmatch(r"session_\d+", key)]
    paired = [(key, conversation.get(f"{key}_date_time", ""), conversation[key]) for key in keys]

    def sort_key(entry: tuple[str, str, list[dict[str, Any]]]) -> tuple[int, datetime]:
        parsed = _parse_date(entry[1])
        if parsed:
            return 0, parsed
        number = int(re.search(r"\d+", entry[0]).group())
        return 1, datetime(2000, 1, number)

    return sorted(paired, key=sort_key)


def _message(turn: dict[str, Any], speaker_a: str) -> Message | None:
    text = turn.get("text", "") or ""
    caption = turn.get("blip_caption", "") or ""
    query = turn.get("query", "") or ""
    if query and caption:
        tag = f"[Sharing image - query: {query}. The image shows: {caption}]"
    elif query:
        tag = f"[Sharing image - query for: {query}]"
    elif caption:
        tag = f"[Sharing image that shows: {caption}]"
    else:
        tag = ""
    if tag:
        text = f"{text} {tag}" if text else tag
    if not text:
        return None
    speaker = turn.get("speaker", "")
    return Message(
        role="user" if speaker == speaker_a else "assistant",
        content=f"{speaker}: {text}",
        evidence_id=turn.get("dia_id"),
    )


@dataclass(frozen=True)
class LoCoMoAdapter:
    path: Path = DATASET_PATH
    name: str = "locomo"

    def load(self) -> list[BenchmarkItem]:
        data = json.loads(self.path.read_text())
        items: list[BenchmarkItem] = []
        for conversation_index, entry in enumerate(data):
            conversation = entry["conversation"]
            speaker_a = conversation["speaker_a"]
            speaker_b = conversation["speaker_b"]
            sessions: list[Session] = []
            evidence_to_session: dict[str, str] = {}
            for session_id, timestamp, turns in _sessions(conversation):
                messages = tuple(
                    message for message in (_message(turn, speaker_a) for turn in turns) if message
                )
                if not messages:
                    continue
                sessions.append(Session(session_id=session_id, timestamp=timestamp, messages=messages))
                for message in messages:
                    if message.evidence_id:
                        evidence_to_session[message.evidence_id] = session_id
            reference_date = sessions[-1].timestamp if sessions else ""
            subject = (
                f"two people, {speaker_a} and {speaker_b}, built from their past conversations with each other. "
                f"Record facts about each of them and start every atomic key with the person's name, "
                f"such as \"{speaker_a}'s dog's name\". Facts stated by {speaker_a} are about {speaker_a} unless they say otherwise; the same for {speaker_b}"
            )
            for question_index, question in enumerate(entry["qa"]):
                category = question.get("category")
                if category not in CATEGORY_NAMES:
                    continue
                answer = str(question["answer"])
                if category == 3 and ";" in answer:
                    answer = answer.split(";")[0].strip()
                evidence = tuple(value for value in question.get("evidence", ()) if isinstance(value, str))
                items.append(
                    BenchmarkItem(
                        benchmark="locomo",
                        question_id=f"locomo{conversation_index}_q{question_index}",
                        question_type=CATEGORY_NAMES[category],
                        question=question["question"],
                        reference_answer=answer,
                        question_date=reference_date,
                        sessions=tuple(sessions),
                        subject=subject,
                        judge_id="locomo",
                        answer_session_ids=tuple(sorted({evidence_to_session[value] for value in evidence if value in evidence_to_session})),
                        evidence_ids=evidence,
                        conversation=conversation_index,
                    )
                )
        return items

    def source_files(self) -> tuple[Path, ...]:
        return (self.path,)
