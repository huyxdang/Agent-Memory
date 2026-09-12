from __future__ import annotations

from pathlib import Path

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.integrity import sha256_file


RUNTIME_SOURCE_PATHS = tuple(
    sorted(
        str(path.relative_to(PROJECT_ROOT))
        for path in (PROJECT_ROOT / "adaption_memory").rglob("*.py")
    )
) + (
    "third_party/mem0/beam_prompts.py",
    "third_party/mem0/locomo_prompts.py",
)


def source_hashes(root: Path = PROJECT_ROOT) -> dict[str, str]:
    missing = [name for name in RUNTIME_SOURCE_PATHS if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Runtime source manifest contains missing files: {missing}")
    return {name: sha256_file(root / name) for name in RUNTIME_SOURCE_PATHS}
