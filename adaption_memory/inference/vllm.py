from __future__ import annotations

import hashlib
import json

GPU_RATES = {"L4": 0.000222, "L40S": 0.000542}


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def prompt_ids(tokenizer, messages: list[dict]) -> list[int]:
    ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
        return_dict=False,
    )
    if not isinstance(ids, list) or not ids or any(type(token) is not int for token in ids):
        raise ValueError("Expected a nonempty flat list of token IDs")
    return ids


def output_valid(text: str) -> bool:
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return False
    return (
        isinstance(data, dict)
        and set(data) == {"narrative", "atomic"}
        and isinstance(data["narrative"], list)
        and all(isinstance(value, str) for value in data["narrative"])
        and isinstance(data["atomic"], list)
        and all(
            isinstance(value, dict)
            and set(value) == {"key", "value"}
            and all(isinstance(part, str) and bool(part.strip()) for part in value.values())
            for value in data["atomic"]
        )
    )


def resource_rate(gpu: str) -> float:
    if gpu not in GPU_RATES:
        raise ValueError(f"Unsupported GPU: {gpu}")
    return GPU_RATES[gpu] + 4 * 0.00003942 + 32 * 0.00000667


def request_model(payload: dict) -> str:
    return (payload.get("adapter") or {}).get("name", payload["model"])


def normalize_messages(payload: dict, messages: list[dict]) -> list[dict]:
    if not payload["merge_user_messages"]:
        return messages
    if not messages or messages[0]["role"] != "system" or any(message["role"] != "user" for message in messages[1:]):
        raise ValueError("Expected one system message followed by extractor user blocks")
    return [messages[0], {"role": "user", "content": "\n\n".join(message["content"] for message in messages[1:])}]


def server_command(payload: dict, adapter_path: str | None = None) -> list[str]:
    engine = payload["engine"]
    command = [
        "vllm",
        "serve",
        payload["model"],
        "--revision",
        payload["revision"],
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--dtype",
        engine["dtype"],
        "--max-model-len",
        str(payload["context_window"]),
        "--max-num-seqs",
        str(payload["concurrency"]),
        "--max-num-batched-tokens",
        str(engine["max_num_batched_tokens"]),
        "--gpu-memory-utilization",
        str(engine["gpu_memory_utilization"]),
        "--enable-chunked-prefill",
        "--enable-prefix-caching",
        "--generation-config",
        "vllm",
        "--seed",
        "0",
    ]
    if engine["language_model_only"]:
        command.append("--language-model-only")
    adapter = payload.get("adapter")
    if adapter:
        if adapter_path is None:
            raise ValueError("Adapter path is required")
        command.extend(
            [
                "--enable-lora",
                "--max-lora-rank",
                str(adapter["rank"]),
                "--lora-modules",
                f"{adapter['name']}={adapter_path}",
            ]
        )
    return command
