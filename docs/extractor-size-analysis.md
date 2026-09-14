# Why a 9B extractor matches a frontier one, and why a 4B one does not

Written 2026-09-14. Paired analysis of the recorded runs; no new model calls
were made for this document. Where a run was still grading at the time of
writing it is marked preliminary.

## Context

The memory system in this repo separates two jobs. A **write-time extractor**
reads one conversation session at a time, together with the memory written so
far, and appends dated facts under a fixed JSON schema (narrative lines plus
atomic key/value lines). An **answerer** later receives the entire memory for
that history, with no retrieval step, and answers the question. The answerer
is GPT-5.6 Luna with reasoning off in every run, and the judges are Mem0's
vendored prompts, so the only thing that changes across the columns below is
the extractor. Three extractors have been evaluated on the same frozen
question sets:

| Extractor | Size | Serving | Decoding |
|---|---|---|---|
| GPT-5.6 Luna, low reasoning | frontier, hosted | OpenAI API | provider default |
| Qwen3.5-9B (`c2022362`) | 9B, open weights | vLLM 0.21 on one L40S, BF16, 65,536-token window | sampling: temperature 0.7, top-p 0.8, top-k 20, presence penalty 1.5; structured JSON output |
| Gemma 3 4B it (`093f9f38`) | 4B, open weights | vLLM 0.21 on one L4, BF16, 65,536-token window | greedy, frequency penalty 0.3; structured JSON output; prompt blocks merged into one user message because the chat template rejects consecutive user turns |

Benchmarks and sizes: LoCoMo 50 questions over 10 histories of about 21k
tokens; BEAM 100K, 50 questions over 5 chats of 145k to 190k tokens; BEAM
500K, 40 questions over 2 chats of 520k and 750k tokens; LongMemEval 100
questions, one 110k-token history each, about 48 sessions per history.
Noise at these sizes is roughly 6.5 points on 50 questions, 7.5 on 40, and
4.5 on 100.

## Results

Accuracy, or BEAM pass rate (a question passes at a rubric score of 0.5 or
more). Blocked questions count as wrong, the repo's convention.

| Benchmark | Full history | Luna extractor | Qwen 9B | Gemma 4B | Mem0 OSS, no retrieval |
|---|---:|---:|---:|---:|---:|
| LoCoMo, 50 | 47 (94%) | 44 (88%) | 44 (88%) | 32 (64%)* | 42 (84%) |
| BEAM 100K, 50 | 39 (78%) | 37 (74%) | 34 (68%) | 20 (40%) | 36 (72%) |
| BEAM 500K, 40 | 26 (65%) | 24 (60%) | 24 (60%) | 13 (32.5%) | 27 (67.5%) |
| LongMemEval, 100 | 85 (85%) | 85 (85%) | 61 (61%)† | not run | 88 (88%) |

\* The Gemma LoCoMo run in this repo had 34 of 50 questions blocked by
extraction failures; the cell mixes failed extraction with memory quality.

† 61 correct of 97 graded; 3 histories were lost to the structured-output
whitespace loop and count as wrong. Per type against the Luna extractor:
knowledge-update 11/18 vs 16/18, multi-session 10/16 vs 12/16,
single-session-assistant 4/16 vs 12/16, single-session-preference 13/18 vs
15/18, single-session-user 11/16 vs 16/16, temporal-reasoning 12/16 vs 14/16.
Mean answer prompt 8.7k tokens against 110k for full history.

Mem0 on BEAM (run `beam-mem0-90-002`, completed 2026-09-14 08:42 UTC) is the
first Mem0 result on BEAM in this repo; the earlier per-question design was
never run because it would have ingested each chat once per question. Mean
nugget scores 0.673 at 100K and 0.615 at 500K. Mem0 stored 3,655 memories
across the seven chats (161 to 1,140 per chat); the answer prompt averaged
17.4k tokens at 100K and 70.5k at 500K, against 6.8k and 22k for Qwen 9B's
memory and 9.7k and 38k for Luna's. By ability: preference following 9/9,
instruction following and summarization 8/9, information extraction,
knowledge update and multi-session reasoning 7/9, event ordering and
temporal reasoning 6/9, contradiction resolution 3/9, abstention 2/9.
Ingestion $1.20 (853 adds), answering $0.79, judging $1.49.

