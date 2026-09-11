# Qwen extractor training and evaluation plan

Recorded 2026-09-11, Asia/Ho_Chi_Minh.

Status: approved experiment scope; full-run implementation, split verification and credit checks remain pending. Writing this plan does not launch jobs.

Execution update, 2026-09-11: follow the authoritative [BEAM split decision](beam-split-decision.md). Train uses eight new histories per tier, dev uses two other new histories per tier, and BEAM final reuses all five original 100K histories with their original 50 questions plus both original 500K histories with their original 40 questions. No 1M data. BEAM train/dev/final manifests and exact-overlap audit are complete; teacher targets remain pending. The earlier [preflight findings](qwen-experiment-preflight.md) concern the archived LongMemEval training proposal, not the active BEAM-only training split. Verified credit balances and the full inference estimate are still required before paid jobs. Tune only on dev and report all trials without forcing a positive outcome.

This is the current execution plan. It supersedes the earlier proposal to first compare original versus repaired training data. Copy 1 stays preserved, but training on Copy 1 is not a fourth experiment tonight. Follow `rules.md` throughout.

## Goal and experiment arms

Measure whether fine-tuning Qwen3.5-9B improves our memory extractor, and whether adding synthetic training data improves it further. Compare downstream benchmark results with the previous GPT-5.6 extractor runs.

| Arm | Extractor | Training data | Training service | Extractor execution |
|---|---|---|---|---|
| A: baseline | Untuned Qwen/Qwen3.5-9B | None | None | Modal |
| B: fine-tuned, no synthetic | Same Qwen base | Reviewed BEAM teacher traces from the frozen training split | AutoScientist | Modal |
| C: fine-tuned, with synthetic | Same Qwen base | Same BEAM training traces plus Adaptive Data synthetic examples | AutoScientist | Modal |
| Historical reference | Previous GPT-5.6 extractor | Existing saved run configuration | Not retrained | Reuse recorded results where comparable |

B and C each start from the same untuned base checkpoint. C does not continue training B. Disable additional AutoScientist augmentation in both arms so C's added examples come only from the explicitly recorded Adaptive Data job. Verify that these controls are supported before submission.

Use the audited manifests `work/beam_split_v2/train.json`, `dev.json` and `final.json`; see [the rebalanced split](beam-split-rebalanced.md). Sixteen training histories provide 588 update slots; four dev histories provide 150 separate steps and 80 dev questions. Teacher targets are not generated yet. Build each history once with the existing eight-pair windows. Keep all updates from a conversation in one split; do not randomly split rows. Preserve both LongMemEval copies and earlier BEAM audits unchanged, but do not merge the LongMemEval copies into training. Synthetic rows do not add independent original histories.

## Spending authorization

Update 2026-09-11: the user set the OpenAI cap to **$30**, separate from the unchanged **$30 Modal cap**. Allocate at most $10 to the resumable teacher job and reserve $20 for baseline-related OpenAI extraction, answering and judging. Do not launch multiple jobs each with the full $30 allowance. Account credit balance remains unverified; stop on insufficient-credit responses without purchasing or topping up. The full Qwen baseline is currently budget-blocked under the prior Modal pilot throughput estimate; see [execution status](resumable-teacher-and-baseline.md).

- Modal: **$30 total across all work in this plan**, including quick checks, all three arms, startup, downloads, idle time, failed attempts and retries. This is not $30 per arm or per benchmark. Earlier two-example pilot attempts belong to their earlier authorization and must remain separately recorded.
- Adaption: may spend up to the account's available existing credits on Adaptive Data and AutoScientist.
- Answering and judging APIs: may spend up to their available existing credits. Judge usage counts against provider credits even though it is excluded from reported system costs.
- No credit purchases, top-ups, auto-recharge, billed overage or unlimited postpaid usage are authorized. Do not change billing settings to expand these limits.
- Before paid work, record balances and outstanding commitments. Convert available credits into concrete job budgets using the provider's units and estimates. If a balance cannot be verified or a provider cannot bound a job within it, stop and ask for a numeric cap or verified balance.
- Request the Adaptive Data estimate using the intended configuration before generation. Check training costs and iteration limits before AutoScientist submission. Reserve enough credits for evaluations rather than spending them all on synthesis or training.
- Track cumulative Modal spending and reserve a shutdown/billing margin. Do not launch a job unless its conservative cost allowance plus outstanding jobs fits the remaining $30. Estimates are not invoices; account for uncertainty and delayed billing.
- Run only enough work to answer the experiment question. Permission to use available credits is not an instruction to exhaust them. Stop at budget limits and report partial results honestly.

