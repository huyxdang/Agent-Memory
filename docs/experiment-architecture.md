# Experiment architecture

This document defines the target structure for new experiment runs. The refactor removes the old orchestration APIs after their callers move. It does not translate historical artifacts.

## Caller usage

A local or Modal command resolves a short preset into a complete `ExperimentSpec`. The resolved specification records every model revision, prompt hash, source hash, price, token limit, and runtime choice that can affect a result.

```python
spec = presets.resolve("locomo-qwen-08b-finetuned-final50")
run = coordinator.prepare(spec)
coordinator.run(run.run_id, paid=authorization)
coordinator.resume(run.run_id, paid=authorization)
coordinator.report(run.run_id)
```

`resume` continues only a non-terminal run whose saved hashes match the current inputs. Retrying a terminal run creates a new run and records the old run ID in `retry_of`.

## Data flow

Each stage writes a content-addressed artifact. An artifact records the hashes of its parents and the implementation revision that produced it.

```text
resolved experiment specification
  -> dataset snapshot
  -> history and memory build
  -> answer call
  -> judge call
  -> derived report
```

The run manifest points to the artifacts. Reports do not become a second source of truth.

## Core types

`ExperimentSpec` is the immutable, fully resolved input to a run. `BenchmarkItem` is the normalized question and history shape. `MemoryArtifact` is the extractor output for one history. `CallRecord` tracks one external call and its outcome. `RunManifest` names the run, the specification hash, the selected questions, and the artifact references. The coordinator receives its backend explicitly for each execution.

The call state transitions are:

```text
not_dispatched -> in_flight -> response_saved -> complete
                         |                 -> invalid_output
                         -> unknown_outcome
```

Only `not_dispatched` and `invalid_output` are safe automatic retry sources. A timeout after dispatch is `unknown_outcome` because the provider may have processed and billed the request.

## Module map

```text
adaption_memory/
  benchmarks/
    base.py
    longmemeval.py
    locomo.py
    beam.py
  inference/
    openai.py
    vllm.py
    models.py
    adapters.py
  evaluation/
    extractors.py
    answering.py
    judges.py
    pipeline.py
  execution/
    local.py
    modal.py
    mem0.py
  run_store/
    records.py
    checkpoints.py
    accounting.py
    reporting.py
  domain.py
  config.py
  cli.py

experiment_specs/
runs/
tools/
```

`runs/` contains data only. `run_store/` owns persistence and validation.

## Ownership rules

- A benchmark module owns its source data, normalization, split selection, weights, and default judge kind.
- Benchmark modules may import `benchmarks.base`. They may not import sibling benchmarks, a runner, or a model profile.
- An extractor owns memory instructions, parsing, and application policy.
- A transport owns provider calls and call-state recording.
- A model specification owns the pinned model revision, sampling settings, context limit, and engine settings.
- An adapter specification owns a pinned LoRA revision and its required base model.
- The evaluation pipeline coordinates typed collaborators. It does not receive a module object.
- An executor owns local or Modal process lifecycle. It does not choose a benchmark or judge.
- Memories built outside the pipeline (Modal vLLM, Mem0) arrive through one importer as per-history checkpoints plus one executor cost record; the pipeline answers and judges them without a second path.
- The run store owns atomic writes, validation, retry lineage, artifact hashes, and accounting summaries.
- The CLI resolves configuration and performs boundary validation. It does not contain benchmark or provider logic.

## Persistence contract

Each checkpoint writes a new generation under the run directory. The generation contains a manifest, results, and a commit record with both hashes. The store updates `current.json` only after the generation is durable. Readers validate the pointer, commit record, manifest hash, result hash, selected question hash, exactly-once IDs, and artifact graph before returning data.

Terminal manifests are immutable. The run index is append-only and rejects a second row for the same run ID.

A run is gated on its configuration hash, not its code hash. `Coordinator.open` refuses a run prepared for a different experiment configuration and continues one whose implementation changed, writing an `implementation_change` artifact (previous and new spec hashes, implementation revisions, the current source hashes, and the generation it was recorded at) and moving the manifest to the new spec hash. Every artifact still carries the implementation revision that produced it. Executor payload fingerprints exclude the recorded source hashes for the same reason, so checkpoints on a Modal volume or in a Mem0 store stay valid after a source edit; `prepare` on an existing directory rewrites the recorded code hashes rather than refusing.

Answering and judging run in a worker pool sized by the specification's `concurrency`, with one lock around artifact writes, row updates, and checkpoints. The budget cap doubles as a throttle: a worker whose upper-bound reservation does not fit waits for in-flight calls to settle. New specifications should size `judge_max_tokens` to the judge's real output (a few thousand tokens), because the reservation multiplies that allowance by the judge's output price per concurrent call.

## Configuration and authorization

Human presets contain short selectors. `presets.resolve` expands a preset and writes the complete specification into the run. Paid authorization is a separate command input. A preset cannot grant permission to spend money.

## Rejected shapes

The design does not use one generic result dictionary for every stage. Question records and shared history artifacts have different identity and retry rules.

The design does not make LoRA an extractor backend. LoRA changes the model served by a transport.

The design does not create a Python package named `runs` because that path already stores experiment data.

The design does not keep import wrappers for deleted modules. Callers move in one verified unit, then the old API is deleted.

## Established pattern

Inspect AI separates tasks, solvers, scorers, model roles, and durable evaluation logs. This repo follows that separation while retaining its shared-history memory build and stricter artifact provenance. See the official Inspect AI documentation for [tasks](https://inspect.aisi.org.uk/tasks.html), [scorers](https://inspect.aisi.org.uk/scorers.html), and [evaluation logs and retries](https://inspect.aisi.org.uk/eval-logs.html).

## Design decision

Use a typed coordinator over a content-addressed artifact graph. This keeps the public command small while preserving the different identities of datasets, histories, questions, calls, and reports. Start with the run store and one offline end-to-end benchmark. Move the other paths only after that slice passes.
