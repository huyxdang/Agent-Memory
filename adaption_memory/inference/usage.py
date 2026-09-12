from __future__ import annotations

from typing import Any


def usage_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    result = {
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    prompt_details = getattr(usage, "prompt_tokens_details", None)
    completion_details = getattr(usage, "completion_tokens_details", None)
    result["cached_input_tokens"] = getattr(prompt_details, "cached_tokens", 0) or 0
    result["reasoning_output_tokens"] = getattr(completion_details, "reasoning_tokens", 0) or 0
    if result["output_tokens"] is None:
        result["non_reasoning_output_tokens"] = None
    else:
        result["non_reasoning_output_tokens"] = max(
            result["output_tokens"] - result["reasoning_output_tokens"], 0
        )
    return result
