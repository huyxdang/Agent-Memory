# Eight-conversation BEAM training candidate

Historical preparation checkpoint. The later [approved split decision](beam-split-decision.md) requires sixteen new training histories and four new dev histories, with the original 90-question BEAM final cohorts. This eight-history audit is not the completed approved split. Its reproduction instructions describe the earlier script, now replaced by `prepare_beam_split.py`; use [the current audit](beam-split-audit.md) for active commands.

Prepared 2026-09-11. This replaces the six-conversation proposal for future teacher generation. The original sources/report remain at `work/beam_training_candidate/`; the new artifacts are at `work/beam_training_candidate_v2/`. No teacher targets have been generated and no paid model calls were made.

| Tier | Chat IDs | Conversations | Eight-pair update slots | History content tokens |
|---|---|---:|---:|---:|
| 100K / 128K | 7, 11, 14, 18 | 4 | 60 | 575,811 |
| 500K | 9, 23, 27, 32 | 4 | 240 | 2,157,585 |
| Total | | 8 | 300 | 2,733,396 |

Tier names are upstream labels. Content counts use `o200k_base`, not the Qwen tokenizer or actual billed input usage. For example, 500K/32 contains 702,311 content tokens under this tokenizer. No history was shortened to make its tier label exact.

Retained 100K/7 academic writing, 100K/11 AI hiring ethics, 500K/23 nutrition and 500K/27 renting. Added 100K/14 family movie recommendations, 100K/18 workplace burnout, 500K/9 sequences and series, and 500K/32 building a startup. Removed 1M/19 and 1M/30 from the active proposal without deleting their cached files.

This gives eight source conversations instead of six, but 300 update slots instead of 389. The removed 1M histories supplied 239 steps; the four additions supply 150. Keep the existing adapter's maximum eight user/assistant pairs per window and final partial windows. One history is processed once, sequentially from empty memory. Each teacher input contains prior memory and the next source window, never a benchmark question or reference answer.

The 160 associated questions belong to these training-source histories. They are not extra extraction examples and cannot serve as held-out evaluation of a model trained on these histories. The 300 slots are potential examples, not quality-approved targets. Separate dev/final sources have not been selected or frozen. If any of these eight histories is assigned to dev later, its updates must be removed from the training count.

## Verification

- All 24 JSON files match Git blob hashes at BEAM revision `b2da22eac88bb0874c64665f13457eb99835774a` and have saved SHA-256 hashes.
- All eight histories load through the existing adapter, with 20 distinct question IDs each.
- Zero identical histories, eight-pair windows or adjacent message pairs shared with all ten previously downloaded BEAM histories. This pool includes the earlier 90-question 100K/500K cohorts.
- Zero matching windows or adjacent pairs across the 28 pairs of selected conversations.
- All eight numeric IDs are distinct and absent from the protected historical pool at every scale. This is a conservative exclusion, not proof that equal numeric IDs share an origin.

These checks detect exact duplicates, not semantic overlap. They do not certify a complete train/dev/final split. Benchmark source folders, existing LongMemEval exports and the six-history report are unchanged.

## Teacher-writing forecast

The forecast uses the same saved reference as the first candidate: 134 calls from two unique BEAM 500K builds in run `20260909T064305432208Z_memory_e66fa47`. The recorded extractor was `gpt-5.6-luna`, reasoning `low`. Historical rates per million tokens were $0.20 input, $0.02 cached input and $1.20 output. Current provider prices and credit balances have not been verified.

| Scenario | All eight histories |
|---|---:|
| Estimated prior-memory input effectively cached | $0.96 |
| Estimated prior-memory input uncached | $1.75 |
| Uncached estimate with 50% planning reserve | $2.63 |

The estimate includes instructions, incoming windows, repeated prior memory and output including reasoning. It excludes Modal, fine-tuning, synthesis, answering and judging. The reserve is not a hard maximum; output growth and retries can exceed it.

Removing 1M reduces the late-stage accumulated-memory risk. It does not prove prompt fit. Once teacher traces exist, count each complete input plus target with the student tokenizer against the planned 65,536-token training limit. Never silently truncate. Review factual support, attribution and empty updates before exporting training rows.

## Reproduce

From the repository with its existing environment:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem PYTHONDONTWRITEBYTECODE=1 .venv/bin/python prepare_beam_training_candidate.py --download
```

Omit `--download` for the offline source-verification/counting pass. The script saves source revision, file and code hashes, selected history IDs/hashes, overlap counts and forecast assumptions in `work/beam_training_candidate_v2/report.json`. It does not invoke models or upload data.
