# No-retrieval comparison

All comparisons use the same question IDs and history hashes within each named cohort. First-50, second-50 and combined-100 results are separately labeled; do not add their costs together.

Input = API-reported answering input, including instructions and question. Context = supplied history/memory block, counted with o200k_base. Latency = mean answer-call wall time, excluding writing and judging. Costs are totals for the named cohort, not per-question averages. Writing cost includes the original reused writing; it is not charged again. Judge costs are excluded from system costs.

## LoCoMo shared 50

| System | Correct / 50 | Valid outputs | Avg answer input | Avg context | Answer latency | Writing cost | Answer cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full history | 47/50 | 50/50 | 25,159 | 24,952 | 1.82s | $0.0000 | $0.2547 |
| Ours, no retrieval | 44/50 | 50/50 | 11,540 | 11,296 | 1.41s | $1.2823 | $0.1177 |
| Mem0, no retrieval | 42/50 | 50/50 | 21,405 | 21,168 | 2.01s | $10.0617 | $0.2171 |
| Mem0, retrieval (historical) | 42/50 | 50/50 | 10,663 | 10,427 | 2.86s | $10.0617 | $0.1096 |

Historical retrieval is a separate ablation, not part of the no-retrieval comparison. Failures count as non-correct in the full cohort denominator; token and latency means use calls with measured usage.

## LongMemEval second 50

| System | Correct / 50 | Valid outputs | Avg answer input | Avg context | Answer latency | Writing cost | Answer cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full history | 44/50 | 50/50 | 110,446 | 110,229 | 8.96s | $0.0000 | $1.1111 |
| Ours, no retrieval | 41/50 | 50/50 | 22,555 | 22,301 | 5.18s | $3.1003 | $0.2307 |
| Mem0, no retrieval | 45/50 | 50/50 | 30,794 | 30,547 | 2.49s | $6.8430 | $0.3141 |
| Mem0, retrieval (historical) | 46/50 | 49/50 | 11,519 | 11,273 | 3.58s | $6.7111 | $0.1188 |

Historical retrieval is a separate ablation, not part of the no-retrieval comparison. Failures count as non-correct in the full cohort denominator; token and latency means use calls with measured usage.

Failures for Mem0, retrieval (historical): `[{"question_id": "3b6f954b", "status": "extraction_api_error"}]`

New API spend across unique no-retrieval runs, including judges: **$1.1315**. Authorized ceiling: $15.

## Provenance

- LoCoMo shared 50, Full history: `20260908T192232760084Z_full-history_8cc5c91`
- LoCoMo shared 50, Ours, no retrieval: `20260908T190559396590Z_memory_6a360f8`
- LoCoMo shared 50, Mem0, no retrieval: `20260909T121234546331Z_mem0_1f69942`
- LoCoMo shared 50, Mem0, retrieval (historical): `20260908T222244440761Z_mem0_388f915`, `20260909T005041106821Z_mem0_e2ba6d1`
- LongMemEval second 50, Full history: `20260909T034523377052Z_full-history_707cb39`
- LongMemEval second 50, Ours, no retrieval: `20260909T034510538614Z_memory_707cb39`
- LongMemEval second 50, Mem0, no retrieval: `20260909T121243562166Z_mem0_1f69942`, `20260909T121716575119Z_mem0_1f69942`
- LongMemEval second 50, Mem0, retrieval (historical): `20260909T092328675957Z_mem0_e911e4d`

Writing costs cover the retained stores; discarded failed ingestion attempts are not included in those cohort figures. Latencies are observed call times from different runs and concurrency settings, not a controlled speed benchmark. LoCoMo and second-50 cohort reruns use concurrency 3; the one-question recovery uses 1; the first-50 extension uses 8.

The JSON companion contains usage details, model configuration, failures and judge-control outcomes. API billing for timed-out calls with no usage is unknown, not proven zero. Stored-memory token size does not include hidden reasoning; output usage does.
