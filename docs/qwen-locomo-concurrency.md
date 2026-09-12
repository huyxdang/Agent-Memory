# Qwen LoCoMo concurrent extraction

> Historical execution record. The commands below describe the retired runner; use the canonical commands in the repository `README.md` for new runs.

LoCoMo now uses the same Qwen worker and collector as LongMemEval. Its original
50 selected questions share ten histories and 272 natural-session updates.
Build each history once. Its selected questions all use that completed memory.
The selected question counts per history are 7, 6, 5, 5, 5, 5, 5, 4, 4 and 4.

Histories run concurrently, but sessions within a history stay ordered. The
collector's four answer/judge workers start when each complete memory arrives,
while extraction continues on the other histories. Run the collector with
`--watch --evaluate` to keep that overlap active. Cloud extraction survives
collector disconnection; collection and answering can resume later.

## Offline preparation

From the repository root:

```sh
.venv/bin/python qwen_vllm.py prepare --benchmark locomo \
  --concurrency 8 --directory work/qwen_locomo_c8
```

This makes no API calls. Concurrency may be 1, 2, 4, 8 or 16; with ten histories,
at most ten extraction requests can be active. Actual GPU capacity and throughput
at these settings require measurement. One L40S and the existing model settings
remain unchanged, not a GPU per history.

For a separate operational smoke, add `--smoke`. Every concurrency level uses
the same ten histories, first two sessions each, for a 20-update workload.
Smoke memories cannot answer final questions. This early-session smoke alone
does not establish full-history throughput or late-stage context fit.

No paid launch or budget increase was made. The existing baseline allocation
guard remains in place and is mostly used. Reconcile remaining funds and agree
on a pilot allocation before using `launch --budget-usd ...`. Then use
`collect --directory ... --watch --evaluate` for concurrent answer/judge work.

## Data and grading integrity

- `locomo_qwen_inputs.py` pins the SHA-256 of `question_ids_locomo_50.json` and
  `work/locomo10.json`. The upstream dataset commit is not recorded in this
  snapshot; `dataset_revision` is explicitly null, not an invented revision.
- Reuses the existing LoCoMo adapter, including chronological natural sessions,
  speaker names, two-person extractor subject, captions and reference processing.
  No question-dependent retrieval. No reference answers or evidence labels in
  the extractor payload or answer prompt.
- Uses the vendored Mem0 LoCoMo system and judge prompts with CORRECT/WRONG
  parsing. Stores the raw judge explanation, maps labels to yes/no, and reports
  invalid or truncated responses as failures. Luna answerer and GPT-5 judge
  settings come from the existing configuration.
- Per-question results record the shared history and memory hashes. Checkpoints,
  queued-versus-in-flight handling, token usage, cost accounting and timing use
  the shared runner. Completed work is not regenerated on a normal resume.
- Source, adapter and judge code hashes are frozen in the prepared configuration.
  Existing results and all earlier prepared configurations remain untouched.

## Verification

The pinned real-data preparation verified 50 questions, ten histories and 272
updates, speaker attribution, label isolation and exact preparation replay.
Tests cover CORRECT/WRONG/invalid grades, exact judge prompts, resume without
duplicate API calls, fixed smoke workloads, and multiple questions concurrently
sharing one immutable memory before the other history finishes.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

No real Qwen inference or speedup measurement was performed for this change.
