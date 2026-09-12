from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from adaption_memory import memory


class ExtractorPolicy(Protocol):
    name: str
    response_format: dict[str, Any] | None

    def system_prompt(self, subject: str) -> str: ...

    def user_messages(
        self,
        lines: list[dict[str, Any]],
        session_number: int,
        session_count: int,
        timestamp: str,
        messages: list[dict[str, str]],
    ) -> tuple[dict[str, Any], ...]: ...

    def apply(
        self,
        lines: list[dict[str, Any]],
        content: str,
        session_number: int,
        timestamp: str,
        messages: list[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]: ...


@dataclass(frozen=True)
class AppendOnlyMemoryExtractor:
    name: str = "append-only-memory-v1"
    response_format: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "response_format", memory.EXTRACTION_RESPONSE_FORMAT)

    def system_prompt(self, subject: str) -> str:
        return memory.extraction_system_prompt(subject)

    def user_messages(
        self,
        lines: list[dict[str, Any]],
        session_number: int,
        session_count: int,
        timestamp: str,
        messages: list[dict[str, str]],
    ) -> tuple[dict[str, Any], ...]:
        parts = memory.extraction_parts(lines, session_number, session_count, timestamp, messages)
        return tuple(memory.extraction_messages(parts))

    def apply(
        self,
        lines: list[dict[str, Any]],
        content: str,
        session_number: int,
        timestamp: str,
        messages: list[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        parsed = memory.parse_extraction(content)
        return memory.apply_extraction(
            lines,
            parsed,
            session_number,
            timestamp,
            memory.session_text(messages),
        )
