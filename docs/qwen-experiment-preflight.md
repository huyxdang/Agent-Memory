# Qwen experiment preflight, 2026-09-11

Status: paid experiments not launched. Awaiting a final-set decision and verified provider credit balances.

## Passed

- Both required API keys are present; values were not printed.
- Installed the official Adaption SDK 0.12.0 in the existing environment and pinned it in `requirements-adaption.txt`.
- Authenticated read-only `autoscientist.list_models()` succeeded and listed `Qwen/Qwen3.5-9B` with SFT and LoRA support. The returned serving context does not establish training context limits.
- All 38 local tests pass, including the new regression test for histories with different IDs but shared sessions. Test dollar output is mocked, not paid usage.
- The repaired Copy 2 has 2,428 training updates from 51 LongMemEval histories, and 478 dev updates from 10 LongMemEval histories. Exact train/dev session overlap is zero.

## Final-set constraint

`experiment_preflight.py` checks normalized source-message session hashes, ignoring timestamps, against all current training and dev histories. It does not inspect evaluation answers to choose examples.

| LongMemEval source records | Count |
|---|---:|
| Same whole history as train/dev | 61 |
| Different history, but at least one shared source session | 418 |
| Pass exact history and session disjointness | 21 |
| Total | 500 |

All 100 previously evaluated LongMemEval records fall in the first two groups. None qualifies as an independent final record under the agreed rule. Overlap is not proof that the answer-bearing session leaked; repeated distractor sessions also trigger this conservative guard. Near-duplicate/semantic overlap remains unreviewed.

The 21 eligible records contain 18 non-abstention and 3 abstention questions. Their question-type distribution differs from the original 100. The 18 non-abstention subset has no single-session-user question. Reporting these as an equivalent replacement for the historical 100 would be misleading.

The historical 10 LoCoMo and 2 BEAM 500K conversations have no exact training/dev session overlap with this LongMemEval-only training copy. They have been evaluated previously and should not be described as never-seen data. Any question subset used for tuning must have a whole-history dev/final assignment; using different questions from the same final conversation does not solve this.

## Recommended decision

Preserve the repaired training copy. Use the 21 eligible LongMemEval records as a smaller final evaluation, explicitly report its changed size/type mix, and retain the original 100 as a historical reference only. This needs user approval because it changes the planned final sample size. Keeping an independent final 100 instead requires redesigning the training/dev split, rebuilding exports and rechecking feasibility; it is not yet proven feasible with at least 1,000 training rows.

Do not freeze final IDs or train until this decision is resolved. Do not choose between splits based on benchmark scores.

## Credit constraint

Modal authorization is $30 total for the new experiment plan. Adaption and answering/judging authorization is existing credits only. Authentication does not establish a remaining balance. The installed Adaption resource/type inspection did not expose a credit-balance method; user-provided dashboard balances or another verified read-only billing source are still needed. No charged job has been used as a credit probe.

## Hill-climbing protocol

The user authorizes iterating toward matching/exceeding the historical Luna extractor. Use dev final-answer accuracy as the primary selection metric, with per-type results, factual checks, context size and cost as diagnostics. Record every trial and retain negative results. Freeze a common final protocol before scoring final examples. Stop when budgets are insufficient, not only when a positive result appears.

Do not silently replace final-answer accuracy with JSON validity, lower token count or a favorable subset. Token/cost improvements are separate findings. A failure to improve is a valid outcome.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiment_preflight.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

Detailed counts, eligible IDs, file hashes and limitations are in `work/qwen_experiment_preflight/report.json`. The audit does not modify training data or select final IDs.
