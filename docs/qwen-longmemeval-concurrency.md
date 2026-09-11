# Qwen LongMemEval concurrent extraction

Implemented for the original LongMemEval 100-question evaluation only. LoCoMo
is not added by this change. Existing BEAM selection and grading stay unchanged.

## Execution

One L40S runs one vLLM server. `--concurrency` controls the maximum concurrent
extraction requests and vLLM's `--max-num-seqs`, with values 1, 2, 4, 8 or 16.
Each history processes natural sessions sequentially using its own preceding
memory. Separate histories can submit requests simultaneously. There is no
barrier requiring every history to finish session N before any starts N+1.

This uses vLLM continuous batching, described in the
[Modal input concurrency documentation](https://modal.com/docs/guide/concurrent-inputs).
The existing Sandbox runs the async scheduler internally, so no additional
Modal Function decorator or GPU-per-history fan-out is needed.

`collect --watch --evaluate` submits a question to the independent four-worker
answer/judge pool as soon as its complete memory appears. It does not wait for
all extraction to finish. The collector must remain running for this overlap;
the cloud extractor continues even if the collector disconnects.

## Prepare without spending

From the repository root, using the existing `.env`:

```sh
.venv/bin/python qwen_vllm.py prepare --benchmark longmemeval \
  --concurrency 8 --directory work/qwen_longmemeval_c8
```

This freezes exactly `question_ids_50.json` plus `question_ids_50b.json`, with
their checked hashes. Dataset revision is
`98d7416c24c778c2fee6e6f3006e7a073259d48f`. Actual preparation verified
100 questions, 100 histories and 4,803 sessions. Complete histories are retained.
Only sanitized timestamps and role/content messages reach the extractor.
Questions and reference answers remain in the local configuration.

For an operational smoke, add `--smoke` and use a separate directory. It selects
the same first 16 histories and processes two sessions each at every concurrency
setting. This makes the 32-update workload comparable between concurrency levels.
It must not answer final questions. BEAM retains its original two-history smoke.
An early-session smoke does not measure late-stage memory pressure or guarantee
full-run throughput.

Launch remains the existing `launch --directory ... --budget-usd ...` command,
followed by `collect --directory ... --watch --evaluate`. **No launch is approved
or performed by this code change.** The existing $10 baseline allocation guard
is unchanged and mostly used. Reconcile remaining account funds and explicitly
allocate a pilot before attempting a paid launch. No automatic budget increase.

## Checkpoints and reporting

- Histories own separate state files. Completed histories are reused, not rebuilt.
- Queued requests have not been sent and can resume. Saved responses are applied
  without another inference call. Unknown in-flight outcomes require review.
- `resume_qwen_vllm.py` uses the frozen image and checkpoints. Changing concurrency
  requires a separate configuration, not mutation of an existing experiment.
- Qwen output uses remaining space in the 65,536-token serving window. Overflow
  and truncated/invalid outputs are explicit failures, never silent truncation.
- Answerer remains Luna; LongMemEval uses the existing pinned Mem0 yes/no judge
  prompt, not BEAM's nugget rubric. API usage, reasoning-token metadata, per-call
  duration and cost estimates remain recorded separately from GPU accounting.
- `finished.json` records extraction wall time, concurrency, newly completed
  updates and throughput. Previously completed updates are not counted as new work.
- `summary.json` checks missing, failed, unexpected and duplicate question IDs.
  Collection timing is monotonic; launch-to-finalization elapsed time is recorded
  separately and includes offline gaps. Overlapping durations must not be added.
- No measured GPU speedup is claimed. Test concurrency proves scheduling, not
  performance, VRAM fit at eight or sixteen concurrent long prompts, or cost.

## Verification

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

New tests cover 100 simulated histories at concurrency eight, session ordering,
completed and queued recovery, label isolation, exact Mem0 prompt routing,
invalid judges, result accounting, and answering before other extraction ends.
The real pinned dataset preparation and identical preparation replay also passed.
