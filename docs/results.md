# Results against the article

Reproduction of Adaption Labs, "Better Agent Memory Starts Before Retrieval"
(August 13, 2026). Final numbers as of 2026-09-09. Every run is in
`runs/index.jsonl`; the experiment log with predictions and outcomes is
`docs/progress.md`.

## Setup

- Answerer: GPT-5.6 Luna, reasoning off, the same model for every system.
- Judges: Mem0's own prompts, vendored verbatim under `third_party/mem0/`.
  LongMemEval yes/no, LoCoMo CORRECT/WRONG with partial credit, BEAM
  per-rubric-nugget 0/0.5/1 with a pass at 0.5.
- Extractor for our memory: GPT-5.6 Luna, low reasoning; also Mem0's LLM.
- Both answerers use the same three reasoning rules (the "v2" prompt).
  Earlier "v1" runs with the one-line prompt are kept in the log.
- Samples: LongMemEval 100 questions, 8 or 9 per type across all six
  types; LoCoMo 154 questions, 10 percent of the scored set in the
  benchmark's own proportions; BEAM 50 questions at the 100K scale, ten
  ability types across five chats. Mem0 OSS ran on the first 50 of
  LongMemEval and LoCoMo only.
- "Reweighted" rescales per-type accuracy to each benchmark's real
  category proportions so numbers are comparable in shape to published
  ones.

## Accuracy

| Benchmark | Article: theirs | Article: Mem0 OSS | Article: full history | Ours: memory | Ours: Mem0 OSS (50 q) | Ours: full history |
|---|---|---|---|---|---|---|
| LongMemEval, reweighted | 90.6 | 71.6 | 60.6 | **84.5** | 78.6 | 79.3 |
| LoCoMo, reweighted | 88.2 | 82.2 | not run | 89.1 | 88.2 | **91.0** |
| BEAM, pass rate | 61.3 (1M+) | 39.7 | not run | 74.0 (100K) | not run | **78.0** (100K) |

Raw counts: LongMemEval memory 85 of 100, full history 85 of 100;
LoCoMo memory 137 of 154, full history 140 of 154; BEAM memory 37 of 50
pass (mean nugget score 0.656), full history 39 of 50 (0.685).

Per type where it matters:

| LongMemEval, 100 | Full history | Memory |
|---|---|---|
| single-session-user | 16/16 | 16/16 |
| single-session-assistant | 16/16 | 12/16 |
| single-session-preference | 16/18 | 15/18 |
| multi-session | 10/16 | 12/16 |
| temporal-reasoning | 11/16 | 14/16 |
| knowledge-update | 16/18 | 16/18 |

| LoCoMo, 154 | Full history | Memory |
|---|---|---|
| single-hop | 79/84 | 75/84 |
| temporal | 28/32 | 31/32 |
| multi-hop | 28/28 | 27/28 |
| open-domain | 5/10 | 4/10 |

## Tokens, latency, cost

| Sample | Answer tokens, full history | Answer tokens, memory | Answer latency mean, p95 change |
|---|---|---|---|
| LongMemEval 100 | 11.0M | 2.2M (20%) | −37%, −34% |
| LoCoMo 154 | 3.9M | 1.7M (45%) | −36%, −46% |
| BEAM 100K 50 | 6.4M | 0.47M (7%) | −27%, −3% |

The article reports mean latency down 45 percent and p95 down 67 percent
on long conversations; ours are smaller because its figure is for BEAM at
around a million tokens, ten times our scale.

Memory writing costs about $0.07 per LongMemEval question at 68 to 78
percent prompt-cache reads; Mem0 OSS about $0.23 because it writes one
call per message pair. Total spend for the whole project: $47.39 over 57
runs.

## What reproduced

- The direction on LongMemEval, and the category pattern. Memory beats
  full history on multi-session and temporal questions, which are 53
  percent of the real benchmark, and trails on single-session-assistant
  questions, 11 percent. Reweighted lead 84.5 to 79.3 at a fifth of the
  answer tokens. The raw 100-question score is a tie; the first 50's
  three-question raw lead did not survive doubling the sample.
- Memory over Mem0 OSS on LongMemEval, 84.5 to 78.6 reweighted. Mem0
  lands where full history does, with perfect assistant recall and weak
  multi-session.
- LoCoMo memory against Mem0 to the decimal: 89.1 and 88.2 reweighted
  against the article's 88.2 and 82.2.
- Fewer answer tokens and lower latency everywhere, smaller than claimed.

## What did not

- The size of the LongMemEval gap. The article's baseline scored 60.6;
  ours scored 68 with the plain prompt and 79.3 reweighted once given the
  same reasoning rules as memory. A 1M-context model that reads 110k
  tokens well leaves memory less to fix.
- Full history beats both memory systems on LoCoMo and BEAM at the
  scales we ran, where the whole conversation fits comfortably. The
  article never compares against full history there and says it only
  used it where the history fits; the BEAM claim is about the 1M and 10M
  scales, which we did not run.

## Caveats

- Noise: about 4.5 points on 100 questions, 3.5 on 154, 6.5 on 50.
- Eight of memory's original thirteen-question LongMemEval lead came
  from answer-side prompt rules; the baseline got the same rules before
  the final numbers, which is why its score rose from 68 to 82 percent.
- The article withholds prompts, schemas, and model names. Our Mem0 OSS
  is version 2.0.20, add-only, with the session date passed as metadata
  because the OSS SDK rejects the platform timestamp parameter.
- BEAM at 100K only; Mem0 on BEAM not run by decision.
