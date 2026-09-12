from __future__ import annotations

from pathlib import Path

from .base import BenchmarkAdapter, BenchmarkItem
from .beam import BeamAdapter
from .locomo import LoCoMoAdapter
from .longmemeval import LongMemEvalAdapter


def adapter(name: str) -> BenchmarkAdapter:
    adapters: dict[str, BenchmarkAdapter] = {
        "longmemeval": LongMemEvalAdapter(),
        "locomo": LoCoMoAdapter(),
        "beam": BeamAdapter(),
    }
    try:
        return adapters[name]
    except KeyError as error:
        raise ValueError(f"Unknown benchmark: {name!r}") from error


def load_items(name: str) -> list[BenchmarkItem]:
    return adapter(name).load()


def load_records(name: str) -> list[dict]:
    return [item.to_record() for item in load_items(name)]


def source_files(name: str) -> list[Path]:
    return list(adapter(name).source_files())