## Benchmarks and split isolation

Target evaluation benchmarks: LongMemEval, LoCoMo, BEAM 100K and BEAM 500K. Exclude 1M.

BEAM final is fixed to `question_ids_beam_50.json` and `question_ids_beam_500k_40.json`: 50 original questions across five 100K conversations and 40 original questions across two 500K conversations. Do not subsample the five conversations or expand their question lists. They are previously inspected historical evaluation sets, not untouched tests. Additional intended final cohorts remain LongMemEval 100 questions and LoCoMo 50 questions across ten conversations; this update does not certify their exact manifests or split isolation.

Before calling any score held-out final performance:

1. Resolve and freeze exact final question IDs, source-history IDs, dataset revisions and history hashes. Check that the intended counts are feasible.
2. Audit overlap against all training and dev histories, including alternate question records, repeated sessions and synthetic parents. A different question about a training conversation is not an independent test history.
3. Keep whole histories together in train, dev or final. Do not supply dev or final histories, questions, answers or evidence to synthetic generation or training.
4. If the proposed final set overlaps, do not silently relabel it or change sample size. Report the overlap and resolve an independent split before training/evaluation claims. If independent histories are unavailable for a benchmark, report that constraint explicitly.

Use one identical final manifest for A, B and C. Select checkpoints and settings on dev only. Do not use A's final score to tune B or C, and do not repeatedly tune against final results.

## Quick signal runs

The user authorizes small subsets of all three benchmarks for quick checks during the process.

- For checks that influence prompts, hyperparameters, synthetic generation or checkpoint selection, use small fixed **dev** subsets, not final subsets.
- Save subset IDs before running and reuse them across arms. Cover several question types where feasible. Keep complete source histories even when selecting only a few questions.
- Quick checks should test actual sequential memory building, output validity, downstream answer accuracy, runtime and budget feasibility.
- A small question subset may still require a full long-history extraction. Estimate cost by unique histories and update counts, not only number of questions.
- If no independent dev data is available for one benchmark, flag it rather than quietly borrowing final examples.
- Any final-set canary is operational verification only. If its results influence tuning, those examples can no longer serve as untouched final evaluation.

## Fixed evaluation protocol

- Pin the same Qwen base revision, extractor prompt, memory schema, thinking setting, inference engine, precision and generation settings across A, B and C, apart from trained weights. Record unavoidable differences.
- Build memory from empty state for each unique sanitized history and extractor configuration. Each update consumes that extractor's own previous memory. Do not use teacher-generated prior memory at evaluation time.
- Extract without the evaluation question or reference labels. Give the answerer the completed memory and question, with the existing timestamp conventions. Keep reference answers and evidence annotations out of model inputs.
- No question-based retrieval in any memory arm. Supply all completed memories.
- Keep extraction sequential within each history. Share each completed immutable memory across its questions. Overlap independent histories and answering of finished histories where supported. Never answer from a changing memory.
- Freeze answerer and judge model IDs, prompts and scoring per benchmark using the verified project configuration. Change only the extractor between arms.
- Check complete training prompt-plus-target sequences and inference prompt-plus-output allowances against actual backend limits. Never silently truncate or drop oversized examples.
- Use the same training recipe, selection criterion and comparable training/search budgets for B and C where AutoScientist supports this. Record resolved settings and actual token exposure. If AutoScientist independently optimizes them, label the result a comparison of training pipelines, not a clean data-only causal effect.
- Synthetic quantity, mixture ratio, generation instructions and filtering rules must be frozen before training C. Generate from training sources only, retain parent IDs, and validate factual consistency, format, duplicates and held-out overlap.

## Execution order

