# Adaption Memory

Experiment harness for write-time memory on LongMemEval, LoCoMo, and BEAM. The runner separates benchmark normalization, extraction policy, model and LoRA configuration, provider transport, judging, execution, and durable run storage. The supported systems are `full-history` and the append-only `memory` extractor; older Mem0 comparison records remain historical artifacts and are not a supported runtime path.

## Setup

Python 3.10 or newer is required.

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements.txt -r requirements-inspect.txt
```

## One experiment command

Experiments are frozen JSON files under `experiment_specs/`. A preset contains human choices; preflight resolves it to a complete immutable specification with source, prompt, model, adapter, pricing, and implementation hashes. Paid authorization is deliberately not stored in a preset.

```bash
.venv/bin/python -m adaption_memory.cli preflight \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json

.venv/bin/python -m adaption_memory.cli prepare \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001
```

For a local OpenAI-compatible extractor, set `EXTRACTOR_BASE_URL` and, if needed, `EXTRACTOR_API_KEY`. The answerer and judge use the normal OpenAI client configuration. Paid work requires command-local authorization and an explicit API budget:

```bash
.venv/bin/python -m adaption_memory.cli run \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001 \
  --allow-paid --budget-usd 10
```

For a preset whose executor is `modal`, `prepare` also freezes the remote payload. `run` launches only after a separate Modal budget is supplied. `resume --watch` collects extraction checkpoints into the version 2 artifact graph, then performs answering and judging when an API budget is authorized.

```bash
.venv/bin/python -m adaption_memory.cli run \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001 \
  --allow-paid --modal-budget-usd 4

.venv/bin/python -m adaption_memory.cli resume \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001 --watch \
  --allow-paid --budget-usd 10
```

An interrupted call that was already dispatched becomes `unknown_outcome` and is never replayed automatically. Reconciliation is read-only until provider evidence establishes the outcome:

```bash
.venv/bin/python -m adaption_memory.cli reconcile \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001
```

A terminal run is immutable. Retry it under a new identity:

```bash
.venv/bin/python -m adaption_memory.cli resume \
  --spec experiment_specs/locomo-qwen-08b-finetuned-final50.json \
  --run-id locomo-08b-ft-001 --retry-as locomo-08b-ft-002 \
  --allow-paid --budget-usd 10
```

Reports load through the same strict validator as resume:

```bash
.venv/bin/python -m adaption_memory.cli report \
  --run-id locomo-08b-ft-001 --output reports/locomo-08b-ft-001
```

## Run records

New runs use schema version 2 under `runs/<run-id>/`:

```text
artifacts/<kind>/<sha256>.json
generations/<generation>/manifest.json
generations/<generation>/results.jsonl
generations/<generation>/commit.json
current.json
```

The pointer is published only after a coherent generation is durable. Each artifact records parent hashes and the implementation revision. Readers verify the pointer, commit, manifest, results, question set, exactly-once IDs, artifact contents, and graph edges. Terminal manifests cannot be changed; retries record `retry_of`.

The memory format and prompt rationale are documented in [docs/memory-design.md](docs/memory-design.md). The architecture contract is in [docs/experiment-architecture.md](docs/experiment-architecture.md).

## Tests

```bash
.venv/bin/python -m unittest discover
```
