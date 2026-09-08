# Progress log

One entry per change or iteration, newest at the bottom. Times are local
(UTC+7); run IDs carry UTC. "Smoke" means `fixtures/memory_smoke_test.json`,
the 8-session cut of knowledge-update question 6a1eabeb.

## 2026-09-08

### 12:48 and 12:57 — Full-history baseline, two paid runs
Five fixed questions, GPT-5.6 Luna answering with no reasoning, GPT-5 judging
with Mem0's prompt. First run 3 of 4 graded correct with one judge API error.
Second run 4 of 5. The miss is the multi-session counting question
(0a995998): three clothing items across sessions 12, 20, and 31 of 44, model
found two. History is about 110k tokens per question, 552k across five.

### 14:13 — Immutable run records
Every invocation writes `runs/<id>/` with manifest, results, summary; terminal
runs append to `runs/index.jsonl`. Resume and retry-of. Commit d581a9b.

### 15:00 — Inspect AI viewer via a bridge
Decision: keep the runner and Inspect as separate systems; `inspect_bridge.py`
converts run records to Inspect logs, runner never imports Inspect. Bumped
tiktoken to 0.13.0 so one Python 3.14 venv holds both. Found the viewer caps a
single text block at 250,000 characters, so the history is expanded to one
bubble per turn with session and timestamp metadata. Dataset evidence labels
(never shown to the model) are flagged on bubbles and linked from an evidence
block at the top of each transcript. Commits beafaaa, 1fb4a05.

### 16:24 — Extraction model set, smoke-test fixture cut
GPT-5.6 Luna, medium reasoning, 128,000-token output cap. Fixture: sessions
19, 20, 21, 29, 35, 38, 39, 40 of question 6a1eabeb, real question and answer.
Evidence 27:12 in session 2 and 25:50 in session 8; marathon distractor in
session 4; prompt injection opens session 7. Commits 3194692, 71d6591.

### 21:30 — Design settled, literature surveyed
Two forms (atomic `key: value`, narrative sentences), append-only store,
supersession as a new line carrying the whole chain newest first
(`25:50 <- 27:12`), answerer sees the last line per key. Chunk = dataset
session when one exists, fixed turn window otherwise (BEAM has no sessions).
Literature: every LongMemEval system that keeps old facts scores 92 to 96 on
knowledge updates, in-place updaters 74 to 83; nobody renders supersession to
the reader; fact-only memory is lossy; key consistency is the hard skill.
Notes in `docs/memory-design.md`, `docs/literature.md`, `docs/research/`.

### 22:28 — Memory v1, smoke run 1 (20260908T152807Z)
`memory.py` plus `--system memory` and `--test`. Result: correct, judge yes.
Chain `charity 5K personal best: 25:50 <- 27:12` intact. Marathon session
produced separate keys. Injection session produced zero lines. Answerer read
2,517 memory tokens instead of about 25.7k of history. Spend $0.045.
Problems: zero cached tokens on sessions 2 to 8; validator flagged three
resolved dates that cannot appear in the text by construction; 46 atomic
lines, many of them whole sentences under a key.

### 22:33 — Caching fix, smoke run 2 (20260908T153339Z)
Cause: GPT-5.6 only matches cached prefixes at breakpoints, and memory plus
session in one message moved the breakpoint every call. Probe confirmed Chat
Completions accepts `prompt_cache_breakpoint` on a content block. Extractor
now sends one message per earlier session's memory with an explicit
breakpoint on the last, then the new session. Sessions 4 to 8 read 27 to 47
percent from cache; 1 to 3 miss under the 1,024-token minimum. Validator
exempts date-like anchors whose year matches the session. Result: correct,
zero flags, 68 lines. Spend $0.038. Commit 0b715ca.

### 23:23 — Prompt revision, smoke run 3 (20260908T162318Z)
Huy's rewrite: no examples, atomic only for values a future question could
ask for, values are the fact itself not the sentence, plans and goals go to
narrative. Kept the key-consistency rule; dropped a reversed chain example.
Atomic lines 46 to 18, narrative 22 to 26, memory tokens 2,517 to 1,815,
zero flags, correct. Keys switched to snake_case on their own. A few
plan-shaped atomics remain; leaving the prompt alone until the five-question
run says otherwise. Cache read 21 percent. Spend $0.045.

