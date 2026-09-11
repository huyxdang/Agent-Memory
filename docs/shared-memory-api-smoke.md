# Real-API shared-memory smoke test

Run `20260910T050844115482Z_memory_a79fc91`, 2026-09-10 UTC.
Synthetic fixture: `fixtures/shared_memory_smoke.json`. This is not a benchmark score.
Code HEAD `a79fc917e3bb5d705c53e20285179beb03df5ccb` plus uncommitted shared-pipeline
changes; exact source hashes and prompts are in the local run manifest.

## Result

- Three unique questions completed exactly once; three correct judge verdicts.
- Two unique histories, two sessions each: four extraction calls, three answer
  calls and three judge calls. No failures or unknown usage/cost.
- Two questions referenced the same build ID and identical completed memory.
  Both immutable artifact hashes verified. All answer prompts fit.
- Real overlap observed: answering started at 05:08:51.019707 UTC while the
  other history's build finished at 05:08:51.866710 UTC.
- Recorded run time 13.087159 seconds; invocation through finalization 13.284083
  seconds; first graded answer 11.123142 seconds after run start.

| Stage | Calls | Input tokens | Output tokens, including reasoning | Reasoning subset | Cost USD |
|---|---:|---:|---:|---:|---:|
| Memory writing | 4 | 3,884 | 265 | 129 | 0.00109480 |
| Answering | 3 | 824 | 29 | 0 | 0.00019960 |
| Judging, internal | 3 | 2,159 | 362 | 256 | 0.00631875 |

Total recorded spend **$0.00761315**, under the authorized **$0.10** cap.
System cost excluding judging: $0.00129440. Costs use API-reported usage and
existing project token prices; these are not a reconciled provider invoice.

Resolved extractor/answerer: `gpt-5.6-luna`, extraction reasoning low and answering
reasoning none. Resolved judge: `gpt-5-2025-08-07`, using the vendored Mem0 LoCoMo
judge prompt. No separate factual judge-control suite was run for this smoke test.

## Command

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python longmemeval_eval.py \
  --system memory --benchmark locomo --test fixtures/shared_memory_smoke.json \
  --spending-limit 0.10 --extraction-max-tokens 2048 --answer-max-tokens 128 \
  --judge-max-tokens 1536 --concurrency 3 --build-workers 2 \
  --answer-workers 2 --judge-workers 2
```

The free preflight used a 2048-token judge cap and projected $0.10171364.
Before paid dispatch, the judge cap was reduced to 1536; the actual run's
preflight projected $0.08635364. No paid attempt exceeded or raised the cap.

Sixteen offline tests and the whitespace check also passed. This verifies basic
real-provider integration and overlap, not large-history throughput, benchmark
accuracy, or observed historical speedup. Raw outputs remain local under
`runs/20260910T050844115482Z_memory_a79fc91/`.
