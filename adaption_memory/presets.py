from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adaption_memory import memory
from adaption_memory.benchmarks.base import BenchmarkItem, select_items
from adaption_memory.benchmarks.registry import adapter as benchmark_adapter
from adaption_memory.config import PROJECT_ROOT
from adaption_memory.domain import AdapterSpec, ExperimentSpec, PromptDigest, SourceDigest
from adaption_memory.evaluation.answering import ANSWER_SYSTEM_PROMPTS
from adaption_memory.evaluation.judges import LONGMEMEVAL_JUDGE_PROMPT
from adaption_memory.inference.adapters import adapter_spec
from adaption_memory.inference.models import model_spec
from adaption_memory.integrity import canonical_json, sha256_bytes, sha256_file, sha256_text
from adaption_memory.source_manifest import source_hashes
from third_party.mem0 import beam_prompts, locomo_prompts


PRESET_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ExperimentPreset:
    name: str
    benchmark: str
    selections: tuple[Path, ...]
    system: str
    extractor_model: str
    executor: str
    answerer: str
    judge: str
    answer_reasoning_effort: str | None
    judge_reasoning_effort: str | None
    concurrency: int
    answer_prompt: str
    answer_context_window: int
    extraction_max_tokens: int
    answer_max_tokens: int
    judge_max_tokens: int
    answer_input_cost: float
    answer_cached_input_cost: float
    answer_output_cost: float
    judge_input_cost: float
    judge_cached_input_cost: float
    judge_output_cost: float
    adapter_repo: str | None = None
    adapter_revision: str | None = None


def load_preset(path: Path) -> ExperimentPreset:
    value = json.loads(Path(path).read_text())
    if value.get("schema_version") != PRESET_SCHEMA_VERSION:
        raise ValueError("Unsupported experiment preset schema")
    root = Path(path).resolve().parent
    selections = tuple((root / name).resolve() for name in value["selections"])
    adapter = value.get("adapter")
    return ExperimentPreset(
        name=value["name"],
        benchmark=value["benchmark"],
        selections=selections,
        system=value["system"],
        extractor_model=value["extractor_model"],
        executor=value["executor"],
        answerer=value["answerer"],
        judge=value["judge"],
        answer_reasoning_effort=value["answer_reasoning_effort"],
        judge_reasoning_effort=value["judge_reasoning_effort"],
        concurrency=int(value["concurrency"]),
        answer_prompt=value.get("answer_prompt", "v2"),
        answer_context_window=int(value["answer_context_window"]),
        extraction_max_tokens=int(value["extraction_max_tokens"]),
        answer_max_tokens=int(value["answer_max_tokens"]),
        judge_max_tokens=int(value["judge_max_tokens"]),
        answer_input_cost=float(value["prices_usd_per_million_tokens"]["answer_input"]),
        answer_cached_input_cost=float(value["prices_usd_per_million_tokens"]["answer_cached_input"]),
        answer_output_cost=float(value["prices_usd_per_million_tokens"]["answer_output"]),
        judge_input_cost=float(value["prices_usd_per_million_tokens"]["judge_input"]),
        judge_cached_input_cost=float(value["prices_usd_per_million_tokens"]["judge_cached_input"]),
        judge_output_cost=float(value["prices_usd_per_million_tokens"]["judge_output"]),
        adapter_repo=adapter.get("repo") if adapter else None,
        adapter_revision=adapter.get("revision") if adapter else None,
    )


