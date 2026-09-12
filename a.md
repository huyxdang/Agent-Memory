# Experiment architecture refactor

**Status:** complete
**Started:** 2026-09-12 02:55 +07:00
**Baseline:** commit `5d1012d`, with an existing dirty worktree that this task must preserve

This file is the durable task record for the refactor. Update it after every verified unit so the work can resume after context compaction without relying on chat history.

## Definition of done

The refactor is complete when all of these statements are true:

- One canonical command prepares, runs, resumes, reconciles, and reports every supported experiment.
- LongMemEval, LoCoMo, and BEAM implement one benchmark contract and do not import one another.
- Extractor policy, inference transport, model specification, optional LoRA adapter, answerer, judge, executor, and run storage are separate choices.
- Runtime modules depend on typed records and explicit context. No module receives `longmemeval_eval` or another module as a service object.
- New run records use one versioned schema and an immutable artifact graph.
- A terminal run never reopens. A retry creates a new run with `retry_of`.
- Every external call records a state that distinguishes a safe retry from an unknown outcome.
- Resume validates configuration, code, source, prompt, and parent artifact hashes before paid work starts.
- Reports and inspection tools load artifacts through the same strict validator.
- Accounting separates known spend from unknown or reserved exposure.
- The package has no direct imports of the obsolete orchestration API.
- Obsolete prepare, completion, resume, reconcile, and report scripts are deleted after their callers move to the canonical command.
- Contract tests enforce the dependency boundaries.
- The full offline test suite passes.

## Constraints

- Preserve prompts, frozen splits, hashes, and benchmark behavior unless a test proves that an integrity fix requires a change.
- Do not rewrite historical run artifacts. New runs use the new schema.
- Do not add compatibility wrappers, fallback code, or migration logic.
- Keep `runs/` as experiment data. Put Python run-storage code in `run_store/`.
- Reuse project dependencies. Add no package unless the standard library and current dependencies cannot meet a requirement.
- Do not start paid or hosted experiments during this refactor.

## Work plan

### 0. Ground and record the baseline

- [x] Read the architecture, progress-log, writing, and verification instructions.
- [x] Capture the current Git state without changing or hiding user edits.
- [x] Run the baseline offline suite. Result: 112 tests passed in 3.776 seconds.
- [x] Save the chosen module map, public types, and caller examples in `docs/experiment-architecture.md`.
- [x] Add an append-only decision trail in `decisions.tsv`.

### 1. Lock current behavior with tests

- [x] Add characterization tests for exact extraction, answer, and judge prompts.
- [x] Add characterization tests for split hashes, question-set hashes, and experiment fingerprints.
- [x] Add parser tests for valid, invalid, partial, and fenced model output.
- [x] Add state-transition tests for external calls and retries.
- [x] Add accounting tests for known cost, missing usage, unknown outcome, and reserved exposure.
- [x] Add tests that prove terminal runs cannot reopen.
- [x] Add tests that reject mixed or tampered artifact generations.

### 2. Fix experiment-integrity failures

- [x] Replace terminal-run reopening with a new run whose manifest records `retry_of`.
- [x] Define one external-call state machine: `not_dispatched`, `in_flight`, `unknown_outcome`, `response_saved`, `invalid_output`, and `complete`.
- [x] Make OpenAI and vLLM calls use the same retry rules. Never auto-retry `unknown_outcome`.
- [x] Validate payloads, source hashes, code hashes, prompt hashes, model revisions, and parent artifact hashes on resume.
- [x] Record artifact hashes in the version 2 manifest and publish a commit marker only after a coherent checkpoint is durable.
- [x] Make all new-run readers use the strict run validator. Historical aggregate documents remain read-only records.
- [x] Add version 2 accounting that reports known spend and unknown or reserved exposure as different totals.

### 3. Establish the package and domain records

- [x] Create the `adaption_memory/` package without moving behavior yet.
- [x] Define `ExperimentSpec`, `BenchmarkItem`, `MemoryArtifact`, `CallRecord`, `RunManifest`, and `ExecutionContext` as small standard-library types.
- [x] Split human preset selection from the fully resolved immutable experiment specification.
- [x] Keep paid-work authorization outside experiment presets.
- [x] Give model revision, sampling, engine settings, and optional adapter one source of truth.
- [x] Package source from one manifest instead of maintaining `qwen_vllm.CODE` and a separate upload list.

### 4. Separate benchmark ownership

- [x] Add one benchmark registry and one adapter contract.
- [x] Move LongMemEval loading and normalization to its adapter; keep generic selection in the benchmark contract and record its judge ID on normalized items.
- [x] Move LoCoMo loading, normalization, split selection, weights, and judge defaults to `adaption_memory/benchmarks/locomo.py`.
- [x] Move BEAM loading, normalization, split selection, and judge defaults to `adaption_memory/benchmarks/beam.py`.
- [x] Remove imports between benchmark modules.
- [x] Remove benchmark-specific model revision and answer-setting imports.
- [x] Add dependency tests that reject sibling benchmark and orchestration imports.

