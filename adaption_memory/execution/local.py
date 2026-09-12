from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from adaption_memory.domain import CallState
from adaption_memory.inference.openai import ChatRequest, OpenAITransport, Price


class CompletionBackend(Protocol):
    def complete(
        self,
        *,
        call_id: str,
        stage: str,
        model: str,
        system: str,
        user_messages: tuple[dict[str, Any], ...],
        max_output_tokens: int,
        reasoning_effort: str | None,
        response_format: dict[str, Any] | None,
        observe: Callable[[dict[str, Any]], None],
        item: dict[str, Any],
    ) -> dict[str, Any]: ...


@dataclass
class OpenAIBackend:
    transport: OpenAITransport
    extractor_price: Price
    answer_price: Price
    judge_price: Price

    def complete(self, *, call_id: str, stage: str, model: str, system: str,
                 user_messages: tuple[dict[str, Any], ...], max_output_tokens: int,
                 reasoning_effort: str | None,
                 response_format: dict[str, Any] | None, observe: Callable[[dict[str, Any]], None],
                 item: dict[str, Any]) -> dict[str, Any]:
        price = {"extract": self.extractor_price, "answer": self.answer_price, "judge": self.judge_price}[stage]
        request = ChatRequest(
            call_id=call_id,
            model=model,
            system=system,
            user_messages=user_messages,
            max_output_tokens=max_output_tokens,
            price=price,
            reasoning_effort=reasoning_effort,
            response_format=response_format,
        )
        return self.transport.chat(request, observe=observe, finalize=False)


class FixtureBackend:
    """Deterministic no-network backend used only for end-to-end verification."""

    def complete(self, *, call_id: str, stage: str, model: str, system: str,
                 user_messages: tuple[dict[str, Any], ...], max_output_tokens: int,
                 reasoning_effort: str | None,
                 response_format: dict[str, Any] | None, observe: Callable[[dict[str, Any]], None],
                 item: dict[str, Any]) -> dict[str, Any]:
        base = {
            "call_id": call_id,
            "requested_model": model,
            "resolved_model": "offline-fixture-v1",
            "reserved_usd": 0.0,
            "cost_usd": 0.0,
            "usage": {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "ok": False,
        }
        observe({**base, "state": CallState.IN_FLIGHT.value})
        if stage == "extract":
            content = '{"narrative":[],"atomic":[]}'
        elif stage == "answer":
            content = str(item["answer"])
        elif item.get("judge") == "locomo":
            content = '{"reasoning":"fixture","label":"CORRECT"}'
        elif item.get("judge") == "beam":
            content = '{"score":1.0,"reason":"fixture"}'
        else:
            content = "<judge_thinking>fixture</judge_thinking>\nyes"
        saved = {**base, "state": CallState.RESPONSE_SAVED.value, "content": content, "response_id": call_id}
        observe(saved)
        return saved


@dataclass
class RoutedBackend:
    extractor: CompletionBackend
    evaluator: CompletionBackend

    def complete(self, **kwargs: Any) -> dict[str, Any]:
        backend = self.extractor if kwargs["stage"] == "extract" else self.evaluator
        return backend.complete(**kwargs)
