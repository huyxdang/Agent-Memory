# Rebalanced BEAM split

Revised 2026-09-11 following the user's request to improve topic balance. Keep eight train and two dev conversations per tier. Final remains the exact original fifty 100K questions and forty 500K questions. The previous manifests and report remain under `work/beam_split/`; the active set is `work/beam_split_v2/`.

## What changed and why

| Change | Reason |
|---|---|
| Move 100K/10, self-editing, from train to dev | Give 100K dev a writing conversation instead of two legal conversations |
| Move 100K/20, patent applications, from dev to train | Keep the split sizes unchanged and represent legal conversations in training |
| Replace 500K/24, chronic illness, with 500K/3, computer-vision programming | Add coding while retaining nutrition as a health topic |
| Replace 500K/25, photography, with 500K/7, mathematical induction | Add math; avoid leaving both coding and math entirely absent from training |

The broad training categories now cover all four dev categories: writing, legal, finance and sports. Dev still uses distinct source histories. Topic similarity is intentional; shared source messages across splits are forbidden. Choices used topic metadata, not dev/final answer scores. The final topic mix was already known, so this is a deliberate design revision, not evidence of improved accuracy.

## Active selection

| Split | Tier | IDs | Topics |
|---|---|---|---|
| Train | 100K | 7, 8, 9, 11, 14, 17, 18, 20 | Essays, cover letters, personal statements, AI hiring ethics, family movies, time management, burnout, patents |
| Train | 500K | 3, 7, 21, 23, 27, 29, 32, 34 | Computer vision, mathematical induction, investing, nutrition, renting, cooking, startups, hockey |
| Dev | 100K | 10, 19 | Self-editing, wills and estate planning |
| Dev | 500K | 22, 33 | Investment portfolios, basketball |
| Final | 100K | 1, 4, 6, 13, 16 | Original fifty selected questions, unchanged |
| Final | 500K | 1, 13 | Original forty selected questions, unchanged |

The earlier numeric-ID exclusion across different tiers was too broad. `100K/7` and `500K/7` are different source identities. The audit still compares actual histories, extraction windows and adjacent message pairs against every protected local evaluation history and all selected train/dev histories. It does not infer overlap from a number alone.

## Limits and execution

Verified counts: sixteen training histories provide **588 update slots**, and four dev histories provide **150 steps and 80 questions**. The coding replacement has 49 windows and the math replacement 59, replacing two 60-window histories. This accounts for the twelve-slot reduction; no truncation was applied.

All sixty source JSON hashes passed verification, with no matching histories/windows/pairs against the ten protected local histories and no matching windows/pairs across the 190 selected-history pairs. The final manifest matches the earlier final manifest exactly, including all ninety questions and source hashes. Forty-seven local tests passed, including a check that equal numeric IDs in different tiers are not automatically treated as the same history.

Updated historical-rate teacher-writing forecast: training **$1.88 cached to $3.40 uncached**, approximately **$5.10** with a 50% reserve on the uncached estimate. Optional teacher dev traces are **$0.47 to $0.87**. These are not current verified prices or hard caps and exclude student inference, fine-tuning, synthetic generation, answering and judging. No paid calls were made.

This is a manually balanced pilot, not a random or representative sample. Three of eight 100K training histories are still writing-related. Four dev histories cannot represent all topics or support extensive checkpoint searching reliably. No claim of better model accuracy follows from this selection alone.

Train/dev source files remain pinned to BEAM revision `b2da22eac88bb0874c64665f13457eb99835774a`. Each history retains complete eight-pair extraction windows. The preparation script verifies source hashes and the original final selection hashes before writing train/dev/final manifests. Exact overlap checks do not certify absence of semantic duplication.

Run `tools/prepare_beam_split.py --download` with the existing environment to prepare sources, or omit `--download` to audit the local cache. Artifacts are `work/beam_split_v2/{train,dev,final,source_manifest,report}.json`. No teacher or student model calls are made by the preparation script. The earlier audit's cost forecast is historical; use the revised report for this selection's forecast.

LongMemEval and LoCoMo final plans remain unchanged. Teacher quality, student prompt fit, provider credits and the full three-arm Modal budget still require verification before paid execution.
