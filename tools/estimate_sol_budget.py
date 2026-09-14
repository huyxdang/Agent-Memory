"""Reprice saved unique-history extraction usage; no model calls or cache assumptions."""
import json
from pathlib import Path

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.integrity import atomic_json, sha256_file


SOURCES = {
    "beam_gemma_proxy": "runs/gemma3-beam-90-003/modal",
    "beam_qwen_proxy": "work/qwen_beam_vllm_max",
    "locomo_qwen_proxy": "work/qwen_locomo_sampling_completion",
}


def estimate(directory):
    paths = sorted((directory / "memories").glob("*.json"))
    if not paths:
        raise ValueError(f"No saved histories in {directory}")
    states = [json.loads(path.read_text()) for path in paths]
    calls = [call for state in states for call in state["calls"] if call["status"] == "complete"]
    if any(type(call.get("input_tokens")) is not int or
           type(call.get("output_tokens")) is not int for call in calls):
        raise ValueError("Saved usage is missing; cannot estimate it as zero")
    cost = sum((call["input_tokens"] * (8 if call["input_tokens"] > 272_000 else 4)
        + call["output_tokens"] * (30 if call["input_tokens"] > 272_000 else 20)) / 1e6
        for call in calls)
    return {"histories": len(states), "updates": len(calls),
        "input_tokens": sum(call["input_tokens"] for call in calls),
        "output_tokens": sum(call["output_tokens"] for call in calls),
        "standard_uncached_extraction_proxy_usd": cost,
        "source_sha256": {str(p.relative_to(PROJECT_ROOT)): sha256_file(p) for p in paths}}


if __name__ == "__main__":
    result = {"approved_total_usd": 20.0,
        "pricing_source": "https://developers.openai.com/api/docs/models/gpt-5.6-sol",
        "pricing_checked_on": "2026-09-12",
        "limitations": "Historical model tokenizer and generated memory sizes are proxies, not Sol measurements. Excludes answering, judging, retries, cache reads and cache-write premiums. LongMemEval is not estimated. Not a spending guarantee.",
        "estimates": {name: estimate(PROJECT_ROOT / path) for name, path in SOURCES.items()}}
    atomic_json(PROJECT_ROOT / "work/sol-budget-preflight-20260912.json", result)
    print(json.dumps({k: {field: value for field, value in row.items() if field != "source_sha256"}
        for k, row in result["estimates"].items()}, indent=2))
