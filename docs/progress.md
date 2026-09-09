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
Got: run 20260908T175547Z, complete_with_failures. 21 of 50 questions hit
429 tokens-per-minute errors late in extraction (sessions 36 to 46, when
stores are large) and the client's two quick retries gave up, so those
questions never answered. Not a result. Completed stores are much bigger:
18,793 lines over the run (11,226 before), largest 676 lines, and 4,010
flags, almost all value_not_in_session on assistant_ list values that the
model reformats. Cost $2.96. Cache share 76 percent.
Verdict: rerun required. Fixes: rate-limit backoff inside the API call (up
to six waits, 5 s doubling to 60 s), concurrency 10. The answer prompt
changed after this run launched, so the rerun carries Experiments A and B
together; B is then ablated by re-answering the rerun's stores with the
old prompt via `--memory-from --answer-prompt v1`.

### 02:25 — Experiments A+B rerun, five questions first as a canary
Tried: the A extractor rules and the B answer prompt (v2), backoff on 429,
concurrency 10. Run on the five questions first (about $0.30, 4 min) to
confirm nothing broke, then the 50.
Expected on five: 4 or 5 of 5, no failed calls. On 50: 36 to 40 of 50.
Got on five: run 20260908T181548Z, 4 of 5, same boots miss, no failed
calls, no rate-limit retries. Stores doubled: 2,353 lines against about
1,130, answer context 114,824 tokens against about 53,000, extraction
$0.32 against $0.23. The temporal answer now lists the two dated lines
before computing, as the v2 prompt asks.
Verdict on five: proceed to the 50 at concurrency 10. Store growth is the
price of the assistant_ rule; if the 50 shows the gain, trim afterwards.
Got on 50: run 20260908T182110Z, complete, no failed calls, no rate-limit
retries at concurrency 10, controls agree. 44 of 50 (88 percent; 90.8
reweighted) against the baseline's 34 (68; 65.9 reweighted) and the
first memory run's 31. Per type, baseline to now: single-session-user 8/8
to 8/8, single-session-assistant 8/8 to 6/8, preference 3/9 to 7/9,
multi-session 3/8 to 7/8, temporal 5/8 to 8/8, knowledge-update 7/9 to
8/9. Six misses: two assistant (shift-sheet cell, hostel name), two
preference, the boots count, Rachel's move. Answer context 1.09M tokens
against 5.51M for full history and 535k for the first memory run; 22,402
lines, 4,414 flags (assistant_ list values). Extraction $3.18, answering
$0.23, total $3.70. Wall 28.3 min.
Verdict: kept. Above the 36 to 40 predicted. The article's shape is
reproduced on this sample: 90.8 against 65.9 reweighted, at a fifth of
the answer tokens. Ablation next to see how much of the gain is the
answer prompt.

### 03:20 — Run-record compaction
GitHub rejected the 44-of-50 run: its results.jsonl was 130 MB because
every extraction call stored its full prompt, which repeats the growing
memory for each session. The memory messages are a deterministic
rendering of lines already in the store, so extraction calls now keep
only the session message plus the prompt hash, and the bridge rebuilds
the memory messages from the store. `compact_runs.py` converted every
finished run after verifying that the rebuilt prompt's SHA-256 equals the
recorded one: 14,491 calls, zero mismatches, 620 MB of run records down
to 358 MB, the largest file to 41 MB. Records stay reproducible; the
bytes on disk changed, which is the one deliberate exception to run
immutability, and it is hash-checked.

