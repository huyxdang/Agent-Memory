# Results

Four memory systems on four fixed test splits, one judge, one answerer.
Final numbers as of 2026-09-14. Every cell has a frozen experiment file under
`experiment_specs/` named `<split>-<system>.json`; the log with predictions
and outcomes for every run is `docs/progress.md`.

## Setup

- **Answerer**: GPT-5.6 Luna, reasoning off, for every system.
- **Judges**: Mem0's own prompts, vendored verbatim under `third_party/mem0/`.
  LongMemEval yes/no; LoCoMo CORRECT/WRONG; BEAM one score per rubric
  nugget at 0, 0.5, or 1, a question passing at 0.5 or more.
- **Systems**:
  - *Luna extractor*: GPT-5.6 Luna at low reasoning writes the memory, one
    session at a time, appending dated narrative and atomic lines under a
    fixed JSON schema. The answerer reads the whole memory; nothing is
    retrieved per question.
  - *Qwen 9B extractor*: the same memory format written by Qwen3.5-9B
    (revision `c2022362`) served by vLLM 0.21 on one L40S, structured JSON
    output, sampling as pinned in the spec.
  - *Mem0*: Mem0 OSS 2.0.20 with GPT-5.6 Luna as its model, one store per
    conversation, four messages per add; every stored memory goes to the
    answerer, oldest first, with no search.
  - *Full history*: the answerer reads the entire conversation.
- **Splits**: LongMemEval 100 questions, 8 or 9 per type across all six
  types, one 110k-token history each; LoCoMo 50 questions over 10
  conversations of about 21k tokens; BEAM 100K, 50 questions over 5 chats;
  BEAM 500K, 40 questions over 2 chats. Selection files are in the repo root.
- A history whose extraction fails counts every question on it as wrong.

## Accuracy

Correct out of asked, or for BEAM passed out of asked.

| Split | Luna extractor | Mem0 | Full history | Qwen 9B |
|---|---:|---:|---:|---:|
| LongMemEval, 100 | **85%** · 85/100 | **88%** · 88/100 | **85%** · 85/100 | **61%** · 61/100 † |
| LoCoMo, 50 | **88%** · 44/50 | **84%** · 42/50 | **94%** · 47/50 | **88%** · 44/50 |
| BEAM 100K, 50 | **74%** · 37/50 | **72%** · 36/50 | **78%** · 39/50 | **68%** · 34/50 |
| BEAM 500K, 40 | **60%** · 24/40 | **67.5%** · 27/40 | **65%** · 26/40 | **60%** · 24/40 |

† 61 correct of 97 graded; 3 histories were lost to a structured-output
whitespace loop during extraction and count as wrong.

Noise at these sizes is about 4.5 points on 100 questions, 6.5 on 50, and
7.5 on 40. BEAM mean nugget scores: Luna 0.656 and 0.596, Mem0 0.673 and
0.615, full history 0.685 and 0.617, at 100K and 500K respectively.

## Larger samples: Qwen 9B against the Luna extractor

Added 2026-09-15 on branch `expand-splits`. The table above rests on 50 and 40
question samples, small enough that its central claim, that a 9B extractor
matches a frontier one, could not be distinguished from no evidence. These cells
re-ask three of the four splits at two to ten times the size, with the same
answerer, judge and prompts, and only the two systems the claim is about. They
are a different question set and are reported here rather than folded into the
table above.

| Split | Questions | Conversations | Luna | Qwen 9B |
|---|---:|---:|---:|---:|
| LoCoMo | 500 | 10 | **87.2%** · 436/500 | **85.6%** · 428/500 |
| BEAM 100K | 100 | 5 | **72.0%** · 72/100 | **60.0%** · 60/100 |
| BEAM 500K | 100 | 5 | **72.0%** · 72/100 | **67.0%** · 67/100 |

Both systems answer the same questions, so the comparison is paired. Totals alone
understate how differently they behave, and a paired test is far more powerful
than the unpaired noise bands quoted above.

| Split | Both right | Luna only | Qwen only | Both wrong | Sign test | 95% interval on the gap |
|---|---:|---:|---:|---:|---:|---|
| LoCoMo, 500 | 401 | 35 | 27 | 37 | p = 0.37 | −4.7 to +1.5 points |
| BEAM 100K, 100 | 53 | 19 | 7 | 21 | **p = 0.029** | −21.7 to −2.3 points |
| BEAM 500K, 100 | 61 | 11 | 6 | 22 | p = 0.33 | −13.0 to +3.0 points |

