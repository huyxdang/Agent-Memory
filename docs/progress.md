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
Got: L40S completed 96/96 updates, all valid, in 233.9 s of extraction wall
after 291.5 s startup: 0.41 updates/s, 1,362 prompt tok/s, 77 output tok/s,
per-call elapsed mean 35.1 s (median 36.9, max 55.6), semaphore queue mean
9.7 s, mean prompt 3,318 tokens, mean output 186 tokens. Accounted $1.1084
(upper bound with the $0.50 allowance), extraction-only $0.0022 per update.
Well under the 1.0 to 1.5 updates/s expected. The vLLM stats lines explain
it: the engine held at most 15 running requests and usually 2 to 5, with
zero waiting and GPU KV cache use under 14 percent, while 24 histories were
nominally in flight. Time to first token was 0.4 s median, so prefill is not
the cost. Each update triggers about 8 durable commits (four persists plus a
stream snapshot every 10 s), all serialized through the worker's commit lock
with `sync /state`; about 765 commits over 234 s is 0.31 s each, which
matches the wall time on its own. The GPU was mostly idle. Prefix-cache hit
rate stayed at 0.0 percent in every stats line even though the system prompt
is shared by all 48 histories; vLLM 0.21 reports Mamba `align` cache mode as
experimental for this model, and it did not produce hits.
H100 never served a request: `fatal.json` is `TimeoutError: vLLM startup
exceeded ten minutes`. Weights loaded in 15 s and torch.compile finished at
03:34:41 UTC, then nothing was logged before the worker's 300 x 2 s poll
limit killed it. On the L40S the same post-compile profile and warmup phase
took 2.6 minutes; on the H100 it exceeded 8.5, most likely Triton kernel
compilation for the hybrid Mamba layers on a new GPU architecture with no
cached artifacts plus CUDA-graph capture for 48 sequences. Accounted $1.4958
for zero updates. Total smoke accounting $2.6042, both terminations confirmed.
Verdict: inconclusive on GPU choice, conclusive on the bottleneck. Raising
concurrency alone does not help because the worker's per-persist volume sync
throttles the engine; the GPU comparison is meaningless until commits are
batched. H100 also needs a longer startup allowance before any retry.

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

### 10:00 — Continuity for all three systems (Huy's request)
State of resume: full history checkpoints after answer and judge; our
memory system checkpoints the store after every session and resumes
from the recorded session; Mem0 stores persist on disk since this
morning. New: `--resume --retry-failed` also continues questions that
stopped on an API error, from the stage they reached, instead of
preserving them as failures. Proof (run 20260909T034024Z): the smoke run was killed by PID after its
second checkpoint, leaving status running with sessions 1 and 2
recorded; `--resume` continued at session 3, finished sessions 3 to 8
without repeating any, answered correctly, and the run was indexed
once. Two earlier attempts at this test were invalid: the API was
unreachable, so the first call failed and the run ended terminal with
$0 spent. Those exposed a real gap, fixed above: a run that ends
"complete with failures" can now be reopened with `--retry-failed`.

