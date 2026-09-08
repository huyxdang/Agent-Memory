# Agent-Memory

Minimal full-history baseline for the cleaned LongMemEval-S dataset. It uses
Mem0's existing LongMemEval judge prompt and yes/no scoring method. Memory
extraction and retrieval are intentionally out of scope.

## Setup

Python 3.11 to 3.13 is required. Python 3.14 cannot install the pinned
`tiktoken` wheel without a Rust compiler.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run the free preflight first. It verifies the dataset checksum, five fixed IDs,
complete history transfer, label exclusion, prompt token counts, and the
exactly-once accounting check. If the dataset is absent, the script downloads
the pinned 277 MB file into the ignored `work/` directory.

```bash
.venv/bin/python longmemeval_eval.py --preflight
```

Every invocation creates a unique immutable record under `runs/<run-id>/` and
prints the run ID. A preflight is indexed with status `preflight_only`. The
current configuration reserves 1,024 answer tokens and a 256-token framing
margin within GPT-5.6 Luna's 1,050,000-token context window. It never truncates.
The GPT-5 judge has a separate 4,096-token output allowance so its internal
reasoning does not consume the entire response budget before a visible yes/no
verdict.

## Paid run

Copy `.env.example` to the ignored `.env`, then add an OpenAI Platform API key:

```bash
cp .env.example .env
nano .env
```

Paste the key after `OPENAI_API_KEY=`, save with `Ctrl-O`, press Enter, and exit
with `Ctrl-X`. Then run:

```bash
.venv/bin/python longmemeval_eval.py
```

Use the exact per-million-token prices charged by the selected provider. Set
`OPENAI_BASE_URL` for an OpenAI-compatible endpoint. Every run records the
requested and API-resolved models, usage, timing, calculated cost, prompts,
dataset and upstream revisions, dependency versions, Git state, and script
SHA-256. The runner checks the worst-case projected cost against the spending
limit before its first API call.

Token reporting uses `o200k_base` for the supplied history size and API usage
metadata for calls. API output tokens already include hidden reasoning tokens;
the report derives non-reasoning output as output minus reasoning. For this
full-history baseline, memory-writing usage is explicitly zero. Answering usage
is the reported system usage, while all benchmark and control-judge usage is
kept as separate internal accounting. Total API spend still includes both.

The paid run first sends six judge-control cases: a known answer, a paraphrase,
and a wrong answer for each of two factual questions. Disagreements are reported
as-is. It then answers and judges each of the five benchmark questions. API
errors, invalid verdicts, missing records, and duplicate records remain explicit
in the run record.

## Run records

Each run has one directory:

```text
runs/<run-id>/
  manifest.json
  results.jsonl
  summary.md
```

`manifest.json` is the machine-readable run envelope: status, timestamps,
dataset and code revisions, ordered question IDs and hashes, exact prompt
templates, model configuration, token and cost totals, validation controls,
failures, and the experiment fingerprint. `results.jsonl` contains exactly one
checkpointed record for each selected question, including its exact rendered
prompts, answer, grade, usage, cost, timing, and errors. `summary.md` is the
readable report.

The script writes checkpoints atomically while a run is `running`. Once a run
reaches a terminal status, its directory is immutable and one compact row is
appended to `runs/index.jsonl`. The index is for comparisons; the run directory
is the source of truth.

Resume an interrupted run only when its original code and configuration are
available:

```bash
.venv/bin/python longmemeval_eval.py --resume <run-id>
```

The experiment fingerprint must match. Successful questions and judge controls
are skipped, an answer checkpoint can continue directly to judging, and failed
records are preserved. To intentionally repeat a terminal run, create a new run
linked to it:

```bash
.venv/bin/python longmemeval_eval.py --retry-of <run-id>
```

Legacy result files can be converted without API calls:

```bash
.venv/bin/python longmemeval_eval.py \
  --backfill-existing path/to/attempt.json path/to/final.json
```