### 23:36 — Memory on the five questions, first attempt
Tried: `--system memory` on the five fixed questions, 235 sessions total,
current prompt (smoke run 3 version). Spending limit overridden to $40 for
this run only via `--spending-limit`, because the guard projects $37.50
worst case from the 128k output cap times 235 calls; `.env` unchanged.
Goal: the actual comparison against the full-history baseline (4 of 5).
Answers whether write-time memory holds accuracy at a fraction of the
tokens, and whether the multi-session counting miss (0a995998) is fixed.
Expected: 4 or 5 of 5. Most likely miss is still 0a995998 if the three
clothing items land under differently named keys. Memory context 2k to 4k
tokens per question against about 110k. Cache reads 30 to 50 percent of
extraction input. Total spend around $0.50, of which judge about $0.15.
Got: 4 of 5, run 20260908T163607307304Z, complete, judge controls all
agree. Correct: single-session-user, preference, temporal (7 days), and
knowledge-update (25:50). Miss: multi-session counting 0a995998, answered
"one item", same question full history missed with "two". The store had all
three items (blazer at dry cleaner s12, Zara boots exchange s20, pickup
s31), so it is a reading failure by the answerer at reasoning none, not a
writing failure. Answer context 47,365 tokens across five questions against
551,577 for full history, 7.8k to 10.7k per question, 173 to 261 lines
each. Extraction: 235 calls, 1.93M input tokens of which 68 percent cached,
63k output. Cost: memory writing $0.226, answering $0.010, judge $0.052,
total $0.287. 14 flagged lines out of 1,123, mostly resolved dates whose
year is not in the text and list-valued facts the validator cannot anchor.
Wall time 27 min sequential, of which about 9 min were three hung calls.
Verdict: kept as the memory baseline. Matches full history on accuracy at
about a twelfth of the answer tokens; does not yet beat it.

### 23:50 — Concurrency across questions, smoke run 4 (20260908T165003Z)
Tried: questions and judge controls run in a thread pool (`--concurrency`,
default 5); sessions within a question stay sequential because each
extraction needs the memory from the one before. All run-record mutation and
checkpointing under one lock, API calls outside it. Client timeout 180 s to
60 s, after three extraction calls in the five-question run each took 184 s,
which is a hung request plus a fast retry.
Goal: wall time. Five questions sequentially is about 235 calls in a row;
in parallel it is bounded by the longest question, about 53 calls.
Expected: same result as smoke run 3; wall time well under the 90 s of the
sequential smoke runs since the six controls overlap.
Got: complete, correct, controls all agree, audit clean, 44 lines, zero
flags. Wall time 56 s. Spend $0.037.
Verdict: kept. Concurrency is safe on real calls.

## 2026-09-09

### 00:20 — Five questions again, concurrent runner, timing test
Tried: identical configuration to run 20260908T163607Z, on the concurrent
runner with `--concurrency 5` so all five questions and the six judge
controls run at once. Spending limit overridden to $40 again.
Goal: measure wall time when the critical path is the longest question
(53 sessions) instead of all 235 sessions in a row, and get a second sample
of the same configuration for variance.
Expected: 4 or 5 of 5 with the same likely miss. Wall time about 4 to 6
minutes against 27 sequential (median extraction call 4.0 s, so 53 x 4 s
plus answer and judge, plus any hung calls at the new 60 s timeout). Cache
read share about 68 percent again. Spend about $0.29.
Got: run 20260908T171347Z, complete, controls agree. Wall time 5.0 min
against 27 sequential; 235 calls, median 4.1 s, three over 30 s at the new
60 s timeout. Cache share 67 percent. Spend $0.287. Score 3 of 5: the
temporal question flipped from "7 days" to "9 days", and counting said
"two items" (same as full history, still judged no). Cause of the temporal
flip: in both runs the MoMA visit was stored as "recently attended", with
no date in the line, although the user said "I just got back". Run 1's
answerer used the line's session date; run 2's read "recently" as earlier.
Verdict: timing kept, concurrency 5 is the floor from here. Quality
finding: the extractor must resolve "just", "today", "yesterday" to an
absolute event date in the line. Run-to-run variance on five questions is
at least one question; treat single-run differences of one as noise.