- **The claim holds on LoCoMo and fails on BEAM 100K.** At 500 questions the
  LoCoMo gap is 1.6 points with an interval of −4.7 to +1.5: the first cell in
  this project where "no meaningful difference" is a supported conclusion rather
  than an absence of evidence. The 50-question sample admitted a 9-point gap.
- **BEAM 100K is a real deficit**, not the 6-point wobble the 50-question sample
  showed. The interval excludes zero.
- **BEAM 500K stays undecided.** Going from two conversations to five narrowed it,
  but 100 questions over 5 chats cannot separate a 5-point gap from noise.
- **They disagree far more than the totals suggest.** On LoCoMo the two differ on
  62 of 500 questions while landing 1.6 points apart. They are not making the same
  decisions; they are making different mistakes at a similar rate.

### How much each extractor writes

Mean per conversation, memory block only, excluding the system prompt and
instructions. "Atomic" lines record a single fact as a key and value; the rest are
narrative summaries of a session.

| Split | Luna lines | Luna tokens | Luna atomic | Qwen lines | Qwen tokens | Qwen atomic |
|---|---:|---:|---:|---:|---:|---:|
| LoCoMo | 280 | 11,900 | 54% | 281 | 9,935 | 55% |
| BEAM 100K | 265 | 9,465 | 70% | 158 | 5,039 | 47% |
| BEAM 500K | 961 | 39,846 | 64% | 478 | 15,547 | 40% |

The split where the two write comparable memories is the split where they score
alike. Where Qwen under-writes it also shifts away from atomic lines toward
prose, so specific values have to be recovered from inside a sentence rather than
looked up. That matches the LongMemEval finding in `docs/extractor-size-analysis.md`,
where Qwen's worst category by a wide margin was recalling what the assistant
said, 4 of 16 against 12 of 16, exactly the content atomic lines capture. With
three splits and one significant gap this is a hypothesis worth testing, not a
finding: the cheap test is an extraction prompt that asks explicitly for atomic
facts, before any fine-tuning.

### Provenance

Runs `locomo-500-{luna,qwen9b}-001`, `beam-100k-100-luna-002`,
`beam-100k-100-qwen9b-002`, `beam-500k-100-luna-002`, `beam-500k-100-qwen9b-001`;
reports under `reports/`. Selections `question_ids_locomo_500.json`,
`question_ids_beam_100k_100.json`, `question_ids_beam_500k_100.json`, each
containing the frozen smaller selection it extends. BEAM 500K adds chats 11, 19
and 30 to the original 1 and 13, converted from the published parquet by
`tools/convert_beam_500k.py`. Mem0 and full history were not run at these sizes;
their columns above remain at the original sample.

## Tokens

Mean tokens the answerer reads per question, as reported by the API. For the
three memory systems this is the size of the memory plus the question and
instructions; for full history it is the conversation.

| Split | Luna extractor | Mem0 | Full history | Qwen 9B |
|---|---:|---:|---:|---:|
| LongMemEval, 100 | 22,300 (20%) | 31,167 (28%) | 110,432 | 8,726 (8%) |
| LoCoMo, 50 | 11,540 (46%) | 21,405 (85%) | 25,159 | 12,131 (48%) |
| BEAM 100K, 50 | 9,716 (8%) | 17,408 (14%) | 127,306 | 6,772 (5%) |
| BEAM 500K, 40 | 38,102 (7%) | 70,530 (13%) | 552,766 | 22,098 (4%) |

Percentages are relative to full history on the same split.

## By question type

LongMemEval, 100, correct per type:

| Type | Luna extractor | Full history | Qwen 9B |
|---|---:|---:|---:|
| single-session-user | 16/16 | 16/16 | 11/16 |
| single-session-assistant | 12/16 | 16/16 | 4/16 |
| single-session-preference | 15/18 | 16/18 | 13/18 |
| multi-session | 12/16 | 10/16 | 10/16 |
| temporal-reasoning | 14/16 | 11/16 | 12/16 |
| knowledge-update | 16/18 | 16/18 | 11/18 |

