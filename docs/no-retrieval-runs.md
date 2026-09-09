# Running the all-memory comparison

Use the repository's `.venv` and existing `.env`. No API keys belong in run artifacts.

New Mem0 ingestion defaults to two messages per add, one user-assistant pair. `--mem0-chunk-messages 4` was an explicit override for the completed LongMemEval runs, not a changed default. Reusing those stores does not rewrite them into two-message chunks.

Raw run manifests, question-level answers and memory stores stay local. Publish code and aggregate comparison reports only. Regenerating reports requires the local run artifacts; a fresh clone contains the published aggregates, not the raw responses. Historical run artifacts already committed before this change are unchanged.

```sh
.venv/bin/python -m unittest test_all_memories -v
.venv/bin/python longmemeval_eval.py --system mem0 --benchmark locomo \
  --questions question_ids_locomo_50.json \
  --mem0-all-from 20260908T222244440761Z_mem0_388f915 20260909T005041106821Z_mem0_e2ba6d1 \
  --spending-limit 5 --concurrency 3 --preflight
```

Remove `--preflight` only to authorize another paid run. The source runs are immutable. `--mem0-all-from` loads complete final memory lines, verifies the history hash and completed session count, supplies all lines with dates, and never calls search. It rejects missing stores unless their exact question IDs are supplied with `--mem0-ingest-missing`. It rejects old truncated exports. No top-k filtering, deduplication, or question-based selection is performed. Equal-date lines retain saved order.

Answering and judging use existing model, tokenizer, context-window and price settings. The system prompt differs from the retrieval prompt only by changing “retrieved” to “stored”; the input header says “All stored”. Reference answers and labels go only to the judge, not to the answerer.

The 2026-09-09 jobs use answer model `gpt-5.6-luna` with reasoning `none`, and judge `gpt-5` with provider-default reasoning. Each new run records configured and returned model IDs, full answer/judge prompts, file hashes and source-run provenance. Reused stores retain historical extraction usage but do not add to new API spending.

The spending guard reserves uncached input/output cost before every wrapped call, disables SDK automatic retries, and retains reservations when billing is unknown. A missing-store rebuild uses the configured extraction output cap explicitly because Mem0's reasoning-model path omits it. Existing extraction preflight projections are estimates, not a guaranteed maximum; runtime reservations enforce the limit. No embedding-input truncation is allowed in this mode.

Each run saves `manifest.json`, `results.jsonl`, and `summary.md` under `runs/RUN_ID/`. Do not restart the full cohort to recover one failed question. Use an explicit one-question selection and link it with `--retry-of`; the comparison merges that successful recovery with the other 49 outputs, checking exactly one result per selected ID.

After all jobs finish:

```sh
.venv/bin/python compare_no_retrieval.py
```

This produces `docs/no-retrieval-comparison.md` and its JSON companion. The comparison checks identical question sets, history hashes and reference answers. Historical retrieval is separately labeled. Mean latency is observational across runs, not a controlled speed test. Writing costs are for retained stores; discarded failed attempts are excluded and must not be mistaken for free work.

## Remaining LongMemEval 50

Run `20260909T135940974756Z_mem0_1f69942` covers `question_ids_50.json`: reuse two complete exports, rebuild exactly 48, chunk size four, concurrency eight, cap $13.86. This extends LongMemEval to 100; LoCoMo remains 50.

`--mem0-cost-reference 20260909T092328675957Z_mem0_e911e4d` uses observed per-add ingestion cost from matching settings with a 25% margin. It is a forecast, not a hard bound. The guard reserves uncached maximum cost before each call, then settles confirmed cached tokens at the configured cached rate. Unknown failed-call reservations are retained. See [OpenAI's usage metadata](https://developers.openai.com/api/docs/guides/prompt-caching).

After that run is terminal, generate the first-50, second-50 and combined-100 tables without overwriting the earlier report:

```sh
.venv/bin/python compare_no_retrieval.py \
  --longmemeval-first-run 20260909T135940974756Z_mem0_1f69942
```

Outputs: `docs/longmemeval-100-no-retrieval.md` and `.json`. Costs across overlapping first/second/combined tables must not be added; incremental spend counts each unique run only once.
