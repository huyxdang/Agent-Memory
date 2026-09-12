from __future__ import annotations

import json
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from adaption_memory.integrity import sha256_file

from .base import BenchmarkItem


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "work" / "longmemeval_s_cleaned.json"
DATASET_REVISION = "98d7416c24c778c2fee6e6f3006e7a073259d48f"
DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
DATASET_URL = (
    "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/"
    f"{DATASET_REVISION}/longmemeval_s_cleaned.json"
)


def download_dataset(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".download")
    with urllib.request.urlopen(DATASET_URL, timeout=60) as source, temporary.open("wb") as target:
        while chunk := source.read(1024 * 1024):
            target.write(chunk)
    digest = sha256_file(temporary)
    if digest != DATASET_SHA256:
        raise RuntimeError(f"Downloaded dataset SHA-256 mismatch: {digest}")
    temporary.replace(path)


@dataclass(frozen=True)
class LongMemEvalAdapter:
    path: Path = DATASET_PATH
    name: str = "longmemeval"

    def load(self) -> list[BenchmarkItem]:
        if not self.path.exists():
            download_dataset(self.path)
        digest = sha256_file(self.path)
        if self.path == DATASET_PATH and digest != DATASET_SHA256:
            raise RuntimeError(f"Dataset SHA-256 mismatch. Expected {DATASET_SHA256}, found {digest}.")
        data = json.loads(self.path.read_text())
        if not isinstance(data, list):
            raise RuntimeError("LongMemEval dataset must be a list")
        if self.path == DATASET_PATH and len(data) != 500:
            raise RuntimeError(f"Expected 500 dataset records, found {len(data)}")
        ids = [item.get("question_id") for item in data]
        duplicates = [key for key, count in Counter(ids).items() if count != 1]
        if duplicates:
            raise RuntimeError(f"Dataset question IDs are not unique: {duplicates}")
        return [BenchmarkItem.from_record(item) for item in data]

    def source_files(self) -> tuple[Path, ...]:
        return (self.path,)
