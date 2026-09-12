from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence


USER_SUBJECT = "one user, built from their past conversations with an assistant"


@dataclass(frozen=True)
class Message:
    role: str
    content: str
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        if self.role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported message role: {self.role!r}")
        if not isinstance(self.content, str):
            raise TypeError("Message content must be text")

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.evidence_id is not None:
            value["dia_id"] = self.evidence_id
        return value


@dataclass(frozen=True)
class Session:
    session_id: str
    timestamp: str
    messages: tuple[Message, ...]

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError(f"Session {self.session_id!r} has no messages")


@dataclass(frozen=True)
class BenchmarkItem:
    benchmark: str
    question_id: str
    question_type: str
    question: str
    reference_answer: str
    question_date: str
    sessions: tuple[Session, ...]
    subject: str
    judge_id: str
    answer_session_ids: tuple[str, ...] = ()
    rubric: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    conversation: int | None = None
    topic_category: str | None = None
    difficulty: str | None = None

    def __post_init__(self) -> None:
        if not self.question_id or not self.question:
            raise ValueError("Benchmark questions require an ID and text")

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "benchmark": self.benchmark,
            "judge": self.judge_id,
            "question_id": self.question_id,
            "question_type": self.question_type,
            "question": self.question,
            "answer": self.reference_answer,
            "question_date": self.question_date,
            "haystack_dates": [session.timestamp for session in self.sessions],
            "haystack_sessions": [
                [message.to_dict() for message in session.messages] for session in self.sessions
            ],
            "haystack_session_ids": [session.session_id for session in self.sessions],
            "answer_session_ids": list(self.answer_session_ids),
            "subject": self.subject,
        }
        if self.benchmark == "beam":
            record["rubric"] = list(self.rubric)
        if self.benchmark == "locomo":
            record["evidence_ids"] = list(self.evidence_ids)
        if self.conversation is not None:
            record["conversation"] = self.conversation
        if self.benchmark == "beam":
            record["topic_category"] = self.topic_category
        if self.benchmark == "beam":
            record["difficulty"] = self.difficulty
        return record

    @classmethod
    def from_record(
        cls,
        record: dict[str, Any],
        benchmark: str = "longmemeval",
        judge_id: str = "longmemeval",
    ) -> BenchmarkItem:
        dates = record["haystack_dates"]
        messages = record["haystack_sessions"]
        session_ids = record["haystack_session_ids"]
        if not (len(dates) == len(messages) == len(session_ids)):
            raise ValueError(f"History arrays have different lengths for {record['question_id']}")
        sessions = tuple(
            Session(
                session_id=session_id,
                timestamp=timestamp,
                messages=tuple(
                    Message(
                        role=message["role"],
                        content=message["content"],
                        evidence_id=message.get("dia_id"),
                    )
                    for message in session
                ),
            )
            for timestamp, session, session_id in zip(dates, messages, session_ids, strict=True)
        )
        return cls(
            benchmark=record.get("benchmark", benchmark),
            question_id=record["question_id"],
            question_type=record["question_type"],
            question=record["question"],
            reference_answer=str(record["answer"]),
            question_date=record["question_date"],
            sessions=sessions,
            subject=record.get("subject", USER_SUBJECT),
            judge_id=record.get("judge", judge_id),
            answer_session_ids=tuple(record.get("answer_session_ids", ())),
            rubric=tuple(str(value) for value in record.get("rubric", ())),
            evidence_ids=tuple(record.get("evidence_ids", ())),
            conversation=record.get("conversation"),
            topic_category=record.get("topic_category"),
            difficulty=record.get("difficulty"),
        )


class BenchmarkAdapter(Protocol):
    name: str

    def load(self) -> list[BenchmarkItem]: ...

    def source_files(self) -> tuple[Path, ...]: ...


def select_items(items: Sequence[BenchmarkItem], selection_path: Path) -> list[BenchmarkItem]:
    value = json.loads(selection_path.read_text())
    selected = value["questions"]
    wanted_ids = [entry["question_id"] for entry in selected]
    if not wanted_ids or len(wanted_ids) != len(set(wanted_ids)):
        raise ValueError(f"{selection_path.name} must contain unique question IDs")
    by_id = {item.question_id: item for item in items}
    missing = [question_id for question_id in wanted_ids if question_id not in by_id]
    if missing:
        raise ValueError(f"Selected question IDs are missing: {missing}")
    result = [by_id[question_id] for question_id in wanted_ids]
    mismatches = [
        item.question_id
        for item, expected in zip(result, selected, strict=True)
        if item.question_type != expected["question_type"]
    ]
    if mismatches:
        raise ValueError(f"Selected question types differ: {mismatches}")
    return result
