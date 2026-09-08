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

## Open

- Run memory on the five questions and compare with the baseline's 4 of 5.
- The spending guard projects worst case with the 128k output cap per call,
  about $36 for five questions against a $10 limit. Either raise the limit
  for that run or lower the extraction output allowance.
- Judge reasoning is mostly hidden (GPT-5 reasons in hidden tokens); decide
  whether a separate explanation call is worth breaking Mem0 parity.
- Ablation planned: arrow chains versus flat dated append, same extractor
  and answerer.