1. Verify credits, credentials without exposing values, supported Qwen training model, checkpoint export/load compatibility, context limits and split handling. Freeze train/dev/final manifests and the historical comparator mapping.
2. Extend the working Modal pilot into modular shared-memory extraction and evaluation. Keep data preparation, training orchestration, inference and reporting separate. Add visible startup stages and bounded startup waits; test locally before paid runs.
3. Run A's small dev checks, resolve operational failures without looking at final scores, estimate the full workload, then run A on the frozen final set. Freeze the evaluation protocol before final scoring.
4. Generate and review BEAM teacher traces, verify complete prompt/target fit with the Qwen tokenizer, then train B with AutoScientist on the frozen BEAM training split only. Keep external dev/final out of provider training and automatic row splitting. Download the chosen checkpoint, verify it loads on Modal, run dev checks, then final evaluation.
5. Obtain the Adaptive Data estimate, generate the approved synthetic mixture and validate it. Train C with AutoScientist from the same original Qwen base. Run the same dev checks and final evaluation on Modal.
6. Produce the three-arm comparison and historical GPT-5.6 reference, including failure counts and cost accounting. Close all GPU resources.

Independent preparation or synthesis can overlap other stages when budgets and lineage are tracked. Do not promise overnight completion until estimates and provider queues are known. Credit, compatibility or data-isolation blockers take priority over finishing all jobs tonight.

## GPT-5.6 comparison

Resolve the exact historical extractor, answerer and judge versions from saved manifests; do not assume the shorthand GPT-5.6 uniquely identifies the run.

Reuse historical results for direct paired comparison only when histories/questions, prompts, scoring and relevant configurations match. Different final samples or historical per-question memory rebuilding make the reference observational. Label those differences rather than implying a controlled comparison. A new GPT-5.6 run is not one of the three requested jobs; report if a matched fresh reference would require expanding scope.

## Accounting and deliverables

Save one experiment ID linking arm IDs, parent training/synthetic job IDs, checkpoint hashes, memory-build IDs, answer/judge IDs and the final comparison. Preserve every attempt, including failures. Never silently resubmit an uncertain provider job; resolve its existing ID and state first.

For each arm and benchmark report:

- Expected/completed/failed questions and unique histories; verify every question exactly once.
- Final answer accuracy using the same benchmark scoring, paired deltas where valid, and question-type breakdowns. Do not equate AutoScientist's internal win rate or valid JSON with benchmark accuracy.
- History/context tokens and resulting memory tokens using one fixed reporting tokenizer. Also record backend-native input/output usage; these are different measurements.
- Extraction, answering and judging input/output usage separately. Output totals include reasoning when reported; do not add reasoning twice. Missing reasoning metadata stays unknown, not zero.
- Writing and answering costs as system costs; judging as separate internal accounting. Record synthetic generation and training costs separately, plus total project spend.
- Total wall-clock elapsed time, startup/loading time, extraction/answering/judging durations, time to first/all graded answers, concurrency and retries. Do not add overlapping durations to claim total wall time.
- Observed historical speedup only for genuinely comparable completed workloads, following `rules.md`. The two-example pilot is not a full-run baseline.
- Dataset/code/model revisions, exact prompts, generation/training settings, source and checkpoint hashes, UTC timestamps, provider job IDs and actual-versus-estimated billing.

Keep raw prompts, memories, answers, training data and credentials local/private. Publish only code and aggregate results if later asked; this plan does not request a commit or push.

## Current verified starting point

The new-account Modal pilot completed two teacher-forced extractor calls, not full sequential-history evaluation. Inputs were 16,022 and 36,620 tokens; both returned valid JSON. Total runtime was 530.469 seconds; actual invoice cost is still unverified. Artifacts: `work/modal_qwen_pilot_new_account/`.

No complete untuned benchmark run, AutoScientist fine-tune or Adaptive Data generation has been verified for this plan yet.

## Provider references for execution preflight

- [AutoScientist quickstart](https://docs.adaptionlabs.ai/autoscientist-quickstart)
- [Adaptive Data quickstart](https://docs.adaptionlabs.ai/adaptive-data-quickstart)
- [AutoScientist supported models](https://docs.adaptionlabs.ai/autoscientist/supported-models/)
- [Modal Sandbox API](https://modal.com/docs/sdk/py/latest/Sandbox)

Recheck current API contracts and authenticated model availability during implementation. These references do not replace credit, split or runtime verification.