### 03:05 — Ablation: v1 answer prompt on the A+B stores
Tried: `--memory-from 20260908T182110999548Z_memory_b5424ef
--answer-prompt v1`, so the stores are identical and only the answer
prompt reverts to the original.
Goal: split the 13-question gain between the extractor rules (A) and the
answer prompt (B).
Expected: 38 to 41 of 50. The assistant_ lines should still be found
without the hint, so A carries most of the assistant gain; B carries the
temporal and preference gains, about 3 to 6 questions. Cost about $0.35.
Got: run 20260908T185059Z, 36 of 50 (72 percent; 67.6 reweighted), same
stores. Per type with v1: user 7/8, assistant 7/8, preference 5/9,
multi-session 2/8, temporal 6/8, knowledge-update 9/9. Cost $0.51.
Verdict: the extractor rules alone move memory from 31 to 36; the v2
answer prompt adds 8 more, concentrated in multi-session (2 to 7),
preference (5 to 7), and temporal (6 to 8), which is the
enumerate-then-count and tailor-to-stored-facts instructions doing their
job. Below the 38 to 41 predicted because B matters more than expected.
Caveat for the write-up: the baseline keeps its original answer prompt
by Huy's instruction, so about 8 of the 13-question lead comes from
answer-side prompting that a tuned full-history prompt might partly
recover. The write-side lead (36 against 34) is the clean comparison;
the full system lead (44 against 34) is the product comparison.

### 03:40 — Phase two: LoCoMo and BEAM samples
Goal reached on LongMemEval (44 against 34, 90.8 against 65.9
reweighted), so per Huy's instructions: build stratified samples of
LoCoMo and BEAM at a comparable scale, run the frozen baseline, then the
memory system.

Built: `benchmarks.py` adapts both into the runner's item format. LoCoMo
(10 conversations, dated sessions, two human speakers) follows Mem0's
rendering: speaker A as the user role, speaker B as the assistant role,
speaker name in the text, image captions as a bracketed tag; the
reference date is the last session's date; categories 1 to 4 only,
open-domain gold answers cut at the semicolon, all as Mem0 does. BEAM
100K chats have no sessions, so the chunk is a window of 8 user-assistant
pairs inside a batch, dated by the batch's time anchor; 12 to 15 windows
per chat. Judges are Mem0's own, vendored verbatim with hashes under
`third_party/mem0/`: LoCoMo's CORRECT/WRONG JSON judge with partial
credit, BEAM's per-rubric-nugget 0/0.5/1 judge with the question score as
the mean and a pass at 0.5. The extractor prompt takes a per-benchmark
subject; for LoCoMo it names both people and prefixes atomic keys with
the person's name. The six LongMemEval judge controls are skipped on the
other benchmarks.