### 10:30 — Expansion: LongMemEval to 100, LoCoMo to 154 (Huy's decision)
Tried: `question_ids_50b.json` (the next 50 LongMemEval questions by the
same per-type rule, no overlap with the first 50) and
`question_ids_locomo_154.json` (10 percent of LoCoMo's scored questions
in the benchmark's own proportions, containing the earlier 50). Full
history v2 and memory only; no Mem0, no BEAM additions. Kill-and-resume
test first, on record, before spending.
Goal: halve the noise on the LongMemEval comparison, where the article's
claim lives and memory leads; make LoCoMo a proper 10 percent sample.
Expected: LongMemEval second 50, full history v2 38 to 42 and memory 42
to 46, so a combined 100 with memory ahead by 4 to 8 questions.
LoCoMo 154, full history v2 93 to 95 percent, memory 86 to 90 percent.
Cost about $10, wall time about 90 minutes at concurrency 10 for memory
and 3 to 5 for full history.
Got, LongMemEval second 50, full history v2: run 20260909T034523Z, 44
of 50 (80.0 reweighted), above the 38 to 42 predicted. Per type: user
8/8, assistant 8/8, preference 9/9, multi-session 6/8, temporal 4/8,
knowledge update 9/9. Combined 100: 85 of 100. Cost $1.40, 11 min at
concurrency 2.
Got, LongMemEval second 50, memory: run 20260909T034510Z, 41 of 50
(78.2 reweighted), under the 42 to 46 predicted. Per type: user 8/8,
assistant 6/8, preference 8/9, multi-session 5/8, temporal 6/8,
knowledge update 8/9. Cost $3.62, 34 min at concurrency 10.
Combined 100: full history v2 85 of 100 (79.3 reweighted), memory 85 of
100 (84.5 reweighted). Per type over 100, full history against memory:
user 16/16 both, assistant 16/16 against 12/16, preference 16/18 against
15/18, multi-session 10/16 against 12/16, temporal 11/16 against 14/16,
knowledge update 16/18 both. Answer context 11.0M against 2.2M tokens.
Verdict, LongMemEval: the first half's three-question raw lead was
noise; over 100 the raw scores tie. What survives is the shape: memory
wins multi-session and temporal, the two largest categories in the real
benchmark (53 percent of it), and loses single-session-assistant (11
percent). Reweighted, memory leads 84.5 to 79.3 at a fifth of the answer
tokens. The article's 90.6 against 60.6 is not reproduced in size; the
direction and the category pattern are.
Got, LoCoMo 154, full history v2: run 20260909T042204Z, 140 of 154
(90.9 percent; 91.0 reweighted), just under the 93 to 95 predicted.
Per type: single-hop 79/84, temporal 28/32, multi-hop 28/28,
open-domain 5/10. Cost $1.28, 14 min at concurrency 2.
Got, LoCoMo 154, memory: run 20260909T042316Z, 137 of 154 (89.0
percent; 89.1 reweighted), inside the 86 to 90 predicted. Per type
against full history: temporal 31/32 against 28/32, multi-hop 27/28
against 28/28, single-hop 75/84 against 79/84, open-domain 4/10 against
5/10. Answer context 1.75M tokens against 3.88M (45 percent). Cost
$4.72, 44 min plus a 15-min retry. The first pass lost 31 questions to
"Connection error" when the network dropped near the end; `--resume
--retry-failed` reopened the run, kept the 123 finished questions, and
redid the 31, which is the continuity feature doing its job on a real
run. Guard raised to $700 for this run (worst-case projection $659,
realistic $4).
Verdict, LoCoMo: full history leads by three questions, 91.0 against
89.1 reweighted, at 154 questions. Memory's temporal edge is real and
consistent across both samples (31/32 here, 11/12 on the 50); its
single-hop loss is the verbatim-detail softening seen before. On a
benchmark whose conversations fit in 25k tokens, full history is the
stronger system and memory is the cheaper one.

### 13:45 — BEAM 500K on 40 questions, two chats (Huy's decision)
Context: BEAM's 100K chats fit comfortably in context and full history
won 39 to 37 there. The article's BEAM claim lives at 1M and above,
where it did not run full history at all. Probing the answer model's
window with oversized requests: 855k tokens accepted, about 945k
rejected, so the window is a bit under 1M. BEAM's scale labels undercount
for this tokenizer (100K chats measure 116k to 162k tokens), so 1M chats
at roughly 1.3M to 1.6M tokens cannot run as full history. 500K is the
largest scale with a head-to-head. Population at 500K: 35 chats, 20
questions each, 700 questions. Huy chose two chats, 40 questions, over
the 10-percent rule's 70.
Tried: chats 1 (Coding, 53 windows, 422k content tokens) and 13
(Relationship & Family, 81 windows, 571k content tokens) from the
HuggingFace 500K split, converted to the 100K layout under
`work/beam/500K/`; every probing question of both, four per type,
`question_ids_beam_500k_40.json`. Same prompts, judge, models and
per-question extraction as the 100K runs; adapter now loads every scale
on disk; client timeout raised to 180 s through CLIENT_TIMEOUT_SECONDS
for the 600k-token answers. Full history at concurrency 2, memory at 8.
Goal: the first comparison at a scale where full history is near its
ceiling, against the article's 61.3 (theirs) and 39.7 (Mem0) at 1M+.
Expected: full history 26 to 30 of 40 pass (65 to 75 percent), a few
points under its 78 percent at 100K, with information extraction and
event ordering degrading first. Memory 26 to 30 as well, roughly flat
from its 74 percent at 100K since the store size does not grow with the
chat the way the prompt does; the abstention and summarization types stay
its weak spots. Memory answer tokens under 5 percent of full history.
Cost: full history about $5 at $0.20 per million input, memory $8 to $12
in extraction. Full-history answer latency mean 20 to 40 s.

Got, full history: run 20260909T064208Z, 26 of 40 pass (65 percent),
mean nugget score 0.617, inside the 65 to 75 predicted and down from 78
percent at 100K. Per type: preference 4/4, information extraction 3/4,
instruction following 3/4, knowledge update 3/4, multi-session 3/4,
temporal 3/4, event ordering 2/4, contradiction 2/4, summarization 2/4,
abstention 1/4. Chat 1 11/20, chat 13 15/20. Answer tokens 22.1M,
latency mean 43.7 s, p95 99.9 s. Cost $5.13, 27 min at concurrency 2.
Got, memory: run 20260909T064305Z, 24 of 40 pass (60 percent), score
0.596, under the 26 to 30 predicted and down from 74 percent at 100K.
Per type against full history: multi-session 4/4 against 3/4 (score
0.98 against 0.62), event ordering 3/4 against 2/4, preference 4/4 both,
information extraction 3/4 both, instruction following 3/4 both,
abstention 1/4 both, knowledge update 2/4 against 3/4, temporal 2/4
against 3/4, contradiction 1/4 against 2/4, summarization 1/4 against
2/4. Chat 1 9/20, chat 13 15/20. Stores averaged 782 lines on chat 1
and 1,194 on chat 13. Answer tokens 1.52M (7 percent of full history),
latency mean 7.7 s (−82 percent), p95 20.4 s (−80 percent). Extraction:
2,680 calls, 79.8M input tokens at 70 percent cache reads, 1.6M output.
Cost $8.82, 67 min at concurrency 8. Twelve of the misses are shared;
full history misses 14, memory 16.
Verdict: at 500K both systems drop about 13 points from 100K and full
history keeps a two-question lead, 65 against 60 percent, inside the
noise of a 40-question sample (about 7.5 points). The article's 61.3 at
1M+ is matched in level by both of our systems at 500K. Memory's gains
are where the store helps, multi-session reasoning and event ordering;
its losses are knowledge update, temporal and contradiction, where the
chain must carry a change across 50 to 80 windows and the latest value
sometimes fails to land. The latency story is the strongest yet: the
memory answer is six times faster at a fourteenth of the tokens.

### 15:30 — Mem0 OSS on the LongMemEval second 50, chunk 4 (Huy's decision)
Context: Mem0 on the first 50 took 153 min and $11.35 at two messages
per add, about 250 sequential extractor calls per question. Huy asked
for the second 50 to complete a 100-question Mem0 column for the
Figure 2 comparison, and to run it at four messages per add, stating
that his earlier experiments showed chunk 2 and chunk 4 give the same
answers. The two halves are to be added together as one Mem0 score.
Tried: `--system mem0 --questions question_ids_50b.json
--mem0-chunk-messages 4 --concurrency 15`, everything else as the first
50 (top_k 200, Mem0 extractor at low reasoning, same answer prompt and
judge).
Goal: Mem0 on all 100, same questions as full history v2 and memory.
Expected: 40 to 43 of 50 (full history v2 got 44 on this half, memory
41). Mem0 keeps perfect assistant recall and single-session-user, loses
on multi-session (around 4 of 8) and one or two on knowledge update.
Combined 100: Mem0 81 to 84 raw, roughly 78 reweighted, against full
history 85 (79.3) and memory 85 (84.5). Cost $5 to $7, 45 to 80 min.
Half the extractor calls of the first run; memory-writing tokens about
60M against 115M.

## 2026-09-12

### 02:46 — Gemma 3 4B on BEAM final 90, partial (qwen-35e2ad7c74607f69)
Tried: first full benchmark for `google/gemma-3-4b-it` at revision
`093f9f388b31de276ce2de164bdc2081324b9767`, BF16 on one Modal L4, two
concurrent histories, Luna answering, BEAM per-nugget judge. Frozen BEAM
final 90 over seven histories, 203 extraction updates. Artifacts in
`work/gemma3_beam_final_c2/`.
Goal: establish whether a 4B extractor is usable on the hardest benchmark
after the smoke passed usability but failed strict fidelity.
Expected: completion inside the $2.10 Modal reservation; a score materially
below the Qwen 9B LoCoMo result but above the article's 39.7 full-history
BEAM baseline.
Got: incomplete. Extraction reached 125 of 203 updates and four of seven
histories before the hard Modal timeout at 46m 04s. Forty of ninety questions
were answered and graded, all status `success`, mean judge score 0.4488.
The four graded histories are all 100K; both 500K conversations and one 100K
conversation produced no graded answers. Two histories ended in
`unknown_outcome`. Per category, over four questions each: instruction
following 1.000, preference following 0.896, abstention 0.750, event ordering
0.440, multi-session reasoning 0.433, summarization 0.334, information
extraction 0.292, contradiction resolution 0.219, knowledge update 0.125,
temporal reasoning 0.000. Cost: $2.10 Modal, $0.7397 OpenAI.
Verdict: inconclusive as a benchmark number. The 0.4488 mean covers only the
four smallest histories, so it is not comparable to the article's BEAM figures
and must not be reported as a BEAM score. Temporal reasoning at 0.000 and
knowledge update at 0.125 do match the smoke's finding that Gemma leaves
relative dates unresolved and repeats superseded facts.

### 03:35 — LoCoMo final 50 launch failed on a packaging bug (qwen-89b2109b87c4452f)
Tried: launch the same Gemma configuration on the frozen LoCoMo final 50,
concurrency two, $2.30 Modal reservation. Directory
`work/gemma3_locomo_final_c2/`.
Goal: the second half of the approved BEAM-then-LoCoMo sequence.
Expected: 272 extraction updates across ten histories, 50 graded answers.
Got: the container exited during startup after about 23 seconds of billed
GPU time, before Gemma loaded. Zero extraction calls, zero OpenAI calls,
0 of 50 questions. The recorded cause was
`ModuleNotFoundError: adaption_memory.execution.context`: the Modal image
copied the execution package, whose `__init__` imported `context.py`, while
the runtime source manifest omitted that file. Cost: $0.5136 Modal, mostly
the fixed startup reserve. No durable log survives in the run directory, so
that error line comes from the session transcript, not from an artifact.
Verdict: reverted and retried. The manifest now enumerates package sources by
globbing `adaption_memory/**/*.py`, so an omitted module cannot recur; the
`context.py` module itself was later removed by the refactor.

### 03:40 — Gemma 3 4B on LoCoMo final 50 retry, no graded answers (qwen-086b5b5bb15cc25b)
Tried: relaunch LoCoMo with the packaging fix and concurrency raised from two
to four to fit the remaining Modal window. $1.80 reservation. Directory
`work/gemma3_locomo_final_c4_retry1/`.
Goal: recover the LoCoMo half of the sequence inside the money left under the
$35 cumulative Modal ceiling.
Expected: higher concurrency would finish more of the 272 updates than
concurrency two managed on BEAM.
Got: incomplete, and the concurrency increase backfired. Extraction reached
170 of 272 updates in 38m 19s, but only one of ten histories completed. Four
histories ended in `unknown_outcome` from client timeouts and five were still
running at termination. Zero of 50 questions were graded, so no OpenAI money
was spent. Cost: $1.80 Modal, $0 OpenAI.
Verdict: inconclusive, and concurrency four is rejected for this workload.
Each successive update carries a larger accumulated memory, so late prompts
grow until they cross the client response timeout. Four workers on one L4
queue those long calls past the limit. This contradicts the expectation that
more concurrency buys proportional throughput.

### 04:19 — Budget position after the Gemma sequence
Tried: reconcile both budgets after the three runs above.
Goal: know what remains before proposing any further paid work.
Got: Modal accounting reached $34.999 against the $35.00 cumulative ceiling,
leaving about one tenth of a cent. OpenAI accounting reached $3.8682 against
the $6.1285 cap, so $2.2603 of the approved $3 allowance is unspent. Actual
provider invoices remain unverified; these are conservative local figures.
Verdict: no further Modal work is possible without raising the ceiling.

### 08:20 — Gemma 3 4B rerun of BEAM and LoCoMo, predictions registered before results
Tried: two new frozen specs, `experiment_specs/beam-gemma3-4b-final90.json` and
`experiment_specs/locomo-gemma3-4b-final50.json`. Each copies the corresponding
Qwen spec and changes only `extractor_model`, so the comparison isolates the
extractor. Both run at concurrency four through the canonical command. BEAM is
run `gemma3-beam-90-001`, sandbox `sb-Xyx8SaP2vV1MuSRHZnaXg7`, $4.77 Modal
reservation giving a 7,199s window. LoCoMo is prepared as `gemma3-locomo-50-001`
and launches after BEAM. Payloads verified against the earlier attempts: BEAM
203 updates over seven histories (12, 12, 15, 15, 15, 53, 81), LoCoMo 272 over
ten. LoCoMo's question-set hash matches the frozen Qwen LoCoMo 50.
Goal: produce the first complete Gemma 3 4B numbers on both benchmarks. The
three earlier attempts all ended incomplete, so no Gemma score is reportable yet.

Correction to the earlier diagnosis. The 2026-09-12 03:40 entry blamed
concurrency four for client timeouts. That was wrong, and this rerun rests on
the correction. Extraction calls peaked at 104.9s on LoCoMo and 94.6s on BEAM,
against a 600s client timeout. Every history held exactly one call with no
elapsed time and no finish reason, and both GPU windows closed within a minute
of their paid deadline: BEAM ran 2,748s against a 2,697s budget timeout, LoCoMo
2,220s against 2,191s. The `unknown_outcome` states were the sandbox deadline
converting in-flight calls, exactly as designed. Concurrency four was healthy,
so holding concurrency at two would have cut throughput for no benefit.

Expected, recorded before any result is known:
- BEAM extraction finishes all 203 updates in roughly 3,200s, about $2.40,
  inside the 7,199s window. The 81-update history is the critical path.
- LoCoMo extraction finishes all 272 updates in roughly 3,600s, about $2.64.
- OpenAI answering and judging costs about $2.50 for BEAM's 90 questions and
  about $0.50 for LoCoMo's 50, against a $10 authorized cap.
- BEAM mean judge score lands near the 0.4488 seen on the four small histories,
  and probably below it, because the two 500K histories are harder and were
  excluded from that partial figure.
- Temporal reasoning stays near zero and knowledge update stays low, since the
  smoke found Gemma leaves relative dates unresolved and repeats superseded
  facts. If either rises sharply, the partial figure was unrepresentative.
- LoCoMo scores well below the Qwen 9B result of 44/50, or 88 percent.
Got: run vllm-ccfdf55d727267bc. 96/96 updates valid in 65.9 s of extraction
wall after 249.2 s startup: 1.457 updates/s (3.5x the 0.41 before), 4,822
prompt tok/s, 262 output tok/s. Engine stats held 24 running requests for
the whole active window with KV cache at 18 to 20 percent; vLLM logged up to
7,004 prompt tok/s and 405 generation tok/s. Per-call elapsed mean 14.7 s,
median 11.7, max 52.6; queue mean 11.9 s, which is now real waiting for a
slot rather than waiting on syncs. Same prompts: mean 3,310 input and 180
output tokens. Accounted $0.9625 upper bound; extraction-only $0.00063 per
update against $0.0022 before. Prefix-cache hit rate reached 15.6 percent,
not zero as expected; the first smoke's zeros were sampled while the engine
was nearly empty. Total for the three smokes today $3.5667. The tool exited
2 because `summarize()` in `execution/modal.py` counts `smoke_complete` as
failed; the smoke tool now judges completeness itself.
Verdict: kept. The commit lock was the limiter. For the full LongMemEval run
the early-session smoke still cannot measure late-history prompts of 20k to
40k tokens; prefill at 5k to 7k tok/s on an L40S puts 55M to 90M prompt
tokens at 2 to 4 hours unless prefix caching hits on the shared memory
prefix, so the H100 question is now about prefill, not about concurrency.

### 08:29 — Base-model routing bug killed the first BEAM relaunch (gemma3-beam-90-001)
Tried: first launch of `beam-gemma3-4b-final90` at concurrency four, $4.77 Modal
reservation, sandbox `sb-Xyx8SaP2vV1MuSRHZnaXg7`.
Goal: the full 203-update BEAM extraction, as pre-registered above.
Expected: all seven histories inside the 7,199s window.
Got: the worker died 268s after GPU start, before Gemma loaded. Zero histories,
zero updates, zero graded answers. `fatal.json` recorded
`AttributeError: 'NoneType' object has no attribute 'get'`. Cost: $0.6592 Modal,
$0 OpenAI.
Cause: `request_model` in `adaption_memory/inference/vllm.py` read
`payload.get("adapter", {}).get("name", payload["model"])`. A prepared payload
always carries an `adapter` key, set to null when there is no LoRA, and
`dict.get` returns that stored null rather than the default, so the chained
`.get` raised. The fine-tuned Qwen spec was unaffected because its adapter key
holds a dict, which is why the offline suite and the earlier fine-tuned smoke
never caught it. Every base-model Modal run would have failed the same way.
Verdict: fixed, with regression tests for the null, present, and absent adapter
key. The fix is `(payload.get("adapter") or {}).get(...)`. Offline suite 99
tests pass. Relaunched as `gemma3-beam-90-002`, sandbox
`sb-et1EhwDKRQYnIuhQke8pyz`.

Note on run lineage: `gemma3-beam-90-001` was not retried through `--retry-as`.
`Coordinator.retry` validates the parent against the current specification hash,
and fixing the bug changed the implementation revision, so the parent no longer
matches. That is the intended contract, since run identity includes the code.
The failed run stays as an immutable record of a different code revision.

### 09:28 — Bounded extraction output, frequency penalty, and a 500K smoke (vllm-5daf850dd5847a7e)
Tried: two fixes for the repetition loop that killed history `1a85ba42`, then a
targeted smoke on only the two BEAM 500K conversations, six updates each,
`work/gemma3_beam500k_smoke_fix`, sandbox `sb-dSCya8maTRQzZYOQmURPxh`, $1.20
reserved for a 1,180s window.

The first fix is a plumbing defect, not a tuning choice. `extraction_max_tokens`
is declared in the preset, hashed into the resolved specification, and applied
by the local pipeline, but the payload never carried it and the Modal worker
used the entire remaining context window. The failing call therefore had a
49,543 token ceiling on a task whose output averages 271 tokens across 447
recorded calls. Both executors now honour the value. Qwen specs keep 65,536,
which equals their context window, so their allowance stays 49,543 exactly.

Sizing, from those 447 calls: maximum output 2,554, p99 1,782, so 8,192
truncates none with 3.2x headroom. It must also stay under what the model can
emit inside the 600s client timeout, about 13,200 tokens at 22 tokens per
second, because reaching the cap yields a length finish recorded as
`invalid_output`, which a resume may re-attempt, whereas a timeout yields
`unknown_outcome`, which is permanently blocked. A larger cap would guarantee
the worse state.

The second fix is decoding. Gemma ran pure greedy with no penalty and emitted
61,115 characters over 12,120 chunks using 43 distinct characters. It now
carries `frequency_penalty` 0.3, which required adding that parameter to the
worker's allowed sampling set. Frequency rather than presence because it scales
with occurrence count, punishing a loop hard while barely touching an entity
name repeated across facts. Not `repetition_penalty`, which in this server also
penalises prompt tokens and would fight the requirement to preserve exact
wording. Structured output constrains the JSON grammar, so validity is
unaffected either way.

Goal: establish that the 500K histories advance without a runaway before
spending another full BEAM window.
Expected, before the result is known: both histories reach six of six updates
with `stop` finish reasons and valid JSON; no call approaches 8,192 output
tokens; per-call output stays near the observed 2,554 maximum. If a runaway
still occurs, it should now end at the cap with a `length` finish reason and be
recorded as `invalid_output` rather than timing out.
Got: passed on every criterion. Both 500K histories reached six of six updates.
All 12 calls returned `stop` with valid JSON and status `complete`. Output was
mean 80 tokens, maximum 140, so nothing came near the 8,192 cap. Elapsed time
was mean 7.0s, maximum 13.6s, against the 600s timeout. History `1a85ba42`,
which previously died at session 2, advanced cleanly through session 6.
Accounted $0.7061 of the $1.20 reservation.

The result that matters is the like-for-like comparison, same histories, same
sessions, against the unpenalised run:

| History 2dad6077, sessions 1-6 | Output tokens | Mean |
|---|---|---:|
| Greedy, no penalty | 104, 105, 50, 59, 60, 37 | 69 |
| frequency_penalty 0.3 | 104, 105, 51, 98, 60, 37 | 76 |

Four of the six are identical and session 1 of `1a85ba42` moved only from 147 to
140 tokens. So the penalty does not suppress extraction on healthy generations,
which was the fidelity risk worth worrying about. Warnings fell to 0 and 3.
Verdict: kept. Both fixes go into the full rerun. The cap itself was not
exercised, since no runaway occurred; it stays covered by unit tests.

Caveat on what this can prove: the loop hit session 2, but the penalty changes
generation from session 1 onward, so session 2 no longer receives a byte
identical prompt. The smoke tests whether these histories now advance, not
whether one specific prompt was repaired.

Also note: `gemma3-beam-90-002` did not hit its own deadline. It stopped at
1,442s of 7,199 because the Modal workspace spending limit of $20 was reached.
That limit has since been raised. Accounted $1.3554, five histories complete,
both large ones unresolved.

### 11:05 — Gemma 3 4B completes BEAM final 90 (gemma3-beam-90-003)
Tried: the full frozen BEAM 90 with both fixes in place, concurrency four,
sandbox `sb-Y2IhVDyxzzCiudw9LOmTM0`.
Goal: the first complete Gemma 3 4B number on BEAM after three failed attempts.
Got: complete. All 203 extraction updates across all seven histories, including
both 500K conversations, then 90 of 90 questions answered and judged with
status `success`. No failed calls, no unknown outcomes, no unknown usage or
cost. Mean judge score **0.3657**, weighted identically since all ten types
carry nine questions.

| Question type | n | Mean |
|---|---:|---:|
| preference_following | 9 | 0.926 |
| instruction_following | 9 | 0.639 |
| abstention | 9 | 0.611 |
| summarization | 9 | 0.431 |
| event_ordering | 9 | 0.339 |
| multi_session_reasoning | 9 | 0.331 |
| contradiction_resolution | 9 | 0.194 |
| information_extraction | 9 | 0.130 |
| knowledge_update | 9 | 0.056 |
| temporal_reasoning | 9 | 0.000 |

Cost: Modal $1.6269, OpenAI $3.1650 across 555 calls, 4.54M input tokens and
166k output tokens of which 89k were reasoning. Evaluation elapsed 4,345s.

Against the predictions registered at 08:20, before any result existed:
- "lands near 0.4488 and probably below it" — correct, 0.3657. The earlier
  partial figure was optimistic exactly as expected, because it covered only
  the four smallest 100K histories and excluded both 500K conversations.
- "temporal reasoning stays near zero" — correct, and it is exactly 0.000 across
  all nine questions.
- "knowledge update stays low" — correct, 0.056.
- Extraction was cheaper and faster than predicted: $1.63 rather than about
  $2.40, finishing in 25 minutes of a 120 minute window.
- OpenAI came in at $3.17 against an estimate of about $2.50, still well inside
  the $10 authorized.

Verdict: kept, and this is the first reportable Gemma 3 4B BEAM score. Context
for comparison: the article reports 61.3 for its memory system and 39.7 for
full history on BEAM. A 4B extractor at 36.6 sits below both. The category
profile is the useful signal, not the headline: Gemma is strong where the task
is to follow a stated preference or instruction and to abstain, and it fails
where the task requires resolving time or superseding an earlier fact. That
matches the smoke's manual review, which found unresolved relative dates and
repeated facts that should have been superseded.

Note on the earlier 0.4488: it must not be cited. It was 40 of 90 questions
drawn only from small histories.

## 2026-09-14

### 10:28 — LongMemEval Qwen 9B GPU sizing smokes (vllm-24b712233b8c351f, vllm-5c1586542f6d1508)
Tried: two extraction-only smokes on the same 48 LongMemEval histories, first
two sessions each (96 updates), from `experiment_specs/longmemeval-qwen-9b-smoke-c24.json`
on one L40S (concurrency 24, reservation $1.50) and `...-smoke-c48.json` on one
H100 (concurrency 48, reservation $2.50). Same model revision, prompts, BF16,
structured output, 65,536 window, 8,192 batched tokens. New `tools/modal_smoke.py`
drives prepare, launch, and collect; `GPU_RATES` gained H100 at $0.001097/s from
the Modal pricing page. Directories `work/qwen_lme_smoke_l40s_c24` and
`work/qwen_lme_smoke_h100_c48`. No answering or judging.
Goal: size the LongMemEval final-100 run (4,803 updates, est. 55M to 90M prompt
tokens). The frozen preset uses concurrency 4 on an L40S, projected at about 5
hours and $16 to $18 of GPU, over the 7,200-second single-sandbox cap. The user's
own estimate for the full run was about $35.
Expected: L40S at 24 in flight reaches 1.0 to 1.5 updates/s (LoCoMo final at
concurrency 8 with 10 chained histories measured 0.25). H100 at 48 in flight
reaches 2.5 to 4 updates/s, so cost per update is equal or lower than L40S
despite the 2x per-second price. Per-call latency stays 10 to 15 s on L40S and
drops to 6 to 10 s on H100. Prefix-cache hit rate on session 2 is nonzero if
vLLM 0.21 caches Qwen3.5's hybrid state; the repo notes this as experimental.
Startup 4 to 5 minutes each; actual accounted cost about $0.8 to $1.0 each.
The user authorized this spend in chat on 2026-09-14; it is outside the earlier
$30/$35 Modal ceiling, which was already reported exhausted.
Got: run vllm-b04b810e02da9352. 120/120 updates valid, 229 s extraction wall
after 253 s startup, accounted $0.9867. Prompts grew from 2,169 tokens at
session 1 to 9,722 at session 24, about 330 tokens per update, far below the
15k to 25k expected; memory reached 87 to 144 lines per history. Output
averaged 189 tokens per update. Per-update elapsed stayed at 4 to 10 s
(mean 7.4) with no trend against prompt size; time to first token was 0.4 to
1.4 s on prompts up to 9.7k tokens, so a single prefill runs at roughly 7k to
10k tok/s and decode dominates each call. Chains of 24 updates took 128 to
228 s per history. Prefix-cache hit rate was 0.0 percent in every stats line
until the last three requests, where it reached 5.9 percent: the Mamba align
cache does not reuse the memory prefix between updates, and the 15.6 percent
seen in the c24 rerun was the shared system prompt across 48 histories.
Verdict: kept as the sizing basis. Extrapolating 330 tokens per update to 48
sessions gives about 490k prompt tokens per history and 49M for the final
100, plus about 1M output tokens. Every prompt is prefilled in full. At the
L40S engine's observed 5k to 7k prompt tok/s ceiling that is 1.5 to 2.5
hours and $5 to $8, at or over the 7,200-second single-launch cap; an H100
at three to four times the prefill rate is about 35 to 50 minutes and $4 to
$5 in one launch, but pays a first-boot compile that took more than 8.5
minutes before (limit now twenty minutes). Four smokes today total $4.55.

### 11:05 — Debounced checkpoint commits, L40S smoke rerun (work/qwen_lme_smoke_l40s_c24_v2)
Tried: `adaption_memory/execution/vllm_worker.py` now routes every persist and
stream snapshot through a `Committer` that marks the volume dirty and syncs
at most once per 5 seconds from a background task, with an explicit flush
after `loaded.json` and at the end of the run. The worker's startup limit
rose from ten to twenty minutes. Two unit tests cover coalescing and flush.
Same 48 LongMemEval histories, two sessions each, L40S, concurrency 24,
$1.50 reservation; new directory because the worker's code hash is part of
the payload fingerprint.
Goal: confirm the serialized `sync /state` calls were the throughput limiter
in the 10:28 smoke, where the engine ran 2 to 5 requests instead of 24.
Expected: engine stats show 15 to 24 running requests most of the time,
per-call elapsed rises to 40 to 60 s from real batching, and aggregate
throughput reaches 1.0 to 1.5 updates/s against 0.41 before, so the 96
updates finish in 65 to 100 s of extraction wall. Accounted cost about $1.0.
Prefix-cache hit rate stays at zero since nothing changed on the engine side.
Got: pending.
Verdict: pending.

### 11:20 — Late-session L40S smoke, 5 histories x 24 sessions (work/qwen_lme_smoke_l40s_late5x24)
Tried: same c24 preset and debounced worker, first 5 LongMemEval histories
run through their first 24 sessions each (120 updates), one L40S, $2.00
reservation. Only 5 requests can be in flight, so this measures per-update
prefill and prefix-cache behaviour on long prompts, not batch throughput.
Goal: decide whether the LongMemEval final-100 is prefill-bound on the L40S.
Late-session prompts carry the whole memory so far; if vLLM's prefix cache
hits on that shared prefix, prefill per update shrinks to the new session
plus new lines and the full run fits one L40S launch.
Expected: prompt size grows from about 3k to 15k to 25k tokens by session 24.
Prefix-cache hit rate climbs past 50 percent by mid-run if the Mamba align
cache works across updates; if it stays near 15 percent the cache is only
catching the system prompt. Time to first token on a 20k prompt is 3 to 5 s
without cache hits and under 1 s with them. Per-update elapsed 15 to 25 s,
decode-dominated. Extraction wall 8 to 12 minutes; accounted about $1.2.
Got: pending.
Verdict: pending.

### 12:05 — LongMemEval Qwen 9B final-100 launched on H100 (qwen9b-longmemeval-100-001)
Tried: canonical CLI run of the new frozen spec
`experiment_specs/longmemeval-qwen-9b-h100-final100.json`: same 100 questions
and model revision as the final-100 preset, concurrency 48, new `gpu` preset
field set to H100. Presets gained an optional `gpu`, read by
`modal.build_payload` ahead of the model default. Modal cap $9 (sandbox
lifetime 96 minutes), OpenAI cap $10 for answering and judging. Runs on the
fresh `hellgod67` workspace: both volumes are created empty, so the image
builds from scratch and the 9B weights download and compile on first boot.
The user authorized both caps in chat on 2026-09-14; earlier Modal ceilings
belonged to the previous workspaces.
Goal: the first completed LongMemEval result for the Qwen 9B extractor,
filling the "No completed results" cell in the comparison table.
Expected: startup 10 to 15 minutes including image build and download; 4,803
updates in 35 to 50 minutes at 1.6 to 2.3 updates/s; about 49M prompt and
1M output tokens; all 100 histories complete with few or no invalid outputs.
GPU accounting $4 to $6 upper bound; OpenAI $2 to $3. Accuracy near the
Luna extractor's 85/100 is plausible given Qwen 9B matched Luna on LoCoMo
and BEAM 500K, but the smokes measured speed, not quality, so no prediction
beyond 75 to 88 correct.
Got: no extraction. The H100 sandbox (sb-ivEB73hBuQ7bYiRZrdKsSq) loaded
weights in 15 s and finished torch.compile at 04:50:58 UTC, then logged nothing
until the worker's twenty-minute limit wrote `fatal.json`
(`TimeoutError: vLLM startup exceeded twenty minutes`) at about 05:08. This is
the same silent stall as the 10:28 H100 smoke, now with twice the allowance,
so it is not a slow first boot: vLLM 0.21 with Qwen3.5-9B hangs on Hopper in
the profile and warmup step after compile, most likely an unlogged kernel JIT
that the cache volume does not persist. On the L40S the same step takes 2.6
minutes. Sandbox terminated explicitly (exit 137); about 22 minutes of H100
at $0.001468/s, roughly $1.95 of the $9 reservation. The collector imported
no memories, so the OpenAI ledger spent nothing. The image build and weight
download on the fresh workspace succeeded and are cached for later launches.
Verdict: abandoned for the H100. Two identical failures at the same point
are enough; diagnosing Hopper support costs more than the L40S run it would
save. Relaunched on the L40S as run 002 below with the sandbox lifetime cap
raised from 7,200 s to four hours so one launch can finish.

### 12:12 — LongMemEval Qwen 9B final-100 relaunched on L40S (qwen9b-longmemeval-100-002)
Tried: new frozen spec `experiment_specs/longmemeval-qwen-9b-l40s-final100.json`,
identical to the H100 spec except `gpu: L40S` and concurrency 24. Modal cap
$10 (sandbox lifetime 2.9 hours after the raised cap), OpenAI cap $10. Same
fresh workspace; weights already cached from the H100 attempt.
Goal: same as the 12:05 entry.
Expected: startup 4 to 6 minutes (fresh compile for the L40S). 4,803 updates
at 1.0 to 1.5 updates/s once prefill on the late sessions bites, so 55 to 85
minutes of extraction and GPU accounting $4 to $6. All 100 histories
complete. Answering and judging $2 to $3. Score 75 to 88 of 100.
Got: **61 of 100** (61 correct of 97 graded; the 3 histories lost to the
structured-output whitespace loop count as wrong). Per type: knowledge-update
11/18, multi-session 10/16, single-session-assistant 4/16,
single-session-preference 13/18, single-session-user 11/16,
temporal-reasoning 12/16. Extraction: 4,750 updates in 4,768 s (0.996/s)
after a 6-minute startup, 42.9M prompt tokens and 0.72M output tokens, GPU
accounting $5.35 upper bound. Answering 97 calls, mean 8,726 input tokens
(about 8 percent of the 110k-token histories), $0.18; judging $0.54. Total
$6.07 plus the H100 false start. Grading was interrupted by the network
outage at 07:01 UTC and finished after the person-run reconciliation; the
run manifest is `blocked` because of the 3 blocked histories. Report in
`reports/qwen9b-longmemeval-100-002/`.
Verdict: kept as the first completed Qwen 9B LongMemEval number, and it
contradicts the prediction. Timing and cost landed inside the expected
ranges; accuracy did not. Against the Luna extractor's 85 the loss is
concentrated in single-session-assistant (4/16 versus Luna's 12/16), the
questions that need what the assistant wrote, plus the three whitespace-loop
failures. See `docs/extractor-size-analysis.md`.

### 12:25 — Mem0 on BEAM: shared-store executor implemented, not launched
Tried: `adaption_memory/execution/mem0.py` builds one Mem0 store per history
(mem0ai 2.0.20, Qdrant local, text-embedding-3-small, GPT-5.6 Luna at low
reasoning, four messages per add) and writes the same per-history checkpoint
layout the Modal executor does; `Coordinator.import_memories` replaces
`import_modal_memories` and takes the executor's cost record, so answering
and judging reuse the pipeline. The answer prompt is byte-identical to the
retired runner's no-retrieval mode (sha256 pinned in `test_mem0_executor.py`).
Presets accept `system: mem0` with `executor: mem0`; new spec
`experiment_specs/beam-mem0-final90.json`, concurrency 7. Mem0's OpenAI
clients are wrapped so each call reserves and settles on the run's ledger.
Goal: fill the two "Not run" BEAM cells in the Mem0 column without the old
runner's cost. The old design built a store per question: 90 BEAM
ingestions over about 33M conversation tokens, $40 to $50 at the measured
$1.2 per million (LongMemEval, chunk 4) and 10+ hours, which is why BEAM
Mem0 was skipped. One store per history is 7 ingestions over 2.08M tokens.
Expected (when launched): ingestion $2.5 to $4 and about one hour, the
1,234-message 500K chat being the critical path at 309 sequential adds;
answering and judging $1 to $1.5. Requested cap $8. Accuracy near Mem0's
LoCoMo behaviour, a few points under full history: 30 to 36 of 50 at 100K,
20 to 26 of 40 at 500K.
Got: 128 tests pass, including build, resume, interrupted-session refusal,
budget refusal, import, and Mem0-prompt answering with a stub store. No paid
call has been made through the new path yet; a real one-history smoke is the
first step once a cap is approved.
Verdict: pending launch approval.

### 12:35 — Mem0 live smoke on one BEAM history (work/mem0_beam_smoke_1x2)
Tried: `tools/mem0_smoke.py` on the first BEAM 100K history, first two
sessions, through the new metered executor, $0.50 ledger.
Goal: prove the wrapped Mem0 clients, budget accounting, checkpoint layout,
and line ordering against the live API before the 90-question run.
Expected: about 8 adds, one LLM call each, a few cents, memories dated
March-15-2024 in stored order.
Got: 10 adds over 32 messages, 10 LLM calls (Mem0 2.0.20 is add-only, one
call per add, confirmed), 20 embedding calls, 50 memories, all ADD events.
Per session about 55k prompt tokens of which 55 to 69 percent cached, 2.7k
output with 0.7k reasoning; $0.0169 total, 95 s wall, 9.5 s per add.
Memories are dated, specific, and readable (sample in the smoke summary).
Verdict: kept. Extrapolated to BEAM's 3,320 messages (about 853 adds):
ingestion about $1.5 and 50 minutes wall with all seven histories in
parallel, the 1,234-message 500K chat setting the critical path. Answering
40 questions over roughly 70k to 100k tokens of 500K memories plus 50 over
about 20k is under $1; BEAM judging with GPT-5 about $1 to $1.5. Expected
total $3.5 to $4.5 under an $8 cap.

### 13:40 — Mem0 BEAM final-90 launched (beam-mem0-90-002)
Tried: canonical `run` of `experiment_specs/beam-mem0-final90.json` from an
isolated source copy (`/private/tmp/adaption-beam-mem0`), $8 OpenAI cap shared
by ingestion, answering, and judging. Seven histories build in parallel,
adds sequential within a history; then serial answering and judging.
Goal: fill the BEAM 100K and 500K cells of the Mem0 column.
Expected: about 853 adds, ingestion $1.5 in about 50 minutes (the
1,234-message 500K chat is the critical path); answering plus judging
$2 to $2.5 over 30 to 45 minutes; total $3.5 to $4.5. All seven stores
complete. Accuracy 30 to 36 of 50 at 100K and 20 to 26 of 40 at 500K.
Got: **36 of 50 at 100K (72%) and 27 of 40 at 500K (67.5%)**, 63 of 90,
mean nugget scores 0.673 and 0.615, all 90 answered, no failures. Seven
stores, 853 adds, 3,655 memories (161 to 1,140 per chat). Ingestion $1.20
by the session call records; answering $0.79 (mean prompt 17.4k tokens at
100K, 70.5k at 500K); judging $1.49; total $3.48 plus the $0.017 smoke.
Ingestion took about 50 minutes of work spread across the network
interruption (launched 06:37 UTC, stopped 07:06, resumed 07:14, stores
complete 07:36); serial grading 66 minutes. The run's executor cost
artifact says $0.31 because `build()` summed the resumed process's ledger
rather than the call records; fixed for future runs (sum of session call
costs), and the artifact is left as written since the run is terminal.
Report in `reports/beam-mem0-90-002/`.
Verdict: kept. Accuracy came in at the top of the expected range on 100K
and above it on 500K, where Mem0 edged full history (27 vs 26) and both
memory extractors (24). Cost landed under the estimate. The shared-store
design turned a run that was skipped as unaffordable into $3.50.

### 14:10 — OpenAI unreachable from this network; both runs stopped by hand
Tried: nothing new. At 07:01 UTC every answer call in the LongMemEval
grading loop started failing with `APIConnectionError: Connection error.`
after 3 to 4 s, and the Mem0 build's in-flight adds failed the same way.
`curl -v https://api.openai.com` shows the TLS Client Hello reset by peer in
under 0.1 s on every attempt, while api.anthropic.com, modal.com, and
github.com answer and status.openai.com reports all systems operational.
This network resets api.openai.com; nothing was sent. Killed the LongMemEval
collector (pid 84667) and the Mem0 run (pid 84907) at 07:06 to stop the
cascade of unknown outcomes.
Got: LongMemEval run 002: extraction finished on the sandbox at 4,750/4,803
updates in 4,768 s (0.996 updates/s, concurrency 24), 97 histories complete,
3 stopped by the structured-output whitespace loop (ebea1f90, 43482c7f,
ea2086bd), GPU accounting about $5.3. Grading reached 19 questions, 10
correct, before the outage; 17 answer calls recorded `unknown_outcome`
(question ids listed by `tools/reconcile_connection_failures.py`); 61 remain
`memory_complete`; 3 `blocked_memory`. Mem0 run 002: five 100K stores
complete; the 500K stores stopped mid-session at 37/53 and 41/81 sessions,
with 16 and 4 memories already written for the interrupted sessions;
ingestion so far 638 adds, $0.89.
Verdict: paused, not lost. Two person-run reconciliations are prepared and
dry-run: `tools/reconcile_connection_failures.py` returns the 17 calls to
`not_dispatched` with the evidence recorded as a chained call state, and
`tools/mem0_rollback_partial_session.py` deletes the 20 partial memories and
drops the in-flight call records so the sessions re-ingest without
duplicates. Both wait for approval and for a network where api.openai.com
completes a TLS handshake; then the same resume/run commands from the
isolated copies finish both runs.

### 15:25 — Concurrent grading, and resume gated on configuration instead of code
Tried: `Coordinator.run` answers and judges questions in a worker pool sized
by the spec's `concurrency`, with one lock around artifact writes, row
updates, and checkpoints (`update()`, `put()`, `checkpoint()`). The OpenAI
transport gained `reservation_wait_seconds`: a call whose upper-bound
reservation does not fit the cap waits (5 s polls, up to 30 minutes from the
CLI) for in-flight calls to settle instead of recording a failed attempt.
`Coordinator.open` replaces the full-spec-hash gate: a run must match the
experiment configuration hash; a changed implementation is recorded as an
`implementation_change` artifact (previous and new spec hashes, revisions,
current source hashes, generation) and the manifest moves to the new spec
hash. Modal and Mem0 payload fingerprints now exclude `code_sha256`, so
checkpoints survive source edits and `prepare` on an existing directory
rewrites the recorded code hashes instead of refusing. `reconcile` and
`retry` use the configuration check. Docs: architecture persistence
contract and README.
Goal: stop paying serial grading time (50 minutes for 100 LongMemEval
questions, 40 for 90 BEAM) and stop losing runs to the code-hash gate,
which killed the first LongMemEval collector this morning and forced both
runs onto isolated source copies.
Expected: grading wall time divided by the worker count for new runs;
existing runs continue after a code change with the change on record;
a changed prompt, model, or question set still refuses.
Got: 132 tests pass, including a pooled fixture run that observes overlapping
calls with intact checkpoints and unique call ids, an implementation change
recorded on resume, a configuration change refused, and a Modal payload
fingerprint stable across a source-hash change. No paid run has used the
pool yet; the two runs in flight still run the old serial code from their
isolated copies.
Verdict: kept. New specs should set `judge_max_tokens` near the judge's real
output, since each concurrent judge call reserves that allowance at the
judge's output price; the frozen specs keep 128k and rely on the wait.

## Task log, 8 to 12 September (formerly the root PROGRESS.md)

Task-oriented entries kept from the second log; the dated entries above are the primary record for the same period.

### Gemma 3 4B extractor smoke, 2026-09-12

**Status:** four-update live smoke complete; usable but not fidelity-ready.

- Added a model-profile layer under `extractors/vllm.py` so model sampling, GPU,
  gated access and engine settings no longer require another Qwen-specific branch.
- Pinned `google/gemma-3-4b-it` at `093f9f388b31de276ce2de164bdc2081324b9767`.
  Hugging Face access verified. Ran BF16 on one Modal L4 with two concurrent
  histories and two updates per history.
- First attempt reached a healthy server but produced zero outputs because Gemma's
  chat template rejects consecutive user messages. The corrected run joined the
  same ordered prompt blocks into one user message. Prompt text and source data did
  not change.
- Corrected run completed 4/4 updates with valid JSON and no runaway repetition:
  8,168 input tokens, 1,119 output tokens, 14.26s mean call time, 40.47s extraction
  wall time. Total accounting across both attempts is $1.4600 under the user-approved
  $5 smoke budget. Actual Modal invoice remains unverified.
- Manual review found good readability and mostly grounded extraction, but strict
  fidelity still fails: unresolved relative dates, unstable keys, paraphrased
  atomic values, one inferred business name, repeated facts, and one clear Paris
  speaker-attribution error. Verdict and evidence: `docs/gemma3-4b-smoke.md`.
- Full offline suite: 112 tests passed. No answering, judging, full benchmark,
  fine-tuning, commit or push performed in this task.

### Task: Replace sequential GPU runner with cloud-owned vLLM pipeline, 2026-09-11

**Status:** implementation complete, live validation in progress.

- User explicitly stopped the current run. Terminated `sb-D2FR0jmZXdkpwfuqIUKq2u`, exit 137 confirmed; old controller exited and accounted the attempt at $1.69831. Both old baseline attempts total $3.16795 including allowances. Historical state and source snapshots preserved under `work/qwen_beam_baseline/`; obsolete executable controller, acknowledgement worker and transition script removed, report caller updated.
- Invalid outputs diagnosed as misspelled schema key `narrature` and malformed JSON punctuation. No failures were silently corrected. New engine is a separately fingerprinted variant using existing schema-constrained output; engine/decoding changes are not attributed solely to training quality.
- Added `beam_final_inputs.py`, `qwen_vllm.py`, `qwen_vllm_worker.py`: pinned vLLM image built before GPU allocation; persistent model/compile cache; at most two concurrent requests from independent histories; chunked prefill and experimental hybrid prefix caching; per-history cloud checkpoints with Volume v2 sync; independent reconnectable collector and answer/judge execution. Each history stays sequential and question-blind. No laptop acknowledgement in the GPU critical path. No automatic GPU replacement or uncertain-call replay.
- Six async regression tests added. Full suite 68 passed; git diff whitespace check passed. Old runner source imports removed. Documentation: `docs/qwen-vllm-inference.md`.
- Four-update smoke configured under `work/qwen_vllm_smoke/`, two original histories, no final answering. $2 launch reservation includes prior costs against the original baseline $10 allocation. Live dependency image build underway; no speedup or live vLLM success claimed yet. New full baseline not launched. Overall Modal cap remains $30. Two-minute monitor now tracks the new cloud ledger, not the stopped sandbox.

#### Cloud smoke launched and restart controls tested

- Reusable image `im-AVJnDICbscYGPY2qXmAgIa` built successfully before GPU allocation. Smoke sandbox `sb-TOe7GEGuBFzBkcz5goODNl` running with a 1,642-second lifetime. Pinned Qwen weights downloaded and loaded; engine logs confirm FlashAttention/GDN prefill and cached compilation. First-start warmup still underway at this checkpoint.
- Added explicit `resume_qwen_vllm.py`: exact frozen image and cloud state reused, previous costs retained, unknown/invalid histories refused. Collector can reconnect separately. Tests now 69 passing; command help and whitespace checks passed. GPU-kill recovery has not been fault-injected live. No full baseline launch or speedup claim.

#### Live vLLM validation passed

Four of four updates completed with valid JSON across two histories. Extraction wall time 33.66s; first engine startup 349.71s. Cloud checkpoints and progress copied successfully without per-update laptop acknowledgement. Sandbox exited and termination confirmed by collector. Accounted estimate including $0.50 allowance: $0.90264, below $2 reservation; actual invoice unverified. Full benchmark not launched. Results and limitations: `docs/qwen-vllm-smoke.md`. Teacher remains stopped at 578/588 with an uncertain timeout; no paid teacher retry made during this implementation task. All launched jobs are now stopped; monitor may pause after reporting outcomes. No commit or push requested.

### Teacher stopped short of completion, 2026-09-11 07:17 UTC

Teacher controller ended at 578/588 updates, 15/16 complete histories. One history needs reconciliation; this is not budget exhaustion, accounted upper bound including reservations $4.24123. Do not automatically replay its uncertain call. Qwen controller remains active at 17 completed updates, three invalid-output histories, zero graded answers. No decoding or input settings changed by the monitor.

### Qwen invalid outputs detected, 2026-09-11 07:14 UTC

Live monitor: teacher 573/588, controller active. Qwen 11 completed updates, controller active, but two history checkpoints now carry invalid_output; zero graded answers. The worker skips blocked histories and continues others rather than answering from incomplete memories. Do not treat these as benchmark wrong answers or change decoding/output limits silently. Inspect the saved failed calls before deciding a separately recorded repair or rerun.

### Teacher accounting corrected and resumed, 2026-09-11

User authorized correction and continuation under the unchanged $10 teacher allocation. Repriced the 548 saved responses using reported cached/uncached input and total output tokens, including reasoning exactly once. Conservatively applies cache-write uplift to all uncached tokens; long-context uplift only above 272K actual input. Successful-call upper estimate is $2.15057907, not the previous $8.0734482; six abandoned unknown-call reservations remain $1.6088235. Starting accounted total therefore $3.75940257 before new in-flight reservations. Original configuration/accounting archived in `work/beam_teacher_traces/accounting_reconciliation.json`. Prompt, model, decoding and max-output cap unchanged; worst-case pre-dispatch reservations retained. Restart confirmed with new updates 549-552 saved. Qwen L40S also advancing, four saved updates confirmed. Full suite: 63 tests passed, including cache discount, long-context uplift and no double-counting of reasoning. No increased budget or new unknown-call replay.

### Qwen restarted on L40S, 2026-09-11 07:07 UTC

User explicitly requested continuation after sizing. Archived the original configuration, payload, first A100 checkpoint and attempt ledger in `work/qwen_beam_baseline/runtime_transition.json`; retained the original checkpoint and spending. Recorded L40S batch-size-one execution, unchanged model revision/prompts/precision/decoding/final questions, and mixed-hardware provenance. Fixed acknowledgement regression is covered by a durable-save-before-ack test. TLS uses the existing verified certifi bundle, and the sandbox has an overall lifetime limit instead of the unsafe 60-second setup idle timeout. New sandbox `sb-D2FR0jmZXdkpwfuqIUKq2u` confirmed in setup, controller session 7931, 8,500-second limit and $8.09138 reservation within the original baseline allocation after prior accounting. No new completed inference claimed yet. Two-minute monitor updated to inspect the current sandbox ledger rather than the terminated original sandbox. Teacher invocation ended at 548/588, 14/16 histories complete, accounting upper bound $9.68227; remaining work budget-blocked. No teacher budget expansion made.

### L40S sizing completed, 2026-09-11 07:00 UTC

All six measurements completed; sandbox termination confirmed. Both 16,022- and 36,620-token prompts fit on L40S in BF16, individually and together. Sequential pair times 49.37s and 47.19s; batch times 56.58s and 56.98s. This padded batch was 15-21% slower, not faster; peak allocated memory increased from 27.28 GiB to 40.07 GiB. All eight generated outputs across four single calls and two two-row batches stopped with valid JSON, but single/batch texts differed; factual quality not graded. Report: `work/qwen_gpu_sizing_l40s/summary.md`. Combined resource estimate across failed and successful attempts $0.64426; retaining both $0.50 allowances gives $1.64426 accounted, below the $2 sizing cap. Invoice unverified. Teacher at 487/588 with 14 histories complete and two advancing. Baseline remains paused at one checkpoint; no automatic GPU restart. L40S single inference is the measured candidate, not a demonstrated fit for every future BEAM prompt.

### Continuation and L40S sizing, 2026-09-11

User requested continuation. Read-only OpenAI connectivity passed. Explicitly reconciled six unrecoverable teacher attempts using `reconcile_teacher_calls.py`: original calls and full reservations retained as abandoned_unknown, replacement attempts allowed, prior configuration archived. No completed memory rebuilt. Teacher restarted with the same $10 allocation and two workers; fresh saved updates confirmed. Added a regression test for retained charges after an explicit replacement. Qwen host acknowledgement now uses named SDK arguments, with a test checking durable save before acknowledgement. Baseline fingerprint reconciliation and full restart remain pending sizing results.

Added `qwen_gpu_sizing.py` and offline `report_qwen_gpu_sizing.py`. Fixed two pilot prompts, BF16, thinking off, sequential versus batch size two in opposite-order repetitions; no final scores used for hardware selection. First L40S attempt failed before inference during file transfer because Python's default CA bundle was absent; sandbox termination confirmed, resource estimate $0.25498 plus retained $0.50 allowance, not an invoice. Verified TLS using existing certifi, keeping certificate verification enabled. Explicit replacement retains the first attempt in its ledger and reduces timeout to keep both sizing attempts within $2. Teacher and sizing are separate active jobs; two-minute ASCII monitor re-enabled. All prior Modal baseline spending remains recorded and the overall Modal cap stays $30.

### Both experiment controllers stopped, 2026-09-11 05:19 UTC

Teacher saved 274/588 updates and completed 10/16 histories. Its invocation ended at 04:55:43 UTC after two APITimeoutError and four APIConnectionError outcomes; all six affected histories require reconciliation before any paid replay. Accounting upper bound is $4.7303291, including uncertain-call reservations, not an invoice. Both controller locks are unheld. Qwen remains at 1/203 updates, zero graded answers out of 90, with its original sandbox termination confirmed in the attempt ledger. L40S sizing code was written but no sizing run ledger exists and no test has launched. No automatic restart or new paid calls. The two-minute monitor is being paused after reporting these terminal invocations; the underlying experiments remain incomplete.

### Qwen interruption and reminder update, 2026-09-11

User requested ASCII progress on every five-minute reminder and a Qwen ETA. Live inspection found Qwen paused after one durable checkpoint. `qwen_beam_baseline.py` passed `Sandbox.filesystem.write_text` positional arguments in the wrong order while acknowledging that checkpoint; the SDK treated the receipt as a path and raised InvalidError. The first 43.92-second inference result is saved locally. Sandbox termination is confirmed. Attempt elapsed 476.17 seconds, accounted resource-plus-reserve estimate $1.46964, not a verified invoice. No automatic restart was made. Teacher is still running. Reminder updated to send extraction and graded-answer progress bars every check and label Qwen paused. Fix and explicitly reconcile operational code fingerprints before resume; do not discard the checkpoint or reset spending.

### Task: Resumable teacher generation and Qwen BEAM baseline, 2026-09-11

Status: running. User requested two asynchronous jobs with resume support, then narrowed Qwen to BEAM final only. OpenAI cap raised from $10 to $30 explicitly; Modal cap remains $30. Current allocations: teacher OpenAI $10, baseline OpenAI $20, baseline Modal $10. No training or synthetic-generation job launched.

- Added durable checkpoints and locks in `checkpoint_io.py`, resumable teacher generation in `teacher_traces.py`, GPU worker/controller in `qwen_beam_worker.py` and `qwen_beam_baseline.py`, per-call answer/judge checkpoints in `beam_baseline_answers.py`, and `report_beam_baseline.py` for the historical Luna comparison. Unknown paid API outcomes block replay and retain reservations. GPU checkpoints require a durable host acknowledgement before proceeding.
- Full requested dev/all-final workload was counted at 5,428 extraction steps. Two prior pilot calls extrapolated to 42.84 hours / $152.11, excluding API stages, so it was not launched under the $30 Modal cap. User narrowed scope to seven BEAM-final histories, 203 extraction updates and the original ninety questions. Earlier projection saved by `baseline_workload.py`; it is not the current scope or a measured run cost.
- Current Modal pricing and Luna pricing verified from official docs. Luna cache-write/long-context uplifts require a more conservative runtime reservation than the old point forecast. No credentials displayed. Account credit balance is unverified; explicit numeric caps bound execution, and no top-ups/overages beyond those caps are authorized.
- Teacher launched under managed terminal session 9772 after a nohup attempt exited without creating checkpoints. Confirmed no old process before restart. Real teacher updates are now checkpointing. Baseline managed terminal session 16300 created sandbox `sb-LfwS5Q36i6MMPReQkfF1fk`, with 8,500-second lifetime and $9.38338 resource-plus-overhead reservation. Setup/inference status must be checked before claiming completed GPU inference.
- Initial workload script incorrectly used `benchmarks.load_items('longmemeval')`; corrected to the separate LongMemEval dataset loader. The Modal CLI has no `sandbox` command in installed 1.5.5; used documented SDK listing, which found no active sandboxes before launch. Initial teacher test fixtures omitted session IDs; corrected fixtures and reran. First local `ps` was sandbox-denied; read-only escalation confirmed the old process had exited.
- Ten new offline teacher/API resume tests passed before paid launches. Full suite completed with 57 tests passing. Tests cover skipping saved calls, saved-response replay without a paid call, unknown-outcome blocking, budget-before-dispatch and changed-input rejection. Remote crash/reconnect behavior is implemented but not yet fault-injected on a live GPU.
- Live checkpoint: more than fifty real teacher updates saved; Modal dependencies installed successfully and worker/model loading began. GPU extraction output is not yet confirmed at this checkpoint. Created thread heartbeat `teacher-and-qwen-beam-run-checks` every five minutes, quiet during normal progress and notifying only meaningful outcomes. First automation call lacked destination and was rejected; adding `destination=thread` created it successfully. Monitoring must not automatically replay uncertain paid calls or create replacement GPU jobs.
- See `docs/resumable-teacher-and-baseline.md` for scope, resume commands and limits. Raw states remain ignored under `work/`. Next: verify live GPU output, monitor completion/errors, then generate aggregate comparisons. No commit or push requested.

### Task: Rebalance BEAM topics, 2026-09-11

Status: complete for rebalanced source selection. Preserve the original split under `work/beam_split/`; the revised audit targets `work/beam_split_v2/`. Swap 100K self-editing ID 10 into dev and patent ID 20 into train, so dev has writing and legal topics. Replace 500K chronic illness ID 24 and photography ID 25 with coding ID 3 and math ID 7. Keep finance and sports represented in train and dev. Final lists and split sizes remain unchanged. Remove the overly broad cross-tier numeric-ID exclusion; retain exact source-overlap guards. Selection uses topics, not grades. No paid calls.

- All sixty source files hash-verified; no exact overlaps across 190 selected-history pairs or with the protected pool. Final manifest equals the prior final manifest exactly. Forty-seven tests passed. The two replacements have 49 and 59 windows, so train is now 588 slots, not 600; dev remains 150 steps / 80 questions. No truncation.
- Active plan and split decision now point to the rebalanced manifests and `docs/beam-split-rebalanced.md`. Earlier report preserved and marked historical. Forecast train writing $1.88-$3.40 at historical rates; not verified current cost or a hard cap. Full Modal estimate, paid execution and target quality remain pending. No commit or push.

### Task: Implement the approved BEAM split, 2026-09-11

Status: complete for BEAM source selection and manifests. Prepared sixteen new train histories and four separate dev histories, preserving exact original 50-question 100K and 40-question 500K final lists. The replacement `prepare_beam_split.py` writes separate train/dev/final manifests and checks source hashes and overlap. Earlier source caches/reports remain unchanged. This preparation makes no model calls; LongMemEval and LoCoMo remain additional evaluations and are not reselected here.

#### Split audited and saved

- All sixty new JSON sources verified at pinned BEAM revision. Sixteen train histories yield 600 update slots; four dev histories yield 150 steps and 80 questions. Final preserves ninety unique questions across seven histories. No overlap with the ten protected local histories or across 190 selected-history pairs using exact windows/pairs. Semantic overlap is not certified.
- Saved `work/beam_split/{train,dev,final,report,source_manifest}.json` and `docs/beam-split-audit.md`. Final selection hashes are fixed in code; report includes history/source/code hashes. Offline rerun passed. Actual teacher targets, Qwen prompt fit and full Modal workload cost remain unverified.
- Forty-six unittest tests passed including five new split guard tests. No paid calls; test spend output is mocked. `git diff --check` passed. During editing, a source helper name was corrected to the existing `source_files` before the final offline run; no failed model jobs or data changes resulted.
- Teacher-writing forecast using historical rates: train $1.85 cached to $3.44 uncached; optional teacher dev $0.48 to $0.88. Not a quote or hard cap. Student dev must use its own extracted memories, not teacher memories.
- Next: budget the three-arm inference workload and verify credits before teacher generation. No commit or push requested.

### Task: Record authoritative BEAM split decision, 2026-09-11

Status: complete. Saved `docs/beam-split-decision.md` and synchronized the execution plan. Train: eight new histories per tier. Dev: two other new histories per tier. Final: all five existing 100K histories with the original 50 questions and both existing 500K histories with the original 40 questions. No final expansion or two-history 100K subsampling. LongMemEval and LoCoMo remain additional final evaluations. New train/dev selection and overlap verification remain pending; no dataset selections or model jobs changed in this documentation step. Earlier eight-history audit marked historical. Next: implement the full source split and workload estimate.

### Task: Matched no-retrieval comparisons, 2026-09-09

Status: in progress. Scope: LoCoMo shared 50; LongMemEval second 50. No BEAM or first-50 ingestion.

- Verified complete saved Mem0 stores for LoCoMo 50 and LongMemEval 49. Only `3b6f954b` may be recreated.
- Implementing explicit all-memory reuse with per-question source provenance, complete-history checks, prompt-fit checks, and no search.
- Budget allocation: LoCoMo at most $5; LongMemEval at most $10. Combined authorized ceiling $15. Existing writing costs excluded from incremental spend.
- Existing retrieval runs are preserved. No paid calls made yet.
- Next: offline validation, preflight estimates, then paid runs and matched comparisons.

#### Offline checks passed

- Three unit tests passed: full-memory inclusion/no search, overflow rejection, budget blocking and retained reservations after unknown failures.
- Corrected an estimate lookup from `input_tokens` to `input_tokens_estimated`; initial LoCoMo estimate overstated inputs. No paid calls occurred during correction.
- Final preflights: LoCoMo `20260909T121140756473Z_mem0_1f69942`, projected $2.43922099. LongMemEval `20260909T121141648956Z_mem0_1f69942`, projected $3.56368041.
- Starting paid jobs with concurrency 3 and limits $5/$10. SDK automatic retries disabled in this mode. Per-call reservations remain charged internally when billing is unknown.

#### Rebuild guard caught an uncapped SDK call

- Jobs: LoCoMo `20260909T121234546331Z_mem0_1f69942`; LongMemEval `20260909T121243562166Z_mem0_1f69942`.
- Mem0's reasoning-model parameter filter removes the output cap. The new spending guard blocked `3b6f954b` before dispatching its extraction call. Other questions continue from saved memories.
- Updated Mem0 wrapper to send the existing configured extraction limit explicitly, 128000 tokens. The prior ingestion projection assumed 2000 and is an estimate, not a hard bound. Per-call reservations enforce the budget.
- Will recover only the failed question in a separate run after confirming remaining allocation. No retrieval or bulk re-ingestion.

#### Reused-store runs finished

- LoCoMo: 50/50 valid outputs, 42/50 correct, $0.36865160 incremental spend. Exactly-once audit passed; all answer/judge finish reasons were `stop`.
- LongMemEval: 49/50 valid outputs, only the blocked extraction missing, $0.59466835 incremental spend. Six judge controls agreed with expectations.
- Recovery `20260909T121716575119Z_mem0_1f69942` rebuilds only `3b6f954b` with limit $9, concurrency 1. Prior jobs are stopped; total maximum is now $9.96331995.
- The comparison script will merge recovery with the 49 existing outputs. Final reporting refuses to run while a no-retrieval job is active.

#### Background follow-up configured

- Recovery reached 7/50 sessions without errors; its recorded spend was $0.04649920. Combined new spend $1.00981915.
- Four offline tests passed, including a regression check that Mem0 reasoning calls receive the explicit output cap. `git diff --check` passed.
- Updated existing heartbeat `mem0-benchmark-progress` to monitor this recovery every minute, provide ASCII progress, generate and verify the final comparison after completion, then pause itself. No new paid calls are authorized through the heartbeat.
- Current Markdown/JSON comparison files are explicitly provisional and will be regenerated when recovery ends. Source retrieval runs are unchanged. No git push performed.

#### 2026-09-09 19:33 - Comparison complete

Status: complete.

- Recovery finished all 50 sessions and answered correctly. Final matched Mem0 outputs: LoCoMo 42/50; LongMemEval second 50 45/50. No missing, duplicated, invalid or failed outputs remain in the merged no-retrieval cohorts.
- Final comparison regenerated in `docs/no-retrieval-comparison.md` and `.json`. Exact matching question IDs, history hashes and reference answers verified against full-history and custom-memory baselines.
- All 100 Mem0 answer prompts fit with answer room; every saved memory line is included; retrieval is null; all answer/judge finish reasons are `stop`. All six expected-vs-actual judge controls passed in both LongMemEval jobs. LoCoMo uses its own judge, with no separate control suite in this runner.
- New spend across both cohorts plus recovery: $1.13154761, including judges and $0.13185966 for the one rebuilt store. Prior writing is not charged again. Historical retrieval remains separately labeled, including its unrecovered failed question.
- Tables exclude discarded failed ingestion costs; latency is observational across different runs/concurrency, not a controlled speed comparison. Those limitations remain explicit.
- Pausing the progress heartbeat after reporting completion. No new cohort, paid retry, git commit or push.

### Task: Remaining LongMemEval 50, 2026-09-09

Status: in progress.

- User repeated "Do the other 50" after clarification. Proceeding with the remaining LongMemEval first-50 cohort, not another LoCoMo cohort. This will complete LongMemEval 100.
- Reuse full-history `20260908T192233799242Z_full-history_8cc5c91` and ours `20260908T182110999548Z_memory_b5424ef`, both 50/50 successful.
- Reuse complete Mem0 stores from `20260908T222249129132Z_mem0_388f915` and `20260908T222250256294Z_mem0_388f915`. Rebuild exactly the other 48; do not use the old 20-line exports as complete stores.
- Preserve four-message chunks, Luna low extraction, Luna none answering, GPT-5 judging, and no question-based retrieval. No BEAM or LoCoMo changes.
- New job cap $13.86, plus $1.13154761 previously spent, stays below the existing $15 total ceiling. No paid calls yet for this extension.
- Corrected budget settlement to honor API-reported cached input at configured cached-token rates; uncached upper-bound reservations still precede calls, and unknown failures retain reservations.
- Added a labeled empirical ingestion forecast from the same-settings completed second-50 run, with 25 percent margin. This is not a guaranteed maximum; runtime reservations enforce the cap. Next: preflight and offline tests.

#### First-50 preflight passed

- Preflight `20260909T135852076119Z_mem0_1f69942`: all 50 IDs present, two complete stores reused, exactly 48 authorized rebuilds. Forecast $11.91691165 under new cap $13.86.
- Five offline tests passed, including cached-input settlement, blocked dispatch, retained reservations after unknown failures, full-memory prompt inclusion, and explicit reasoning output caps. Diff whitespace check passed.
- Starting one paid job with concurrency 8. Session order remains sequential within each history. The budget state is saved with checkpoints, including reservations retained for unknown failures.

#### Remaining-50 job started

- Active run `20260909T135940974756Z_mem0_1f69942`, local process session 89279. Two source stores reused; 48 histories total 2310 sessions to rebuild. At the first checkpoint reviewed: 28 new sessions, one question graded, $0.10740036 spent, no API/extraction errors.
- Added `compare_no_retrieval.py --longmemeval-first-run RUN_ID` to generate separate first-50, second-50 and combined-100 comparisons into new files, preserving the previous 50-question report. Unique run costs are counted once, not again in the combined table.
- Reusing full-history and ours gives 100 distinct IDs per system. The combined final report is blocked until the active run is terminal. No extra paid cohort or LoCoMo work.

#### Background monitoring active

- Updated `mem0-benchmark-progress` to monitor the remaining-50 run every minute, produce ASCII updates and generate the combined-100 report on completion, then pause. The heartbeat cannot launch additional paid calls.
- Latest check: 61/2310 newly ingested sessions, 1/50 graded, $0.20431242 spent by this job. All six judge controls agreed with expectations; no API/extraction failures.
- Five offline tests and the active-run final-report guard passed. Full-history and ours each have 100 matching distinct questions, 85/100 correct before the new Mem0 comparison.
- Next: allow the existing run to finish, verify every output and produce the final first-50/combined-100 tables.

#### 75-percent milestone notified, 2026-09-09 15:14 UTC

- Observed 38/50 successful, validly graded unique questions. This crosses the requested 75-percent milestone; do not notify it again.
- Monitoring is now milestone-only per user request: stay silent until 50/50 valid outputs, then verify and report the final comparison. No additional paid calls or retries are authorized by monitoring.

#### 2026-09-09 15:33 UTC - Remaining 50 complete

Status: complete.

- Run finished at 15:30:28 UTC after 90 minutes 48 seconds. All 50 unique outputs succeeded, with 43 yes and 7 no verdicts and no memory failures. Run spend $7.26510582; cumulative new no-retrieval spend $8.39665343, below $15.
- Verified complete sessions and inclusion of every stored memory text, null retrieval, prompt fit, and stop finish reasons for answering and judging. All six factual judge controls matched expected grades: correct yes, paraphrase yes, wrong no for both questions.
- Generated docs/longmemeval-100-no-retrieval.md and .json. Matched unique IDs, history hashes and reference answers across systems for first 50, second 50 and combined 100. Combined no-retrieval scores: full history 85/100, ours 85/100, Mem0 88/100. Historical retrieval is separate, with one previously failed output explicitly retained.
- Corrected report concurrency note to include the first-50 extension's eight workers. Writing costs describe retained stores, not discarded failed attempts; call latency is not a controlled speed comparison. Provider billing for unknown-usage calls is not reconciled.
- No new paid calls, retries, commit or push during final verification. Monitoring will pause after the completion notice. No remaining run work.

#### Publication scope corrected

- User requested code and aggregate results only. Removing newly added raw run manifests and summaries from the unpublished commit, retaining all local files. Aggregate exports now retain only expected/actual control grades, not question text, answers or judge responses.
- Verified Mem0 ingestion already defaults to two messages in both the CLI and store implementation; four was a historical run override. No completed-run metadata or memories changed, and no new API calls made.

### Task: Shared-memory async inference, 2026-09-10

Status: implementation complete; paid benchmark unverified.

- Implement history-level memory builds for our extractor, with independent bounded building, answering and judging workers. Mem0 ingestion remains unchanged.
- Parent run ID links immutable memory artifacts and per-question stage records. Measure parent wall time, first/all graded time and stage durations; count writing usage once per build.
- Preserve prompts and chunk boundaries; no paid calls, commit or push authorized in this task. Verify with offline fake-provider integration tests, including overlap, failure and restart behavior.

#### Verification

- All 16 offline tests passed with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -v`; `git diff --check` passed.
- Fake-provider end-to-end run built two unique histories for three questions using four extraction calls, then reused the saved memories in a separate answer-only run with zero extraction calls. Temporary artifacts were cleaned up by the tests. Printed test costs are simulated, not API spend.
- Event-based tests verified overlap and barrier behavior. Other tests covered the global in-flight cap, failed builds, invalid judges, corrupted artifacts, artifact restart reuse and retained failed-answer accounting.
- Added unique stage-attempt IDs, UTC/monotonic timings, rate-limit waits, known-versus-unknown usage accounting, and pre-dispatch budget checkpoints. Build-only runs are labeled `memory_ready`, not completed QA evaluations.
- Instructions: `docs/shared-memory-inference.md`. No paid calls, historical-result edits, commit or push. Real provider throughput, observed historical speedup and shared-memory accuracy remain unverified.

#### Authorized real-API smoke test, 2026-09-10

- User approved a $0.10 cap for two synthetic histories and three questions.
- Run `20260910T050844115482Z_memory_a79fc91` completed 3/3 with correct grades, four extraction calls, three answers and three judges. Cost $0.00761315 at configured rates. Recorded wall time 13.087159 seconds.
- Verified matching shared memory IDs/content, both artifact hashes, prompt fit, exactly-once outputs and real overlap between answering and another history's build. No failures or unknown usage.
- Extended test fixtures to support a list of unique questions. All 16 offline tests passed after the change. Aggregate report: `docs/shared-memory-api-smoke.md`. No commit or push; full benchmark speedup and accuracy remain unverified.

### Task: Audit teacher traces and split train/dev, 2026-09-10

Status: in progress.

- Audit all saved our-memory runs without API calls; preserve original runs and prior uncommitted work.
- Deduplicate source histories, reconstruct and validate sequential extraction inputs/targets, and keep every version of a history within one split.
- Default to seeded 80/20 whole-history train/dev, stratified by benchmark where possible. Exclude synthetic smoke fixtures and record unavailable or invalid traces explicitly.
- Save reproducible split manifests and an aggregate audit report. Existing evaluation histories used here cannot remain held-out final evaluation.

#### Inventory and leakage findings

- Scanned 630 our-memory trace occurrences. 468 complete occurrences reconstructed exactly; exclusions: 100 reused copies, 21 incomplete histories, 30 missing/retried call sequences, 11 non-full-source or synthetic fixtures.
- Selected 117 canonical full-history trajectories, newest fully reconstructible run then stable question ID, without consulting answer accuracy. Retained alternate versions in the inventory instead of mixing their updates.
- Recovered 5,278 update pointers. Exact prior-memory prompt hashes, source-history hashes, target-to-appended-line consistency and complete session sequences verified.
- All 100 LongMemEval histories form one connected component through shared session content. Assigned the component to train to avoid leakage; no LongMemEval dev subset is possible under this policy. BEAM same-chat scale variants stay together.
- Current split: 112 train histories / 5,112 updates and 5 dev histories / 166 updates. Zero exact session overlap. This is not an 80/20 split overall because connected components cannot be divided.
- All 10 local LoCoMo conversations are in train/dev. Future final questions from these conversations would be contaminated. Quality warnings remain separate: 1,727 train updates and 42 dev updates have no target flags, but only 178 and 7 also have no prior-memory flags. These heuristics are not human truth labels.
- Twenty offline tests passed. Final provenance and artifact checks in progress; no paid API calls, training, source-run modifications, commit or push.

#### Task complete, with LongMemEval dev limitation

- Saved `work/training_trace_audit/` with history assignments, canonical update pointers, exclusions and source/run hashes. Aggregate report: `docs/training-trace-audit.md`; rerunnable tool: `audit_training_traces.py`.
- Final checks passed: 117 unique canonical histories, 5,278 unique update IDs, complete partition, zero cross-split exact-session overlap, audit code hash, and unchanged hashes for every inventoried original run file. No API spend.
- Audit and leakage-safe assignments are complete. LongMemEval-specific dev evaluation and independent future LoCoMo final evaluation need a different source-data plan. Quality review and model-specific fine-tuning payload export remain separate tasks; this task did not train a model.

### Task: LongMemEval split feasibility, 2026-09-10

Status: in progress.

- Reserve dev histories, remove all training histories sharing any exact session with dev, and count surviving histories and updates.
- Compare a fixed 20-history dev set, seeded alternatives, and smaller dev sizes. Candidate search uses source overlap only, never answer grades.
- Preserve existing split assignments. Save diagnostics and candidate IDs separately; no API calls or training.

#### Feasibility check complete

- Fixed seed 20260910 with 20 dev histories leaves 20 train histories / 938 updates; removes 60 overlapping histories. With 10 dev histories, 51 train histories / 2,428 updates survive; removes 39. Both candidates have zero exact session overlap.
- Tested 1,000 seeds per dev size. 951/1,000 of the 20-dev trials and all 1,000 of the 10-dev trials retained at least 1,000 updates. Candidates use the fixed seed, not the best sampled outcome. No answer grades used.
- A connected overlap graph can be split when bridge histories are discarded. The earlier train-only assignment kept every history; this check trades coverage for separation.
- Saved candidate pointers and provenance in `work/longmemeval_split_feasibility/`; aggregate report `docs/longmemeval-split-feasibility.md`. Original audit/split input hashes verified unchanged.
- 22 offline tests passed, both candidate partitions verified, script provenance verified, whitespace check passed. No API calls or training.
- Recommend the 10-dev candidate for quality review before adoption. It has 762 training updates with no target warnings, not 2,428 quality-approved examples. No final evaluation set reserved or other benchmark split changed.

### Task: Review sampled teacher-trace quality, 2026-09-10

Status: in progress.

- Use the accepted 10-dev candidate as the review population. Sample training traces only; do not inspect dev answers or tune on final evaluation.
- Fixed diagnostic sample: two distinct histories each for memory-update warnings, date/number warnings, value warnings and no warnings. Preserve exact source/target hashes.
- Assistant review of factual support, attribution, temporal resolution and update consistency; distinguish warning false positives from real target defects. This is not independent human annotation or a dataset-wide quality estimate.
- No paid calls, training, automatic filtering or changes to original traces.

#### Sample review complete

- Read all eight sampled sessions and targets, with prior same-key memory lines. Added targeted prior-memory checks for two attribution/completion findings. Saved one evidence-linked assistant annotation per sample in `work/trace_quality_review/review_annotations.json`.
- Findings include false-positive warnings for joined lists, normalized port mappings and a resolved prior-year date; actual update-chain defects and unsupported completion/attribution; uncertainty loss and format concerns. One unflagged narrative misattributes assistant suggestions to the user.
- Do not blanket-reject warned targets or blanket-approve unflagged targets. Keep source faithfulness, contract compliance and coverage separate. No thresholds, targets, splits or filters changed from this diagnostic review.
- Aggregate report: `docs/trace-quality-review.md`. Reproducible sampler: `sample_trace_review.py`. This is assistant review, not human ground truth or an estimated dataset error rate.
- 23 offline tests passed; eight distinct training histories, hashes, annotation accounting and quoted evidence presence verified. No paid calls or training. Broader quality review/target repair is still needed before claiming 1,000 approved examples.

### Task: Paired original and repaired training copies, 2026-09-10

Status: in progress.

- Freeze the 10-dev candidate as a self-contained original copy and create a separate repaired pilot with identical example IDs, source histories, prompts and dev examples.
- Apply only the six reviewed target repairs; keep original teacher output bytes in the control. Rebuild subsequent memory inputs in the repair arm and list affected rows for dependency review.
- Preserve originals and source runs. No blanket quality filter, paid calls, training or benchmark evaluation. The pilot is not a fully cleaned dataset.

#### Paired copies saved and verified

- Created self-contained `work/training_copies_v1/copy_1_original/` and `copy_2_repaired_pilot/`, each with 2,428 training rows from 51 histories and identical 478 dev rows from 10 histories. IDs and ordering align; original prompt/target hashes verified.
- Applied six reviewed target edits. Replayed memory to rebuild 155 later inputs; their semantic dependency review remains pending. Zero later targets directly reuse edited atomic keys, which is not proof of complete semantic consistency.
- Saved exact repair spec, edit log, pending-review queue, frozen split and artifact/source hashes. Builder refuses overwrite. No original source run or pre-existing split file changed.
- `verify_training_copies.py` passed all artifact, ID alignment, unchanged-context/source, repair and dev-identity checks. All 25 offline tests and whitespace checks passed.
- Report: `docs/paired-training-copies.md`. Copy creation and the six-target repair pilot are complete; broader cleaning and dependency review are unfinished. Neither arm was trained or evaluated. No paid calls, commit or push.

### Task: Delegated dependency repair and Adaption setup, 2026-09-10

Status: in progress.

- User authorized Sol and Terra subagents. One Sol and two Terra agents review disjoint whole-history groups covering the 155 pending dependent rows. Each writes review evidence and proposed target repairs only to its own directory under `work/repair_agents/`; frozen copies remain unchanged.
- Read the official AutoScientist and Adaptive Data quickstarts and AutoScientist create reference. Saved provider roles, controlled-comparison requirements and unresolved upload/split/budget choices in `docs/adaption-integration.md`.
- Added blank `ADAPTION_API_KEY` entries to `.env` and `.env.example` without displaying existing credential values. Supplied a hidden-input terminal command for the user. No SDK install, upload or paid job.
- Verification passed: `.env` is Git-ignored, whitespace checks, frozen-copy/source hashes and all 25 offline tests. Test cost lines are mocked, not paid calls. The agents' assignments cover 53, 47 and 55 rows; semantic review is still in progress.

### Task: Finish the scoped copy 2 repair, 2026-09-10

Status: in progress.

- Finish all 155 dependent-row reviews, adjudicate source-supported proposals, replay memory into a new snapshot and verify complete accounting. Preserve copy 1 and the six-fix pilot unchanged.
- Incremental review files now exist from all three agents. These are proposals, not accepted edits. Found a proposal-format inconsistency and a narrative attribution fix that retained the same unsupported atomic attribution; sent both back for correction.
- Use a reproducible consolidation/replay tool and require final-context checks after applying new repairs. Unreviewed remainder of the 2,428-row corpus is not silently certified clean. No paid calls, training, commit or push.

#### Repair export built; final-context checks underway

- All 155 queue IDs now have exactly one review: 120 keep, 28 proposed repairs, 7 uncertain. Accepted 27 proposals; rejected removal of a repeated book from a sourced recommendation list. Retained all seven ambiguous rows with explicit decisions, without filtering.
- Consolidation caught and corrected a mistyped review ID, inconsistent evidence/target schemas, an unsupported attribution left in an atomic fact, and a stale `next week` chain after an earlier timing deletion. Rejected added date precision and inferred separate game playthroughs where source evidence did not settle them.
- Saved `work/training_copies_v2/copy_2_repaired/`: 33 target changes versus original, 155 changed prior-memory inputs, 113 input changes versus the pilot. All 2,428 training rows and 478 dev rows retained. Source sessions, system prompts and dev bytes preserved.
- First decision-file write failed with Desktop sandbox `Operation not permitted`; reran the same authorized offline generator with escalation. No data was lost or overwritten. No paid call was made.
- Full deterministic replay, v1 provenance verification, 30 offline tests and whitespace checks passed. Final-context attestations for the six changed histories remain required before sealing the new snapshot.

#### Scoped copy 2 repair complete, 2026-09-10

Status: complete.

- All three agents checked the six exported history hashes, applied targets and downstream contexts. Final attestations are frozen in v2, with known source ambiguities distinguished from newly introduced dependencies. No repair-induced dependency remains unresolved in this review scope.
- Sealed v2 as `scoped_repair_complete`; reran deterministic replay verification after sealing: 2,428 rows / 51 train histories, identical dev data. Original v1 source/artifact verification and all 30 offline tests passed. Seven ambiguous examples remain unchanged with explicit records; this is not exhaustive corpus-wide factual approval.
- Delivered report `docs/copy-2-repair-comparison.md`, repeatable `finalize_repaired_copy.py`, and five new regression checks in `test_finalize_repaired_copy.py`. The control and pilot are preserved. No paid calls, training, commit or push.
- Repair task complete. Measuring the effect on accuracy requires the separately configured and authorized training/evaluation comparison; it has not been run.

### Task: Modular Qwen 3.5-9B Modal pilot

Status: in progress.

- User selected Qwen/Qwen3.5-9B and approved a $2 pilot. Keep local dataset selection/accounting separate from Modal transport and GPU inference. Do not run training or full benchmarks.
- Modal SDK and credentials absent. Implement and test locally; cloud execution awaits user authentication. Read current Modal Sandbox/SDK documentation and Qwen's model card.
- Network diagnostics: sandbox DNS blocked; escalated Python HTTPS then failed certificate validation. System curl with normal certificate verification and escalation succeeded; no TLS checks disabled. Verified package versions from PyPI for dependency pins.
- Implemented separate core selection/accounting, Modal orchestration and GPU worker modules, pinned dependencies, and `docs/modal-pilot.md`. Installed local tokenizer and Modal dependencies; no model weights or GPU calls.
- Real-tokenizer preflight exposed a dictionary-versus-token-list counting bug. Fixed with explicit `return_dict=False`, a flat-integer-list guard and regression test. Preserved invalid preflight separately at `work/modal_qwen_pilot_invalid_token_count`; never use that directory for execution.
- Corrected preflight at `work/modal_qwen_pilot`: scanned 2,428 original training examples; median prompt 16,022 tokens, longest 36,620. Both fit the 65,536-token pilot window with 2,048 output tokens reserved; full prompts retained and teacher targets excluded.
- Verification: all 37 local tests and `git diff --check` pass. Initial full-suite failure was public tokenizer download DNS, resolved using system CA and permitted network. Test spend output comes from mocks, not paid API usage.
- Status: local setup complete; GPU pilot blocked on user Modal browser login (`.venv/bin/modal token new`). GPU execution, output quality, latency, GPU memory and actual invoice cost remain unverified. No cloud invocation, training, commit or push. Planned resource envelope plus reserve is about $1.68; not a provider-enforced $2 cap.

### Task: Launch authorized Modal pilot, 2026-09-11

Status: in progress.

- User completed authentication and explicitly authorized launch. Started the frozen two-example pilot at 2026-09-10 17:50:49 UTC on A100-80GB, with the existing 1,200-second timeout and $2 spending estimate policy. No automatic retry.
- Modal authenticated and returned sandbox `sb-2rs0jzrK5BzGR0920O1vch`. Ledger: `work/modal_qwen_pilot/run.json`. Waiting for remote setup and inference; actual cost and output quality remain unknown.
- Attempt failed before dependency installation. The first `filesystem.copy_from_local` never completed; a separate read-only `ls` check also waited for sandbox task availability. After over five minutes without progress, terminated the sandbox to preserve budget. Provider poll confirmed exit code 137. Upload raised `SandboxFilesystemError` after termination; this does not establish the underlying startup cause.
- Both expected outputs are explicitly missing, with zero inference results. Runner saved failed status, confirmed termination, elapsed time and null actual invoice cost in its ledger and summary. No retry launched. Next: inspect Modal startup diagnostics and reconcile billing before considering another paid attempt. Model fit, quality and speed remain unverified.

### Task: User-authorized new-account retry, 2026-09-11

Status: in progress.

- User explicitly approved a retry under the same $2 pilot limit after switching accounts. Verified active profile `new-account`; explicitly selected it for launch. Preserved prior attempt and copied frozen payload/preflight into `work/modal_qwen_pilot_new_account`.
- Run began 2026-09-10 18:06:22 UTC; sandbox `sb-LEvtoad5u2EQnm2esotxw6`. Still waiting before installation. Monitoring startup and will terminate after five minutes without progress; no automatic retry.
- Retry completed: uploads and installation succeeded; Qwen BF16 with thinking disabled loaded in 193.804 seconds. Typical prompt: 16,022 input / 517 output tokens, 30.382 seconds, 23,446,724,608 peak allocated GPU bytes. Longest: 36,620 input / 413 output tokens, 26.443 seconds, 29,292,839,936 peak allocated GPU bytes. Both stopped normally and passed JSON schema checks; source fidelity remains ungraded.
- Total elapsed 530.469 seconds including startup/setup/loading/finalization. All two IDs accounted for exactly once, no failures or missing outputs. Runner confirmed termination. Actual provider charge remains unknown; elapsed multiplied by configured resource rate is approximately $0.52, not an invoice. Saved artifacts in `work/modal_qwen_pilot_new_account`; previous failed attempt remains unchanged. Status: pilot complete, no training or benchmark evaluation performed.

### Task: Three-arm experiment execution preflight, 2026-09-11

Status: blocked before paid jobs.

- User authorized dev-based iteration toward Luna performance within $30 Modal and existing provider credits. No positive result is guaranteed; retain regressions and do not tune on final results.
- Added repeatable `experiment_preflight.py`, a split-overlap regression test, pinned Adaption SDK dependency and `docs/qwen-experiment-preflight.md`. Installed Adaption 0.12.0; authenticated read-only model lookup confirmed Qwen3.5-9B SFT/LoRA availability. Both credentials present, values not exposed.
- Offline audit found 61 exact LongMemEval training/dev histories, 418 other records sharing sessions, and only 21 exact-session-disjoint records out of 500. All historical 100 overlap train/dev sources. LoCoMo's 10 and BEAM 500K's 2 historical conversations do not overlap current training/dev. Current training copy contains only LongMemEval, not all three benchmarks.
- All 38 tests pass. The saved audit includes source/code hashes. No paid inference, synthesis, upload or training launched in this step.
- Need approval to reduce LongMemEval final to the 21 eligible records or redesign the train/dev split; cannot silently claim the old 100 are held out. Also awaiting verified Adaption and answering/judging credit balances. Continue from the preflight report once resolved; no background paid jobs are running.

### Task: Audit a published LongMemEval split, 2026-09-11

Status: in progress.

- User approved checking a third-party split before adoption. Start with BudgetMem's published train/val/test index file, verify its dataset ordering, and measure cross-split session overlap.
- Preserve our current Copy 2 train/dev exports and leave final IDs unfrozen. No paid calls or experiment launches.
- Prior discussion explored a 50-question final by removing overlapping whole training histories, but that candidate was not adopted. The earlier 21 eligible count applies only while keeping all current train/dev histories fixed.

#### Source audit and dataset connectivity

- Pinned BudgetMem at `91c17435f3b7634711a22fe9cb303ec15069a7aa` and LazyMem at `af4109960aacb90d6dba994e9103a36a165cc380`. Inspected source only, did not run their code or install dependencies.
- BudgetMem publishes 297/98/105 row indices, covering 0 through 499 once. Its loader merges train and val. Its processed dataset and verified question-ID mapping are absent, so cross-split session counts remain unverified.
- LazyMem documents 360/40/100, seed 42, but its split ID files are absent. No split-generation implementation was found in the tracked source. Did not invent an equivalent seed-based split.
- Initial local exact role/content graph puts all 500 LongMemEval-S histories in one connected component. This proves that keeping all complete histories cannot yield nonempty, session-disjoint partitions, regardless of row ordering. It does not prove every pair overlaps or audit the authors' actual processed inputs.
- Added `audit_published_split.py` and three focused tests; running reproducibility and full-suite checks next. Current exports remain unchanged.

#### Published split audit complete

Status: complete for the available public artifacts. Exact author partition overlap remains unverified.

- Reproducible audit found one 500-history component using exact role/content, corroborated by a separate session-ID graph. There are 4,366 distinct text sessions present in multiple histories. Keeping all 500 complete histories makes any nonempty multi-part split fail the zero-session-overlap rule.
- Saved aggregate/provenance JSON at `work/published_split_audit/report.json` and readable findings at `docs/published-longmemeval-split-audit.md`.
- All 41 local tests pass, including three new audit checks. Full-suite spend messages came from mocks. No provider calls, training, synthetic generation, data uploads, commit, or push.
- Recommendation: do not adopt either split as a verified session-disjoint replacement. Keep current Copy 2 intact and choose our final split separately. Source ordering/IDs remain the blocker to exact cross-partition counts for the public splits.
- Final ad hoc row-count check initially failed because Python `str.splitlines()` split a Unicode line separator inside a JSON string. Retried using file-line iteration, the project's JSONL reading method. Both exports parse: 2,428 rows / 51 train histories and 478 rows / 10 dev histories. Code/report hashes match and both export hashes are unchanged. `git diff --check` passed.

### Task: Check split isolation and evaluation sample size, 2026-09-11

Status: in progress.

- User requested current-state verification and online research on whether dev/final sample sizes are sufficient. Check saved train/dev exports, final manifest status, question-type coverage, and statistical uncertainty.
- Research primary guidance on small-sample proportion intervals, paired model comparisons, and repeated dev-set selection. No dataset changes or paid jobs authorized by this research request.

#### Split and sample-size review complete

Status: complete for the current saved artifacts and research question.

- Recomputed Copy 2 source matching: 51 train histories / 2,428 updates and 10 dev histories / 478 updates. All map to source records. Train/dev share zero full histories, zero exact role/content sessions, and zero session IDs. Dev has ten separate exact-session components. Export hashes match the prior audit.
- No new frozen final manifest found. Existing plan and reports still explicitly leave final unresolved. Thus train-final and dev-final cannot yet be certified. The proposed 32/10/50 counts remain unadopted.
- Dev has all six question types but only 1-3 each, no abstention, and overrepresents preference questions. Its 478 updates are not 478 downstream accuracy samples.
- Read NIST confidence-interval guidance, Card et al. on NLP power, Dror et al. on paired tests/dependence, and Cawley/Talbot on model-selection overfitting. Computed illustrative Wilson intervals at 80% accuracy: n=10 gives 49.0-94.3%; n=50 gives 67.0-88.8%. These are not actual model results or certified intervals for our chosen subset.
- Recommendation: 10 dev and proposed 50 final can support a limited exploratory pilot, not extensive hill-climbing or strong claims about small improvements. Investigate larger/better-balanced dev only through a separate feasibility audit, without silently changing the split.
- One orchestration call failed to parse due to a quoting typo, before any commands ran; corrected and reran successfully. An optional arXiv v3 HTML URL returned 404; used the accessible primary sources above. No data loss or paid calls.
- Saved `docs/evaluation-split-size-review.md`. No training, synthetic generation, split edits, commit, or push.

### Task: Revise BEAM selection to eight conversations, 2026-09-11

Status: complete for source selection, counts and forecast. User approved four 100K and four 500K histories, omitting 1M. Preserve the six-history sources/report under `work/beam_training_candidate/`; the current script now targets `work/beam_training_candidate_v2/`. Keep eight-pair extraction boundaries. No paid calls in this preparation step.

#### Eight-history audit complete, 2026-09-11

- Selected 100K IDs 7, 11, 14, 18 and 500K IDs 9, 23, 27, 32. All 24 JSON sources verified against pinned Git blobs. The offline rerun also passed. Exact counts: 60 + 240 = 300 update slots, 160 associated training-source questions, 2,733,396 o200k content tokens. These are not generated or quality-approved teacher targets.
- No matching histories/windows/pairs with all ten protected local histories; no matching windows/pairs across the 28 selected-history pairs. Added pair-overlap rejection and exact source-manifest membership checks to the audit. Semantic overlap remains unverified.
- Historical-rate teacher-writing forecast: $0.96 with effective prior-memory caching, $1.75 uncached, $2.63 with a 50% planning reserve. Not current verified pricing or a hard maximum. No source truncation, model calls, uploads or GPU jobs.
- Saved `docs/beam-training-candidate-v2.md`; marked the old document historical and synchronized `docs/qwen-training-evaluation-plan.md` to BEAM-only teacher training. Archived LongMemEval exports and old six-history artifacts remain untouched. Separate dev/final manifests and actual student-tokenizer prompt/target fit remain pending.
- Initial test command failed because pytest is not installed. Used the existing unittest runner instead: all 41 tests passed. Printed API-spend figures were from mocks, not paid calls. `git diff --check` passed.
- Next: reserve and verify separate dev/final sources, then generate/review teacher traces under verified provider credits and a concrete job budget. No commit or push requested in this step.

### Task: Prepare six BEAM training candidates, 2026-09-11

Status: in progress.

- User approved identifying two conversations each at 100K, 500K and 1M, counting teacher updates and estimating generation cost. Added `prepare_beam_training_candidate.py` for pinned source downloads, exact overlap checks and a historical-rate cost forecast.
- Candidate IDs: 100K/7 and 11; 500K/23 and 27; 1M/19 and 30. Six categories: writing, ethics, health, housing, education and travel. Exclude all historical BEAM evaluation numeric IDs at every scale as a conservative family guard. Actual topic equality is not established by numeric ID alone.
- Pin BEAM Git revision `b2da22eac88bb0874c64665f13457eb99835774a`; download JSON only to `work/beam_training_candidate/source`, verify against Git blob hashes. Keep the runner's normal source folder unchanged.
- Estimate one teacher build per conversation from historical Luna low-reasoning usage, including repeated prior memory and hidden output reasoning. Current provider pricing and actual future outputs remain unverified. No model calls launched.

#### Six BEAM sources prepared and audited

Status: complete for selection, source download, counts and forecast. Teacher generation remains pending.

- Downloaded and verified 18 JSON files against the pinned Git blobs. Exact counts: 100K/7=15 updates, 100K/11=15, 500K/23=60, 500K/27=60, 1M/19=119, 1M/30=120. Total 389 update slots / 3,296,498 content tokens, below the earlier 1,000-example aspiration.
- Expanded overlap protection to all ten locally downloaded BEAM histories. No identical history, window or message pair with that pool; no matching windows or pairs among selected histories. Numeric IDs are distinct and excluded from the protected pool. All 120 associated question IDs belong with training sources.
- Calibrated teacher cost on 134 calls from two distinct historical memory builds. Forecast $1.28 with effective prior-memory caching, $3.18 without it, approximately $5 with a 50% reserve. Historical Luna rates only; not verified current pricing or a guaranteed cap. No paid calls, uploads or GPU jobs.
- Late 1M memory is projected around 70K o200k tokens before the next source window, so actual student-tokenizer/training-context fit needs attention before export. No silent truncation or training-readiness claim.
- Saved `docs/beam-training-candidate.md`, repeatable script and local source/report manifests. Offline rerun, exact overlap/accounting assertions and code hashes passed. The existing LongMemEval copies and benchmark source folders remain unchanged.
- Public HF tree browsing returned a fetch/safety error; used the official Git repository and pinned raw sources instead. The first Git tree/topic diagnostic was overly verbose and truncated in tool display; the preparation script subsequently fetched and validated the full inventory programmatically.
# 2026-09-11: post-commit Qwen concurrency smoke

- User requested a smoke before the full Qwen run. Ran two fresh four-update
  BEAM smokes on one L40S each, sequentially, at concurrency one then two.
- Both completed 4/4 valid updates; both GPU shutdowns confirmed. No OpenAI calls.
- Extraction wall time: 46.197s versus 47.661s. Two requests were 3.17% slower
  in this small trial. Output differences changed the second-update prompts;
  this is not an identical-token causal comparison or an accuracy evaluation.
- Combined accounted estimate $1.720018, including overhead allowances; actual
  invoices unverified. Baseline allocation remaining approximately $4.209397.
- Full optimized baseline has not launched. Code unchanged from c446631.
- Evidence and timing boundaries: docs/qwen-speed-smoke-comparison.md.
# 2026-09-11: full Qwen BEAM baseline launched

- User authorized full launch after the speed smoke. Run `qwen-fa7c676b0b79b019`
  is running in sandbox `sb-HlcUf0YrEqYg0dRf7Pw2Ps` with a $4 Modal reservation
  and 3,833-second timeout, within the remaining baseline allocation.
- Exact original seven BEAM histories / ninety questions. One active Qwen
  extraction request on L40S. Collector is running with `--watch --evaluate`.
- Answering/judging use four independent question workers and start per completed
  history, overlapping subsequent cloud extraction. Judging waits for its own
  answer; it does not wait for all histories. No partial memory is evaluated.
- User reaffirmed extraction and judging must overlap. Existing implementation
  supports this; no code change or GPU restart was needed. Actual overlap will
  be established from run evidence once the first history completes.
# 2026-09-11: Luna teacher completed and SFT candidates exported

- Separate delegated teacher session finished the last ten updates after the
  user authorized replacing the unresolved timeout. 16/16 histories and 588/588
  updates complete. Invocation 99.60s; total accounted upper bound $4.28748212,
  including all seven historical abandoned reservations, under the $10 cap.
- New offline prepare_teacher_sft.py replays source inputs, targets and final
  memory states; verifies train/dev/final exact history/window/pair isolation;
  exports immutable chat candidates with separate provenance and token counts.
- 588 replay-valid targets, 564 within Qwen 65,536-token SFT context, 24 overlength
  retained separately. 366 updates carry heuristic warnings, not rejection labels.
- Snapshot work/beam_teacher_sft/e18563c1a02ce127. No truncation, repairs, held-out
  mixing, uploads, synthesis or fine-tuning. Qwen was not changed by this work.
- 75 tests passed. AutoScientist 1,000-row minimum leaves at least 436 additional
  fitting examples needed; semantic review and provider preprocessing verification
  also remain. See docs/beam-teacher-sft-preparation.md.
# 2026-09-11: user-authorized maximum Qwen output continuation

- Stopped original full-run sandbox and collected checkpoints; termination
  confirmed. Original run accounted $2.0230254473, keeping prior costs intact.
- Four histories complete; three had length-truncated extraction responses.
  Successful prefixes total 107/203 updates. Existing answer/judge records retained.
- Removed the pilot's fixed 2,048-token cap. Each new extraction may use all
  remaining space in its 65,536-token serving context; exact per-call allowance
  is recorded. No prompt truncation or context-window/GPU expansion.
- Added explicit continue_qwen_output.py: imports verified stopped checkpoints,
  preserves truncated attempts and provenance, refuses unknown/non-length failures,
  and retains answering/judging results. Current path work/qwen_beam_vllm_max.
- 77 tests passed, including remaining-space allowance and safe length-failure
  reconciliation. Continuation reservation $2.10 within approximately $2.186
  remaining baseline allocation. No cap increase or unrelated API retry.
# 2026-09-11: answer-only completion with Luna maximum output

- User authorized replacing three 1,024-token truncated answers and completing
  40 pending questions. GPU extraction is complete (203/203, 7/7); shutdown
  confirmed and all cloud memories collected. No GPU relaunch.
- finish_beam_answers.py prepares work/qwen_beam_answers_max, copies saved
  immutable memories and 47 successful results, and archives the three truncated
  answer calls under api_calls/abandoned_* so their cost remains counted.
- New answers permit Luna's documented 128,000 maximum output tokens; complete
  prompt plus allowance must fit. Judge settings unchanged. Local .env and its
  example updated; old frozen configurations remain unchanged.
- Four workers run under the existing $20 answer/judge allocation. Explicit
  guards reject unknown outcomes and non-length failures. 79 tests passed.
- Attempt to retarget the two-minute automation failed: app reported the
  automation no longer exists. Direct monitoring continues during this task.
# 2026-09-11: Qwen BEAM evaluation complete

- work/qwen_beam_answers_max now contains 90/90 unique valid question results,
  zero failed/missing/unexpected. All three truncated answers replaced successfully
  at 1,694/1,923/1,878 output tokens; old attempts remain archived and charged.
- Answer-only invocation 370.739s. Additional accounted API upper estimate
  $1.476545; cumulative answer/judge estimate $2.373199, under the $20 allocation.
  All 354 API records complete; GPU shutdown remains confirmed, no restart.
- Accuracy: Qwen 100K 34/50 (68%) vs historical Luna37/50 (74%); Qwen500K24/40
  (60%) vs Luna24/40 (60%). Observational, shared-memory and mixed-output-cap
  continuation caveats explicitly documented in docs/qwen-beam-final-completion.md.
- 79 tests passed before paid launch; final artifact completeness and accounting
  verified after completion. No synthetic generation or training launched.

### Task: LongMemEval concurrent Qwen histories, 2026-09-11

**Status:** in progress. Code-only authorization; no paid calls.

- Existing vLLM worker already schedules independent histories. The missing
  parts were LongMemEval preparation, local question routing and Mem0 judging.
- Adding the original 100 questions, complete sanitized natural sessions,
  concurrency 1/2/4/8/16 on one GPU, independent answering/judging, and strict
  result accounting. LoCoMo and historical BEAM selections remain unchanged.
- Queue checkpoints distinguish not-yet-sent requests from unknown in-flight
  calls. Tokenization moves off the event loop. New-update throughput is recorded
  separately from inherited completed updates for honest continuation estimates.
- Next: offline concurrency, recovery, judge-routing and real-selection tests.
  Existing budget guards are not raised; deployment timing remains unverified.

#### Offline implementation verified

- Pinned real-data preparation and exact replay passed: 100 questions, 100
  histories, 4,803 updates. Labels excluded from GPU payload; no truncation.
- Simulated 100-history worker reached eight concurrent requests, retained
  within-history order and skipped completed work on replay. Collector test
  confirms answering begins before the other history finishes extracting.
- First test attempt failed because the public o200k tokenizer was not cached
  and sandbox DNS was unavailable. Retried with download permission; tests passed.
- Fixed LongMemEval smoke selection at 16 histories / 32 updates for every
  concurrency level, avoiding confounded throughput comparisons across sizes.
- Instructions: docs/qwen-longmemeval-concurrency.md. No GPU launch, model API
  calls, budget changes, or modifications to saved benchmark results.

**Status:** complete for the code change. All 88 local tests and `git diff --check`
passed. Actual L40S throughput, concurrent long-prompt capacity and paid end-to-end
execution remain unverified pending an explicitly budgeted pilot.

### Task: LoCoMo concurrent Qwen support, 2026-09-11

**Status:** in progress. Code and offline tests only.

- Reusing the existing scheduler and collector for the original 50 questions
  across ten complete histories. Preserve two-person attribution and the
  existing LoCoMo adapter's dates, image-caption rendering and reference handling.
- Pin selection and source content hashes; keep references and evidence out of
  extraction. Route grading to the vendored Mem0 LoCoMo CORRECT/WRONG prompt.
- Next: real-data preparation and tests for shared-memory question fan-out,
  concurrent answers, resume, grading and unchanged smoke workload.

#### LoCoMo implementation verified

- Real-data preparation passed: 50 questions, ten histories, 272 updates.
  Exact replay, speaker attribution and payload label exclusion passed.
- Added tests for CORRECT/WRONG/invalid grading and cached-call resume, fixed
  ten-history smoke selection across concurrency levels, and three questions
  sharing one immutable memory concurrently before other extraction finishes.
- Instructions saved in docs/qwen-locomo-concurrency.md. No paid calls, GPU
  launches, budget increases or changes to historical benchmark results.

**Status:** complete for implementation. All 91 tests, CLI help and
`git diff --check` passed. Real GPU throughput and paid end-to-end evaluation
remain unverified until a budgeted pilot is authorized.

### Task: Run Qwen LoCoMo then LongMemEval, 2026-09-11

**Status:** preflight. User authorized final runs with a smoke first, within the
existing $30 total Modal cap. GPU choice: one L40S 48GB, concurrency eight;
Luna answerer and GPT-5 judge unchanged.

- Live Modal billing summary: $5.58 metered, covered by credits. The hourly
  billing request initially exceeded its seven-day range; the supported monthly
  Workspace billing summary succeeded. Local estimates remain conservative.
- Original baseline accounted $9.913628. For new benchmarks, retain that charge
  plus a conservative $6 for both earlier pilots and hardware sizing, leaving
  $14.086372 under the $30 ceiling before these new jobs. Old BEAM cap unchanged.
- First LoCoMo full-history smoke uses two original histories, then answers and
  judges their selected questions. Reserve at most $2; GPU timeout enforces the
  resource envelope. Full memories can be imported into the final ten-history run.
- Added explicit full-history pilot/import preparation and cross-run deduplicated
  API accounting. The existing partial-session throughput smoke remains isolated.

#### LoCoMo smoke launched, sequence queued

- All 92 tests passed before launch. Three additional sequence-gate tests passed.
- Pilot run qwen-3315a8399e999f85, sandbox sb-SiP6eI0rKbkbklPbW6Hj5d,
  $2 reservation, 1,642-second GPU timeout. Two histories, 38 updates, 13 questions.
- Live GPU check confirmed L40S and two running requests. Model startup and JIT
  warm-up completed; first extraction update saved. Collector is independently
  watching and will answer/judge complete histories.
- Started run_qwen_final_sequence.py to gate and execute LoCoMo final, then
  LongMemEval pilot and final. Budget checks include all prior reservations.
- Details and accounting boundaries: docs/qwen-generalization-run.md.

#### Real smoke passed; LoCoMo final running

- The first collector exited on a malformed/partial Modal checkpoint download
  with UnicodeDecodeError. GPU extraction continued. Added a failing-before
  regression test and bounded read-only download retries; reconnected the same
  collector without regenerating model outputs. Persistent corruption still fails.
- LoCoMo pilot completed all 38 extraction updates and 13/13 valid answer/judge
  results. Extraction wall time 312.515s after startup; accounted Modal upper
  estimate $1.098575. GPU termination confirmed. All 96 tests now pass.
- Final LoCoMo sandbox sb-h9oFbCtdYQCq2bKy57Z48e is running with a $4 reservation,
  3,833-second timeout, and the same cached image. Both pilot memories imported
  after validating unchanged worker/model/prompt hashes. Only collector/orchestration
  code changed; both source and destination code hashes remain recorded.
- Sequence controller remains live and will start LongMemEval pilot only after
  LoCoMo final completes successfully. Status: work/qwen_final_sequence/status.json.
  Full benchmark scores and total runtimes are not yet available.

### Task: Adaption augmentation of teacher traces, 2026-09-11

**Status:** awaiting user direction before external mutation or spending.

- Read the requested Adaption Docs skill and quickstart. Generated Augment
  reference failed to load; retrieved the official OpenAPI spec over HTTP and
  checked it against installed adaption 0.12.0.
- Verified Augment retrieves existing rows from a curated pool, using topic
  matching or general-topic counts. It does not generate new extractor traces
  from our seeds and exposes no custom task-generation prompt.
- Corrected docs/adaptive-data-training-plan.md. The previous seeded 32/600-row
  plan must not be executed through this endpoint as trace-based synthesis.
- Existing 564 fitting BEAM teacher candidates remain unchanged. No upload,
  quote request, generation, training or credit spend. Need a choice between
  curated-pool augmentation and investigating a task-specific generation route.
- Did not modify or interrupt the independently running Qwen evaluation sequence.

### Task: Recover LoCoMo final timeout, 2026-09-11

**Status:** in progress. User authorized recovery of the unfinished history.

- Remote sandbox poll returned 0; remote checkpoint matches local state exactly.
- LoCoMo final stopped at 266/272 updates, 45/50 valid answers/judges. History 5
  completed 22 sessions; session 23 has APITimeoutError with no saved response.
- Server log shows generation continued until the 600-second client deadline.
  This does not establish whether the unfinished output was useful or repetitive.
- Recovery retains the original run and failed call, imports nine complete
  histories plus the 22-update prefix, and reuses all 45 existing answers.
- Request timeout increases to 1,800 seconds; prompts, output allowance, model,
  precision, GPU and answer/judge settings stay unchanged. No blind API retry.
- Reserve at most $2.50 additional Modal cost inside the original $30 cap.
  Conservative available amount before recovery was $10.721112 after margin.
- Added a reconciliation regression test for prefix reuse and rejection of saved
  responses or non-timeout failures. LongMemEval remains gated on completion.

#### Recovery launched

- All 97 local tests passed. Continuation preparation independently verified each
  reused answer's source memory hash; 45 unique successful results copied intact.
- Run qwen-fae81752b877dc40, sandbox sb-SfcjJwlsspAQVn3lIKnceM,
  directory work/qwen_locomo_final_recovery. GPU timeout 2,190 seconds, $2.50
  reservation, prior project accounting $18.778888. Old records remain unchanged.
- GPU start recorded 2026-09-11T12:32:37.935452+00:00. Collector watches separately
  and will answer/judge the missing five questions after their memory completes.
- Longer request timeout is recorded in the payload and new worker code hash.
  Recovery timing must be reported separately from original and pilot stages;
  the offline gap is not a GPU runtime or a valid fresh-run speedup comparison.

#### User stopped excessive generation; streaming diagnostics added

**Status:** GPU stopped; diagnostics undergoing offline verification.

- User authorized stopping the second session-23 attempt and adding streamed
  diagnostics. Sandbox termination and collector exit confirmed. Progress
  heartbeat paused. No additional retry or LongMemEval run launched.
- Recovery recorded $1.333978 additional GPU cost and finished at
  2026-09-11T12:47:51.263196+00:00. Still 266/272 updates and 45/50 valid results.
- Prior updates in this history averaged 368.864 output tokens, maximum 605.
  Server logs showed around 41 tokens/second for the ongoing session-23 request.
  Repetition remains an inference, not confirmed from response text.
- Added streamed completion snapshots separate from memory, final API usage
  validation, an absolute request deadline, and local collector mirroring.
- Initial test fixture rejected nullable streamed finish reasons; corrected it
  to model SDK stream objects. All four new tests then failed because streaming
  was absent; after implementation, all 14 targeted tests passed.
- No partial response is accepted as a memory update. Frozen historical configs
  and their original checkpoints are unchanged. See docs/qwen-streaming-diagnostics.md.

#### Streaming diagnostics verified offline

**Status:** implementation complete; live verification not run.

- Full suite initially found two collector mocks missing the real checkpoint
  `calls` field. Updated their fixtures and added a streamed-artifact mirroring
  assertion without weakening the async fan-out checks.
- All 101 tests passed; git diff --check passed. Test API responses are mocked,
  not paid calls. Live vLLM streaming and generation root cause remain unverified.
- The stopped recovery retains 45 valid results, five explicitly missing results,
  no discarded completed answers, and an unresolved in-flight extraction attempt.
- No new GPU/API calls launched. Next step requires an explicitly authorized,
  bounded diagnostic retry of the single failing update using the new worker.

### Task: Launch streamed LoCoMo diagnostic, 2026-09-11

**Status:** preparing. User explicitly requested a new run.

- Confirmed the stopped recovery sandbox exit code 137. Remote state still has
  22 completed updates in history 5; no new result from that attempt to recover.
- Reuse the original final run's intact 266-update checkpoint and 45 answers.
  The stopped sibling recovery and its $1.333978 cost remain preserved separately.
- New directory work/qwen_locomo_stream_diagnostic. Streaming worker keeps the
  same prompt, decoding settings, full remaining output allowance and GPU.
- Restore a 600-second absolute request deadline for a bounded diagnostic;
  partial text is now saved separately and never applied as a memory update.
- Reserve at most $1.50 inside the $30 total Modal cap; available before launch
  is $9.387134 after the existing safety margin. No automatic further retries.

#### Streaming diagnostic launched

- Run qwen-f98b73613d26e596, sandbox sb-Z7wVxKMWQnSTvZix1CUbYg,
  image im-Vxb1JoCvTgMaRjaQw1vfUC. GPU start 2026-09-11T12:57:21.917204+00:00.
- GPU timeout 1,095 seconds, $1.50 reservation, prior accounted total $20.112866.
- Independent collector started with answering/judging enabled only for complete
  histories; 45 prior results already imported. New stream artifacts are separate.
- Resumed the existing one-minute ASCII heartbeat targeting this diagnostic,
  excluding stale failures from archived attempts. It cannot retry or spend.

### Task: Commit and push current code and reports, 2026-09-11

- Staged only code, tests, configuration example and aggregate documentation.
  Credentials, raw answers, memories and training traces remain ignored/local.
- Independent review identified a frozen-payload integrity gap: launch checked
  code hashes but did not compare payload.json against configuration.json.
- Added payload equality and canonical fingerprint validation before launch and
  when reusing a prepared directory. Regression failed before implementation.
- The active diagnostic uses its already uploaded payload and frozen image;
  this local validation change does not alter that run or launch new work.
- All 102 offline tests passed after the fix; git diff --check passed. Fetched
  origin/main matched the starting revision. Secret-pattern scans found no
  matches in publication candidates. Live streaming validation remains separate.

#### Streamed diagnostic confirmed repetition; stopped by user

**Status:** stopped; no further paid retry authorized.

- Live snapshot showed session 23 repeatedly extending its narrative array.
  At 316.5 seconds it held 54,116 characters: 588 quoted strings longer than
  40 characters, only 125 distinct; each distinct string appeared repeatedly,
  up to five times. This confirms repetition within one generated response.
- Prior complete updates averaged 368.864 API output tokens, maximum 605.
  Diagnostic chunk/character counts are not API token usage; final usage was
  unavailable while the stream was ongoing.
- User authorized stopping. Sandbox termination and collector exit confirmed;
  one-minute heartbeat paused. Completed memories/results remain intact.
- Decoding uses temperature=0 and does not explicitly set the Qwen-recommended
  presence penalty. Official Qwen3.5-9B guidance recommends non-thinking general
  sampling temperature=0.7, top_p=0.8, top_k=20 and presence_penalty=1.5, and
  discusses presence penalties for endless repetition. This is a plausible
  contributor, not an isolated causal finding. JSON constraints and this prompt
  remain other possible contributors.
- Maximum remaining output allowed the failure to continue; raising timeouts
  did not solve it. No decoding, prompt or schema settings changed in this turn.
- Source: https://huggingface.co/Qwen/Qwen3.5-9B#best-practices

### Task: One-update Qwen decoding experiment, 2026-09-11

**Status:** launch requested by user; isolated from final benchmark results.

- Preserve parallel small-model/GPU configuration work. Explicitly use original
  Qwen3.5-9B revision on L40S, BF16, structured output, concurrency eight.
- Prepare only LoCoMo history 5 session 23 from its exact 22-update prefix.
  Full history remains intact so session-count prompt text does not change.
  Reconstructed prompt hash matches the original failing request exactly.
- Test the documented non-thinking general sampling bundle: temperature .7,
  top_p .8, top_k 20, min_p 0, presence_penalty 1.5, repetition_penalty 1.
  Prompt, JSON schema, seed and full remaining output-token allowance unchanged.
- Diagnostic deadline 180 seconds; GPU reservation at most $1.25. Only one new
  update is allowed, no answering/judging. Outputs stay in a separate probe run.
- Sampling regression failed before implementation (temperature remained zero),
  then passed. Full current checkout suite: 106 tests passed, no paid test calls.
- Testing the sampling bundle does not isolate which individual parameter helps,
  and one successful update would not establish general benchmark improvement.

#### Decoding probe launched

- Run qwen-2a2fcabfa6ff70fb, sandbox sb-nuPklNfWogzQJP9a6SKQX4,
  GPU start 2026-09-11T13:21:28.562720+00:00, timeout 821 seconds.
- Prior total accounting including other reservations $22.799836; this probe
  reserves at most $1.25 under the same $30 cap. Other experiments unchanged.
- Collector started without --evaluate. The smoke scope prevents benchmark
  answering. Its selected-question summary will remain missing by design;
  evaluate this probe using exactly one new extraction result, not QA completion.
- Startup observation: no worker log during the initial several-minute wait.
  Remote process inspection then showed worker elapsed time zero, followed by
  successful weight loading at 13:29:15 UTC and compilation warmup. Thus the
  initial delay preceded worker execution, not an extraction repetition loop.
  The ledger's gpu_started_at is the allocation-request timestamp, not a
  verified container-start timestamp; elapsed accounting remains conservative.

#### Decoding probe completed; separate 0.8B status checked

- 9B probe completed exactly one update with identical prompt hash, 14,624 API
  input tokens, 307 API output tokens and stop finish reason. Request elapsed
  13.469 seconds; extraction phase 16.392 seconds. Valid JSON and no duplicate
  entries. Sandbox stopped with termination confirmed; conservative cost
  $1.141364, invoice unknown. No answering/judging or final-memory promotion.
- Quality is not fully cleared: five new automatic warning records, including
  an existing-key chain mismatch; manual check also found prompt-rule issues.
  Details in docs/qwen-decoding-probe.md. No final accuracy inference made.
- User separately requested checking the 0.8B run. Read-only live observation
  around 13:34 UTC: work/qwen08_locomo_smoke_c10, qwen-c9655d422b33689e,
  sandbox sb-K0qgHjWqFLdrGzzLtHjBU3, L4, concurrency 10, two updates per
  history across ten histories. Model loaded after 438.432 seconds of startup.
  Only one of twenty planned updates complete; ten requests in flight.
- Confirmed repetition in one 0.8B stream at elapsed 286.104 seconds: 56,835
  characters, 913 quoted strings longer than forty characters, only seven
  distinct, with one sentence repeated 906 times. API output usage unavailable
  while streaming. Payload has no explicit sampling bundle, so temperature=0
  default applies. This shows a generation failure, not lack of concurrency.
- 0.8B reservation is $1.25. No stopping, retrying, decoding changes or new
  cloud resources were authorized by the status-check request or performed.

#### User-authorized 0.8B stop

- User explicitly approved stopping the looping 0.8B smoke run. Verified local
  model/run identity before terminating sb-K0qgHjWqFLdrGzzLtHjBU3. Subsequent
  remote poll returned exit code 137, confirming termination.
- Saved artifacts remain in work/qwen08_locomo_smoke_c10: ten history states,
  one completed update, and eleven stream snapshots at the post-stop check.
  In-flight outputs are diagnostic partials, not valid completed updates.
- Existing collector owns the directory lock; did not override it or race its
  writes. Final accounting is left to that collector. No retry or new run
  launched; no changes made to the separate 9B diagnostic.

### Task: Finish 9B LoCoMo and test corrected 0.8B, 2026-09-12

**Status:** in progress

#### Sampling and continuation implemented

- User authorized finishing the 9B LoCoMo evaluation and testing a corrected
  0.8B run. Modal total cap remains $30; current conservative availability is
  $5.703559 after the existing accounting margin. No cap increase.
- Failing-before regression showed normal prepared payloads omitted sampling
  and therefore used the worker's temperature-zero fallback. New preparations
  now freeze model-specific settings from the official model cards: 9B general
  non-thinking uses .7/.8/top-k 20/presence 1.5; 0.8B text non-thinking uses
  1.0/1.0/top-k 20/presence 2.0. Both use min-p 0 and repetition penalty 1.
- Focused regression now passes. The streaming transport preserves structured
  output and the full remaining-context allowance.
- Added prepare_qwen_locomo_completion.py. It validates stopped source runs,
  exact history identity and first-22-call equality; imports nine complete
  histories plus the successful session-23 probe; copies exactly 45 results
  only after memory-hash verification; and resumes the affected history at
  session 24. Raw source runs remain immutable.
- Ten focused continuation, small-model and streaming tests pass. Full checkout
  validation and offline preparation remain next, before paid launch.
- Sources: https://huggingface.co/Qwen/Qwen3.5-9B#best-practices and
  https://huggingface.co/Qwen/Qwen3.5-0.8B#best-practices.

#### Offline gates passed and both runs launched

- Full checkout: 108 tests passed. Initial continuation preparation failed
  before any cloud action because the helper had not loaded `.env`; its empty
  lock-only directory then exposed a restart edge case. Fixed both without
  weakening state checks, reran focused tests, and prepared successfully.
- 9B continuation preflight: ten histories, 267/272 updates already present,
  45 exact results reused, one history resumes at session 24. Run
  qwen-803dc93943549265 on L40S, sandbox sb-beHtUW8LPQKMAMR5GrOp5z,
  $1.50 reservation. Collector includes answering/judging for only the five
  missing questions.
- Corrected 0.8B smoke preflight: ten histories, 0/20 updates, no answers or
  results. Run qwen-81727a19ffb04ccc on L4, sandbox
  sb-0gYg75inHHG4Wu8h9yZwpl, $1.25 reservation. Collector has no evaluation.
- The two collectors and GPUs are independent. Combined new reservation $2.75
  under $5.703559 available after the project accounting margin.

#### 9B complete; corrected 0.8B smoke passed

- 9B continuation completed five new updates in 60.417 seconds after 233.286
  seconds of startup. All ten histories and 272 updates complete. The five new
  questions produced five valid answers and five valid judge calls; final
  accounting is 50/50 unique valid results, no missing/unexpected/failed IDs.
  Accuracy is 44/50, 88%; the new five scored 4/5. Launch-to-finalization time
  422.639 seconds. Modal accounting $0.868042; invoice unverified. New answer
  usage 58,538 input / 219 output tokens and new judge usage 3,813 input /
  1,084 output tokens; estimated costs $0.029663 and $0.016798 respectively.
- Corrected 0.8B smoke completed 20/20 extraction updates over ten concurrent
  histories. Every call returned valid JSON with stop finish reason; no failures
  or runaway string loop. Extraction wall time 179.162 seconds after 421.443
  seconds startup. API-reported totals: 39,511 input and 3,200 output tokens.
  One response duplicated three narrative entries within a nine-entry list, so
  generation stability passed but output quality is not perfect.
- 0.8B smoke sandbox termination confirmed. Modal accounting $0.920109;
  invoice unverified. Smoke intentionally made no answer/judge calls; its
  question-level summary remains missing by design and is not an operational
  failure.
- Remaining conservative Modal availability after margin: $3.915407. Remaining
  answer/judge accounting allocation: $17.056340. User authorized the 0.8B run;
  next step is a fresh full LoCoMo 50 preparation, not reuse of partial smoke
  memories.

#### Full 0.8B extraction launched; answer/judge permission blocked

- Fresh full LoCoMo preparation passed payload fingerprint, code hash, frozen
  sampling and workload checks: ten histories, 272 updates, original 50
  questions, no smoke checkpoint reuse.
- Run qwen-6f28185da3f7666b launched on L4 in sandbox
  sb-vzqYBEAOGt8d8iUThLNiYX with concurrency ten and $3.25 Modal reservation.
  Prior Modal accounting $25.584593, so the total remains below $30.
- Attempt to start collection with Luna answering and GPT-5 judging was blocked
  by the environment safety reviewer because those calls send conversation-
  derived memory/questions to external OpenAI services. No such call was sent.
  A Modal-only checkpoint collector is running so extraction continues.
- Required user confirmation: explicitly authorize sending extracted memory plus
  benchmark questions to gpt-5.6-luna, then sending question, reference answer
  and generated answer to the GPT-5 judge for these 50 LoCoMo items.

#### 2026-09-12 01:16 +07 - Fine-tuned 0.8B benchmark preflight

**Status:** in progress

**Completed**

- Inspected `huyxdang/adaption_agent_memory` at pinned Hub revision
  `8bcb7c3e333fb1b5577330886820150c68b7860f`. It is a rank-32 LoRA adapter
  for Qwen3.5-0.8B, not a merged checkpoint.
- Added pinned adapter configuration, vLLM LoRA startup arguments and adapter
  request routing. The tokenizer and served base remain the exact pinned
  `Qwen/Qwen3.5-0.8B` revision used by the baseline.
- Prepared a no-cloud LoCoMo smoke run in
  `work/qwen08_ft_locomo_smoke_c10`: ten histories, two updates each,
  concurrency ten, L4 and the same base-model sampling bundle.
- The current untuned full run had 101 call records, including 91 completed
  updates, one unknown outcome and nine active calls. One history is terminal
  at one completed session because its second request timed out. The other nine
  histories continue; no retry was made.

**Evidence**

- The two new adapter tests failed before implementation because `prepare()`
  rejected the adapter arguments. After the change, all 110 offline tests and
  `git diff --check` passed.
- Hub metadata and the model card identify the intended official base, while
  `adapter_config.json` contains the stale path
  `togethercomputer/Qwen3.5-0.8B`, which the Hub no longer resolves. A live
  adapter smoke is required to prove compatibility.
- vLLM 0.21 documentation requires `--enable-lora` and
  `--lora-modules name=path`; the configured maximum rank is 32.

**Decisions**

- Compare the fine-tuned adapter on the exact same frozen LoCoMo 50 with the
  same extraction prompt, sampling, Luna answerer and GPT-5 judge.
- Do not launch the paid smoke until the current reservation is reconciled and
  the user explicitly authorizes another Modal job. The existing $30 total cap
  remains unchanged.

**Next**

- Let the untuned run reach a terminal state, reconcile its Modal accounting,
  then run the prepared fine-tuned smoke before preparing a full evaluation.

**Blockers**

- A full second run will not fit the currently reserved remainder of the $30
  Modal cap. Exact headroom depends on the untuned run's terminal accounting.

#### 2026-09-12 01:45 +07 - Fine-tuned LoRA smoke stopped on runaway output

**Status:** smoke failed; full fine-tuned benchmark not authorized

**Completed**

- Launched the pinned adapter smoke as run `qwen-5078c60ff3f8eac2` in sandbox
  `sb-TySYERzllY8IFtpQX6bMgJ` on one L4. The adapter downloaded and vLLM served
  it successfully over the official pinned Qwen3.5-0.8B base.
- Nineteen of twenty extraction updates completed with valid JSON and stop
  finish reasons. Their API usage was 39,154 input and 4,055 output tokens.
  Mean completed-call time was 44.371 seconds; range 38.291 to 49.326 seconds.
- The final call produced 110,712 whitespace characters across 19,535 streamed
  chunks for 283.169 seconds without a finish reason or final usage. Stopped the
  exact sandbox to prevent further spend. The other 19 outputs were preserved.
- Confirmed sandbox termination with exit code 137 and no remaining Modal
  containers. Conservative Modal accounting reached the full $1.10 smoke cap;
  actual provider invoice remains unverified. No answer or judge calls ran.
- Reconciled the interrupted call to an explicit `unknown_outcome` with
  `SandboxStopped`. Nine histories are `smoke_complete`; one is blocked after
  its first successful update.

**Evidence**

- No repeated entries appeared within the 19 successful JSON responses. Their
  output-token range was 49 to 439, mean 213.421. Automatic memory validation
  recorded 47 warnings, which are heuristics rather than accuracy grades.
- Added a failing-before regression for stopped in-flight calls. All 111
  offline tests and `git diff --check` pass after the reconciliation fix.
- The separate untuned run stopped normally at its sandbox timeout. Final
  collection found six complete histories, 184 completed updates, three
  unknown-outcome histories and one invalid-output history. Exactly 32 of its
  50 questions have valid saved evaluations; 18 remain missing. Modal
  accounting is $2.405934 against its $3.25 reservation.

**Decisions**

- Do not launch the full fine-tuned benchmark from this smoke. Loading works,
  but generation stability does not yet pass the gate.
- Keep the fine-tuned and untuned partial results labeled as incomplete. A low
  partial score would not diagnose the pipeline or model.

**Next**

- Diagnose the single whitespace loop and test one bounded decoding change in
  a small probe before another full fine-tuned run.
- Reconcile the untuned run through an explicit continuation if completing its
  final 18 questions remains desired.

**Blockers**

- Only about $0.91 remains under the existing $30 Modal ceiling using current
  conservative accounting. No additional paid retry is authorized.

### Task: Gemma partial grading, stopped-run accounting, and failure replay

#### 2026-09-12 - Recovery fixes and bounded diagnostic

**Status:** in progress

**Completed**

- Removed the complete-all-histories gate after Modal has stopped. Complete
  memories can now be graded; failed and missing memories remain explicitly
  blocked and cannot trigger replacement extraction. Reports state coverage
  and whether scores cover only a subset.
- Stop waits for confirmed termination and records cost once. Repeated
  collection no longer increases a stopped run's cost. Collecting saved cloud
  artifacts validates their frozen identity without requiring today's source
  files to match the historical worker.
- Verified both LoCoMo 003 and 004 exited with code 137. Contrary to the prior
  handoff, neither has a complete history: 57 and 84 updates respectively were
  saved. There are no completed memories to grade from either attempt.
- Saved provider billing evidence for both stopped runs. The shared app
  interval totals $0.64367187; this is not a per-sandbox allocation. Each run's
  conservative ledger bound is $1.14367187, deliberately counting the full
  shared interval plus a startup allowance for each.

**Evidence**

- 23 focused offline tests passed; full suite running.
- `work/gemma-locomo-billing-reconciliation.json` preserves original ledgers
  and provider metering. Raw artifacts remain local.
- `tools/replay_extraction.py` isolates LoCoMo 004's failed fourth session,
  reuses its original image and prompt, and compares a fixed-schema sentinel,
  streamed replay, and non-streamed replay. Reservation: $1.10 Modal;
  no OpenAI calls. Original competing traffic is not recreated.

**Next**

- Inspect diagnostic outputs before changing decoding or launching another
  full benchmark. Malformed JSON under a requested grammar is not sufficient
  evidence to blame the model alone.

#### 2026-09-12 16:46 - Recovery checks completed

**Status:** complete

**Completed**

- The fixed-schema sentinel passed. Both isolated failed-prompt replays
  returned byte-identical valid JSON with a normal stop and 724 output tokens.
  The earlier malformed JSON did not reproduce. Five narrative lines contain
  only three unique entries, so extraction quality still needs attention.
- Confirmed diagnostic sandbox exit 0. Conservative cost $0.70434086 against
  its $1.10 reservation; zero OpenAI calls. Diagnostic input/output usage:
  10,338 / 1,464 tokens across three calls.
- Full offline suite passed: 116 tests. `git diff --check` passed. Added a
  regression for collecting historical partial runs after local code changes.

**Evidence**

- `docs/gemma3-locomo-recovery.md` contains the verified state, fixes, billing
  caveats, replay results, and limitations. Raw evidence remains in
  `work/gemma-locomo-schema-replay-001`.
- A diagnostic log read initially used an unsupported SDK `timeout` argument;
  no sandbox was affected. Subsequent collection reads saved volume artifacts.

**Next**

- The original concurrent failure remains unexplained. A bounded concurrency
  reproduction is the next diagnostic, not an unverified decoding change.
- No full benchmark, commit, or push was performed in this recovery.

### Task: Push recovery and continue Gemma; review Sol and fine-tuning

**Status:** in progress

**Completed**

- Committed recovery code, tests, diagnostic tooling, and aggregate report as
  `f291c5497602742e536870f96dd8349a11422581`. Push and remote SHA verified.
  Unrelated existing documentation edits and raw run records were not included.
- Prepared `gemma3-locomo-50-005` and requested its launch using the pushed,
  frozen source, one L4, four histories concurrently, and a $2.50 reservation.
  BEAM final-90 is already complete and is not repeated. OpenAI continuation
  allocation is $1.45; no allocation for Sol or LongMemEval has been increased.
- Read current Adaption documentation and existing account results. Gemma's
  best internal fine-tuning win rate was 45.57%; Qwen 0.8B's was 56.32% on the
  same `agent-memory` dataset. Both completed three iterations without meeting
  the 70% target. Both checkpoints are available.
- Dataset adaptation score fell from 10 to 7, but the training jobs selected
  original columns, so this is not an established explanation of Gemma's result.
- Read-only access check succeeded for `gpt-5.6-sol`; no Sol inference started.

**Evidence**

- `docs/extractor-next-experiments.md` records the scopes, cost boundaries,
  verified training results, next experiments, and open data/context questions.
- `work/adaption-training-review-20260912.json` retains relevant API responses.

**Next**

- Collect the launched LoCoMo histories and grade complete memories within the
  remaining OpenAI allocation. Keep failures and partial coverage explicit.
- Test the already-trained Gemma checkpoint on dev before paying for another
  training run. Size Sol extraction separately and obtain its spending cap.

#### 2026-09-12 16:58 - LoCoMo launched

- Sandbox `sb-pZ3lhh7o1Bay0b0CSrJxCz`, immutable image
  `im-U9cTKFqyF0bBIs3blZDkwv`, volume run `vllm-aa2e72a70bcf9555`.
- GPU reservation started at 09:57:30.650260 UTC. Hard timeout 3,371 seconds.
- Collector and subsequent bounded OpenAI evaluation started through the
  canonical CLI, execution session 74749. It waits for extraction to stop,
  imports complete memories, and records blocked questions explicitly.
- No runtime code was changed after preparation. Documentation updates remain
  local; the requested recovery commit is already pushed and verified.

#### 2026-09-12 - Sol budget approved and sized

- User approved $20. Recorded it as one total cap for Sol extraction plus
  answering/judging and unresolved exposure, separate from Gemma allocations.
- Added `tools/estimate_sol_budget.py` to reprice saved per-history usage.
  BEAM extraction proxy $15.06-$18.33; LoCoMo $12.13. Both together exceed $20
  at standard uncached rates even before evaluation; LongMemEval is additional.
- No Sol paid call has run and no serving/runtime code was changed while the
  Gemma collector is active. Benchmark priority needs clarification.
- Gemma's saved checkpoint reached 40/272 updates with nine running histories
  and one invalid-output history. The unaffected histories continue.

#### 2026-09-12 - Five-minute monitoring and isolated Sol preparation

- User confirmed LoCoMo first for Sol and requested ASCII progress for all runs
  every five minutes. Heartbeat `memory-benchmark-progress` is active with that
  interval and read-only checks; it must not dispatch or retry paid calls.
- Sol work is isolated at `/private/tmp/adaption-sol-final-20260912` to preserve
  the active Gemma collector's frozen source hashes. Planned run ID:
  `sol-locomo-50-001`, stored under that worktree's `runs/` directory.
- Sol remains PREPARING (no paid calls). The $20 total includes extraction,
  answering, judging, smoke and unknown exposure. Smoke will pause the same
  final-50 run after two new calls, then resume its saved checkpoints.
- Offline checks cover budget restoration, conservative schema-inclusive
  reservations, prompt fit, metadata persistence, and pause/resume without
  replay. Full-suite verification is underway.
- Latest Gemma checkpoint: 157/272 saved updates; one complete history, seven
  invalid-output histories, two running; no grades yet. Continue unaffected
  histories and report blocked coverage explicitly.

#### 2026-09-12 - Sol smoke passed; final-50 resumed

- 122 offline tests passed. The two initial BEAM fingerprint failures were due
  to a symlink resolving dataset paths outside the isolated checkout; copying
  the same data into the checkout restored the existing hashes without changing
  expected fingerprints or dataset content.
- `sol-locomo-50-001` is now RUNNING from
  `/private/tmp/adaption-sol-final-20260912` (its `runs/` contains checkpoints).
  Full source digest: `9c4eaed13d40e980cafb3aec6fc2ffb01977487a6f0f8e899ca64fb4c91588c5`.
- Paid smoke saved two complete valid extraction responses: 3,938 input tokens,
  592 output tokens, zero reasoning tokens; both normal stop. Spot-check against
  the first two source sessions found supported facts, attribution and dates.
  This is a usability check, not a benchmark accuracy result.
- Conservative accounted smoke cost $0.03153. The same run was resumed with the
  same $20 total cap; its ledger restores smoke spend, not a fresh $20 allocation.
- Executor is serial (concurrency 1). Shared memory is built once per history;
  answering/judging follow extraction. No claim of asynchronous Sol execution.
- Five-minute ASCII monitoring should now report both Gemma and Sol as active.
  Latest Gemma checkpoint was 164/272, one complete, seven invalid-output and
  two running histories. Its frozen runtime remains unchanged.

#### 2026-09-12 - LoCoMo judging argument fix

- Reproduced the missing `category` TypeError with a new test covering all four
  LoCoMo categories. The vendored Mem0 helper requires category but does not use
  it: this version has one unified prompt, not category-specific instructions.
- Fixed the canonical judge adapter to format the existing frozen JUDGE_PROMPT
  directly. Vendored prompt text, rubric, parser and model settings are unchanged.
- Focused tests pass, including real LoCoMo adapter records through offline
  answering/judging for all four categories. The previously blocked saved Gemma
  answer now constructs its judge request correctly without an API call.
- The fix is in the Desktop checkout only. Active Sol's isolated source identity
  was verified unchanged. Do not patch the running process or alter old run
  hashes. After extraction ends, continuation must record the fixed code version
  and reuse the saved memories/answers without paying for extraction again.
- No paid calls were launched by this fix. All 118 tests passed; all 50 frozen
  LoCoMo questions build valid judge requests with unique IDs. Prompt hashes and
  benchmark configuration fingerprints remain unchanged.

#### 2026-09-12 - Preparing fixed-code evaluation continuations

- User authorized continuation. Both original processes have exited.
- Sol finished 272/272 extraction updates, 10/10 histories, one saved answer,
  zero grades. Prior OpenAI cost bound $4.2857236, no unknown exposure.
- Gemma has 3 complete histories covering 16 questions, one saved answer and
  34 explicitly blocked questions. Prior OpenAI cost $0.0023388; Modal bound
  $1.53714900448544 is separately recorded in the original artifact graph.
- New continuation support lives in `/private/tmp/adaption-sol-final-20260912`.
  It verifies identical configuration and question IDs, rejects unfinished
  memories or unknown provider calls, copies artifacts without changing their
  hashes/code provenance, and retains source generation and run lineage.
- Planned child runs in that worktree's `runs/`: `sol-locomo-50-eval-002` and
  `gemma3-locomo-50-eval-006`. They reuse memory and answers, not full-pipeline
  speed measurements. Prior calls remain in each child's budget ledger.
- Existing caps remain $20 Sol total and $1.45 Gemma OpenAI total. No new GPU
  work. Focused continuation/budget/judge/CLI tests passed, full suite running.

#### 2026-09-12 - Both fixed-code evaluations launched

- All 125 tests passed. Isolated source frozen at local commit `5998ba0`, after
  preserving the original Sol source at `014bf0f`. No runtime edits after launch.
- `sol-locomo-50-eval-002` and `gemma3-locomo-50-eval-006` are running concurrently
  from `/private/tmp/adaption-sol-final-20260912/runs`. Each coordinator is serial
  internally. Execution sessions are 37373 and 92684.
- Verified real API judging now succeeds: Sol 3/50 graded; Gemma 5/16 eligible
  graded, with all 34 blocked questions retained. New calls are answering/judging
  only; saved first answers were reused. No new extraction calls.
- At that snapshot cumulative OpenAI accounting was $4.2968172/$20 for Sol and
  $0.032232/$1.45 for Gemma. Child ledgers include inherited calls, so do not add
  parent costs again. Gemma's $1.537149 Modal bound remains separate.
- Five-minute ASCII heartbeat resumed, targeting both child runs. It is read-only
  and will pause once both processes end and final coverage/results are reported.

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

- Modal ceiling exhausted: $34.999 of $35.00 accounted. Neither BEAM nor
  LoCoMo can be finished for Gemma 3 4B without an explicit new cap.
- Extraction call timeout versus concurrency is unresolved. Concurrency four
  produced four `unknown_outcome` histories on LoCoMo; concurrency two
  produced two on BEAM. Decide whether to raise the client timeout, cap
  memory growth, or hold concurrency at two, before any relaunch.
- The partial Gemma runs cannot be resumed. Their `configuration.json`
  predates the version 2 schema and carries no `spec_sha256`, so
  `import_modal_memories` rejects them by design. Finishing either benchmark
  means restarting it.
- No Gemma experiment specification exists. All four files in
  `experiment_specs/` are Qwen, so Gemma cannot be launched through the
  canonical command until one is written.
- Two progress logs are live: this file and `PROGRESS.md` at the repository
  root. Decide which is canonical and fold the other in.
- LongMemEval Qwen 9B full run is sized: about 49M prompt tokens, 1M output
  tokens, full prefill of every prompt. Choose L40S at concurrency 24 (1.5
  to 2.5 h, $5 to $8, likely two launches or a raised 7,200 s cap) or H100
  at concurrency 48 (35 to 50 min, $4 to $5, one launch, first-boot compile
  risk). The final-100 preset still says concurrency 4 and the CLI has no
  GPU flag, so either choice needs a new frozen spec before `prepare`.
- Prefix caching does not reuse the memory prefix for Qwen3.5-9B on vLLM
  0.21 (0 percent across 24 sessions). Do not plan on it; retest on a newer
  vLLM only if the full run's prefill cost matters later.
- Modal spend today: $4.55 of smokes on the old `dxuanhuy2003` workspace,
  then on the new `hellgod67` workspace about $1.95 for the failed H100 run
  and a $10 reservation for run 002. Record the $30 credit as the new ceiling.
- H100 is unusable for Qwen3.5-9B on vLLM 0.21 (two silent stalls after
  torch.compile). Only revisit with a newer vLLM or a logged probe.
- Both interrupted runs finished after the person-run reconciliations
  (LongMemEval 61/100, Mem0 BEAM 63/90). The isolated source copies under
  `/private/tmp` are no longer needed; the configuration-gated resume makes
  them unnecessary for future runs.
- Recover the three LongMemEval histories lost to the whitespace loop, or
  bound extraction output for new specs so a loop fails fast as invalid
  output and the worker's retry path gets another attempt.
- The transport records a connection that never opened as `unknown_outcome`;
  decide whether `httpx.ConnectError` should map to `not_dispatched` in the
  transport itself so future outages do not need a person-run reconciliation.
- Overlap grading with extraction: import complete histories while the
  Modal sandbox runs, with a provisional executor cost record finalized at
  stop. Needs the run store's importer to accept a second executor record.

