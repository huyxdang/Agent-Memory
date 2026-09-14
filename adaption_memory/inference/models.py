from __future__ import annotations

from adaption_memory.domain import ModelSpec


MODEL_SPECS = {
    "Qwen/Qwen3.5-9B": ModelSpec(
        name="Qwen/Qwen3.5-9B",
        revision="c202236235762e1c871ad0ccb60c8ee5ba337b9a",
        context_window=65_536,
        default_gpu="L40S",
        gated=False,
        sampling=(("temperature", 0.7), ("top_p", 0.8), ("top_k", 20.0), ("min_p", 0.0), ("presence_penalty", 1.5), ("repetition_penalty", 1.0)),
        merge_user_messages=False,
        dtype="bfloat16",
        language_model_only=True,
        max_num_batched_tokens=8192,
        gpu_memory_utilization=0.85,
    ),
}


def model_spec(name: str) -> ModelSpec:
    try:
        return MODEL_SPECS[name]
    except KeyError as error:
        raise ValueError(f"Unsupported extractor model: {name}") from error
