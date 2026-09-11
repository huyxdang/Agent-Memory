# Optimized Qwen inference

The prior Transformers run is stopped. Its results, cost ledger, runtime transition and source snapshots remain under `work/qwen_beam_baseline/`. The old executable runner and acknowledgement worker have been removed. The new run is a separate variant, not a continuation with silently changed decoding.

## What changed

- A pinned vLLM 0.21.0 server runs Qwen3.5-9B BF16 on one L40S. It accepts concurrent requests from independent histories, uses chunked prefill and prefix caching, and has no static padding batch. Prefix caching support for Qwen's hybrid state is experimental in the upstream recipe; do not assume a speedup until measured.
- One async task owns each history and processes its updates in order. At most two model requests are active by default. No question or reference answer enters extraction.
- Each history has its own checkpoint and progress file on a Modal v2 Volume. Atomic local writes followed by `sync /state` commit them before that history advances. A short commit lock protects volume-wide sync; GPU requests for other histories can continue during commits. No laptop acknowledgement is required.
- A reusable image contains dependencies and worker code, built before GPU allocation. Another persistent Volume holds model weights and compilation caches. The server listens only on localhost inside the sandbox.
- Schema-constrained decoding enforces the existing JSON schema. Previous failures included `narrature` instead of `narrative` and malformed JSON punctuation. Invalid output remains a failure, never silently repaired or accepted. Constraints do not establish factual correctness.
- No truncation. Pinned chat-template tokenization is checked against the server's usage count; prompt plus output allowance must fit. Changing engine/constraint settings creates a distinct prepared configuration.

## Commands

Run from the repository with the existing `.venv`. `.env` supplies the existing OpenAI credentials for answering; no OpenAI key goes to the GPU worker.

```sh
.venv/bin/python qwen_vllm.py prepare --smoke --directory work/qwen_vllm_smoke
.venv/bin/python qwen_vllm.py launch --directory work/qwen_vllm_smoke --budget-usd 2
.venv/bin/python qwen_vllm.py collect --directory work/qwen_vllm_smoke --watch
```

Smoke means two updates in each of two fixed histories. It never produces final benchmark answers. Launch refuses a pre-existing launch ledger, so interrupted/uncertain launch outcomes must be reconciled before creating a replacement resource.

The full run uses the exact original seven BEAM histories and ninety questions:

```sh
.venv/bin/python qwen_vllm.py prepare
.venv/bin/python qwen_vllm.py launch --budget-usd APPROVED_REMAINING_ALLOCATION
.venv/bin/python qwen_vllm.py collect --watch --evaluate
```

Collection is independent of GPU execution. It can reconnect after a laptop interruption, retrieves cloud checkpoints and dispatches answering/judging for completed histories while extraction continues. A smoke checkpoint is never treated as a complete history. Unknown outcomes stop that history rather than being replayed. Saved responses can be applied after a worker crash without regeneration. Automatic GPU relaunch is deliberately not implemented. After stopping and collecting an interrupted run, explicitly resume safe checkpoints using its exact frozen image and an additional approved allocation:

```sh
.venv/bin/python resume_qwen_vllm.py --directory work/qwen_beam_vllm --budget-usd APPROVED_REMAINING_ALLOCATION
```

Resume retains prior spending and refuses uncertain in-flight calls, invalid outputs, context overflow, or terminal worker failures. Those need separate review, not automatic replay.

To stop the exact current sandbox even while a collector holds its local lock:

```sh
.venv/bin/python qwen_vllm.py stop --directory work/qwen_vllm_smoke
```

No public inference endpoint is deployed. Sandbox lifetime is bounded by the allocated budget. Historical baseline accounting and prior vLLM launch reservations are subtracted from the existing $10 baseline allocation. CPU build/storage overhead allowance is an estimate, not a provider invoice. Both cloud volumes persist after a job; they can incur storage costs and should be reviewed after the experiments.

## What must be measured

Compare identical probes at concurrency one and two, separately from constrained-versus-unconstrained decoding. Record total cloud-job wall time, server startup, per-request queue and inference time, usage, valid updates/minute, and resource cost. Keep all failure counts. Do not equate summed request latency with concurrent wall time or call the old mixed-hardware run a controlled speed comparison.

Sources: [Modal vLLM pattern](https://modal.com/docs/examples/vllm_inference), [durable Volume commits](https://modal.com/docs/guide/sandbox-files), [Qwen engine guidance](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html), [structured outputs](https://docs.vllm.ai/en/latest/features/structured_outputs/).
