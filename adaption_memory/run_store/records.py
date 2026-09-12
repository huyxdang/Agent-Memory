from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Iterable


RUN_SCHEMA_VERSION = 2
ARTIFACT_SCHEMA_VERSION = 1
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def question_set_sha256(question_ids: Iterable[str]) -> str:
    return sha256_bytes(canonical_json(list(question_ids)))


def _validate_sha256(name: str, value: str) -> None:
    if not SHA256_PATTERN.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    COMPLETE_WITH_FAILURES = "complete_with_failures"
    BLOCKED = "blocked"

    @property
    def terminal(self) -> bool:
        return self is not RunStatus.RUNNING


@dataclass(frozen=True)
class ArtifactRef:
    kind: str
    sha256: str
    path: str
    parent_sha256: tuple[str, ...]
    implementation_revision: str

    def __post_init__(self) -> None:
        if not self.kind or "/" in self.kind or ".." in self.kind:
            raise ValueError("Artifact kind must be one path segment")
        _validate_sha256("artifact sha256", self.sha256)
        for parent in self.parent_sha256:
            _validate_sha256("parent sha256", parent)
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Artifact path must stay inside the run directory")
        if not self.implementation_revision:
            raise ValueError("Artifact implementation_revision is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "sha256": self.sha256,
            "path": self.path,
            "parent_sha256": list(self.parent_sha256),
            "implementation_revision": self.implementation_revision,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ArtifactRef:
        return cls(
            kind=value["kind"],
            sha256=value["sha256"],
            path=value["path"],
            parent_sha256=tuple(value.get("parent_sha256", ())),
            implementation_revision=value["implementation_revision"],
        )


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    status: RunStatus
    spec_sha256: str
    question_ids: tuple[str, ...]
    question_set_sha256: str
    artifacts: tuple[ArtifactRef, ...]
    retry_of: str | None
    started_at: str
    finished_at: str | None
    schema_version: int = RUN_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != RUN_SCHEMA_VERSION:
            raise ValueError(f"Unsupported run schema version: {self.schema_version}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", self.run_id):
            raise ValueError(f"Invalid run ID: {self.run_id!r}")
        _validate_sha256("spec_sha256", self.spec_sha256)
        _validate_sha256("question_set_sha256", self.question_set_sha256)
        if not self.question_ids or len(self.question_ids) != len(set(self.question_ids)):
            raise ValueError("question_ids must be non-empty and unique")
        if question_set_sha256(self.question_ids) != self.question_set_sha256:
            raise ValueError("question_set_sha256 does not match question_ids")
        if self.retry_of == self.run_id:
            raise ValueError("A run cannot retry itself")
        artifact_hashes = [artifact.sha256 for artifact in self.artifacts]
        if len(artifact_hashes) != len(set(artifact_hashes)):
            raise ValueError("Artifact hashes must be unique within a run")

    @classmethod
    def new(
        cls,
        run_id: str,
        spec_sha256: str,
        question_ids: tuple[str, ...],
        retry_of: str | None = None,
    ) -> RunManifest:
        return cls(
            run_id=run_id,
            status=RunStatus.RUNNING,
            spec_sha256=spec_sha256,
            question_ids=question_ids,
            question_set_sha256=question_set_sha256(question_ids),
            artifacts=(),
            retry_of=retry_of,
            started_at=datetime.now(timezone.utc).isoformat(),
            finished_at=None,
        )

    def with_status(self, status: RunStatus) -> RunManifest:
        finished_at = datetime.now(timezone.utc).isoformat() if status.terminal else None
        return replace(self, status=status, finished_at=finished_at)

    def with_artifacts(self, artifacts: tuple[ArtifactRef, ...]) -> RunManifest:
        return replace(self, artifacts=artifacts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "status": self.status.value,
            "spec_sha256": self.spec_sha256,
            "question_ids": list(self.question_ids),
            "question_set_sha256": self.question_set_sha256,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "retry_of": self.retry_of,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> RunManifest:
        return cls(
            schema_version=value["schema_version"],
            run_id=value["run_id"],
            status=RunStatus(value["status"]),
            spec_sha256=value["spec_sha256"],
            question_ids=tuple(value["question_ids"]),
            question_set_sha256=value["question_set_sha256"],
            artifacts=tuple(ArtifactRef.from_dict(item) for item in value.get("artifacts", ())),
            retry_of=value.get("retry_of"),
            started_at=value["started_at"],
            finished_at=value.get("finished_at"),
        )
