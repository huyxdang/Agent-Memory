# Agent-Memory

Minimal full-history baseline for the cleaned LongMemEval-S dataset. It uses
Mem0's existing LongMemEval judge prompt and yes/no scoring method. Memory
extraction and retrieval are intentionally out of scope.

## Setup

Python 3.10 or newer is required. The pinned `tiktoken` release ships wheels
through Python 3.14.

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements.txt -r requirements-inspect.txt
```

`requirements.txt` is the runner. `requirements-inspect.txt` is the separate
inspection tool described under "Inspecting runs"; the runner never imports it.

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

## Memory system

`--system memory` replaces the full history with write-time memory. An
extractor (`EXTRACTION_MODEL`, `EXTRACTION_REASONING_EFFORT`) reads each
session in order together with the memory so far and appends new lines of two
kinds: atomic `key: value` facts and narrative context. A changed fact is a
new line for the same key whose value carries the whole chain, newest first,
such as `charity 5K personal best: 25:50 <- 27:12`. Nothing is ever edited.
The answerer sees all narrative lines and the last atomic line per key. The
design and its rationale are in `docs/memory-design.md`; the literature behind
it is in `docs/literature.md`.

`--questions FILE` selects which benchmark questions run. The default,
`question_ids.json`, is the five fixed questions. `question_ids_50.json` is
fifty: the first non-abstention questions of each type in dataset order,
eight per type and nine for knowledge-update and single-session-preference,
so the article's two headline categories have the most items. Report the
plain mean and, for comparison with published scores, the same results
reweighted to the benchmark's type proportions.

`--test FILE` runs one dataset-shaped JSON file instead of the selected questions.
The smoke test is eight sessions cut from the knowledge-update question:

```bash
.venv/bin/python longmemeval_eval.py --system memory --test fixtures/memory_smoke_test.json
```

Extraction uses the answer model's prices. Every extraction call, the final
store, and any flagged lines are in the run record and the summary, and the
viewer shows them as a memory-writing span before the answer call. Extraction
prompts are structured so the earlier memory is served from the provider's
prompt cache; cached tokens are reported per call.

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

## Inspecting runs

Run records are the source of truth but are not readable by eye. The bridge
converts them into Inspect AI log files under the ignored `logs/` directory,
one per run, without any API calls:

```bash
.venv/bin/python inspect_bridge.py
```

Pass run IDs to convert only those runs. Then open the viewer:

```bash
.venv/bin/inspect view --log-dir logs
```

The viewer lists every run with its accuracy, judge-control agreement, and
token totals. Each benchmark question is a sample showing the system prompt,
the full conversation history as one chat message per turn stamped with its
session number and timestamp, the question, the reference answer, the
generated answer, the verdict, and per-call token usage split into input,
cached input, output, and reasoning, with USD cost. The API call itself sent
the history as compact JSON inside a single user message; the bridge expands it
for reading because the viewer caps any single text block at 250,000
characters. The model-call event records the prompt's SHA-256 and length so it
can be matched to the exact rendered prompt in `results.jsonl`.

The dataset labels which sessions and turns hold the answer. The runner strips
those labels from the prompt, so the model never sees them. The bridge reads
them from the pinned dataset and shows them in the viewer only: each evidence
turn's bubble is flagged in its metadata, other turns in an evidence session
carry a weaker flag, and the sample's metadata tab lists the evidence sessions
with timestamps and the evidence turns with their text. The transcript opens
with an evidence block whose links jump to each evidence bubble.

Restart the viewer after regenerating logs; it keeps an index of each file and
reports a ZIP error when a file changes underneath it. The transcript tab shows the answer call and the
judge call in order, and the scoring tab shows the judge's reasoning and the
full judge prompt. The six judge-control cases appear as samples prefixed
`control:`.

The runner and Inspect are separate systems. Anything that should be visible
in the viewer must first be written into the run record, then mapped by the
bridge.
