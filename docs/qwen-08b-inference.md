# Qwen 3.5 0.8B inference

The shared runner supports Qwen/Qwen3.5-0.8B with L4 by default and an explicit
model revision. Existing 9B preparation defaults to L40S. Use a new directory;
model changes must never reuse another model's memories or prepared payload.

New 0.8B preparations freeze Qwen's documented non-thinking text settings:
temperature 1.0, top_p 1.0, top_k 20, min_p 0, presence_penalty 2.0 and
repetition_penalty 1.0. The earlier greedy smoke omitted these settings and
looped; its partial outputs are diagnostics, not training or evaluation data.

Prepare the frozen base-model final configuration through the canonical CLI:

```sh
.venv/bin/python -m adaption_memory.cli prepare \
  --spec experiment_specs/locomo-qwen-08b-base-final50.json \
  --run-id locomo-qwen-08b-base-001
```

Preparation is offline. Omit `--smoke` and choose a separate directory for the
original 50-question final evaluation. Partial smoke memories are not suitable
for answering final questions. Keep the total 0.8B experiment allocation at $5,
including smoke and retries; this document does not authorize a cloud launch.

One GPU serves ten independent history streams through vLLM continuous batching.
Updates within a history remain sequential. BF16, disabled thinking, prefix
caching and chunked prefill remain enabled. The context is deliberately the same
65,536-token serving window as the 9B comparison, with remaining context available
for output and no silent input truncation. The 8,192-token prefill scheduling
budget is not a context or answer-length cap. Host allocation remains four CPU
cores and 32 GiB to avoid starving tokenization and vLLM startup.

GPU selection is frozen into the payload and used for both launch and accounting.
L4 GPU rate is $0.000222/second, plus Sandbox CPU and host RAM charges. Rates:
https://modal.com/pricing . No spending limit is increased by selecting a model.

Run collection with `--watch --evaluate` to overlap answer/judge jobs with
unfinished extraction. Checkpoints remain per history. New configurations contain
the GPU field; historical configurations are not rewritten or migrated.

Before claiming a speedup, measure live throughput, GPU memory pressure, startup,
checkpoint overhead and whole-run elapsed time. Ten concurrency slots do not
guarantee ten resident sequences under all context lengths. An early-session smoke
does not prove late-stage memory fit or full-run speed. The first live greedy
smoke failed through repeated output. A fresh sampling smoke must pass before
any 0.8B final evaluation is authorized.

## Fine-tuned LoRA adapter

`huyxdang/adaption_agent_memory` is a LoRA adapter, not a merged model. Pin the
official base and adapter revisions separately. The runner serves the base,
loads the adapter under a distinct request name and sets vLLM's maximum LoRA
rank to the adapter's rank of 32.

```sh
.venv/bin/python -m adaption_memory.cli prepare \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-qwen-08b-finetuned-001
```

Use a fresh directory for the full fine-tuned run. Never import base-model
memories into an adapter run. Keep the extraction prompt, sampling, questions,
answerer and judge unchanged so the extractor weights are the only experimental
difference.
