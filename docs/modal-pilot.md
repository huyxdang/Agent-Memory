# Qwen 3.5-9B Modal pilot

This is a two-example extractor smoke test, not a full benchmark or training job.
The user authorized up to $2 for this pilot. No cloud invocation occurs during
`prepare`, imports, or unit tests.

## Modules

- `modal_pilot_core.py`: exact-token prompt selection, input/output validation,
  spending estimates and complete result accounting. No cloud or model runtime.
- `modal_pilot_worker.py`: loads pinned Qwen weights and runs text inference with
  Transformers on the GPU. It has no Modal dependency or dataset access.
- `modal_pilot.py`: CLI, local artifacts and Modal sandbox lifecycle. It sends
  only two sanitized prompt records and the worker/core files, never `.env` or
  the repository directory.

The GPU worker is deliberately a Transformers correctness/fit baseline, not an
optimized vLLM throughput result. A later engine can use the same payload and
result contract without changing dataset selection. There is no persistent
endpoint, autoscaling pool or benchmark-runner refactor in this task.

## Setup

Use the existing project environment:

```sh
uv pip install --python .venv/bin/python -r requirements-modal.txt
.venv/bin/modal token new
```

The second command opens Modal's browser login and stores credentials locally.
Do not paste token values into chat. No Modal credentials are sent to the worker.

```sh
.venv/bin/python modal_pilot.py prepare
.venv/bin/python modal_pilot.py run --budget-usd 2
```

On this Mac, if the Python HTTPS certificate store fails, use the system CA
bundle without disabling verification:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem .venv/bin/python modal_pilot.py prepare
```

Preparation resolves a Hugging Face model commit, pins the tokenizer to it,
counts every original-copy training prompt, and chooses the lower median and
maximum by complete chat-template token count, with stable ID tie-breaking.
It preserves system/user text and message boundaries, omits teacher targets
and evaluation metadata, and saves the exact two prompts. The GPU rechecks
token counts before loading weights. Input plus a 2,048-token output allowance
must fit the explicitly configured 65,536-token pilot window. Nothing truncates.
Oversized prompts stop preflight; changing that policy requires a new decision.

Prior memory in these examples was produced by the teacher. This measures
teacher-forced extractor inference, not the student's own sequential memory
rollout. Do not report its result as final benchmark accuracy.

## Spending and failure controls

One A100-80GB sandbox, at most two CPU cores and 32 GiB system RAM, lasts at most
1,200 seconds. Package installation, model download and inference share that
deadline. A 60-second idle timeout and `finally` termination limit idle usage.
There are no automatic job relaunches, and an attempted run cannot be repeated
in the same prepared directory. Reconcile its cost before authorizing another.

At prices checked 2026-09-10, the GPU/CPU/RAM envelope is about $1.18, plus a
$0.50 overhead reserve, below $2. This is a conservative planned resource
envelope, not a provider-enforced dollar cap or a verified invoice. Image
preparation, billing granularity and other charges must be reconciled in Modal;
no account-level spending policy was configured. Do not increase limits or
launch repeated new directories against the same approval.

## Results

`work/modal_qwen_pilot/` holds preflight, payload, a single run ledger, setup and
worker logs, incremental event records, per-example results and a readable
summary. The ledger records code/model provenance, sandbox ID, UTC and elapsed
timings, missing/duplicate/failed outputs and cleanup confirmation. GPU load time
is separate from inference time. Unknown invoice costs stay null.

GPU memory metrics are PyTorch allocator peaks, not total device utilization.
Generated token counts include every generated token; reasoning usage remains
null because this backend has no separate accounting field. Thinking is disabled
explicitly in Qwen's chat template. Length-limited or malformed JSON outputs fail
the pilot's output checks. Factual quality still requires source-based review.

## Checks

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest test_modal_pilot -v
```

Sources: [Modal Sandbox API](https://modal.com/docs/sdk/py/latest/Sandbox),
[Modal pricing](https://modal.com/pricing),
[Qwen model card](https://huggingface.co/Qwen/Qwen3.5-9B).
