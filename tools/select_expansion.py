"""Freeze the expanded question selections: LoCoMo 500, BEAM 100K 100, BEAM 500K 100.

The LoCoMo rule is the one behind question_ids_locomo_50.json, and reproducing that file exactly is
checked before the 500 is written, so the 50 is a subset of the 500 by construction. The BEAM files
take every probing question of their chats.
"""
from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

from adaption_memory.benchmarks.base import BenchmarkItem
from adaption_memory.benchmarks.beam import BeamAdapter
from adaption_memory.benchmarks.locomo import LoCoMoAdapter, WEIGHTS
from adaption_memory.config import PROJECT_ROOT

LOCOMO_50 = PROJECT_ROOT / "question_ids_locomo_50.json"
LOCOMO_500 = PROJECT_ROOT / "question_ids_locomo_500.json"
BEAM_100K_50 = PROJECT_ROOT / "question_ids_beam_50.json"
BEAM_100K_100 = PROJECT_ROOT / "question_ids_beam_100k_100.json"
BEAM_500K_40 = PROJECT_ROOT / "question_ids_beam_500k_40.json"
BEAM_500K_100 = PROJECT_ROOT / "question_ids_beam_500k_100.json"

BEAM_100K_CHATS = (1, 4, 6, 13, 16)
# 1 and 13 are the original two; 11, 19 and 30 are the lowest-numbered chats in the first three topic
# categories, alphabetically, not already represented (Asking Recommendation, Career and Professional
# Development, Cooking), excluding the extractor-fine-tune train and dev chats.
BEAM_500K_CHATS = (1, 11, 13, 19, 30)


def proportional_quotas(total: int) -> dict[str, int]:
    """Largest-remainder split of `total` across categories in the benchmark's own proportions."""
    order = ("single-hop", "temporal", "multi-hop", "open-domain")
    weight = sum(WEIGHTS.values())
    exact = {name: total * WEIGHTS[name] / weight for name in order}
    quotas = {name: int(exact[name]) for name in order}
    for name in sorted(order, key=lambda key: exact[key] - quotas[key], reverse=True)[: total - sum(quotas.values())]:
        quotas[name] += 1
    return quotas


def select_locomo(items: Iterable[BenchmarkItem], quotas: dict[str, int]) -> list[BenchmarkItem]:
    """Per category, round-robin over the conversations in dataset order, taking each one's questions in order."""
    by_key: dict[tuple[int, str], deque[BenchmarkItem]] = defaultdict(deque)
    conversations: list[int] = []
    for item in items:
        if item.conversation not in conversations:
            conversations.append(item.conversation)
        by_key[(item.conversation, item.question_type)].append(item)
    selected: list[BenchmarkItem] = []
    for question_type, quota in quotas.items():
        queues = [by_key[(conversation, question_type)] for conversation in conversations]
        picked: list[BenchmarkItem] = []
        while len(picked) < quota and any(queues):
            for queue in queues:
                if len(picked) == quota:
                    break
                if queue:
                    picked.append(queue.popleft())
        if len(picked) < quota:
            raise ValueError(f"Not enough {question_type} questions for a quota of {quota}")
        selected.extend(picked)
    return selected


def entries(items: Iterable[BenchmarkItem]) -> list[dict[str, object]]:
    return [{"question_id": item.question_id, "question_type": item.question_type, "conversation": item.conversation} for item in items]


def ids(path: Path) -> list[str]:
    return [entry["question_id"] for entry in json.loads(path.read_text())["questions"]]


def build_locomo_500() -> dict[str, object]:
    items = LoCoMoAdapter().load()
    frozen = json.loads(LOCOMO_50.read_text())
    reproduced = [item.question_id for item in select_locomo(items, frozen["per_type"])]
    if reproduced != ids(LOCOMO_50):
        raise ValueError("The LoCoMo selection rule does not reproduce question_ids_locomo_50.json")
    quotas = proportional_quotas(500)
    selected = select_locomo(items, quotas)
    if not set(ids(LOCOMO_50)) <= {item.question_id for item in selected}:
        raise ValueError("The 500 does not contain the 50")
    return {
        "benchmark": "locomo",
        "source": frozen["source"],
        "selection_rule": (
            "Categories 1-4 only (Mem0 excludes 5, adversarial). Quotas in the benchmark's own proportions: "
            + ", ".join(f"{name} {count}" for name, count in quotas.items())
            + ". Round-robin over the 10 conversations in dataset order, taking each conversation's questions "
            "of that category in order; the same rule as question_ids_locomo_50.json, which it therefore contains."
        ),
        "per_type": quotas,
        "questions": entries(selected),
    }


def build_beam(scale: str, chats: tuple[int, ...], frozen_path: Path, rule: str) -> dict[str, object]:
    frozen = json.loads(frozen_path.read_text())
    items = BeamAdapter(scale=scale, chat_ids=chats).load()
    if not set(ids(frozen_path)) <= {item.question_id for item in items}:
        raise ValueError(f"{frozen_path.name} is not contained in the {scale} expansion")
    return {
        "benchmark": "beam",
        "scale": scale,
        "chats": list(chats),
        "source": frozen["source"],
        "selection_rule": rule,
        "window_pairs": frozen.get("window_pairs", 8),
        "questions": entries(items),
    }


def main() -> int:
    files = {
        LOCOMO_500: build_locomo_500(),
        BEAM_100K_100: build_beam(
            "100K", BEAM_100K_CHATS, BEAM_100K_50,
            "The same five 100K chats as question_ids_beam_50.json; every probing question of each chat, "
            "two per ability type, 100 in all.",
        ),
        BEAM_500K_100: build_beam(
            "500K", BEAM_500K_CHATS, BEAM_500K_40,
            "Chats 1 and 13 from question_ids_beam_500k_40.json plus 11, 19 and 30: the lowest-numbered chat in "
            "each of the first three topic categories, alphabetically, not already represented (Asking "
            "Recommendation, Career and Professional Development, Cooking), excluding the extractor-fine-tune "
            "train and dev chats. Every probing question of each chat, two per ability type, 100 in all. "
            "Chosen before any run.",
        ),
    }
    for path, value in files.items():
        path.write_text(json.dumps(value, indent=2) + "\n")
        print(f"{path.name}: {len(value['questions'])} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
