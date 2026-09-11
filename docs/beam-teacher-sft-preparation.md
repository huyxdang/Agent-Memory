# Luna BEAM teacher preparation

Prepared 2026-09-11 from the approved 16-history BEAM training split. No dev,
final, archived LongMemEval or Qwen evaluation traces were included.

## Results

| Check | Result |
|---|---:|
| Completed teacher histories | 16/16 |
| Completed source updates | 588/588 |
| Reconstructed inputs and memory states matching saved traces | 588/588 |
| Valid, non-truncated JSON targets | 588/588 |
| Full training sequences within 65,536 tokens | 564 |
| Oversized sequences preserved outside fitting export | 24 |
| Updates with heuristic warnings | 366 |
| Historical unknown attempts excluded from targets | 7 |
| Exact cross-split history/window/message-pair overlap | 0 |

The final ten updates were generated in a separate teacher session after explicit
user authorization to replace the unresolved timeout. That invocation took
99.60 seconds. Total teacher accounted upper bound is $4.28748212 against its
$10 allocation, retaining all abandoned-call reservations. Actual invoice costs
remain unverified. Preparation itself used no model or Adaption calls and did
not alter or restart Qwen evaluation.

## Files

Snapshot: `work/beam_teacher_sft/e18563c1a02ce127/` (local and gitignored).

- `candidates.jsonl`: all 588 original visible targets and role-preserving inputs,
  with stable history/update IDs, provenance, usage, timing and warnings.
- `train.messages.jsonl`: 564 context-fitting chat rows. Each contains the original
  system/user messages followed by the teacher's visible JSON assistant output.
- `train.provenance.jsonl`: the same row order with IDs, hashes and audit fields,
  excluded from model training input.
- `oversize.provenance.jsonl`: the 24 over-limit update IDs and measurements;
  their full inputs and targets remain in `candidates.jsonl`.
- `excluded_attempts.json`: seven abandoned unknown calls, not training examples.
- `split_manifest.json`: train/dev/final history identities, with no held-out content.
- `teacher_configuration.json` and `report.json`: settings, versions, hashes,
  source accounting, validation results and remaining blockers.

All 16 training histories remain represented. Whole-history split assignments
are unchanged; no random row-level dev split was created. The four dev histories
remain reserved for downstream evaluation. Exact overlap checks do not establish
the absence of paraphrased or semantic near-duplicates.

## Token lengths

Counts use the locally cached Qwen/Qwen3.5-9B tokenizer revision
`c202236235762e1c871ad0ccb60c8ee5ba337b9a`, Transformers 5.17.0, and the pinned
chat template with thinking disabled. Full sequences include chat-template
overhead and the target's end marker. The exporter verifies that the complete
training sequence starts with the inference generation prompt. The Modal runtime
uses Transformers 4.57.6; provider-side training preprocessing still needs a
parity check before upload.

| Tokens per update, all 588 | Minimum | Median* | P95* | Maximum |
|---|---:|---:|---:|---:|
| Prompt | 6,876 | 27,365 | 62,356 | 75,934 |
| Visible target | 9 | 632 | 1,069 | 1,550 |
| Full training sequence | 7,628 | 27,921 | 63,265 | 76,986 |

*Median is the upper middle observation; P95 uses index floor((n-1) × 0.95).
Hidden reasoning is not a training target. Original API usage, including
reasoning-token accounting when supplied, remains in provenance.

## Not yet approved for training

These are mechanically verified candidates, not quality-certified training data.
The warning checker can flag supported paraphrases and miss attribution errors.
Warnings were preserved, not used to automatically remove rows or rewrite targets.
Review source faithfulness, speaker attribution, update semantics and coverage
before choosing the training subset.

[Adaption's documented limits](https://docs.adaptionlabs.ai/autoscientist/supported-models/)
require 1,000 rows and allow 65,536-token Qwen-9B SFT sequences; overlong uploaded
rows are truncated by the platform. The 564 fitting candidates therefore need
at least 436 additional fitting rows, before any quality exclusions. Synthetic
rows could contribute to the synthetic arm, but cannot make the no-synthetic arm
eligible. Do not duplicate examples or use held-out data to meet the minimum.

The canonical chat files are not claimed to be verified AutoScientist uploads.
Before submission, validate role-preserving mapping and thinking-off preprocessing
against its [raw ingestion workflow](https://docs.adaptionlabs.ai/autoscientist/run-on-non-adapted-data)
and [training API](https://docs.adaptionlabs.ai/api/resources/autoscientist/methods/create).
Use completion-only loss for extractor distillation; do not train on provenance
or hidden reasoning. No dataset upload, synthesis or training job was launched.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python prepare_teacher_sft.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

The exporter takes a stable snapshot under the teacher's lock, refuses mismatched
source/configuration/checkpoints, and checks existing artifact hashes on rerun.
It replays the saved outputs locally; it never calls the teacher. Updated source
traces or exporter code produce a new snapshot directory instead of overwriting
the old one. Keep original teacher code available to certify replay.

Validation: 75 tests passed, including six new exporter tests covering exact
targets, evaluation-label exclusion, prompt tampering, duplicate steps, unknown
attempts, overlength preservation and replay-state mismatch.
