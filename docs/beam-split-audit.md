# Approved BEAM split: source audit

Historical audit, superseded by [the rebalanced split](beam-split-rebalanced.md). The artifacts below remain unchanged; the current preparation script writes `work/beam_split_v2/` instead.

Prepared 2026-09-11 under [the split decision](beam-split-decision.md). Source selection and local manifests are complete. No teacher targets, student memories, training jobs or new evaluation scores have been generated.

| Split | Tier | Conversation IDs | Conversations | Questions | Extraction updates |
|---|---|---|---:|---:|---:|
| Train | 100K | 7, 8, 9, 10, 11, 14, 17, 18 | 8 | 160 | 120 |
| Train | 500K | 21, 23, 24, 25, 27, 29, 32, 34 | 8 | 160 | 480 |
| Dev | 100K | 19, 20 | 2 | 40 | 30 |
| Dev | 500K | 22, 33 | 2 | 40 | 120 |
| Final | 100K | 1, 4, 6, 13, 16 | 5 | 50 original | Not rebuilt in this task |
| Final | 500K | 1, 13 | 2 | 40 original | Not rebuilt in this task |

Training has 600 potential input/target updates, not 320 question-conditioned examples. The extractor never sees the benchmark questions or answers. Dev has 80 downstream questions across four histories; its 150 extraction steps must never be exported as training rows or synthetic seeds. Generate teacher dev traces only if needed for a separate validation-loss comparison. Each student must build its own dev and final memories for accuracy evaluation.

## Selection and verification

- New train/dev sources use BEAM revision `b2da22eac88bb0874c64665f13457eb99835774a`. All 60 downloaded JSON files match the pinned Git blob hashes and have saved SHA-256 hashes. No pickle or upstream code execution.
- Selected topics and source availability, not answer scores. Conservatively excluded every numeric ID from all ten earlier local BEAM histories at every tier. Equal IDs across tiers do not prove shared origin. The remaining 100K source pool limits topic balancing; dev legal/finance/sports topics do not exactly match training proportions.
- All twenty histories contain twenty unique question IDs and retain the existing eight-pair window boundaries. No history truncation or chunk-size change.
- No exact history, window or adjacent message-pair overlap with the protected ten-history local pool, which includes all seven final histories. No matching windows or pairs across any of the 190 selected-history pairs, including train/dev pairs.
- Final remains the exact original `question_ids_beam_50.json` and `question_ids_beam_500k_40.json` files. Their SHA-256 hashes are pinned in the preparation script; changing either file rejects the audit. Each final question has a saved sanitized-history hash. Original source file hashes are recorded separately from the newly downloaded source revision.
- Forty-six offline tests passed, including five new split tests for count/membership errors, duplicate histories and protected/source-pair overlap. Printed spend in the test suite is mock accounting, not a paid call.

Checks detect exact shared text, not semantic duplication. New here means not previously used for evaluation or training; some were already downloaded during candidate preparation. Previously prepared source caches, raw runs and the original final selection files remain unchanged. LongMemEval and LoCoMo remain additional final evaluations; this BEAM audit does not certify their split manifests.

## Historical-rate teacher-writing forecast

| Workload | Effective prior-memory caching | No caching | No-cache plus 50% reserve |
|---|---:|---:|---:|
| Training histories only | $1.85 | $3.44 | $5.15 |
| Optional teacher dev histories | $0.48 | $0.88 | $1.31 |
| Both | $2.32 | $4.31 | $6.47 |

Forecasts extrapolate 134 saved Luna extraction calls from two historical 500K histories, including repeated prior memory and output reasoning. Historical rates are not verified current prices; reserve amounts are not hard caps. These figures exclude student dev/final inference, answering, judging, Modal, fine-tuning and synthetic generation. No paid calls were made. The full three-arm Modal workload still needs budgeting against the $30 cap.

Actual Qwen prompt-plus-target fit and teacher fidelity cannot be certified before teacher traces exist. No silent truncation or automatic acceptance of all 600 slots is allowed.

## Artifacts and reproduction

- `work/beam_split/train.json`: sixteen source histories, hashes and associated question IDs.
- `work/beam_split/dev.json`: four separate source histories and question IDs.
- `work/beam_split/final.json`: original ninety evaluation question IDs, history hashes and source/selection file hashes.
- `work/beam_split/source_manifest.json`: pinned source revision and sixty file hashes.
- `work/beam_split/report.json`: full source counts, pairwise audit, code hashes and historical-rate forecast.

From the repository:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem PYTHONDONTWRITEBYTECODE=1 .venv/bin/python prepare_beam_split.py --download
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

Omit `--download` for an offline audit of cached sources. The new script replaces the obsolete candidate-only script; historical reports remain preserved. These manifests select sources and questions, not training-ready chat-format targets. They must be consumed explicitly by the future teacher/inference runner; normal benchmark folders were not repointed.