### 5. Separate inference and evaluation

- [x] Put OpenAI transport in `adaption_memory/inference/openai.py`.
- [x] Put the vLLM-compatible transport in `adaption_memory/inference/vllm.py`.
- [x] Put model specifications in `adaption_memory/inference/models.py`.
- [x] Put LoRA adapter specifications in `adaption_memory/inference/adapters.py`. Do not model LoRA as an extractor backend.
- [x] Put memory extraction policy and parsing behind one extractor interface.
- [x] Put answer generation in `adaption_memory/evaluation/answering.py`.
- [x] Put judge implementations and parsers in `adaption_memory/evaluation/judges.py`.
- [x] Replace `shared_pipeline.execute(module, ...)` with explicit typed collaborators.

### 6. Unify execution and storage

- [x] Put local and Modal execution behind explicit executors.
- [x] Replace the standard, Qwen, and pilot layouts with one new versioned artifact graph for future runs.
- [x] Model the graph as dataset snapshot, memory build, answer call, judge call, and derived report artifacts.
- [x] Store parent hashes and implementation revisions on artifacts, and outcomes, usage, reservation, and cost on external-call artifacts.
- [x] Isolate concurrent writers by artifact path. Use a lock only for the final manifest pointer or index.
- [x] Give every persisted envelope an explicit schema version.

### 7. Provide one experiment command

- [x] Add `prepare`, `run`, `resume`, `reconcile`, and `report` subcommands to one CLI.
- [x] Make every benchmark and model combination a resolved experiment specification, not a new script.
- [x] Preserve dry-run and budget preflight behavior.
- [x] Preserve resumability without mutating a terminal run.
- [x] Migrate LongMemEval end to end first, then verify all three benchmark contracts and frozen selections.
- [x] Migrate all remaining runtime callers.

### 8. Delete obsolete paths

- [x] Delete the old god-module APIs after every caller uses the new owners.
- [x] Delete benchmark-specific prepare, completion, resume, reconcile, and report scripts after their behavior exists in the CLI.
- [x] Keep true inspection and audit utilities under `tools/` only when they have a distinct ongoing job.
- [x] Remove duplicated weights, prices, revisions, sampling settings, hashes, and source-file lists.
- [x] Remove stale tests that only test deleted compatibility behavior.

### 9. Verify the finished system

- [x] Run import-boundary checks.
- [x] Run schema and tamper-detection tests.
- [x] Run crash, saved-response resume, unknown-outcome, retry, and concurrent-checkpoint tests.
- [x] Run a no-network end-to-end experiment through the canonical CLI.
- [x] Run the full offline suite. Result: 96 tests passed.
- [x] Run `git diff --check`. Clean.
- [x] Inspect the final diff for accidental changes to prompts, frozen data, or user-owned work.
- [x] Record the final result and any open item in this file.

## Checkpoints

### 2026-09-12 02:55 +07:00. Baseline captured

**Status:** in progress

The repository has 64 top-level Python files. Thirty-two Python files import `longmemeval_eval` directly. The baseline suite passes 112 tests. Existing changes in Qwen files, tests, docs, `extractors/`, and `PROGRESS.md` predate this task and must remain intact.

The next step is to write the contract sketch, add the decision trail, and add failing integrity tests before changing runtime code.

### 2026-09-12 03:08 +07:00. Version 2 run-store core passes

**Status:** in progress

Added the architecture contract, the call-state model, version 2 run manifests, content-addressed artifact references, coherent checkpoint generations, strict hash checks, immutable terminal runs, retry lineage, and separate known-spend and exposure totals.

**Evidence**

- `docs/experiment-architecture.md`
- `adaption_memory/domain.py`
- `adaption_memory/run_store/`
- `.venv/bin/python -m unittest test_run_store -v` passes 7 tests.

**Next**

Add the remaining core types and benchmark contract. Migrate benchmark loaders without changing their normalized output.

### 2026-09-12 03:21 +07:00. Benchmark and model ownership moved

**Status:** in progress

The top-level `benchmarks.py` and `extractors/` APIs are gone. LongMemEval, LoCoMo, and BEAM now implement one typed benchmark contract. Model, engine, sampling, GPU, and LoRA settings now live under `adaption_memory/inference/`. LoCoMo and BEAM normalization match frozen hashes. The three Qwen input modules no longer import settings or revisions from one another.

**Evidence**

