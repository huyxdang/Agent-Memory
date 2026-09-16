# Results

Four memory systems on four fixed test splits, one judge, one answerer.
Final numbers as of 2026-09-15. Every cell has a frozen experiment file under
`experiment_specs/`; the log with predictions and outcomes for every run is
`docs/progress.md`.

Two tables below. Table 1 compares full history, Mem0 and the Luna extractor at
the original sample sizes and finds no significant difference anywhere. Table 2
compares the Luna extractor against Qwen 9B at samples two to ten times larger
and is where the statistically supported conclusions live.

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

Two tables, because the evidence is of two different kinds. The first compares
the three strong systems on the samples where all three ran. The second compares
the two extractors on much larger samples, and is the one with statistical
content.

Both systems in any comparison answer the same questions, so every test below is
paired: a sign test on the questions where the two disagree, with a 95% interval
on the difference. That is far more powerful than treating each score as an
independent measurement, and it is why the unpaired "noise band" framing used in
earlier versions of this document understated what the data can support.

### Table 1: full history, Mem0 and the Luna extractor

Original samples. Correct out of asked, or for BEAM passed out of asked.

| Split | n | Full history | Mem0 | Luna extractor | Significant pairs |
|---|---:|---:|---:|---:|---|
| LongMemEval | 96 | **84.4%** | **86.5%** | **85.4%** | none |
| LoCoMo | 50 | **94.0%** | **84.0%** | **88.0%** | none |
| BEAM 100K | 50 | **78.0%** | **72.0%** | **74.0%** | none |
| BEAM 500K | 40 | **65.0%** | **67.5%** | **60.0%** | none |

**Twelve pairwise comparisons, none significant.** Full history leads on three
splits and Mem0 on the fourth, and not one of those leads survives a paired test.
At these sample sizes the three systems are indistinguishable on accuracy.

That is a negative result for the article's central claim. Writing memory at read
time does not beat re-reading the conversation here; it matches it. What does
reproduce, and reproduces strongly, is the cost: memory gives the answerer a
twentieth to a fifth of the tokens for the same accuracy (see Tokens below).

LongMemEval runs on 96 rather than 100 because 30 rows across the old Luna and
full-history result files are truncated and will not parse. The published
100-question scores were 85, 88 and 85.

### Table 2: the Luna extractor against Qwen 9B

Larger samples, added 2026-09-15 on branch `expand-splits`. LoCoMo and both BEAM
splits were re-asked at two to ten times the original size with the same answerer,
judge and prompts; LongMemEval was left at 100 because its gap is far outside
anything more questions would change.

| Split | n | Luna extractor | Qwen 9B | Gap | p | 95% interval |
|---|---:|---:|---:|---:|---:|---|
| LongMemEval | 96 | **85.4%** | **60.4%** | −25.0 | **0.0000** | −35.4 to −14.6 |
| LoCoMo | 500 | **87.2%** | **85.6%** | −1.6 | 0.37 | −4.7 to +1.5 |
| BEAM 100K | 100 | **72.0%** | **60.0%** | −12.0 | **0.029** | −21.7 to −2.3 |
| BEAM 500K | 100 | **72.0%** | **67.0%** | −5.0 | 0.33 | −13.0 to +3.0 |

- **A 9B extractor matches a frontier one on LoCoMo.** At 500 questions the gap is
  1.6 points with an interval of −4.7 to +1.5: the first cell in this project
  where equivalence is supported rather than merely undetected. The original
  50-question sample admitted a 9-point gap in either direction.
- **It fails on LongMemEval and BEAM 100K.** Both intervals exclude zero. On
  LongMemEval the two disagree on 32 questions and Luna wins 28 of them.
- **BEAM 500K stays undecided.** Moving from two conversations to five narrowed
  it, but separating a 5-point gap from noise needs about 258 questions.
- **They disagree far more than the totals suggest.** On LoCoMo the two differ on
  62 of 500 questions while finishing 1.6 points apart. They are not making the
  same decisions; they are making different mistakes at a similar rate.

### How much each extractor writes

Mean per conversation, memory block only, excluding the system prompt and
instructions. "Atomic" lines record one fact as a key and value; the rest are
narrative summaries of a session.

