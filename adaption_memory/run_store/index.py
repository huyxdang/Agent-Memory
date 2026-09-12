from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adaption_memory.execution.files import exclusive
from adaption_memory.integrity import atomic_jsonl


class RunIndex:
    """Append-only run index with exactly one immutable row per run ID."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def rows(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]

    def append(self, row: dict[str, Any]) -> None:
        run_id = row.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("Index row requires run_id")
        with exclusive(self.path.parent):
            rows = self.rows()
            if any(existing.get("run_id") == run_id for existing in rows):
                raise RuntimeError(f"Run index already contains {run_id}")
            atomic_jsonl(self.path, [*rows, row])
