from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import BenchmarkItem, Message, Session, USER_SUBJECT


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = PROJECT_ROOT / "work" / "beam"
QUESTION_TYPES = (
    "abstention",
    "contradiction_resolution",
    "event_ordering",
    "information_extraction",
    "instruction_following",
    "knowledge_update",
    "multi_session_reasoning",
    "preference_following",
    "summarization",
    "temporal_reasoning",
)
WEIGHTS = {question_type: 1 for question_type in QUESTION_TYPES}
WINDOW_PAIRS = 8


@dataclass(frozen=True)
class BeamAdapter:
    directory: Path = DATASET_DIRECTORY
    scale: str | None = None
    chat_ids: tuple[int, ...] | None = None
    window_pairs: int = WINDOW_PAIRS
    name: str = "beam"

    def scales(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                path.name
                for path in self.directory.iterdir()
                if path.is_dir() and any(path.glob("*/chat.json"))
            )
        )

    def load(self) -> list[BenchmarkItem]:
        scales = (self.scale,) if self.scale else self.scales()
        return [item for scale in scales for item in self._load_scale(scale)]

    def _load_scale(self, scale: str) -> list[BenchmarkItem]:
        scale_directory = self.directory / scale
        chat_ids = self.chat_ids
        if chat_ids is None:
            chat_ids = tuple(
                sorted(
                    int(path.name)
                    for path in scale_directory.iterdir()
                    if path.is_dir() and path.name.isdigit() and (path / "chat.json").exists()
                )
            )
        items: list[BenchmarkItem] = []
        for chat_id in chat_ids:
            items.extend(self._load_chat(scale, chat_id))
        return items

    def _load_chat(self, scale: str, chat_id: int) -> list[BenchmarkItem]:
        chat_directory = self.directory / scale / str(chat_id)
        batches = json.loads((chat_directory / "chat.json").read_text())
        questions = json.loads((chat_directory / "probing_questions" / "probing_questions.json").read_text())
        topic = json.loads((chat_directory / "topic.json").read_text())
        sessions: list[Session] = []
        last_anchor = ""
        for batch in batches:
            number = batch.get("batch_number")
            pairs = batch.get("turns", [])
            anchor = next(
                (message.get("time_anchor") for pair in pairs for message in pair if message.get("time_anchor")),
                "",
            ) or last_anchor
            last_anchor = anchor or last_anchor
            for start in range(0, len(pairs), self.window_pairs):
                window = pairs[start : start + self.window_pairs]
                messages = tuple(
                    Message(
                        role=message["role"] if message.get("role") in {"user", "assistant"} else "user",
                        content=message.get("content", ""),
                    )
                    for pair in window
                    for message in pair
                    if message.get("content")
                )
                if messages:
                    sessions.append(
                        Session(
                            session_id=f"batch{number}_window{start // self.window_pairs + 1}",
                            timestamp=anchor,
                            messages=messages,
                        )
                    )
        items: list[BenchmarkItem] = []
        for question_type in QUESTION_TYPES:
            for question_index, question in enumerate(questions.get(question_type, ())):
                rubric: Any = question.get("rubric", ())
                if isinstance(rubric, dict):
                    rubric = [
                        nugget.get("description", str(nugget)) if isinstance(nugget, dict) else str(nugget)
                        for nugget in rubric.get("nuggets", ())
                    ]
                items.append(
                    BenchmarkItem(
                        benchmark="beam",
                        question_id=f"beam{scale}_{chat_id}_{question_type}_{question_index}",
                        question_type=question_type,
                        question=question["question"],
                        reference_answer=question.get("ideal_response", ""),
                        question_date=last_anchor,
                        sessions=tuple(sessions),
                        subject=USER_SUBJECT,
                        judge_id="beam",
                        rubric=tuple(str(value) for value in rubric),
                        conversation=chat_id,
                        topic_category=topic.get("category"),
                        difficulty=question.get("difficulty"),
                    )
                )
        return items

    def source_files(self) -> tuple[Path, ...]:
        return tuple(
            sorted(self.directory.glob("*/*/chat.json"))
            + sorted(self.directory.glob("*/*/probing_questions/probing_questions.json"))
            + sorted(self.directory.glob("*/*/topic.json"))
        )