| Split | Luna tokens | Luna atomic | Qwen tokens | Qwen atomic | Qwen size | Gap |
|---|---:|---:|---:|---:|---:|---:|
| LongMemEval | 22,047 | — | 8,474 | — | 38% | −25.0 |
| LoCoMo | 11,900 | 54% | 9,935 | 55% | 83% | −1.6 |
| BEAM 100K | 9,465 | 70% | 5,039 | 47% | 53% | −12.0 |
| BEAM 500K | 39,846 | 64% | 15,547 | 40% | 39% | −5.0 |

The split where the two write comparable memories is the split where they score
alike. Where Qwen under-writes it also shifts away from atomic lines toward
prose, so a specific value has to be recovered from inside a sentence rather than
looked up. That matches `docs/extractor-size-analysis.md`, where Qwen's worst
LongMemEval category by a wide margin was recalling what the assistant said,
4 of 16 against 12 of 16, exactly the content atomic lines capture.

BEAM 500K is the exception that stops this being a finding: Qwen writes the same
39% there as on LongMemEval but loses 5 points rather than 25. Size alone does not
predict the damage. The cheap test is an extraction prompt that demands atomic
facts, run on BEAM 100K where a 12-point deficit is established and 66 questions
would suffice to see it move.

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

Percentages are relative to full history on the same split. This is the claim
that reproduces: the same accuracy as reading the whole conversation, for a
twentieth to a fifth of the tokens the answerer has to read.

### How the memory grows, and what that does not buy

A per-question mean hides the shape, because it samples curves of different
kinds at one point. Measured properly, from the 81 per-session snapshots of the
longest BEAM 500K conversation (622k tokens of raw chat), the memory grows
**linearly** with the conversation:

| After sessions | Memory | Raw chat so far | Memory share |
|---:|---:|---:|---:|
| 1 | 298 | 7,678 | 3.9% |
| 10 | 4,820 | 76,778 | 6.3% |
| 20 | 10,748 | 153,555 | 7.0% |
| 40 | 21,415 | 307,110 | 7.0% |
| 60 | 32,958 | 460,665 | 7.2% |
| 81 | 43,811 | 621,898 | 7.0% |

After the first ten sessions the share settles at 7 percent and stays flat to the
end.

**Reference statement: memory does not grow exponentially with sessions. It grows
linearly, and each session adds a roughly constant amount.** Across the 80
session-to-session increments of this conversation the memory gained a mean of
544 tokens and a median of 556, and the rate does not accelerate: the first
quarter of the conversation averaged 547 tokens per session and the last quarter
511. Banded, it is flat throughout:

| Sessions | Tokens added per session |
|---|---:|
| 1-10 | 482 |
| 11-20 | 593 |
| 21-40 | 533 |
| 41-60 | 577 |
| 61-81 | 517 |

This is the property that makes write-time memory viable at all. The cost of
remembering one more session is bounded and does not depend on how much has
already been remembered, so a long-running conversation does not compound. It is
also the precise limit of the approach: bounded per-session growth still means
unbounded total growth.

**Write-time memory therefore buys a constant factor, roughly 14x here, not better
scaling.** That is a real saving and it is what the token table above reports,
but it does not solve long context asymptotically: extrapolate this conversation
to 10M tokens and the memory is 700k, still past most windows.

The factor does improve as conversations lengthen, then hits a floor:

| Split | Conversation | Luna memory | Share |
|---|---:|---:|---:|
| LoCoMo | 25,159 | 11,900 | 47% |
| LongMemEval | 110,416 | 22,047 | 20% |
| BEAM 100K | 127,306 | 9,465 | 7.4% |
| BEAM 500K | 552,766 | 39,846 | 7.2% |

Qwen 9B sits near 2.8 percent on BEAM 500K: the same compression pushed further,
and the same behaviour that costs it 25 points on LongMemEval and 12 on BEAM 100K.

Two measurement notes, both of which caught us out once:

- **Do not use extraction input as a proxy for memory size.** It includes a fixed
  prompt and the current session, so it flattens for reasons unrelated to the
  memory and makes linear growth look sublinear.
