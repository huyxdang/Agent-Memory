# Six-conversation BEAM training candidate

Historical candidate, superseded by [the eight-conversation selection](beam-training-candidate-v2.md). Its source files and report remain unchanged under `work/beam_training_candidate/`. The current preparation script targets the new selection; the reproduction command below describes the earlier script version, not the current one. Recorded code hashes identify that earlier version.

Prepared 2026-09-11. Six complete source histories are downloaded and hash-verified. Teacher targets have not been generated. This candidate provides 389 extraction update slots, not 1,000 validated training examples.

| Length | Chat ID | Topic | Eight-pair updates | History content tokens |
|---|---:|---|---:|---:|
| 100K | 7 | Academic essay writing | 15 | 122,328 |
| 100K | 11 | Ethics of AI hiring | 15 | 181,678 |
| 500K | 23 | Nutrition and meal planning | 60 | 516,600 |
| 500K | 27 | Renting a home | 60 | 469,760 |
| 1M | 19 | Learning a language | 119 | 1,007,336 |
| 1M | 30 | Patagonia hiking trip | 120 | 998,796 |
| Total | Six histories | Six topic categories | 389 | 3,296,498 |

Token counts use the project's `o200k_base` tokenizer. Length labels are dataset tiers, not exact counts under this tokenizer. Updates preserve the existing adapter: at most eight user/assistant pairs within each source batch, keeping its final partial window. No shortening or truncation was applied.

There are 120 associated benchmark questions, 20 per history. They do not multiply the teacher updates. Each history is built once from empty memory; the teacher receives prior memory and the next window, without benchmark questions or evaluation labels. The 120 questions belong with training sources and cannot later be used as held-out dev/final questions.

## Selection and overlap

Selection used topics and source identity, not answer scores. Chose two histories per tier with distinct categories and distinct numeric IDs. Conservatively excluded every numeric ID in all ten previously downloaded BEAM histories across tiers. Numeric IDs alone do not prove shared source origin.

Checks passed:

- Six complete histories, 20 unique question IDs each, 389 update slots.
- All 18 downloaded JSON files match Git blob hashes at the pinned source revision.
- No identical extraction windows or adjacent message pairs between any two selected histories.
- No identical histories, extraction windows, or adjacent message pairs shared with any of the ten local BEAM histories, including the earlier 100K and 500K evaluation cohorts.
- Report references match current script/adapter/prompt hashes. Existing benchmark input directories remain unchanged.

These are exact text checks, not semantic duplicate detection. Dev/final selections are still to be frozen and checked against these six histories. This preparation does not certify a complete three-way split.

Source: [BEAM revision b2da22e](https://github.com/mohammadtavakoli78/BEAM/tree/b2da22eac88bb0874c64665f13457eb99835774a/chats). Complete JSON sources and SHA-256 manifest are local under `work/beam_training_candidate/`.

## Teacher-generation cost forecast

Reference: the first saved complete memory build for each of the two histories in run `20260909T064305432208Z_memory_e66fa47`, totaling 134 calls. Teacher: `gpt-5.6-luna`, reasoning `low`. Mean output usage was 607.68 tokens per call, including hidden reasoning; mean added formatted memory was 588.68 tokens per update.

Historical rates were $0.20 input, $0.02 cached input, and $1.20 output per million tokens. These are recorded project rates, not verified current provider prices.

| Scenario | Forecast for all six histories |
|---|---:|
| Estimated repeated prior-memory input effectively cached | $1.28 |
| Same estimated memory growth, no input caching | $3.18 |
| No-cache estimate with 50% planning reserve | $4.76, approximately $5 |

The calculation includes current instructions/new-window input, estimated repeated prior memory, and all output usage including reasoning. It excludes synthetic generation, fine-tuning, Modal inference, answerer and judge calls. Source token totals alone are not total API input usage.

Approximately $5 is a planning allowance, not a hard maximum. Actual memory growth, reasoning usage and retries can exceed the forecast. Prices and available credits must be checked when configuring execution. No paid calls have been made for this preparation.

## Remaining checks before usable training data

- Generate teacher traces sequentially within each history and preserve input/target pairs, usage and elapsed time. Empty updates or factual errors may reduce the number of usable rows below 389.
- Check long-history prompt fit using the actual student tokenizer and training limit. Extrapolated prior memory near the end of a 1M history alone is around 70K `o200k_base` tokens. This is a warning to measure actual Qwen prompts against the intended 65,536-token training setup; the tokenizer counts are not interchangeable. Never silently truncate.
- Review teacher fidelity and choose separate dev/final sources before model fitting.
- If 1,000 original teacher examples remains required, this selection is short by 611 update slots. Synthetic rows could increase row count, but would still derive from these six sources. Additional original histories would add source diversity.

## Reproduce

From the project directory, with the existing Python environment:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem PYTHONDONTWRITEBYTECODE=1 .venv/bin/python prepare_beam_training_candidate.py --download
```

Omit `--download` to rerun the audit offline from saved sources. The script verifies cached source hashes and writes `work/beam_training_candidate/report.json`. It does not call a model or upload data.
