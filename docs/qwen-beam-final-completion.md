# Qwen BEAM completion

Completed 2026-09-11. All original 90 questions are accounted for exactly once:
90 valid, zero failed, zero missing, zero unexpected. Extraction completed all
203 updates across seven histories; GPU termination confirmed before this
answer-only continuation. All 354 saved API-call records are complete, including
the three archived truncated responses. No uncertain requests were replayed.

| BEAM tier | Qwen extractor accuracy | Historical Luna extractor accuracy | Qwen mean answer-input tokens | Luna mean answer-input tokens |
|---|---:|---:|---:|---:|
| 100K, 50 questions | 34/50 (68%) | 37/50 (74%) | 6,772 | 9,716 |
| 500K, 40 questions | 24/40 (60%) | 24/40 (60%) | 22,098 | 38,102 |
| Combined, 90 questions | 58/90 (64.4%) | 61/90 (67.8%) | — | — |

Both systems use the Luna answerer and Mem0 BEAM judging. The Qwen comparison is
observational: Luna historically rebuilt memories per question; Qwen shares each
history's memory. Qwen also used explicit output-limit continuations: 107 valid
updates retained from the 2,048-token run, later extraction permitted all remaining
serving context; 47 successful answers retained at their original 1,024-token cap,
three truncated answers and 40 pending questions ran with a 128,000-token answer
allowance. Do not describe this as one clean, constant-configuration run or a
controlled extractor-only causal comparison.

The three replacement answers finished normally at 1,694, 1,923 and 1,878 output
tokens. Their prior truncated outputs and costs remain archived. The new allowance
matches [Luna's documented maximum](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
not a requirement to generate that much text. Prompts and judge settings did not
change. No GPU or memory-building work was repeated for this answer-only finish.

The final answer-only invocation took 370.739 seconds (6m 10.7s), not the total
experiment wall time. Its additional conservative API accounting is $1.476545;
the cumulative answer/judge accounting in the final directory is $2.373199,
including inherited and archived calls. This includes internal judging spend;
it is neither reported system-only cost nor a verified provider invoice.

Local results: `work/qwen_beam_answers_max/{summary,comparison,configuration}.json`,
`comparison.md`, and per-question results/API calls. The source memories and GPU
lineage remain in `work/qwen_beam_vllm_max/` and `work/qwen_beam_vllm/`.

Verification: 79 tests passed before launch; final on-disk checks verified 90
unique successful question IDs, completed call statuses, retained failed-attempt
accounting, replacement finish reasons and confirmed GPU shutdown.

The app reported the prior progress automation no longer exists when an update
was attempted. This completion was monitored directly; no replacement automation
was created.