- **The answerer's input is the headline metric, not total tokens.** Memory exists
  to cut the context a query carries, which is what drives latency and window
  limits; extraction is amortised infrastructure off the query path. Total cost
  is a separate question and changes the answer in exactly one case: ask a
  conversation a single question and writing a memory first costs more than
  reading it. LongMemEval is the only split here where that bites, at roughly six
  times full history once extraction is counted, because every question gets its
  own haystack and nothing amortises.

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

- **Writing memory does not beat reading the conversation. It ties it, far
  cheaper.** Across twelve pairwise comparisons in Table 1, not one is
  significant. Full history leads on three splits and Mem0 on the fourth, and
  none of those leads survives a paired test. The accuracy claim does not
  reproduce; the cost claim reproduces strongly, at a twentieth to a fifth of the
  answer tokens.
- **A 9B extractor matches a frontier one on conversational memory and fails on
  long documents.** LoCoMo at 500 questions is a supported equivalence, 1.6
  points with an interval of −4.7 to +1.5. LongMemEval and BEAM 100K are real
  deficits, 25 and 12 points, both excluding zero. BEAM 500K is still undecided.
  An earlier version of this document claimed a match on three of four splits;
  that rested on samples too small to distinguish equivalence from ignorance.
- **The 9B's failure is that it writes too little, and writes it as prose.** It
  produces 38 to 53 percent of Luna's memory on the splits it loses and 83
  percent on the one it matches, and where it under-writes it also abandons
  atomic fact lines, 40 to 47 percent against Luna's 64 to 70. BEAM 500K breaks
  the pattern, so treat this as the leading hypothesis rather than a finding.
- **Its worst category is recalling what the assistant said**, 4 of 16 on
  LongMemEval against Luna's 12 of 16, which is precisely the content atomic
  lines capture. That is the target for the extractor work continuing on the
  `extractor-fine-tune` branch, and the cheap first test is a prompt change
  rather than training.
- **Mem0 with a shared store holds up.** One store per conversation with every
  memory given to the answerer scores within noise of the Luna extractor
  everywhere, at 13 to 28 percent of the full-history tokens.

## Caveats

- Table 1 is at the original sample sizes, 40 to 96 questions. Its comparisons
  are not significant, which means indistinguishable at this power, not equal.
  Separating the 5-point spread seen there would take several hundred questions.
- LongMemEval runs on 96 of 100 because 30 rows in the old Luna and full-history
  result files are truncated and will not parse.
- The Qwen 9B BEAM run in Table 1's era mixed two extraction output caps (2,048
  tokens, then the full serving window) after an early stop; retained updates are
  valid and nothing was truncated silently.
- The LoCoMo and BEAM question sets have been inspected repeatedly across
  iterations and are historical comparisons, not fresh held-out evidence.
- Full history and Mem0 were not run at Table 2's larger sizes. Estimated at $15
  and $25 respectively from measured per-question costs.
- Prompt caching does not help the answerer: measured under 5 percent of answer
  input on LoCoMo and zero on BEAM, with or without a routing key. Budget future
  runs at full input price.

## Provenance

Table 1, original samples:

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

Table 2, larger samples:

- Luna extractor: `locomo-500-luna-001`, `beam-100k-100-luna-002`,
  `beam-500k-100-luna-002`; LongMemEval reuses the runs above.
- Qwen 9B: `qwen9b-longmemeval-100-002`, `locomo-500-qwen9b-001`,
  `beam-100k-100-qwen9b-002`, `beam-500k-100-qwen9b-001`.
- Selections `question_ids_locomo_500.json`, `question_ids_beam_100k_100.json`
  and `question_ids_beam_500k_100.json`, each containing the frozen smaller
  selection it extends. BEAM 500K adds chats 11, 19 and 30 to the original 1 and
  13, converted from the published parquet by `tools/convert_beam_500k.py`.
- A partial full-history run on the five BEAM 500K chats stopped at 54 of 100
  questions when OpenAI credits ran out: `beam-500k-100-full-history-001`, 68.5
  percent, against 63.0 for Luna and 59.3 for Qwen on the same 54. No pair is
  significant. Reports for every completed run are under `reports/`.
