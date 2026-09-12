from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_json(value: dict[str, object]) -> str:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


class CallState(str, Enum):
    NOT_DISPATCHED = "not_dispatched"
    IN_FLIGHT = "in_flight"
    UNKNOWN_OUTCOME = "unknown_outcome"
    RESPONSE_SAVED = "response_saved"
    INVALID_OUTPUT = "invalid_output"
    COMPLETE = "complete"


_CALL_TRANSITIONS = {
    CallState.NOT_DISPATCHED: {CallState.IN_FLIGHT},
    CallState.IN_FLIGHT: {CallState.NOT_DISPATCHED, CallState.UNKNOWN_OUTCOME, CallState.RESPONSE_SAVED},
    CallState.RESPONSE_SAVED: {CallState.INVALID_OUTPUT, CallState.COMPLETE},
    CallState.INVALID_OUTPUT: {CallState.IN_FLIGHT},
    CallState.UNKNOWN_OUTCOME: set(),
    CallState.COMPLETE: set(),
}


def retry_allowed(state: CallState) -> bool:
    return state in {CallState.NOT_DISPATCHED, CallState.INVALID_OUTPUT}


@dataclass(frozen=True)
class CallRecord:
    call_id: str
    requested_model: str
    state: CallState
    reserved_usd: float
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    cost_usd: float | None = None
    error_type: str | None = None

    @classmethod
    def start(cls, call_id: str, requested_model: str, reserved_usd: float = 0.0) -> CallRecord:
        if not call_id:
            raise ValueError("call_id is required")
        if not requested_model:
            raise ValueError("requested_model is required")
        if reserved_usd < 0:
            raise ValueError("reserved_usd cannot be negative")
        return cls(
            call_id=call_id,
            requested_model=requested_model,
            state=CallState.NOT_DISPATCHED,
            reserved_usd=reserved_usd,
            created_at=utcnow(),
        )

    def transition(self, state: CallState, **changes: object) -> CallRecord:
        if state not in _CALL_TRANSITIONS[self.state]:
            raise ValueError(f"Invalid call transition: {self.state.value} -> {state.value}")
        values = dict(changes)
        values["state"] = state
        if state == CallState.IN_FLIGHT:
            values.setdefault("started_at", utcnow())
            values.setdefault("finished_at", None)
            values.setdefault("error_type", None)
        if state in {CallState.UNKNOWN_OUTCOME, CallState.INVALID_OUTPUT, CallState.COMPLETE}:
            values.setdefault("finished_at", utcnow())
        allowed = {"state", "started_at", "finished_at", "cost_usd", "error_type"}
        unknown = set(values) - allowed
        if unknown:
            raise TypeError(f"Unsupported CallRecord fields: {sorted(unknown)}")
        result = replace(self, **values)
        if result.cost_usd is not None and result.cost_usd < 0:
            raise ValueError("cost_usd cannot be negative")
        return result


@dataclass(frozen=True)
class ModelSpec:
    name: str
    revision: str
    context_window: int
    default_gpu: str
    gated: bool
    sampling: tuple[tuple[str, float], ...]
    merge_user_messages: bool
    dtype: str
    language_model_only: bool
    max_num_batched_tokens: int
    gpu_memory_utilization: float

    def __post_init__(self) -> None:
        if len(self.revision) != 40 or any(character not in "0123456789abcdef" for character in self.revision):
            raise ValueError(f"Model {self.name!r} requires a pinned 40-character revision")
        if self.context_window < 1:
            raise ValueError("context_window must be positive")

    def sampling_dict(self) -> dict[str, float]:
        return dict(self.sampling)

    def engine_dict(self) -> dict[str, object]:
        return {
            "dtype": self.dtype,
            "language_model_only": self.language_model_only,
            "max_num_batched_tokens": self.max_num_batched_tokens,
            "gpu_memory_utilization": self.gpu_memory_utilization,
        }


@dataclass(frozen=True)
class AdapterSpec:
    repo: str
    revision: str
    name: str
    rank: int
    base_model: str

    def __post_init__(self) -> None:
        if len(self.revision) != 40 or any(character not in "0123456789abcdef" for character in self.revision):
            raise ValueError(f"Adapter {self.repo!r} requires a pinned 40-character revision")
        if self.rank < 1:
            raise ValueError("Adapter rank must be positive")


@dataclass(frozen=True)
class SourceDigest:
    name: str
    sha256: str
    revision: str | None = None


@dataclass(frozen=True)
class PromptDigest:
    name: str
    sha256: str


@dataclass(frozen=True)
class ExperimentSpec:
    benchmark: str
    split: str
    extractor: str
    answerer: str
    judge: str
    executor: str
    extractor_model: ModelSpec
    adapter: AdapterSpec | None
    sources: tuple[SourceDigest, ...]
    prompts: tuple[PromptDigest, ...]
    parameters: tuple[tuple[str, str | int | float | bool], ...]
    concurrency: int
    implementation_revision: str

    def __post_init__(self) -> None:
        if self.concurrency < 1:
            raise ValueError("concurrency must be positive")
        if self.adapter and self.adapter.base_model != self.extractor_model.name:
            raise ValueError("Adapter base model does not match the extractor model")

    def configuration_dict(self) -> dict[str, object]:
        """The experiment as configured, independent of the code that runs it."""
        return {
            "benchmark": self.benchmark,
            "split": self.split,
            "extractor": self.extractor,
            "answerer": self.answerer,
            "judge": self.judge,
            "executor": self.executor,
            "extractor_model": {
                "name": self.extractor_model.name,
                "revision": self.extractor_model.revision,
                "context_window": self.extractor_model.context_window,
                "default_gpu": self.extractor_model.default_gpu,
                "gated": self.extractor_model.gated,
                "sampling": self.extractor_model.sampling_dict(),
                "merge_user_messages": self.extractor_model.merge_user_messages,
                "engine": self.extractor_model.engine_dict(),
            },
            "adapter": None if self.adapter is None else {
                "repo": self.adapter.repo,
                "revision": self.adapter.revision,
                "name": self.adapter.name,
                "rank": self.adapter.rank,
                "base_model": self.adapter.base_model,
            },
            "sources": [source.__dict__ for source in self.sources],
            "prompts": [prompt.__dict__ for prompt in self.prompts],
            "parameters": dict(self.parameters),
            "concurrency": self.concurrency,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.configuration_dict(), "implementation_revision": self.implementation_revision}

    def sha256(self) -> str:
        """Full run identity. Changes when the configuration or the implementation changes."""
        return _sha256_json(self.to_dict())

    def configuration_sha256(self) -> str:
        """Frozen experiment identity. Stable across code edits that do not alter the experiment."""
        return _sha256_json(self.configuration_dict())


@dataclass(frozen=True)
class MemoryArtifact:
    history_sha256: str
    subject: str
    lines: tuple[dict[str, object], ...]
    call_ids: tuple[str, ...]
    implementation_revision: str
