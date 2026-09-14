# Qwen 9B extractor LoRA on Adaption: first result

Overnight run of 2026-09-15 on the `extractor-fine-tune` branch. One LoRA
adapter for `Qwen/Qwen3.5-9B` trained on Adaption's AutoScientist from the
repo's own teacher traces plus a small invented set, then benchmarked on
LoCoMo 50 against the base 9B extractor.

## Data

| Source | Rows | Notes |
|---|---:|---|
| BEAM teacher traces (Luna, training split) | 106 | of 564, those fitting the cap |
| LongMemEval repaired training copy | 1,212 | of 2,428, those fitting the cap |
| Invented sessions, Luna-labelled | 98 | Adaption Invent probe of 100, 2 unparsable |
| Total | 1,416 | sequence cap 16,384 tokens, 13.1M tokens |

Rows are the extractor's exact inference input rendered through the Qwen chat
template with thinking off, as the prompt column, and the JSON memory update as
the completion. A first attempt on the uncapped 2,992-row set (57.6M tokens,
sequences to 65k) failed on the platform after 47 minutes with no error
reported; capping at 16k fixed it. A second run with plain-text prompts also
succeeded, so the prompt format was not the problem.

Invented sessions came from `datasets.invent` with a steering prompt asking
for assistant-heavy everyday conversations in our session format, 0.1 credit
per row. Their completions were discarded and the sessions labelled by the
Luna extractor with empty prior memory, so targets match our schema.

## Training

AutoScientist run `e8131921`: LoRA rank 16, alpha 32, on q/k/v/o and
gate/up/down projections, one epoch, completion-only loss, no pool
augmentation, one iteration. 21 optimizer steps; training loss 0.60 to 0.35;
eval loss 0.353; Adaption win rate 0.61. Adapter published privately as
`huyxdang/qwen35-9b-extractor-lora-20260915`, revision `1ce16317`, and
served by the Modal worker through vLLM's LoRA path.

## LoCoMo 50

Same 50 questions, 10 histories, answerer and judge as every LoCoMo cell in
`docs/results.md`. Base 9B: 44 of 50.

| Attempt | Timeout | Histories complete | Graded | Fine-tuned on graded | Base on the same questions | With blocked as wrong |
|---|---:|---:|---:|---:|---:|---:|
| run 001 | 600 s | 8 of 10 | 40 | 34 | 36 | 34 of 50 |
| run 002 | 1,800 s | 8 of 10 | 40 | 36 | 36 | 36 of 50 |
| run 003 | 1,800 s, 8k cap, seed retries | killed at 4 min | 0 | | | |

Run 002 paired: 34 both right, 2 fine-tuned only, 10 base only, of which all
10 are questions on the two histories the adapter failed to extract. By
category on the graded questions: single-hop 16/16 against 15, multi-hop
10/11 against 11, temporal 8/10 against 9, open-domain 2/3 against 3.
Memory size is unchanged: 358 lines and 11.8k tokens per history against
355 and 11.7k for the base; 381 output tokens per update against 390.

## What it says

- **No accuracy change on the questions it could answer.** 36 against 36 on
  run 002. The training data contained no LoCoMo, and no transfer gain
  shows; nothing was harmed either.
- **Worse robustness.** In each attempt the adapter fell into a runaway
  generation on 2 of 10 histories: a 114k-character stream of atomic pairs
  on one, a stall on another. The base looped once in its own first attempt
  and completed on the retry. As a drop-in, the adapter is worse until the
  loop is handled. The worker now retries invalid output with fresh seeds
  and the spec caps extraction output at 8,192 tokens so a loop fails fast;
  run 003 was to measure that and did not get to.
- **Run 003 died with the Modal workspace's spend limit**, which also killed
  run 002's sandbox after its eight histories were safe. Nothing further can
  run on that workspace until the limit is raised.

## Caveats

- Eight of ten histories per attempt; the union of the two attempts covers
  nine. The two attempts are not one run.
- 98 invented rows out of 1,416 cannot be separated from the teacher data.
- One epoch, 21 steps, rank 16, platform-chosen learning rate. Nothing was
  tuned.
- LongMemEval is off limits for this adapter: its training rows share
  histories with the LongMemEval test set.

## Provenance

Datasets `b4d70ae7` (uncapped, failed run `7b81a7ad`), `76ded297`
(templated 16k, run `e8131921`), `b8b0a6c4` (plain 16k, run `5cdd0fa5`,
not evaluated). Invent probe `865b1a78`. Runs
`locomo-qwen-9b-finetuned-001`, `-002`, `-003` under `runs/`; reports under
`reports/`. Specs `locomo-qwen-9b-finetuned-final50.json`,
`-t1800-final50.json`, `-cap8k-final50.json`. Base 9B record:
`work/qwen_locomo_sampling_completion`.
