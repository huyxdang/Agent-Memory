from __future__ import annotations

import json
import threading
import time
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, ContextManager

from adaption_memory.domain import CallState
from adaption_memory.inference.usage import usage_dict
from adaption_memory.run_store.accounting import cost_usd


@dataclass(frozen=True)
class Price:
    input_per_million: float
    cached_input_per_million: float
    output_per_million: float


@dataclass(frozen=True)
class ChatRequest:
    call_id: str
    model: str
    system: str
    user_messages: tuple[dict[str, Any], ...]
    max_output_tokens: int
    price: Price
    reasoning_effort: str | None = None
    response_format: dict[str, Any] | None = None


class BudgetLedger:
    """Tracks upper-bound reservations separately from measured spend."""

    def __init__(self, limit_usd: float):
        if limit_usd <= 0:
            raise ValueError("Paid budget limit must be positive")
        self.limit_usd = limit_usd
        self._reserved: dict[str, float] = {}
        self._known = 0.0
        self._lock = threading.Lock()

    def reserve(self, call_id: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("Reservation cannot be negative")
        with self._lock:
            if call_id in self._reserved:
                raise RuntimeError(f"Call already has a reservation: {call_id}")
            if self._known + sum(self._reserved.values()) + amount > self.limit_usd:
                raise RuntimeError("Spending limit: cannot reserve the next call safely")
            self._reserved[call_id] = amount

    def settle(self, call_id: str, amount: float | None) -> None:
        with self._lock:
            if call_id not in self._reserved:
                raise RuntimeError(f"No reservation for call: {call_id}")
            if amount is not None:
                self._known += amount
                self._reserved.pop(call_id)

    @property
    def known_spend_usd(self) -> float:
        with self._lock:
            return round(self._known, 8)

    @property
    def unknown_or_reserved_exposure_usd(self) -> float:
        with self._lock:
            return round(sum(self._reserved.values()), 8)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reservation(request: ChatRequest) -> float:
    payload = ([{"role": "system", "content": request.system}] if request.system else []) + list(request.user_messages)
    input_bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 512
    return (input_bound * request.price.input_per_million + request.max_output_tokens * request.price.output_per_million) / 1_000_000


class OpenAITransport:
    """OpenAI-compatible chat transport with observable, crash-safe call states."""

    def __init__(
        self,
        client: Any,
        budget: BudgetLedger,
        observe: Callable[[dict[str, Any]], None] | None = None,
        slots: ContextManager[Any] | None = None,
        sleep: Callable[[float], None] = time.sleep,
        rate_limit_error: type[Exception] | tuple[type[Exception], ...] | None = None,
    ):
        self.client = client
        self.budget = budget
        self.observe = observe or (lambda call: None)
        self.slots = slots
        self.sleep = sleep
        if rate_limit_error is None:
            from openai import RateLimitError

            rate_limit_error = RateLimitError
        self.rate_limit_error = rate_limit_error

    def chat(
        self,
        request: ChatRequest,
        observe: Callable[[dict[str, Any]], None] | None = None,
        finalize: bool = True,
    ) -> dict[str, Any]:
        notify = observe or self.observe
        started = time.perf_counter()
        started_at = _now()
        reserved = _reservation(request)
        base: dict[str, Any] = {
            "call_id": request.call_id,
            "state": CallState.NOT_DISPATCHED.value,
            "ok": False,
            "requested_model": request.model,
            "reasoning_effort": request.reasoning_effort,
            "max_output_tokens": request.max_output_tokens,
            "reserved_usd": reserved,
            "started_at": started_at,
        }
        try:
            self.budget.reserve(request.call_id, reserved)
        except Exception as error:
            result = {**base, "error_type": type(error).__name__, "error": str(error), "finished_at": _now(), "elapsed_seconds": 0.0}
            notify(result)
            return result

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": ([{"role": "system", "content": request.system}] if request.system else []) + list(request.user_messages),
        }
        if request.model.lower().startswith(("gpt-5", "o1", "o3", "o4")):
            kwargs["max_completion_tokens"] = request.max_output_tokens
        else:
            kwargs["max_tokens"] = request.max_output_tokens
            kwargs["temperature"] = 0
        if request.reasoning_effort:
            kwargs["reasoning_effort"] = request.reasoning_effort
        if request.response_format:
            kwargs["response_format"] = request.response_format

        retries = 0
        waited = 0.0
        try:
            while True:
                notify({**base, "state": CallState.IN_FLIGHT.value, "rate_limit_retries": retries})
                try:
                    with self.slots if self.slots is not None else nullcontext():
                        response = self.client.chat.completions.create(**kwargs)
                    break
                except self.rate_limit_error:
                    not_dispatched = {
                        **base,
                        "state": CallState.NOT_DISPATCHED.value,
                        "error_type": "RateLimitError",
                        "error": "Provider rejected the request before execution",
                        "rate_limit_retries": retries,
                        "rate_limit_wait_seconds": round(waited, 6),
                    }
                    notify(not_dispatched)
                    if retries >= 6:
                        self.budget.settle(request.call_id, 0.0)
                        result = {
                            **not_dispatched,
                            "error": "Rate limit retries exhausted",
                            "rate_limit_retries": retries,
                            "rate_limit_wait_seconds": round(waited, 6),
                            "finished_at": _now(),
                            "elapsed_seconds": round(time.perf_counter() - started, 4),
                        }
                        notify(result)
                        return result
                    delay = min(60.0, 5.0 * 2**retries)
                    wait_started = time.perf_counter()
                    self.sleep(delay)
                    waited += time.perf_counter() - wait_started
                    retries += 1
        except Exception as error:
            result = {
                **base,
                "state": CallState.UNKNOWN_OUTCOME.value,
                "error_type": type(error).__name__,
                "error": str(error),
                "rate_limit_retries": retries,
                "rate_limit_wait_seconds": round(waited, 6),
                "finished_at": _now(),
                "elapsed_seconds": round(time.perf_counter() - started, 4),
                "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
            }
            notify(result)
            return result

        usage = usage_dict(getattr(response, "usage", None))
        actual = cost_usd(
            usage,
            request.price.input_per_million,
            request.price.cached_input_per_million,
            request.price.output_per_million,
        )
        if actual is not None:
            self.budget.settle(request.call_id, actual)
        choice = response.choices[0]
        content = choice.message.content or ""
        saved = {
            **base,
            "state": CallState.RESPONSE_SAVED.value,
            "response_id": getattr(response, "id", None),
            "resolved_model": getattr(response, "model", None),
            "system_fingerprint": getattr(response, "system_fingerprint", None),
            "finish_reason": choice.finish_reason,
            "content": content,
            "usage": usage,
            "cost_usd": actual,
            "rate_limit_retries": retries,
            "rate_limit_wait_seconds": round(waited, 6),
            "finished_at": _now(),
            "elapsed_seconds": round(time.perf_counter() - started, 4),
        }
        notify(saved)
        if choice.finish_reason == "length":
            result = {**saved, "state": CallState.INVALID_OUTPUT.value, "error_type": "OutputTokenLimit", "error": "Output reached its token cap"}
        elif not content:
            result = {**saved, "state": CallState.INVALID_OUTPUT.value, "error_type": "EmptyModelResponse", "error": "API returned empty content"}
        else:
            result = {**saved, "state": CallState.COMPLETE.value, "ok": True, "content": content.strip()}
        if not finalize and result["state"] == CallState.COMPLETE.value:
            return saved
        notify(result)
        return result