### Paired outcomes, same questions

LoCoMo, 50 shared questions, memory extractors only:

| | Count |
|---|---:|
| Both Luna and Qwen right | 42 |
| Only Luna right | 2 |
| Only Qwen right | 2 |
| Both wrong | 4 |

Of the three questions full history misses, Luna misses one and Qwen misses
one. Memory size per question is the same: 11.3k tokens for Luna, 11.9k for
Qwen, from 21k-token histories.

BEAM, 90 questions, Luna against Qwen:

| | Count |
|---|---:|
| Both right | 47 |
| Only Luna right | 14 |
| Only Qwen right | 11 |
| Both wrong | 18 |

Qwen's memories average 13.3k tokens per question against Luna's 22.1k, 40
percent smaller at the same pass rate. By ability (9 questions each): Qwen
loses on event ordering, 4 against 7, wins on summarization, 7 against 5,
and is within one question everywhere else.

BEAM, 90 questions, Gemma against Qwen:

| | Count |
|---|---:|
| Both right | 27 |
| Only Gemma right | 6 |
| Only Qwen right | 31 |
| Both wrong | 26 |

| Ability (9 each) | Gemma | Qwen |
|---|---:|---:|
| temporal reasoning | 0 | 6 |
| contradiction resolution | 0 | 4 |
| knowledge update | 1 | 5 |
| information extraction | 2 | 5 |
| multi-session reasoning | 2 | 7 |
| summarization | 3 | 7 |
| event ordering | 4 | 4 |
| instruction following | 6 | 8 |
| abstention | 6 | 4 |
| preference following | 9 | 8 |

### Memory volume, matched BEAM histories

| Sessions | Gemma lines | Qwen lines | Gemma memory tokens | Qwen memory tokens | Gemma output tokens per update | Qwen output tokens per update |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 138 | 197 | 3,451 | 8,249 | 263 | 731 |
| 12 | 94 | 68 | 2,011 | 3,312 | 174 | 294 |
| 15 | 46 | 261 | 1,892 | 8,143 | 96 | 623 |
| 15 | 141 | 259 | 4,796 | 7,443 | 329 | 580 |
| 15 | 42 | 207 | 1,395 | 6,088 | 98 | 444 |
| 53 | 133 | 670 | 6,045 | 25,518 | 97 | 488 |
| 81 | 1,031 | 629 | 23,571 | 20,156 | 287 | 261 |

The repo's extractor audit (`docs/extractor-audit-20260913.md`) measured
coverage of reference facts directly on a small matched sample: Gemma base
12 to 22 percent, Luna 83 percent.

One session of one BEAM chat, side by side. Gemma wrote a single line:
"I'm focusing on tailoring my resume for the UK and Canadian markets,
considering the differences in CV and resume conventions." First person, no
name, no date. Qwen wrote 19 lines for the same session, each dated and
attributed, including the declined $75,000 offer, the Squarespace portfolio
redesign finished May 1, 2024, and the five award-winning projects chosen on
Alexis's advice.

## Why Qwen 9B matches Luna

1. **The design gives the extractor the easy job.** Each update is one
   session of two to three thousand tokens transcribed into dated facts under
   a fixed schema. That is note-taking. Multi-hop, temporal arithmetic, and
   contradiction resolution happen later in the frontier answerer over the
   complete memory, with no retrieval step to get wrong. The same answerer
   serves every extractor, so the extractor only has to not lose facts.
2. **Append-only removes the ways a small model would do damage.** The
   extractor never decides to update or delete, so a bad judgement cannot
   erase a fact. Contradictions stay in the record and the answerer resolves
   them by recency.
