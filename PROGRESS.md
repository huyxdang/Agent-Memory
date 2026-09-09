# Progress log

## Task: Matched no-retrieval comparisons, 2026-09-09

Status: in progress. Scope: LoCoMo shared 50; LongMemEval second 50. No BEAM or first-50 ingestion.

- Verified complete saved Mem0 stores for LoCoMo 50 and LongMemEval 49. Only `3b6f954b` may be recreated.
- Implementing explicit all-memory reuse with per-question source provenance, complete-history checks, prompt-fit checks, and no search.
- Budget allocation: LoCoMo at most $5; LongMemEval at most $10. Combined authorized ceiling $15. Existing writing costs excluded from incremental spend.
- Existing retrieval runs are preserved. No paid calls made yet.
- Next: offline validation, preflight estimates, then paid runs and matched comparisons.

### Offline checks passed

- Three unit tests passed: full-memory inclusion/no search, overflow rejection, budget blocking and retained reservations after unknown failures.
- Corrected an estimate lookup from `input_tokens` to `input_tokens_estimated`; initial LoCoMo estimate overstated inputs. No paid calls occurred during correction.
- Final preflights: LoCoMo `20260909T121140756473Z_mem0_1f69942`, projected $2.43922099. LongMemEval `20260909T121141648956Z_mem0_1f69942`, projected $3.56368041.
- Starting paid jobs with concurrency 3 and limits $5/$10. SDK automatic retries disabled in this mode. Per-call reservations remain charged internally when billing is unknown.

### Rebuild guard caught an uncapped SDK call

- Jobs: LoCoMo `20260909T121234546331Z_mem0_1f69942`; LongMemEval `20260909T121243562166Z_mem0_1f69942`.
- Mem0's reasoning-model parameter filter removes the output cap. The new spending guard blocked `3b6f954b` before dispatching its extraction call. Other questions continue from saved memories.
- Updated Mem0 wrapper to send the existing configured extraction limit explicitly, 128000 tokens. The prior ingestion projection assumed 2000 and is an estimate, not a hard bound. Per-call reservations enforce the budget.
- Will recover only the failed question in a separate run after confirming remaining allocation. No retrieval or bulk re-ingestion.

### Reused-store runs finished

- LoCoMo: 50/50 valid outputs, 42/50 correct, $0.36865160 incremental spend. Exactly-once audit passed; all answer/judge finish reasons were `stop`.
- LongMemEval: 49/50 valid outputs, only the blocked extraction missing, $0.59466835 incremental spend. Six judge controls agreed with expectations.
- Recovery `20260909T121716575119Z_mem0_1f69942` rebuilds only `3b6f954b` with limit $9, concurrency 1. Prior jobs are stopped; total maximum is now $9.96331995.
- The comparison script will merge recovery with the 49 existing outputs. Final reporting refuses to run while a no-retrieval job is active.

### Background follow-up configured

- Recovery reached 7/50 sessions without errors; its recorded spend was $0.04649920. Combined new spend $1.00981915.
- Four offline tests passed, including a regression check that Mem0 reasoning calls receive the explicit output cap. `git diff --check` passed.
- Updated existing heartbeat `mem0-benchmark-progress` to monitor this recovery every minute, provide ASCII progress, generate and verify the final comparison after completion, then pause itself. No new paid calls are authorized through the heartbeat.
- Current Markdown/JSON comparison files are explicitly provisional and will be regenerated when recovery ends. Source retrieval runs are unchanged. No git push performed.

### 2026-09-09 19:33 - Comparison complete

Status: complete.

- Recovery finished all 50 sessions and answered correctly. Final matched Mem0 outputs: LoCoMo 42/50; LongMemEval second 50 45/50. No missing, duplicated, invalid or failed outputs remain in the merged no-retrieval cohorts.
- Final comparison regenerated in `docs/no-retrieval-comparison.md` and `.json`. Exact matching question IDs, history hashes and reference answers verified against full-history and custom-memory baselines.
- All 100 Mem0 answer prompts fit with answer room; every saved memory line is included; retrieval is null; all answer/judge finish reasons are `stop`. All six expected-vs-actual judge controls passed in both LongMemEval jobs. LoCoMo uses its own judge, with no separate control suite in this runner.
- New spend across both cohorts plus recovery: $1.13154761, including judges and $0.13185966 for the one rebuilt store. Prior writing is not charged again. Historical retrieval remains separately labeled, including its unrecovered failed question.
- Tables exclude discarded failed ingestion costs; latency is observational across different runs/concurrency, not a controlled speed comparison. Those limitations remain explicit.
- Pausing the progress heartbeat after reporting completion. No new cohort, paid retry, git commit or push.

## Task: Remaining LongMemEval 50, 2026-09-09

Status: in progress.