### 00:35 — Extractor reasoning medium to low, five questions
Tried: same as the previous run with `--extraction-reasoning-effort low`.
Goal: extraction is 85 percent of the cost and half its output tokens are
reasoning; low would save several dollars per 500 questions if quality
holds.
Expected: 3 or 4 of 5, within the observed variance; extraction cost down
about a quarter, from $0.23 to about $0.17; similar line counts; cache
share unchanged since the effort setting is constant within the run.
Got: run 20260908T172003Z, complete, controls agree, 4 of 5, miss is the
counting question again ("two items", same as full history). Extraction
$0.209 against $0.226 and $0.231 at medium; reasoning tokens 15,971 against
about 32,000; 1,030 lines against 1,123 and 1,143; 19 flags; answer
context 44,838 tokens. Wall 4.4 min. Total $0.271.
Verdict: kept, low is the default from here. Saving is 9 percent of
extraction, about $2 per 500 questions, because uncached input dominates
the cost, not reasoning. Quality within variance.

### 00:45 — Extractor date rule, five questions, low reasoning
Tried: prompt line requiring every event in a line to carry an absolute
date when the conversation implies one: "just", "today", "yesterday",
"this morning", "last night" resolve to the session date or the day before.
Everything else as the previous run.
Goal: the temporal question flipped between runs because the MoMA visit
was stored as "recently attended" with no date. The article's temporal
category depends on this, and the session-date column is when the user
said it, not when it happened.
Expected: MoMA line carries 2023-01-08; temporal question correct; 4 of 5
with the counting question still the miss; cost and lines unchanged.
Got: run 20260908T172557Z, complete, controls agree, 4 of 5, miss is the
counting question ("one item"). MoMA line now "On 2023-01-08, the user
returned from a guided Museum of Modern Art tour"; temporal answer 7 days.
Extraction $0.228, total $0.290, 1,138 lines, answer context 53,242
tokens (dates add text), wall 3.4 min. 26 flags: 20 lightly tightened
values, 6 resolved dates; none wrong.
Verdict: kept. Configuration for the 50-question run: low reasoning plus
the date rule.

### 00:58 — Memory on 50 questions (question_ids_50.json)
Tried: `--system memory --questions question_ids_50.json --concurrency 15`,
current prompt, low reasoning. Spending limit overridden to $400 because
the guard projects $381 from the 128k output cap times about 2,350 calls.
Goal: the first sample large enough to see per-type differences, with the
article's two headline categories at nine questions each. Full-history on
the same 50 runs next as the baseline.
Expected: 35 to 40 of 50 (70 to 80 percent). Strongest: single-session-user,
knowledge-update, preference. Weakest: multi-session and
single-session-assistant. Extraction about $2.30, judge about $0.30, total
about $2.70. Wall time 15 to 20 minutes. Risk: 429 rate-limit errors near
the 2M tokens-per-minute cap at 15 in flight; the client retries twice,
and a question that still fails is recorded as an extraction API error.
Got: run 20260908T173055Z, complete, no failed calls, controls agree.
31 of 50 (62 percent; 63.3 reweighted to benchmark proportions), under the
70 to 80 predicted. Per type: single-session-user 8/8, knowledge-update
8/9, temporal 5/8, multi-session 4/8, single-session-preference 4/9,
single-session-assistant 2/8. Wall 19.1 min at concurrency 15, 2,402
extraction calls, 68 percent cached, 11,226 lines, 298 flags. Answer
context 535k tokens total against about 5.5M for full history. Cost:
extraction $2.29, answering $0.11, total $2.68.
Side finding: a U+2028 character inside a memory line broke every reader
that used Python's splitlines on results.jsonl (runner resume, bridge,
report). All three now split on newline only.
Verdict: kept as the 50-question memory baseline. The weak types are
single-session-assistant and preference, the article's headline
categories; miss analysis next.

