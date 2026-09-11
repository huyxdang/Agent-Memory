# Qwen cross-benchmark final run

Authorized 2026-09-11: LoCoMo first, then LongMemEval, each with a full-history
smoke before its final set. Untuned Qwen/Qwen3.5-9B extractor, one L40S 48GB,
vLLM concurrency eight, existing Luna answerer and GPT-5 benchmark-specific judge.

| Stage | Histories | Questions | Maximum new Modal reservation |
| --- | ---: | ---: | ---: |
| LoCoMo pilot | First 2 complete histories | 13 | $2 |
| LoCoMo final | All original 10, reuse pilot memories | 50 | $4 |
| LongMemEval pilot | First 2 complete histories | 2 | $2 |
| LongMemEval final | All original 100, reuse pilot memories | 100 | Up to $8, clamped to remaining budget |

These are reservations, not expected costs. Every launch checks the same original
$30 total Modal ceiling. Historical baseline accounting is $9.913628; reserve
another $6 conservatively for both earlier pilots and sizing, and leave a $0.50
sequence margin. Existing $20 answering/judging allocation is shared across runs,
deduplicating copied API response IDs when counting prior spend.

Modal's live monthly billing summary returned $5.58 metered usage, covered by
credits, at preflight. This may lag and is not substituted for the conservative
local reservations. No purchases, top-ups or total-cap increase are authorized.

The full-history pilots differ from the earlier partial-session throughput
smokes. Pilot histories are complete, so their selected benchmark questions can
be answered and judged meaningfully. They use the first histories in the frozen
selection order, not score-selected histories. A two-history pilot can use two
concurrent requests, not all eight configured slots.

`run_qwen_final_sequence.py` runs the stages in order and stops on missing or
failed results, unknown API outcomes, unconfirmed GPU shutdown, or insufficient
budget. A low benchmark score is not a failed smoke and does not trigger retries.
It never relaunches an interrupted GPU job automatically. Checkpoints remain
available for explicit reconciliation/resume if the budget or process expires.

The sequence status is `work/qwen_final_sequence/status.json`, with its local
controller log in `runner.log`. Each stage owns its configuration, cloud ledger,
memories, API calls and results under `work/qwen_<benchmark>_<pilot|final>_c8`.
Pilot memory imports validate the source histories and extraction settings.
Pilot API calls remain in their source directories; final-stage questions are
answered again against the reused memories, and both sets of API calls are charged.
Report this as a staged continuation, not a fresh uninterrupted speed benchmark.

Initial LoCoMo sandbox: `sb-SiP6eI0rKbkbklPbW6Hj5d`.
First live check confirmed NVIDIA L40S, 46,068 MiB reported total device memory,
37,585 MiB allocated, and two running requests. Startup included compilation.

Sources: [Modal GPU selection](https://modal.com/docs/guide/gpu),
[resource pricing](https://modal.com/pricing),
[billing summary](https://modal.com/docs/sdk/py/latest/Workspace).
