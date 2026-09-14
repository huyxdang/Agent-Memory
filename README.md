# Adaption Memory

Write-time memory for long conversations, evaluated on LongMemEval, LoCoMo,
and BEAM. An extractor reads each conversation session once and appends
dated facts to a memory; an answerer later reads the whole memory, with no
retrieval step, and answers the question. This repository holds the runner,
the four systems compared, and the sixteen frozen experiments behind
[docs/results.md](docs/results.md).

The four systems:

- **Luna extractor**: GPT-5.6 Luna writes the memory (`system: memory`,
  a hosted extractor model).
- **Qwen 9B extractor**: Qwen3.5-9B writes the memory on one L40S through
  vLLM on Modal (`system: memory`, `executor: modal`).
- **Mem0**: Mem0 OSS builds one store per conversation; every stored memory
  goes to the answerer (`system: mem0`).
- **Full history**: the answerer reads the entire conversation
  (`system: full-history`).

Every system uses the same answerer, GPT-5.6 Luna with reasoning off, and
the same judges, Mem0's own prompts vendored under `third_party/mem0/`.

## Setup

Python 3.10 or newer.

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements.txt -r requirements-modal.txt
```

Provider credentials live in `.env` (see `.env.example`). The Qwen 9B
experiments also need a Modal account (`modal token new`).

## The sixteen experiments

`experiment_specs/` holds one frozen JSON file per cell of the results
table, named `<split>-<system>.json`:

| Split | Questions | Selection |
|---|---:|---|
| `longmemeval-100` | 100 | `question_ids_50.json` + `question_ids_50b.json` |
| `locomo-50` | 50 | `question_ids_locomo_50.json` |
| `beam-100k-50` | 50 | `question_ids_beam_50.json` |
| `beam-500k-40` | 40 | `question_ids_beam_500k_40.json` |

with `<system>` one of `luna`, `qwen9b`, `mem0`, `full-history`. A preset
holds the human choices; `preflight` resolves it to a complete specification
with source, prompt, model, pricing, and implementation hashes and never
spends money.

```bash
.venv/bin/python -m adaption_memory.cli preflight --spec experiment_specs/locomo-50-luna.json
```

## Running one cell

Prepare an immutable run, then execute it with an explicit budget. Paid work
always needs `--allow-paid` and a cap on the command line; a preset cannot
authorize spending.

```bash
.venv/bin/python -m adaption_memory.cli prepare \
  --spec experiment_specs/locomo-50-luna.json --run-id locomo-50-luna-001

.venv/bin/python -m adaption_memory.cli run \
  --spec experiment_specs/locomo-50-luna.json --run-id locomo-50-luna-001 \
  --allow-paid --budget-usd 10
```

The same two commands run the `mem0` and `full-history` cells. For a
`qwen9b` cell the extractor runs in a Modal sandbox: `run` launches it under
its own budget, and `resume --watch` collects the checkpoints when the
sandbox stops, then answers and judges under the API budget.

```bash
.venv/bin/python -m adaption_memory.cli run \
  --spec experiment_specs/locomo-50-qwen9b.json --run-id locomo-50-qwen9b-001 \
  --allow-paid --modal-budget-usd 6

.venv/bin/python -m adaption_memory.cli resume \
  --spec experiment_specs/locomo-50-qwen9b.json --run-id locomo-50-qwen9b-001 \
  --watch --allow-paid --budget-usd 10
```

Reports load through the same strict validator:

```bash
.venv/bin/python -m adaption_memory.cli report \
  --run-id locomo-50-luna-001 --output reports/locomo-50-luna-001
```

## Interruptions and retries

A call interrupted after dispatch is recorded as `unknown_outcome` and never
replayed automatically. `reconcile` lists unresolved calls without
replaying them; `tools/reconcile_connection_failures.py` re-opens calls that
provably never reached the provider, and
`tools/mem0_rollback_partial_session.py` rolls back a Mem0 session
interrupted mid-add.

A non-terminal run resumes after source edits: the configuration must match
and the code change is recorded in the run as an `implementation_change`
artifact. A terminal run is immutable; retry it under a new identity with
`resume --retry-as`. Answering and judging use `concurrency` workers, and
the budget cap doubles as a throttle.

Before a full run, `tools/modal_smoke.py` and `tools/mem0_smoke.py` build a
bounded slice of a spec's histories to check throughput and cost.

## Run records

Runs live under `runs/<run-id>/` as a content-addressed artifact graph:

```text
artifacts/<kind>/<sha256>.json
generations/<generation>/manifest.json
generations/<generation>/results.jsonl
generations/<generation>/commit.json
current.json
```

The pointer is published only after a coherent generation is durable. Each
artifact records parent hashes and the implementation revision. Readers
verify the pointer, commit, manifest, results, question set, exactly-once
IDs, artifact contents, and graph edges.

## Documents

- [docs/results.md](docs/results.md): the results table and token usage.
- [docs/extractor-size-analysis.md](docs/extractor-size-analysis.md): why a
  9B extractor matches a frontier one, with paired outcomes.
- [docs/memory-design.md](docs/memory-design.md): the memory format and
  prompt rationale.
- [docs/experiment-architecture.md](docs/experiment-architecture.md): the
  runner's architecture contract.
- [docs/progress.md](docs/progress.md): the experiment log, with predictions
  and outcomes for every run.

Extractor fine-tuning work, including the Gemma 3 4B and Qwen 0.8B
experiments, continues on the `extractor-fine-tune` branch.

## Tests

```bash
.venv/bin/python -m unittest discover
```