LoCoMo, 50, correct per category:

| Category | Luna extractor | Full history | Qwen 9B |
|---|---:|---:|---:|
| single-hop | 17/20 | 20/20 | 18/20 |
| multi-hop | 12/12 | 12/12 | 12/12 |
| temporal | 11/12 | 10/12 | 10/12 |
| open-domain | 4/6 | 5/6 | 4/6 |

BEAM, 90 questions across both scales, passed per ability (9 each):

| Ability | Luna extractor | Mem0 | Qwen 9B |
|---|---:|---:|---:|
| preference following | 9 | 9 | 8 |
| instruction following | 8 | 8 | 8 |
| summarization | 5 | 8 | 7 |
| multi-session reasoning | 6 | 7 | 7 |
| information extraction | 6 | 7 | 5 |
| knowledge update | 6 | 7 | 5 |
| event ordering | 7 | 6 | 4 |
| temporal reasoning | 6 | 6 | 6 |
| contradiction resolution | 4 | 3 | 4 |
| abstention | 4 | 2 | 4 |

## What the numbers say

- **A 9B extractor matches a frontier one on three of four splits.** On
  LoCoMo the two extractors score 44 each and miss almost the same
  questions: 42 both right, 2 each right alone, 4 both wrong. On BEAM the
  totals are 61 and 58 of 90, with Qwen's memories 40 percent smaller. The
  design leaves the extractor a transcription job and moves reasoning to
  the answerer, so a model that reliably writes down dated facts is enough.
  The paired outcomes are in `docs/extractor-size-analysis.md`.
- **Where the 9B model falls short is specific.** On LongMemEval it loses
  half its gap to Luna on single-session-assistant questions, 4 of 16
  against 12 of 16: recording what the assistant wrote, not what the user
  said. That is the target for extractor fine-tuning, which continues on
  the `extractor-fine-tune` branch.
- **Memory is a small fraction of the conversation.** The answerer reads 4
  to 8 percent of the full history on BEAM and LongMemEval with the Qwen
  extractor, 7 to 20 percent with Luna, at accuracy within noise of full
  history on LoCoMo and BEAM and, for Luna, on LongMemEval as well.
- **Mem0 with a shared store holds up.** One store per conversation with
  every memory supplied to the answerer scores within noise of the Luna
  extractor everywhere and edges full history on BEAM 500K, at 13 to 28
  percent of the full-history tokens.
- **Full history is still the strongest answerer at these lengths.** It
  leads on LoCoMo and BEAM 100K, where the whole conversation fits easily
  in the answerer's window. At 500K all systems drop and the spread is
  within noise.

## Caveats

- The Qwen 9B BEAM run mixed two extraction output caps (2,048 tokens, then
  the full serving window) after an early stop; the retained updates are
  valid and no output was truncated silently.
- The LoCoMo and BEAM question sets have been inspected repeatedly across
  iterations and are historical comparisons, not fresh held-out evidence.
- The 500K sample is two chats, so chat-level effects are not averaged out.

## Provenance

- Luna extractor: LongMemEval `20260908T182110999548Z_memory_b5424ef` and
  `20260909T034510538614Z_memory_707cb39`; LoCoMo
  `20260908T190559396590Z_memory_6a360f8`; BEAM
  `20260908T191319329343Z_memory_07ccfb9` and
  `20260909T064305432208Z_memory_e66fa47`.
- Mem0: LongMemEval `20260909T135940974756Z_mem0_1f69942` and
  `20260909T121243562166Z_mem0_1f69942`; LoCoMo
  `20260909T121234546331Z_mem0_1f69942`; BEAM `beam-mem0-90-002`.
- Full history: LongMemEval `20260908T192233799242Z_full-history_8cc5c91`
  and `20260909T034523377052Z_full-history_707cb39`; LoCoMo
  `20260908T192232760084Z_full-history_8cc5c91`; BEAM
  `20260908T190419451554Z_full-history_b9789ba` and
  `20260909T064208621884Z_full-history_e66fa47`.
- Qwen 9B: LongMemEval `qwen9b-longmemeval-100-002`; LoCoMo
  `work/qwen_locomo_sampling_completion`; BEAM `work/qwen_beam_answers_max`.