- `test_benchmark_contracts.py`
- `.venv/bin/python -m unittest discover` passes 124 tests in 10.054 seconds.
- `git diff --check` passes.
- Direct `longmemeval_eval` importers fell from 32 to 29.

**Next**

Move prompts, judges, OpenAI transport, accounting, and run persistence out of `longmemeval_eval.py`. Then replace module injection in `shared_pipeline.py`.

### 2026-09-12 03:34 +07:00. Shared ownership paths removed

**Status:** in progress

The memory policy now lives at `adaption_memory/memory.py`, durable execution files live at `adaption_memory/execution/files.py`, and utility scripts use focused integrity, history, and provenance modules instead of the evaluator. The top-level `memory.py` and `checkpoint_io.py` paths are gone. The pipeline now receives `ExecutionContext` and `PipelineServices` explicitly; the former module-injection API is gone.

**Evidence**

- The targeted Qwen, LongMemEval, LoCoMo, continuation, and pipeline tests pass.
- Direct `longmemeval_eval` imports fell from 32 to 3; the remaining imports are tests/reporting that exercise the old coordinator and will move with the canonical CLI.

**Next**

Extract the OpenAI transport, extraction policy, and remaining run/report functions. Add exact prompt/parser characterization before deleting the coordinator.

### 2026-09-12 05:10 +07:00. Canonical runner replaces legacy orchestration

**Status:** complete

The old evaluator, shared module-injection pipeline, Qwen controller/worker wrappers, benchmark-specific input builders, completion/resume/reconcile scripts, and legacy report/inspection mutators are removed. New runs use the typed coordinator, frozen presets, local or Modal executors, and the version 2 content-addressed run store. Ongoing dataset/training audits live under `tools/`.

The resume path now consumes a durably saved response without replaying it, converts an interrupted in-flight call to an unknown outcome, blocks unknown outcomes, and assigns distinct identities to every extraction session and BEAM rubric-nugget judge call. Reports strictly validate the artifact graph and separate known spend from unknown or reserved exposure.

**Evidence**

- Targeted run-store, transport, coordinator, CLI, vLLM concurrency, prompt, and tool tests pass.
- The append-only and full-history fixture paths both complete through the canonical coordinator.
- Frozen configurations select 90 BEAM, 50 LoCoMo base, 50 LoCoMo fine-tuned, and 100 LongMemEval questions.
- No paid API or Modal execution was started.

**Next**

Run the full offline suite, whitespace/import scans, a clean-process preset preflight, and the independent final review. Then record the final counts and close this checklist.

### 2026-09-12. Refactor complete and verified

**Status:** done

The full offline suite passes with 96 tests. `git diff --check` is clean.

**Final verification**

- Frozen inputs are untouched: `question_ids*.json`, `third_party/`, `fixtures/`,
  `runs/`, `work/`, and `logs/` have no modifications.
- Prompt and normalization characterization tests pass, so extraction, answer,
  and judge prompt text and all three benchmark normalizations are unchanged.
- Historical documents gained only a provenance banner or a `tools/` path
  correction. No historical result was rewritten.
- `PROGRESS.md` changed by addition only.
- Removed 51 orphaned bytecode files for deleted modules, plus the now-empty
  `extractors/` directory. Stale bytecode can mask a broken import.

**Fixed during verification: the frozen fingerprint contract**

`ExperimentSpec.sha256()` mixes `implementation_revision`, a digest of all 40
package files, into the experiment identity. That is correct for resume safety,
because a paid run must not resume after its code changed. It is wrong for a
characterization test, which then asserts only that nobody edited a file and
fails on every commit.

`ExperimentSpec` now exposes two identities:

- `sha256()` is full run identity, including the implementation. Resume,
  prepare, and Modal import still validate against it. Behavior is unchanged.
- `configuration_sha256()` is the frozen experiment identity: benchmark, split,
  extractor, answerer, judge, executor, model and adapter revisions, source
  digests, prompt digests, sampling, limits, and concurrency. It excludes the
  implementation revision.

The characterization test freezes `configuration_sha256()`. Two new tests prove
the split is real: the configuration hash ignores a changed implementation
revision but still changes when a prompt digest, a model revision, or a source
digest changes, and the full run identity still binds the implementation.
`preflight` prints both hashes.

**Open items, none blocking**

- Around ten documents under `docs/` still show commands for deleted scripts.
  They now carry a historical-record banner, so they are labelled but not
  rewritten.
- No Gemma experiment specification exists. All four frozen specs are Qwen, so
  Gemma cannot be launched through the canonical command yet.
- The partial Gemma BEAM and LoCoMo work in `work/` predates this schema. Its
  `configuration.json` has no `spec_sha256`, so `import_modal_memories` will
  reject it by design. Those runs cannot be resumed, only restarted.
