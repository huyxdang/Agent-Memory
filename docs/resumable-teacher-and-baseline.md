# Resumable teacher generation and Qwen baseline

Requested 2026-09-11 as two concurrent jobs. Updated scope: Qwen baseline is BEAM final only, the original ninety questions, not dev or the other final benchmarks. Both jobs have launched. See the current execution section below; the full-workload estimate is retained as the reason for narrowing scope.

## Current Qwen runner

The original Qwen runner below has been stopped and removed. Use
[vLLM inference](qwen-vllm-inference.md) for the current launch, collection,
stop and resume commands. Its [live smoke results](qwen-vllm-smoke.md) cover
four updates; the full optimized benchmark has not restarted. The original
execution notes below are historical, not runnable instructions.

## Original execution (superseded for Qwen)

- OpenAI cap: $30, explicitly approved by the user. Teacher allocation $10; baseline answering/judging allocation $20. `.env` and `.env.example` updated without displaying the key. Modal cap remains independently $30; this baseline allocation is $10.
- Teacher: `tools/teacher_traces.py --run --budget-usd 10 --workers 2`. First real responses and checkpoints confirmed. The initial nohup attempt did not survive shell exit and wrote no checkpoints; verified no process existed before launching under a persistent terminal session.
- Qwen: `qwen_beam_baseline.py --run`, using the same pinned Qwen revision and BF16/SDPA, thinking-disabled settings as the earlier pilot. One A100-80GB, 2 CPU cores, 32 GiB host memory, maximum sandbox lifetime 8,500 seconds. Reserved resource envelope plus overhead is $9.38338, within its $10 allocation.
- Seven source histories, 203 extraction updates and exactly ninety final questions. No teacher labels, benchmark questions or rubrics are sent to the GPU extractor. Local answer/judge workers start as soon as a history's memory is complete and overlap later GPU extraction. Teacher generation is a separate process.
- Each GPU checkpoint is copied to the laptop and fsynced before acknowledgement lets the worker advance. On host disconnect the worker waits at most five minutes for acknowledgement, then exits; the sandbox also has a lifetime and idle timeout. Resume adopts a known live sandbox only in its running phase, or uses saved local memories for a budget-bounded restart. Uncertain creation/startup requires reconciliation, not blind duplicate creation.
- API answers and every rubric-nugget judge call are saved separately. Completed calls are reused; unknown outcomes keep their reservations and block retries. This does not guarantee recovery of an unsaved GPU generation, but all acknowledged checkpoints are durable locally.
- No automatic restarts that alter configuration, retry unknown paid API outcomes, or exceed the allocations are authorized.
- After completion run `report_beam_baseline.py` for the historical Luna comparison. Original Luna references are `20260908T191319329343Z_memory_07ccfb9` and `20260909T064305432208Z_memory_e66fa47`. No new Luna dev run is included in this narrowed task.

## Teacher job

`tools/teacher_traces.py` consumes only `work/beam_split_v2/train.json`, verifies source hashes, and processes each history once using the existing Luna extractor prompt and memory-update semantics. Two histories may progress concurrently; updates inside a history stay sequential.

Before every API dispatch it saves the input, attempt identity and a conservative budget reservation with atomic replacement and file/directory fsync. A completed response is saved before applying the memory update. The checkpoint contains plain training inputs, exact API inputs, response text, resolved model, response ID, usage including reasoning, timings, memory state and quality warnings.

Repeat the identical command and directory to resume. Completed updates are skipped. A saved response that was not yet applied is applied without a new API call. A process lock prevents two runners from writing the same directory. Configuration and code changes reject resume rather than mixing experiments.

An in-flight request interrupted before its response was saved has an unknown outcome. It retains its cost reservation and blocks that history for explicit reconciliation. Invalid outputs are preserved and block that history too. The runner does not automatically retry either case. This avoids pretending that exactly-once provider execution can be guaranteed across a lost network response.

Offline preparation:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/teacher_traces.py
```

Paid execution requires an explicit numeric `--budget-usd` and `--run`. The user has supplied a $30 OpenAI cap; $10 is allocated to this teacher job. State is saved under `work/beam_teacher_traces/`; no raw targets are committed. Check `summary.json` and per-history statuses for partial failures; a finished invocation is not necessarily a complete dataset. Teacher traces still require quality review before training.

The reservation uses a conservative Luna rate envelope, including possible long-context and cache-write uplifts, rather than the smaller planning forecast. Actual billing remains provider-reported separately. Model pricing was checked against [OpenAI's model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## Superseded full-workload estimate

| Cohort | Histories | Questions | Extraction updates |
|---|---:|---:|---:|
| BEAM dev | 4 | 80 | 150 |
| BEAM final | 7 | 90 | 203 |
| LongMemEval final | 100 | 100 | 4,803 |
| LoCoMo final | 10 | 50 | 272 |
| Total | 121 | 320 | 5,428 |

The previous Qwen pilot measured 30.38 and 26.44 seconds per update. Extrapolating their mean to the complete baseline gives about 43 GPU-hours and $152 at the existing A100-80GB sandbox resource envelope. BEAM dev plus final alone projects to about $10. These are rough projections from two teacher-forced calls, not measured full-rollout prices. Startup, retries, answering and judging are excluded. Current [Modal pricing](https://modal.com/pricing) confirms the rates used in the existing pilot calculation.

The $30 cap covers all Modal work, not just baseline. The full baseline must not launch under this estimate. A faster inference implementation and a small timed dev rollout could change the estimate; a reduced benchmark workload requires a deliberate scope decision. Final questions must not be silently dropped.

At the initial workload audit only the two-example Modal pilot existed, and a read-only listing found no active sandboxes. The newly implemented BEAM-only runner is separate from that pilot. See [Modal Sandboxes](https://modal.com/docs/guide/sandboxes) for the lifecycle interfaces used.

For the Luna comparison, existing final scores can be reported as historical references. New dev histories have no Luna baseline yet; a matched dev comparison requires additional Luna extraction, answering and judging. Do not reuse teacher training histories as dev or claim old per-question memory builds are a controlled shared-memory comparison.

Recompute the workload without APIs using `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python baseline_workload.py`. It writes `work/qwen_baseline_workload.json` with counts, selection hashes and pilot assumptions. The original final selections and training split remain unchanged.
