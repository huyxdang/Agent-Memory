from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable

from adaption_memory.domain import CallRecord, CallState


@dataclass(frozen=True)
class CostSummary:
    known_spend_usd: float
    unknown_or_reserved_exposure_usd: float
    unknown_outcome_calls: int


def summarize_calls(calls: Iterable[CallRecord]) -> CostSummary:
    known = Decimal("0")
    exposure = Decimal("0")
    unknown = 0
    for call in calls:
        if call.cost_usd is not None:
            known += Decimal(str(call.cost_usd))
        elif call.state in {CallState.IN_FLIGHT, CallState.UNKNOWN_OUTCOME, CallState.RESPONSE_SAVED}:
            exposure += Decimal(str(call.reserved_usd))
        if call.state is CallState.UNKNOWN_OUTCOME:
            unknown += 1
    return CostSummary(
        known_spend_usd=float(known),
        unknown_or_reserved_exposure_usd=float(exposure),
        unknown_outcome_calls=unknown,
    )


def cost_usd(
    usage: dict[str, Any],
    input_rate: float,
    cached_input_rate: float,
    output_rate: float,
) -> float | None:
    if usage.get("input_tokens") is None or usage.get("output_tokens") is None:
        return None
    cached = usage.get("cached_input_tokens", 0) or 0
    uncached = max(usage["input_tokens"] - cached, 0)
    return round((uncached * input_rate + cached * cached_input_rate + usage["output_tokens"] * output_rate) / 1_000_000, 8)


def aggregate_call_dicts(calls: Iterable[dict[str, Any] | None]) -> dict[str, Any]:
    total: dict[str, Any] = {
        "calls": 0,
        "failed_calls": 0,
        "unknown_usage_calls": 0,
        "unknown_cost_calls": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "non_reasoning_output_tokens": 0,
        "known_spend_usd": 0.0,
        "unknown_or_reserved_exposure_usd": 0.0,
        "elapsed_seconds": 0.0,
    }
    for call in calls:
        if not call:
            continue
        total["calls"] += 1
        total["failed_calls"] += int(not call.get("ok", False))
        usage = call.get("usage") or {}
        unknown_usage = usage.get("input_tokens") is None or usage.get("output_tokens") is None
        total["unknown_usage_calls"] += int(unknown_usage)
        total["unknown_cost_calls"] += int(call.get("cost_usd") is None)
        output = usage.get("output_tokens") or 0
        reasoning = usage.get("reasoning_output_tokens") or 0
        non_reasoning = max(output - reasoning, 0)
        for key, value in (
            ("input_tokens", usage.get("input_tokens") or 0),
            ("cached_input_tokens", usage.get("cached_input_tokens") or 0),
            ("output_tokens", output),
            ("reasoning_output_tokens", reasoning),
            ("non_reasoning_output_tokens", non_reasoning),
        ):
            total[key] += value
        total["known_spend_usd"] += call.get("cost_usd") or 0.0
        if call.get("cost_usd") is None and call.get("state") in {
            CallState.IN_FLIGHT.value,
            CallState.UNKNOWN_OUTCOME.value,
            CallState.RESPONSE_SAVED.value,
        }:
            total["unknown_or_reserved_exposure_usd"] += call.get("reserved_usd") or 0.0
        total["elapsed_seconds"] += call.get("elapsed_seconds") or 0.0
    for key in ("known_spend_usd", "unknown_or_reserved_exposure_usd"):
        total[key] = round(total[key], 8)
    total["elapsed_seconds"] = round(total["elapsed_seconds"], 4)
    return total
