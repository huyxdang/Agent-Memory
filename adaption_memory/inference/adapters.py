from __future__ import annotations

from adaption_memory.domain import AdapterSpec


ADAPTER_SPECS = {
    "huyxdang/adaption_agent_memory": {
        "base_model": "Qwen/Qwen3.5-0.8B",
        "name": "adaption-agent-memory",
        "rank": 32,
    }
}


def adapter_spec(repo: str, revision: str) -> AdapterSpec:
    try:
        value = ADAPTER_SPECS[repo]
    except KeyError as error:
        raise ValueError(f"Unsupported extractor adapter: {repo}") from error
    return AdapterSpec(repo=repo, revision=revision, **value)
