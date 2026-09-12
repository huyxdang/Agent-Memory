from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .records import (
    ARTIFACT_SCHEMA_VERSION,
    ArtifactRef,
    RunManifest,
    RunStatus,
    canonical_json,
    sha256_bytes,
)


POINTER_SCHEMA_VERSION = 1
COMMIT_SCHEMA_VERSION = 1


def _atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def _exclusive(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _results_bytes(results: list[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json(row) for row in results)


def _validate_results(manifest: RunManifest, results: list[dict[str, Any]]) -> None:
    ids = [row.get("question_id") for row in results]
    if ids != list(manifest.question_ids):
        raise ValueError("Results must contain every selected question exactly once and in manifest order")


def _validate_graph(manifest: RunManifest, run_directory: Path, verify_files: bool) -> None:
    refs = {artifact.sha256: artifact for artifact in manifest.artifacts}
    for artifact in manifest.artifacts:
        missing = [parent for parent in artifact.parent_sha256 if parent not in refs]
        if missing:
            raise ValueError(f"Artifact {artifact.sha256} has a missing parent: {missing}")
        if not verify_files:
            continue
        path = run_directory / artifact.path
        if not path.is_file():
            raise RuntimeError(f"Artifact file is missing: {artifact.path}")
        value = path.read_bytes()
        if sha256_bytes(value) != artifact.sha256:
            raise RuntimeError(f"Artifact hash mismatch: {artifact.path}")
        envelope = json.loads(value)
        if envelope.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported artifact schema: {artifact.path}")
        if tuple(envelope.get("parent_sha256", ())) != artifact.parent_sha256:
            raise RuntimeError(f"Artifact parent hashes differ: {artifact.path}")
        if envelope.get("implementation_revision") != artifact.implementation_revision:
            raise RuntimeError(f"Artifact implementation revision differs: {artifact.path}")


@dataclass(frozen=True)
class LoadedRun:
    manifest: RunManifest
    results: list[dict[str, Any]]
    generation: str


class RunStore:
    def __init__(self, root: Path):
        self.root = Path(root)

    def _run_directory(self, run_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id):
            raise ValueError(f"Invalid run ID: {run_id!r}")
        return self.root / run_id

    def put_artifact(
        self,
        run_id: str,
        kind: str,
        payload: Any,
        parent_sha256: tuple[str, ...],
        implementation_revision: str,
    ) -> ArtifactRef:
        envelope = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "kind": kind,
            "parent_sha256": list(parent_sha256),
            "implementation_revision": implementation_revision,
            "payload": payload,
        }
        value = canonical_json(envelope)
        digest = sha256_bytes(value)
        relative = Path("artifacts") / kind / f"{digest}.json"
        path = self._run_directory(run_id) / relative
        if path.exists() and path.read_bytes() != value:
            raise RuntimeError(f"Content-addressed artifact collision: {digest}")
        if not path.exists():
            _atomic_write(path, value)
        return ArtifactRef(
            kind=kind,
            sha256=digest,
            path=relative.as_posix(),
            parent_sha256=parent_sha256,
            implementation_revision=implementation_revision,
        )

    def read_artifact(self, run_id: str, artifact: ArtifactRef) -> Any:
        path = self._run_directory(run_id) / artifact.path
        value = path.read_bytes()
        if sha256_bytes(value) != artifact.sha256:
            raise RuntimeError(f"Artifact hash mismatch: {artifact.path}")
        envelope = json.loads(value)
        if envelope.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported artifact schema: {artifact.path}")
        if envelope.get("kind") != artifact.kind:
            raise RuntimeError(f"Artifact kind differs: {artifact.path}")
        if tuple(envelope.get("parent_sha256", ())) != artifact.parent_sha256:
            raise RuntimeError(f"Artifact parent hashes differ: {artifact.path}")
        if envelope.get("implementation_revision") != artifact.implementation_revision:
            raise RuntimeError(f"Artifact implementation revision differs: {artifact.path}")
        return envelope["payload"]

    def checkpoint(self, manifest: RunManifest, results: list[dict[str, Any]]) -> str:
        _validate_results(manifest, results)
        directory = self._run_directory(manifest.run_id)
        _validate_graph(manifest, directory, verify_files=False)
        manifest_bytes = canonical_json(manifest.to_dict())
        results_bytes = _results_bytes(results)
        generation = sha256_bytes(manifest_bytes + b"\0" + results_bytes)

        with _exclusive(directory / "run.lock"):
            pointer_path = directory / "current.json"
            if pointer_path.exists() and self.load(manifest.run_id).manifest.status.terminal:
                raise RuntimeError(f"Run {manifest.run_id} is terminal and immutable")

            generations = directory / "generations"
            generations.mkdir(parents=True, exist_ok=True)
            final = generations / generation
            if not final.exists():
                temporary = Path(tempfile.mkdtemp(prefix=f".{generation}.", dir=generations))
                try:
                    _atomic_write(temporary / "manifest.json", manifest_bytes)
                    _atomic_write(temporary / "results.jsonl", results_bytes)
                    commit = canonical_json(
                        {
                            "schema_version": COMMIT_SCHEMA_VERSION,
                            "manifest_sha256": sha256_bytes(manifest_bytes),
                            "results_sha256": sha256_bytes(results_bytes),
                            "written_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    _atomic_write(temporary / "commit.json", commit)
                    os.replace(temporary, final)
                    parent = os.open(generations, os.O_RDONLY)
                    try:
                        os.fsync(parent)
                    finally:
                        os.close(parent)
                finally:
                    if temporary.exists():
                        shutil.rmtree(temporary)
            commit_bytes = (final / "commit.json").read_bytes()
            pointer = canonical_json(
                {
                    "schema_version": POINTER_SCHEMA_VERSION,
                    "generation": generation,
                    "commit_sha256": sha256_bytes(commit_bytes),
                }
            )
            _atomic_write(pointer_path, pointer)
        self.load(manifest.run_id)
        return generation

    def load(self, run_id: str, expected_spec_sha256: str | None = None) -> LoadedRun:
        directory = self._run_directory(run_id)
        pointer = json.loads((directory / "current.json").read_text())
        if pointer.get("schema_version") != POINTER_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported run pointer schema for {run_id}")
        generation = pointer.get("generation")
        if not isinstance(generation, str) or not re.fullmatch(r"[0-9a-f]{64}", generation):
            raise RuntimeError(f"Invalid checkpoint generation for {run_id}")
        generation_directory = directory / "generations" / generation
        try:
            commit_bytes = (generation_directory / "commit.json").read_bytes()
        except FileNotFoundError as error:
            raise RuntimeError(f"Run {run_id} points to a missing checkpoint generation") from error
        if sha256_bytes(commit_bytes) != pointer.get("commit_sha256"):
            raise RuntimeError(f"Run {run_id} commit hash mismatch")
        commit = json.loads(commit_bytes)
        if commit.get("schema_version") != COMMIT_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported commit schema for {run_id}")
        try:
            manifest_bytes = (generation_directory / "manifest.json").read_bytes()
            results_bytes = (generation_directory / "results.jsonl").read_bytes()
        except FileNotFoundError as error:
            raise RuntimeError(f"Run {run_id} checkpoint generation is incomplete") from error
        if sha256_bytes(manifest_bytes) != commit.get("manifest_sha256"):
            raise RuntimeError(f"Run {run_id} manifest hash mismatch")
        if sha256_bytes(results_bytes) != commit.get("results_sha256"):
            raise RuntimeError(f"Run {run_id} results hash mismatch")
        manifest = RunManifest.from_dict(json.loads(manifest_bytes))
        if manifest.run_id != run_id:
            raise RuntimeError(f"Run directory and manifest ID differ for {run_id}")
        if expected_spec_sha256 is not None and manifest.spec_sha256 != expected_spec_sha256:
            raise RuntimeError(f"Run {run_id} experiment specification hash mismatch")
        results = [json.loads(line) for line in results_bytes.splitlines() if line.strip()]
        _validate_results(manifest, results)
        _validate_graph(manifest, directory, verify_files=True)
        return LoadedRun(manifest=manifest, results=results, generation=generation)

    def new_retry(self, parent_run_id: str, run_id: str) -> RunManifest:
        parent = self.load(parent_run_id).manifest
        if not parent.status.terminal:
            raise RuntimeError(f"Cannot retry non-terminal run {parent_run_id}")
        if self._run_directory(run_id).exists():
            raise RuntimeError(f"Retry run ID already exists: {run_id}")
        return RunManifest.new(
            run_id=run_id,
            spec_sha256=parent.spec_sha256,
            question_ids=parent.question_ids,
            retry_of=parent_run_id,
        )
