from __future__ import annotations

import subprocess
from pathlib import Path

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.integrity import sha256_file


def git_metadata(script: Path | None = None) -> dict[str, object]:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
        dirty = bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    return {
        "git_head": head,
        "git_dirty": dirty,
        "script_sha256": sha256_file(script) if script is not None else None,
    }