def selected_items(preset: ExperimentPreset) -> list[BenchmarkItem]:
    all_items = benchmark_adapter(preset.benchmark).load()
    selected: list[BenchmarkItem] = []
    for path in preset.selections:
        selected.extend(select_items(all_items, path))
    ids = [item.question_id for item in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("Selections contain duplicate question IDs")
    return selected


def _judge_text(benchmark: str) -> str:
    return {
        "longmemeval": LONGMEMEVAL_JUDGE_PROMPT,
        "locomo": locomo_prompts.JUDGE_PROMPT,
        "beam": beam_prompts.JUDGE_PROMPT,
    }[benchmark]


def _judge_system_text(benchmark: str) -> str:
    return {
        "longmemeval": "",
        "locomo": locomo_prompts.JUDGE_SYSTEM_PROMPT,
        "beam": beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT,
    }[benchmark]


def resolve(preset: ExperimentPreset) -> ExperimentSpec:
    if preset.system not in {"full-history", "memory"}:
        raise ValueError("The canonical runner currently supports full-history and memory systems")
    if preset.executor not in {"local", "modal", "fixture"}:
        raise ValueError("Unsupported executor")
    model = model_spec(preset.extractor_model)
    adapter: AdapterSpec | None = None
    if preset.adapter_repo:
        if not preset.adapter_revision:
            raise ValueError("Adapter revision is required")
        adapter = adapter_spec(preset.adapter_repo, preset.adapter_revision)
    elif preset.adapter_revision:
        raise ValueError("Adapter revision requires an adapter repository")
    def source_name(path: Path) -> str:
        try:
            return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
        except ValueError:
            return str(path.resolve())

    sources = [
        SourceDigest(name=source_name(path), sha256=sha256_file(path))
        for path in (*benchmark_adapter(preset.benchmark).source_files(), *preset.selections)
    ]
    prompts = (
        PromptDigest("extraction", sha256_text(memory.EXTRACTION_SYSTEM_TEMPLATE)),
        # The response schema constrains generation as a grammar, so two runs with
        # the same prompt but different schemas are different experiments.
        PromptDigest("extraction_schema", sha256_bytes(canonical_json(memory.EXTRACTION_RESPONSE_FORMAT))),
        PromptDigest("memory_answer", sha256_text(memory.ANSWER_SYSTEM_PROMPTS[preset.answer_prompt])),
        PromptDigest("full_history_answer", sha256_text(ANSWER_SYSTEM_PROMPTS[preset.answer_prompt])),
        PromptDigest("judge", sha256_text(_judge_text(preset.benchmark))),
        PromptDigest("judge_system", sha256_text(_judge_system_text(preset.benchmark))),
    )
    implementation_revision = sha256_bytes(canonical_json(source_hashes()))
    return ExperimentSpec(
        benchmark=preset.benchmark,
        split=preset.name,
        extractor=preset.system,
        answerer=preset.answerer,
        judge=preset.judge,
        executor=preset.executor,
        extractor_model=model,
        adapter=adapter,
        sources=tuple(sources),
        prompts=prompts,
        parameters=(
            ("answer_prompt", preset.answer_prompt),
            ("answer_reasoning_effort", preset.answer_reasoning_effort or "provider-default"),
            ("judge_reasoning_effort", preset.judge_reasoning_effort or "provider-default"),
            ("answer_context_window", preset.answer_context_window),
            ("extraction_max_tokens", preset.extraction_max_tokens),
            ("answer_max_tokens", preset.answer_max_tokens),
            ("judge_max_tokens", preset.judge_max_tokens),
            ("answer_input_cost", preset.answer_input_cost),
            ("answer_cached_input_cost", preset.answer_cached_input_cost),
            ("answer_output_cost", preset.answer_output_cost),
            ("judge_input_cost", preset.judge_input_cost),
            ("judge_cached_input_cost", preset.judge_cached_input_cost),
            ("judge_output_cost", preset.judge_output_cost),
        ),
        concurrency=preset.concurrency,
        implementation_revision=implementation_revision,
    )


def preset_to_dict(preset: ExperimentPreset) -> dict[str, Any]:
    return {
        "schema_version": PRESET_SCHEMA_VERSION,
        "name": preset.name,
        "benchmark": preset.benchmark,
        "selections": [str(path) for path in preset.selections],
        "system": preset.system,
        "extractor_model": preset.extractor_model,
        "executor": preset.executor,
        "answerer": preset.answerer,
        "judge": preset.judge,
        "answer_reasoning_effort": preset.answer_reasoning_effort,
        "judge_reasoning_effort": preset.judge_reasoning_effort,
        "concurrency": preset.concurrency,
        "answer_prompt": preset.answer_prompt,
        "answer_context_window": preset.answer_context_window,
        "extraction_max_tokens": preset.extraction_max_tokens,
        "answer_max_tokens": preset.answer_max_tokens,
        "judge_max_tokens": preset.judge_max_tokens,
        "prices_usd_per_million_tokens": {
            "answer_input": preset.answer_input_cost,
            "answer_cached_input": preset.answer_cached_input_cost,
            "answer_output": preset.answer_output_cost,
            "judge_input": preset.judge_input_cost,
            "judge_cached_input": preset.judge_cached_input_cost,
            "judge_output": preset.judge_output_cost,
        },
        "adapter": None if not preset.adapter_repo else {"repo": preset.adapter_repo, "revision": preset.adapter_revision},
    }