3. **Structured decoding takes formatting off the table.** The grammar
   guarantees valid JSON. Failures are loud (the whitespace loop, a timeout)
   rather than silent corruption of the store.
4. **Long context is carried by the architecture, not the model.** The
   extractor only ever sees its own compact memory plus one session, so a
   65k window serves histories that would need a million tokens as raw text.
5. **Ceiling and noise.** Full history tops out at 47 of 50 on LoCoMo. Both
   memory extractors sit three below it and miss almost exactly the same
   questions. Within a six-point noise band, "matches Luna" means "within
   noise of the ceiling".

Where the seams show: LongMemEval, 61 against Luna's 85. Half of the gap is
single-session-assistant, 4 of 16 against 12 of 16, where the memory must
record what the assistant wrote, typically long assistant messages that a
small model summarizes down to user facts. The rest is spread thinly across
every type, two to five questions each, plus the three whitespace-loop
failures. LongMemEval histories are also the longest, about
48 sessions, so the memory prefix the model must carry grows to 20k tokens.
That gap, not LoCoMo or BEAM, is the concrete target for fine-tuning.

## Why Gemma 3 4B does not

The design is not model-agnostic; it has a floor. The pipeline moves
reasoning to the answerer, but it cannot recover a fact the extractor never
wrote. Gemma falls below that floor in three ways:

1. **Coverage collapse.** On six of seven BEAM histories it wrote two to five
   times less memory than Qwen, 100 to 300 output tokens per update against
   450 to 700. The seventh history went the other way, over a thousand lines,
   which is repetition rather than coverage.
2. **Low fidelity in what it does write.** First-person, undated narrative;
   relative dates left relative; unstable atomic keys; and, in the audit
   smoke, a fabricated business name and a wrong attribution ("Gina's
   location = Paris" when Gina had said she had never been).
3. **Scores fall exactly where those defects bite.** Everything that needs
   dated, complete, attributed facts collapses: 0 of 9 on temporal reasoning
   and contradiction resolution, 1 of 9 on knowledge update. Preferences
   survive because they are broad and repeated. Abstention actually rewards
   an empty memory, since "I don't have that" is the correct answer when the
   fact was never stored, which is why Gemma beats Qwen there.

Contributing settings that differ from the Qwen runs and are not separated
out: greedy decoding with a frequency penalty rather than sampling, and the
merged single user message forced by Gemma's chat template. The structured
whitespace loop affects both models and is a decoding bug, not this gap.

## Caveats

- Sample sizes are small; see the noise bands above.
- The Qwen BEAM run mixed two output caps (2,048 then the full window) and
  shared memories across a history's questions, while the Luna BEAM run
  rebuilt memory per question. It is an observational comparison.
- The LoCoMo and BEAM question sets have been inspected repeatedly and are
  historical comparisons, not fresh held-out evidence.
- Coverage numbers from the audit come from a small matched sample and are
  not a calibrated metric.

## Provenance

- Luna LoCoMo 50: `20260908T190559396590Z_memory_6a360f8`; full history
  `20260908T192232760084Z_full-history_8cc5c91`.
- Luna BEAM: `20260908T191319329343Z_memory_07ccfb9` (100K),
  `20260909T064305432208Z_memory_e66fa47` (500K).
- Qwen LoCoMo 50: `work/qwen_locomo_sampling_completion`; Qwen BEAM:
  `work/qwen_beam_answers_max` with memories in `work/qwen_beam_vllm_max`.
- Gemma BEAM: `runs/gemma3-beam-90-003`; Gemma LoCoMo:
  `runs/gemma3-locomo-50-005` and its continuation.
- Qwen LongMemEval: `runs/qwen9b-longmemeval-100-002`. Mem0 BEAM:
  `runs/beam-mem0-90-002`.
- Extractor audit: `docs/extractor-audit-20260913.md`.