- User repeated "Do the other 50" after clarification. Proceeding with the remaining LongMemEval first-50 cohort, not another LoCoMo cohort. This will complete LongMemEval 100.
- Reuse full-history `20260908T192233799242Z_full-history_8cc5c91` and ours `20260908T182110999548Z_memory_b5424ef`, both 50/50 successful.
- Reuse complete Mem0 stores from `20260908T222249129132Z_mem0_388f915` and `20260908T222250256294Z_mem0_388f915`. Rebuild exactly the other 48; do not use the old 20-line exports as complete stores.
- Preserve four-message chunks, Luna low extraction, Luna none answering, GPT-5 judging, and no question-based retrieval. No BEAM or LoCoMo changes.
- New job cap $13.86, plus $1.13154761 previously spent, stays below the existing $15 total ceiling. No paid calls yet for this extension.
- Corrected budget settlement to honor API-reported cached input at configured cached-token rates; uncached upper-bound reservations still precede calls, and unknown failures retain reservations.
- Added a labeled empirical ingestion forecast from the same-settings completed second-50 run, with 25 percent margin. This is not a guaranteed maximum; runtime reservations enforce the cap. Next: preflight and offline tests.

### First-50 preflight passed

- Preflight `20260909T135852076119Z_mem0_1f69942`: all 50 IDs present, two complete stores reused, exactly 48 authorized rebuilds. Forecast $11.91691165 under new cap $13.86.
- Five offline tests passed, including cached-input settlement, blocked dispatch, retained reservations after unknown failures, full-memory prompt inclusion, and explicit reasoning output caps. Diff whitespace check passed.
- Starting one paid job with concurrency 8. Session order remains sequential within each history. The budget state is saved with checkpoints, including reservations retained for unknown failures.

### Remaining-50 job started

- Active run `20260909T135940974756Z_mem0_1f69942`, local process session 89279. Two source stores reused; 48 histories total 2310 sessions to rebuild. At the first checkpoint reviewed: 28 new sessions, one question graded, $0.10740036 spent, no API/extraction errors.
- Added `compare_no_retrieval.py --longmemeval-first-run RUN_ID` to generate separate first-50, second-50 and combined-100 comparisons into new files, preserving the previous 50-question report. Unique run costs are counted once, not again in the combined table.
- Reusing full-history and ours gives 100 distinct IDs per system. The combined final report is blocked until the active run is terminal. No extra paid cohort or LoCoMo work.

### Background monitoring active

- Updated `mem0-benchmark-progress` to monitor the remaining-50 run every minute, produce ASCII updates and generate the combined-100 report on completion, then pause. The heartbeat cannot launch additional paid calls.
- Latest check: 61/2310 newly ingested sessions, 1/50 graded, $0.20431242 spent by this job. All six judge controls agreed with expectations; no API/extraction failures.
- Five offline tests and the active-run final-report guard passed. Full-history and ours each have 100 matching distinct questions, 85/100 correct before the new Mem0 comparison.
- Next: allow the existing run to finish, verify every output and produce the final first-50/combined-100 tables.

### 75-percent milestone notified, 2026-09-09 15:14 UTC

- Observed 38/50 successful, validly graded unique questions. This crosses the requested 75-percent milestone; do not notify it again.
- Monitoring is now milestone-only per user request: stay silent until 50/50 valid outputs, then verify and report the final comparison. No additional paid calls or retries are authorized by monitoring.

### 2026-09-09 15:33 UTC - Remaining 50 complete

Status: complete.

- Run finished at 15:30:28 UTC after 90 minutes 48 seconds. All 50 unique outputs succeeded, with 43 yes and 7 no verdicts and no memory failures. Run spend $7.26510582; cumulative new no-retrieval spend $8.39665343, below $15.
- Verified complete sessions and inclusion of every stored memory text, null retrieval, prompt fit, and stop finish reasons for answering and judging. All six factual judge controls matched expected grades: correct yes, paraphrase yes, wrong no for both questions.
- Generated docs/longmemeval-100-no-retrieval.md and .json. Matched unique IDs, history hashes and reference answers across systems for first 50, second 50 and combined 100. Combined no-retrieval scores: full history 85/100, ours 85/100, Mem0 88/100. Historical retrieval is separate, with one previously failed output explicitly retained.
- Corrected report concurrency note to include the first-50 extension's eight workers. Writing costs describe retained stores, not discarded failed attempts; call latency is not a controlled speed comparison. Provider billing for unknown-usage calls is not reconciled.
- No new paid calls, retries, commit or push during final verification. Monitoring will pause after the completion notice. No remaining run work.

### Publication scope corrected

- User requested code and aggregate results only. Removing newly added raw run manifests and summaries from the unpublished commit, retaining all local files. Aggregate exports now retain only expected/actual control grades, not question text, answers or judge responses.
- Verified Mem0 ingestion already defaults to two messages in both the CLI and store implementation; four was a historical run override. No completed-run metadata or memories changed, and no new API calls made.
