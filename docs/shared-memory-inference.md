# Shared-memory inference

> Historical implementation note. The command below describes the retired evaluator; use the canonical commands in the repository `README.md` for new runs.

`--system memory` now builds once per unique sanitized history, subject and
extractor configuration. Updates within a history remain sequential. All its
questions consume the same completed memory, with no question-based retrieval.
Extraction and answering prompts, benchmark chunk boundaries and Mem0 ingestion
are unchanged.

Separate thread pools handle blocking API calls for building, answering and
judging. This is concurrent I/O within one Python process, not separate OS
processes. The default `overlap` schedule starts answers as soon as their history
is complete, while other histories continue building. `barrier` waits for every
build before starting answers. Both share a global in-flight API limit.

## Run

Use the existing `.env` models, prices and spending cap. Review the selected
question IDs before removing `--preflight`. These examples do not authorize spend.

```sh
.venv/bin/python longmemeval_eval.py --system memory --benchmark locomo \
  --memory-schedule overlap --build-workers 2 --answer-workers 4 \
  --judge-workers 4 --concurrency 5 --preflight
```

Keep the existing `--questions` selection and benchmark arguments for your cohort.
Use `--memory-schedule barrier` for condition B; overlap is condition C from
`rules.md`. Start without `--memory-from` to measure the full build-to-grade run.

To separate invocations, first run with `--memory-stage build`. It ends with
`memory_ready`, not a completed benchmark. Then use the same benchmark and
question selection with `--memory-stage answer --memory-from BUILD_RUN_ID`.
This second run makes no extraction calls and records its source run ID.
Its elapsed time alone is **answer-only reuse**, not full-pipeline time.

An interrupted shared-pipeline run can use the existing `--resume RUN_ID`, with
the same configuration. Failed stages require `--retry-failed`. Completed run
records remain immutable. Do not run two coordinators against one run ID.
Pre-existing per-question memories that disagree for the same history are
rejected, rather than silently selecting one version.

## IDs and artifacts

Each new invocation has a parent `run_id`. Within it:

- `memory_build_id` identifies a unique history build and lists its question IDs.
- Each question references that build ID and the immutable artifact hash.
- Answer, judge and build attempts have stage IDs, unique attempt IDs, UTC
  start/finish timestamps, status and monotonic elapsed seconds.
- `runs/RUN_ID/memories/HASH.json` contains the completed memory and extraction
  calls. It is written atomically and its hash is verified before reuse.
- `manifest.json` contains configuration, code hashes, aggregate accounting and
  build/stage metadata. `results.jsonl` contains question-level details.
- `summary.md` contains readable results and timing. `execution_timing.json`
  records invocation time through the terminal checkpoint and index write.

Raw artifacts stay local and are gitignored. No existing result is rewritten.

## How to combine measurements

Within one run, sum API tokens and costs, counting each memory build once.
Only one question owns its writing calls for accounting; the other questions
refer to that build. Answer and judge calls, including saved failed attempts,
are counted separately. Reasoning tokens are already included in output tokens.
Judge costs remain internal, excluded from reported system costs.

Unknown usage/cost is flagged by `unknown_usage_calls` and `unknown_cost_calls`.
Reported numeric totals contain known amounts only. The spending guard keeps
reservations for calls whose billing is unknown and checkpoints before dispatch.
API call duration includes semaphore waiting and rate-limit retries; rate-limit
wait time and retry counts are also recorded explicitly.

**Do not add stage durations to get elapsed time.** They overlap. Use the parent
run's recorded interval. The manifest's `recorded_run_elapsed_seconds` matches
the historical start-to-before-terminal-checkpoint boundary. The separate
`invocation_elapsed_seconds` includes preflight and finalization; on resume it
covers only that invocation. Neither timer includes its own final file write.
First/all graded timestamps describe benchmark questions, not judge controls.

For separate build and answer runs, sum their costs once using the source-run
link. Earliest start to latest finish gives an elapsed span that includes any
gap between invocations. Do not label that span as an uninterrupted full run.

For observed historical speedup, divide the original elapsed seconds by the new
full-run elapsed seconds with the same timing boundary. Follow `rules.md` for
completion checks and differences in settings. Shared memories can change
accuracy, so old accuracy is not proof of the new pipeline's accuracy.

## Offline verification

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -v
```

Tests replace the provider and use temporary run directories. They cover shared
builds, immutable reuse, overlapping/barrier scheduling, failures, retries,
corrupted artifacts, cost accounting, and a build-only to answer-only runner
round trip. They do not measure real API speedup or benchmark accuracy.
