# Evaluation split isolation and sample-size review

Checked 2026-09-11. Scope: LongMemEval-S, current repaired Copy 2, and the proposed 50-question final. This review does not change splits or launch paid work.

## Current isolation checks

Read the saved train/dev JSONL exports, match every history hash to the sanitized 500-record source dataset, then compare full-history hashes, exact role/content session hashes, and dataset session IDs.

| Check | Result |
|---|---|
| Saved training | 51 histories / 51 associated questions / 2,428 extraction updates |
| Saved dev | 10 histories / 10 associated questions / 478 extraction updates |
| Histories present in both | 0 |
| Exact role/content sessions present in both | 0 |
| Session IDs present in both | 0 |
| Shared exact sessions between dev histories | 0; ten singleton components |
| Frozen new final manifest | Not found; current plan and preflight explicitly leave final IDs unresolved |
| Train-final and dev-final isolation | Not yet verified against a frozen final set |

Training contains 2,365 distinct text sessions and dev contains 478. Training can reuse sessions internally; that does not violate the cross-split rule. Exact matching does not certify absence of paraphrases or base-model pretraining exposure.

The proposed 32 train / 10 dev / 50 final candidate is not the saved split. No candidate IDs were adopted in this review.

Verified export SHA-256:

- Train: `df1b32836679be784601b6862db582e40fdd97fbb8c8f5bcb809ed553d8c0991`
- Dev: `2396e1c6185111880ea6edc26f640d2ce020858dd00feca4d2013256935cae35`

## Dev coverage

| Question type | Current dev | Full dataset |
|---|---:|---:|
| Single-session user | 2 | 70 |
| Single-session assistant | 1 | 56 |
| Single-session preference | 3 | 30 |
| Multi-session | 1 | 133 |
| Temporal reasoning | 1 | 133 |
| Knowledge update | 2 | 78 |
| Total | 10 | 500 |

No dev question has the dataset's `_abs` abstention suffix. Dev covers six question types, but preferences are 30% of dev versus 6% of the full dataset. Multi-session and temporal reasoning each have only one dev question. It is a coverage-oriented small set, not a representative accuracy estimate.

The 478 extraction updates support step-level diagnostics. They do not create 478 independent downstream QA outcomes. Full-rollout accuracy here has ten question outcomes.

## Research and numerical illustration

There is no universal sufficient sample size. Required size depends on the improvement we want to detect, variation in results, dependence between questions, and how often we select models using dev. Small NLP evaluations can be underpowered, making meaningful gains hard to distinguish from noise. See [Card et al., 2020](https://aclanthology.org/2020.emnlp-main.745/).

For scale, here are locally calculated 95% Wilson intervals if a hypothetical evaluation scored exactly 80%. The formula is from [NIST's proportion-confidence guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

| Questions | Hypothetical score | One changed answer | Illustrative 95% interval |
|---|---|---|---|
| 10 | 8/10 = 80% | 10 percentage points | 49.0% to 94.3% |
| 20 | 16/20 = 80% | 5 points | 58.4% to 91.9% |
| 30 | 24/30 = 80% | 3.3 points | 62.7% to 90.5% |
| 50 | 40/50 = 80% | 2 points | 67.0% to 88.8% |
| 100 | 80/100 = 80% | 1 point | 71.1% to 86.7% |

These are illustrations under an independent-binomial sampling model, not measured model results or valid uncertainty bounds for our selected subset by default. Type-based selection and within-final source overlap need consideration. More histories do not guarantee proportionally more independent evidence.

Compare model variants on exactly the same questions and analyze paired gains and losses, rather than deciding from overlap of separate accuracy intervals. [Dror et al., 2018](https://aclanthology.org/P18-1128/) describe paired tests and warn about dependent NLP observations. For binary grades, exact McNemar testing can be appropriate with independent pairs; shared-source dependence requires further treatment. We have not performed a power analysis for the actual model pair or chosen a dependence-adjusted test for the unfrozen final.

Repeatedly selecting a model on a small, noisy dev set can overfit the selection criterion itself, even without training directly on dev. This is the risk documented by [Cawley and Talbot, 2010](https://jmlr.org/papers/v11/cawley10a.html).

## Recommendation for this budget

- Ten dev histories can support an initial fixed three-arm pilot and obvious failure checks. They are too weak to justify extensive hill-climbing or choosing a winner from one extra correct answer.
- A 50-question final can be a useful exploratory comparison. It does not by itself substantiate a small improvement, equivalence, or a claim to match Luna. Report question-level paired changes and uncertainty, and allow an inconclusive result.
- If sustained hill-climbing remains the goal, investigate a larger and better-balanced dev set before training. A 20-30-history dev is a practical candidate to investigate, not a research-established minimum or an approved new count. Enlarging it can remove additional training histories and constrain the final set. Re-audit that tradeoff before changing any export.
- Freeze the chosen final IDs and both cross-split overlap checks before any final runs. Do not choose or expand the final based on a favorable model score. Compare all arms, including any fresh Luna reference, on the same final questions.

No dataset, model, or experiment configuration changed. Online research and read-only local checks incurred no model API spend.