Samples: `question_ids_locomo_50.json`, single-hop 20, temporal 12,
multi-hop 12, open-domain 6, round-robin over all ten conversations (the
benchmark's own proportions would give open-domain 3, too few to read).
`question_ids_beam_50.json`, chats 1, 4, 6, 13, 16 (coding, math,
writing, recommendation, lifestyle), the first question of each of the
ten ability types per chat. Both report a plain mean and a reweighted one.

Known inefficiency: memory is extracted per question, so a LoCoMo
conversation with five sampled questions is extracted five times. Cheap
at this scale (about 1,250 small calls); a shared store per conversation
is the fix if this scales up.

### 04:30 — LoCoMo full-history baseline on 50
Tried: `--benchmark locomo --questions question_ids_locomo_50.json
--concurrency 5`, frozen baseline prompt, reasoning none.
Goal: baseline for the LoCoMo sample. The article reports 88.2 for its
system against 82.2 for Mem0 OSS; Mem0's paper had full context at 72.9
on LoCoMo with a weaker model.
Expected: 32 to 38 of 50. Single-hop strongest, temporal weakest since
LoCoMo dates are relative to the session date and the answerer runs with
reasoning off. Answering about $0.30, judge about $0.30.
Got: run 20260908T190414Z, complete, all 50 judged, no invalid judge
outputs. 44 of 50 (88 percent; 91.7 reweighted to LoCoMo proportions).
Single-hop 20/20, multi-hop 12/12, temporal 9/12, open-domain 3/6. Wall
1.2 min, answering $0.25, judge $0.15, total $0.40.
Verdict: frozen baseline for LoCoMo. Above the 32 to 38 predicted: a
25k-token conversation is easy for a 1M-context model, and Mem0's judge
gives partial credit. The bar for memory here is high; the article's
88.2 is what full history already does on this sample.

### 04:30 — BEAM 100K full-history baseline on 50
Tried: `--benchmark beam --questions question_ids_beam_50.json
--concurrency 3`, same frozen baseline. Each call is about 127k tokens.
Goal: baseline for the BEAM sample; the article could not run full
history on BEAM's longer scales but 100K fits our window.
Expected: pass rate 20 to 30 of 50 at the 0.5 threshold, mean nugget
score 0.40 to 0.55. Abstention and summarization should pass easily with
the whole chat in context; contradiction resolution and knowledge update
are the hard ones. Answering about $1.30, judge about $0.60 (about 150
nugget calls).
Got: run 20260908T190419Z, complete, all 50 judged. Pass rate 39 of 50
(78 percent), mean nugget score 0.661. Per type mean score: information
extraction 1.00, preference 0.82, instruction following 0.80, temporal
0.75, multi-session 0.69, knowledge update 0.60, summarization 0.55,
event ordering 0.53, contradiction resolution 0.47, abstention 0.40.
Wall 8.3 min, answering $1.29, judge $0.75, total $2.04.
Verdict: frozen baseline for BEAM 100K. Above the 20 to 30 predicted; at
this scale the whole chat fits and the model reads it well. Abstention
is the weak spot: it answers when it should decline.

### queued — LoCoMo memory on 50
Tried: `--benchmark locomo --system memory --concurrency 10`, the
LongMemEval-tuned extractor (A rules, date rule, low reasoning) and v2
answer prompt, unchanged except the two-speaker subject line.
Goal: does the memory system transfer to a two-person benchmark without
tuning. This is the honest test of the design rather than of prompt
tuning on LongMemEval misses.
Expected: within 4 questions of the baseline either way. Risks specific
to LoCoMo: speaker attribution (facts about Caroline filed under
Melanie), image-caption content, and dates given as "8 May, 2023"
session stamps that the extractor must carry into lines. Extraction
about 1,250 calls at roughly $1.20; answer context far below full
history.
Got: run 20260908T190559Z, complete, all 50 judged, 1,332 extraction
calls, none failed, 79 percent cached. 44 of 50, the same as the
baseline (88 percent; 88.0 reweighted against the baseline's 91.7). Per
type against baseline: single-hop 17/20 against 20/20, temporal 11/12
against 9/12, multi-hop 12/12 against 12/12, open-domain 4/6 against
3/6. Three baseline misses are shared. The three single-hop losses are
softened specifics: "the peaceful moments" became "hiking nature
trails", a friend's advice became a friend's painting, and Dave's
favorite band (Aerosmith) was never stored. Answer context 565k tokens
against 1.25M (45 percent). 13,237 lines. Extraction $1.28, wall 14.7
min at concurrency 10.
Verdict: transfers without tuning: a tie on accuracy at under half the
answer tokens, with the temporal gain and the verbatim-detail loss both
consistent with the design. The article's 88.2 is matched but the
baseline here is already 88. LoCoMo conversations are small enough that
full history is not the bottleneck it is on LongMemEval.

### queued — BEAM 100K memory on 50
Tried: `--benchmark beam --system memory --concurrency 5`, same prompts,
windows of 8 pairs. About 70 extraction calls per chat, 5 chats, but
extracted once per question, so about 700 calls.
Goal: transfer to a session-less, single-topic 130k-token conversation.
The article's claim is strongest here (61.3 against 39.7 for Mem0).
Expected: pass rate within 5 of the baseline; mean nugget score 0.35 to
0.55. Abstention should hold (memory says what is absent), knowledge
update and contradiction resolution should benefit from chains; event
ordering and summarization may suffer because memory compresses. Cost
about $1.50 extraction plus $0.60 judge.
Got: run 20260908T191319Z, complete, 690 extraction calls, none failed,
36 percent cached (windows of 13k tokens dwarf the memory prefix). Pass
rate 37 of 50 against the v1 baseline's 39; mean nugget score 0.656
against 0.661. Per type, memory against baseline: abstention 3/5 against
2/5, contradiction 3/5 against 4/5, event ordering 4/5 against 3/5,
information extraction 3/5 against 5/5, instruction following 5/5 both,
knowledge update 4/5 against 3/5, multi-session 2/5 against 4/5,
preference 5/5 both, summarization 4/5 both, temporal 4/5 both. Answer
context 473k tokens against 6.36M (7 percent). 13,364 lines. Extraction
$1.97, judge $0.74, total $2.83, wall 22 min.
Verdict: a tie at 7 percent of the answer tokens, with the shape the
design predicts: memory better where a current state matters (knowledge
update, abstention), worse where verbatim detail from a specific turn
matters (information extraction, multi-session). The article's BEAM
claim is about the 1M and 10M scales where full history cannot run; at
100K full history fits and reads well.

### 06:20 — Phase three: Mem0 OSS under the same harness (Huy's decision)
The article's headline comparisons are against its own run of Mem0 OSS
with the same answerer and judge, not against full history. Plan: add a
`mem0` system to the runner using the open-source `mem0ai` package with
its default local vector store, an OpenAI embedding model, and GPT-5.6
Luna as its extraction LLM if the provider supports it; ingest each
session with Mem0's add, retrieve the top-k memories for the question,
answer with the v2 prompt, judge as before. Prove on the five-question
sample, then the three 50-question samples.

Built: `mem0_system.py` plus `--system mem0`. mem0ai 2.0.20, Qdrant in a
private directory per question, text-embedding-3-small, GPT-5.6 Luna at
low reasoning as Mem0's LLM (its provider needs the explicit
is_reasoning_model flag or it sends a temperature the model rejects).
Mem0 2.0.20 is ADD-only: one LLM call per add plus two embedding calls,
about 7.7k input tokens of which 97 percent is cached after the first
call. Ingest in chunks of two messages and retrieve the top 200, as
Mem0's own runner does. Token usage is captured by wrapping the OpenAI
clients Mem0 constructs, so cost accounting is exact. Two deviations
from Mem0's platform runner, both forced by the OSS SDK: the platform
`timestamp` parameter is rejected, so the session date goes in as
metadata and as a leading "Session date" line on each chunk; and the
search API takes the user id as a filter. Answer prompt is the v2 rules
worded for retrieved memories with dates.

### 06:50 — Mem0 smoke test on the 8-session fixture
Tried: `--system mem0 --test fixtures/memory_smoke_test.json`. About 48
add calls, one retrieval, one answer, one judge.
Goal: prove the third system end to end before the 50-question runs.
Expected: correct (Mem0 keeps both 27:12 and 25:50 as separate dated
memories and the answerer picks the later one). Cost under $0.10.
Got: run 20260908T194323Z, correct, judge yes. 48 add calls, 48 LLM
calls, all ADD events (no updates or deletes: 2.0.20 is add-only), 451k
input tokens of which 80 percent cached, 14k output. Retrieved 57
memories for the question, 3,882 answer-context tokens. Memory writing
$0.042, total $0.075.
Verdict: the third system works end to end. Cost per add about $0.0009,
so a 50-question LongMemEval run is roughly $12 of ingest; LoCoMo about
the same, BEAM about $5.

### 07:00 — BEAM baseline v2 result
Got: run 20260908T193604Z, 39 of 50 pass, the same as v1, mean nugget
score 0.685 against 0.661. Per type, v2 against memory: abstention 1/5
against 3/5, contradiction 4/5 against 3/5, event ordering 2/5 against
4/5, information extraction 5/5 against 3/5, instruction 5/5 both,
knowledge update 4/5 both, multi-session 4/5 against 2/5, preference
5/5 both, summarization 4/5 both, temporal 5/5 against 4/5. Cost $2.02.
Verdict for the v2 baselines: LongMemEval 34 to 41, LoCoMo 44 to 47,
BEAM 39 to 39 (score 0.661 to 0.685). Against memory: LongMemEval
memory leads 44 to 41; LoCoMo trails 44 to 47; BEAM trails 37 to 39.

### 07:05 — Mem0 OSS on the three 50-question samples
Tried: `--system mem0` on LongMemEval first, then LoCoMo, then BEAM,
sequentially at concurrency 8, spending guard overridden per run.
Goal: the article's actual comparison. Its numbers for Mem0 OSS: 71.6
on LongMemEval, 82.2 on LoCoMo, 39.7 on BEAM, all under the same
answerer and judge as its own system.
Expected: LongMemEval 34 to 40 of 50 (the article's 71.6 was against a
weaker answerer; ours is stronger, but Mem0 2.0.20 is add-only and its
retrieval must find the right memories among hundreds); LoCoMo 40 to
44; BEAM pass 25 to 32 with mean score 0.45 to 0.55. Cost about $12,
$11, and $5 of ingest respectively; wall time about an hour each for the
first two.
Got, LongMemEval (run 20260908T194854Z, partial): 48 of 50 judged, 39
correct on those (78 percent; 75.1 reweighted counting the two
unfinished as misses) against memory 44 (90.8) and full history v2 41
(78.6). Per type: user 6/8, assistant 8/8, preference 7/9,
multi-session 4/8, temporal 7/8, knowledge update 7/9. 12,158 add calls,
113M input tokens of which 79 percent cached, ingest $10.80, total
$11.22, wall about 2 h 20 min at concurrency 8. Two failures, neither a
Mem0 quality issue: question e47becba never started because worker
threads raced the import system at startup (KeyError
'openai.resources'), which also kept the run from finalizing; question
852ce960 failed at session 9 when Mem0 embedded a single turn longer
than the embedding model's 8,192-token limit. Fixes: OpenAI and Mem0
provider modules are imported once in the main thread before the pool;
an add that fails on the embedding limit is retried once with each
message cut to 24,000 characters and the truncation counted. The
unstarted question is being resumed on the unchanged code; the errored
one is rerun alone on the fixed code and reported together with the 49.
Side fix: Mem0's get_all pages 20 by default, so stored-memory counts in
earlier records are floors; now fetched in full.
Got, LongMemEval, complete (main run plus reruns 20260908T222250Z for
852ce960 and 20260908T222249Z for e47becba, both correct): 41 of 50 (82
percent; 78.6 reweighted). Per type: user 7/8, assistant 8/8,
preference 7/9, multi-session 4/8, temporal 7/8, knowledge update 8/9.
Total Mem0 spend on LongMemEval about $11.8. Mem0 lands exactly on the
full-history v2 score and reweighting; memory leads both by 3 questions
and 12 reweighted points, all of it on multi-session (7/8 against 4/8)
and one temporal question. Mem0 is perfect on assistant questions where
memory drops two. Within the article's prediction that Mem0 OSS keeps
old facts and does well on knowledge updates (8/9).
Got, LoCoMo, first attempt (run 20260908T220918Z, killed): at
concurrency 16 the combined load hit the 2M tokens-per-minute limit and
Mem0's own client gives up after two quick retries, outside our backoff;
28 of 50 questions failed inside 30 minutes. About $2.50 spent. The two
single-question LongMemEval reruns failed the same way at the same time.
Fix: Mem0 adds are retried on rate-limit errors with the same doubling
wait as our own calls, up to eight attempts. Relaunched at concurrency 8
along with the two LongMemEval reruns.
Got, LoCoMo (run 20260908T222244Z, relaunch): 48 of 50 judged, 40
correct on those (counted as 40 of 50, 82.7 reweighted, pending the two
reruns); two questions never ran because their worker threads raised
outside the per-session error handling and the run did not finalize.
The Mem0 step is now wrapped so any exception is recorded on the
question instead of aborting the run; the two questions are rerun with
full stderr kept. No rate-limit failures at concurrency 8 with backoff. Per type: single-hop 18/20, temporal 7/12, multi-hop 12/12,
open-domain 3/6. Answer context 500k tokens, ingest $9.69, total $9.96,
about 2 hours. Against memory 44 (88.0 reweighted) and full history v2
47 (95.5). Mem0's weak spot is temporal (7/12 against memory's 11/12),
consistent with the OSS SDK's lack of native timestamps even with the
session date passed in.
Got, BEAM: not run. Huy stopped it at 45 of 690 windows (about 10
minutes, under $1); the LongMemEval and LoCoMo Mem0 comparisons are the
ones the write-up needs.
Got, LoCoMo, complete (rerun 20260909T005041Z for locomo0_q82 and
locomo7_q15, both correct, $0.38): 42 of 50 (84 percent; 88.2
reweighted). Per type: single-hop 20/20, temporal 7/12, multi-hop 12/12,
open-domain 3/6. Total Mem0 spend on LoCoMo about $12.8 including the
killed first attempt.
Verdict: on LoCoMo our memory (44, 88.0 reweighted) and Mem0 (42, 88.2)
tie, and both trail full history v2 (47, 95.5) because a 25k-token
conversation fits easily. Mem0's temporal weakness (7/12 against
memory's 11/12) is offset by perfect single-hop recall, where memory
softened three verbatim details. On LongMemEval memory leads Mem0 by
three questions and 12 reweighted points. BEAM Mem0 not run by Huy's
decision. Phase three complete; write-up next.

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