### queued — Full-history baseline on the same 50 questions
Tried: `--questions question_ids_50.json --concurrency 3`, default
full-history system, answer model with reasoning none. Runs after the
memory run so the two jobs do not fight over the 2M tokens-per-minute
limit; each full-history call is about 110k tokens.
Goal: the baseline the 50-question memory score is compared against. The
article reports 60.6 percent for full history on all 500; our five gave
80 percent.
Expected: 30 to 38 of 50 (60 to 76 percent). Weakest: multi-session and
temporal, where full history has to find and combine facts inside 110k
tokens with reasoning off. Answering about $1.20, judge about $0.30. Wall
time 10 to 15 minutes at concurrency 3. No spending override needed.
Got: run 20260908T175109Z, complete, no failures, controls agree. 34 of
50 (68 percent; 65.9 reweighted), inside the 60 to 76 predicted. Per
type: single-session-user 8/8, single-session-assistant 8/8, preference
3/9, multi-session 3/8, temporal 5/8, knowledge-update 7/9. Answer
context 5.51M tokens, answering $1.11, total $1.43, wall 3.8 min at
concurrency 3.
Verdict: the frozen baseline for the 50. Memory (31) trails by three,
entirely on single-session-assistant (2/8 against 8/8); memory leads on
preference (+1), multi-session (+1), knowledge-update (+1), ties on user
and temporal. 12 questions are missed by both systems.

### 01:40 — Miss analysis of the 50-question memory run
19 misses read against the evidence turns and the memory lines from the
evidence sessions. Write-side (fact never stored): all 6
single-session-assistant misses, because the prompt told the extractor to
record assistant statements only when the user adopts them, and every
question in that category asks what the assistant said (a shop name, a
hostel, the 7th item of a list, a color in a generated story); 2 of 5
preference misses (a kitchen session produced zero lines; general
preferences like "hotels with rooftop pools" not stored); 1 multi-session
(drive durations in "by the way" asides dropped); the 1 knowledge-update
("Rachel just moved back to the suburbs", an aside inside a travel
question). Read-side (stored but the answerer missed it): all 3 temporal
misses (dates were in the narrative lines; the answerer said they were
absent or misread one), 3 preference misses (generic advice, or asked for
the user's location instead of answering), 2 multi-session counts, and the
boots label. Roughly 11 write-side, 8 read-side.

### queued — Experiment A: extractor prompt for asides, assistant specifics, possessions
Tried: four rules added to the extractor prompt: user asides are facts
with their numbers and dates as atomic lines; when the user asks the
assistant to recommend, list, name, schedule, or write something, record
the specifics the assistant gave under keys prefixed "assistant_"; the
user's possessions, home, projects, problems, and stated general
preferences are facts and such a session is never empty; a statement that
changes a fact about anyone already in memory is a chain. Full 50, low
reasoning, concurrency 15, after the baseline finishes.
Goal: the 11 write-side misses. The assistant category is 2/8 and the
preference category 4/9; both are article headline categories.
Expected: 36 to 39 of 50. Assistant 5 to 7 of 8, preference 5 to 6 of 9,
one more multi-session, knowledge-update 9 of 9. Lines up 20 to 40
percent, answer context up accordingly, extraction cost about $2.80.
Risk: more assistant content in memory could distract the answerer on
user-fact questions; watch single-session-user staying 8 of 8.
Got: pending.
Verdict: pending.

### queued — Experiment B: answer prompt for recommendations, counting, dates
Tried: `--memory-from` reuses Experiment A's stores, so only the answer
prompt changes: for advice or recommendation questions, tailor the answer
to the user's stored preferences and facts and say which ones; do not
refuse over missing incidental details such as location; for counting or
date questions, list the relevant memory lines with their dates first,
then compute. Answerer stays at reasoning none, same as the baseline.
Goal: the 8 read-side misses at near-zero cost, about $0.15 per run.
Expected: plus 3 to 5 over Experiment A, mostly temporal and preference.
Got: pending.
Verdict: pending.

## Open

- Multi-session counting (0a995998): the facts are in memory and the
  answerer undercounts. Next experiment: same run, answerer at reasoning
  low or medium. Prediction: fixes it, since the answer prompt is 10.7k
  tokens and the three items are all present.
- Validator false positives: list-valued facts and dates whose year is
  absent from the text. Decide whether to loosen the check or accept the
  flags as a review aid.
- Decide a permanent answer to the spending guard versus the 128k output
  cap: keep overriding per run, or lower the extraction allowance. Actual
  extraction output averaged 270 tokens per call.
- Scale-up: 50 questions, ten per type, once memory beats full history on
  the five.
- Judge reasoning is mostly hidden (GPT-5 reasons in hidden tokens); decide
  whether a separate explanation call is worth breaking Mem0 parity.
- Ablation planned: arrow chains versus flat dated append, same extractor
  and answerer.