### 05:40 — Baseline gets the v2 rules too (Huy's decision)
Tried: a full-history v2 answer prompt with the same three rules as
memory v2, worded for turns and session dates; `--answer-prompt` now
applies to both systems, default v2. Baseline v2 runs on all three
50-question samples; the v1 baseline runs stay as the untouched
reference.
Goal: a fair product comparison. About 8 of memory's 13-question lead on
LongMemEval came from answer-side rules the baseline never got.
Expected: LongMemEval baseline 36 to 40 (from 34), gains on
multi-session and temporal; LoCoMo 44 to 46 (from 44); BEAM pass 40 to
43 (from 39). Memory should still lead on LongMemEval by 4 or more; a
tie or worse on LoCoMo and BEAM is possible.
Got, LoCoMo: run 20260908T192232Z, 47 of 50 (94 percent; 95.5
reweighted) against 44 for v1. Temporal 10/12, open-domain 5/6, the
other two perfect. Cost $0.40. Full history now leads memory (44) by
three on LoCoMo; memory keeps only the temporal edge (11 against 10) and
loses three single-hop verbatim details.
Got, LongMemEval: run 20260908T192233Z, 41 of 50 (82 percent; 78.6
reweighted) against 34 for v1. Per type against memory (44): user 8/8
against 8/8, assistant 8/8 against 6/8, preference 7/9 against 7/9,
multi-session 4/8 against 7/8, temporal 7/8 against 8/8, knowledge
update 7/9 against 8/9. Cost $1.42. Memory leads by 3 on the fair
comparison (90.8 against 78.6 reweighted) at a fifth of the answer
tokens; the lead is multi-session, knowledge update, and temporal, which
is the article's story, minus two assistant questions.
Got, BEAM: pending.
Verdict, so far: the answer rules were worth 7 questions to full history
on LongMemEval and 3 on LoCoMo. Memory's clean lead on LongMemEval is 3
questions; on LoCoMo it trails by 3. Both are within one run's noise on
50 questions, so the honest summary is: LongMemEval, memory wins on the
multi-session and update categories at 20 percent of the tokens; LoCoMo,
full history wins when the whole conversation is 25k tokens.

### 09:10 — Mem0 stores persist and resume (Huy's request)
Each question's Mem0 store (Qdrant local directory plus history
database) now lives under `runs/<id>/mem0/<question>/`, ignored by git,
instead of a temp folder deleted on close. `--resume` reopens the store
and continues from the recorded number of ingested sessions instead of
re-ingesting. Verified: add, close, reopen, memories intact. Applies to
the next Mem0 run; the one in flight was started on the old code.

## Open

- Decision (Huy, 07:30): no scaling beyond 50 questions per benchmark; another
  50 each would cost about $40, mostly Mem0 ingest. Report the 50-question
  numbers with their noise stated.

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
- Final deliverable for Huy: after everything is done, a summary comparing our numbers with the article's (LongMemEval 90.6 vs 71.6 Mem0 vs 60.6 full history; LoCoMo 88.2 vs 82.2; BEAM 61.3 vs 39.7).
