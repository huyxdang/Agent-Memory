# Memory system design

Working notes for the write-time memory system. Decisions recorded here are
current as of 2026-09-08 and will change as the smoke test and the five
benchmark questions push back.

## Goal

Reproduce the claim in Adaption Labs' "Better Agent Memory Starts Before
Retrieval": a memory written carefully at write time, in two forms, with
supersession instead of overwriting, beats full-history inference on
LongMemEval while the answerer processes a small fraction of the tokens. Their
numbers: full history 60.6%, their system 90.6%, Mem0 OSS 71.6%. Our
full-history baseline on five fixed questions is the reference we compare
against.

## Two forms of memory

Every memory line is one of two kinds.

- **Atomic**: an exact fact that must survive verbatim. Written as
  `key: value`. Times, dates, names, amounts, preferences.
- **Narrative**: a concise summary of what happened and why. Context and
  reasoning that make the facts matter.

The extractor decides which form each piece of information takes. Both kinds
carry the date of the session they came from.

## Supersession

A fact that changes is never edited or deleted. The extractor appends a new
atomic line for the same key that carries the whole chain, newest value
first, copied from the previous line for that key:

```
s2   charity 5K personal best: 27:12
s8   charity 5K personal best: 25:50 <- 27:12
s14  charity 5K personal best: 24:10 <- 25:50 <- 27:12
```

Every update is a new line at the bottom. Nothing above is edited. At read
time the answerer sees the last line per key, which is the current value with
its full history. Older lines for that key stay in the file.

Check that falls out for free: the tail of a new chain must equal the previous
line's chain exactly. A mismatch is a recorded extraction failure.

Only atomic lines supersede. Narratives are history by nature and never
replace anything.

## Why append-only, in storage terms

The extractor prompt has the shape `[fixed instructions][memory so far][this
chunk]`. If memory only ever grows at its tail, the prefix through the old
memory is byte-identical between consecutive calls, so provider prompt caching
hits on all of it and only the new chunk and new lines are billed at the
uncached rate. Editing a line in place breaks that prefix. That is why a
chain extension is a new line rather than an edit of the old one.

### Prompt structure that actually caches

Measured on 2026-09-08. GPT-5.6 models only match a cached prefix at a
breakpoint, and the implicit breakpoint sits at the end of the latest message.
With memory and session in one user message, that end changes every call and
nothing is cached: the first smoke run showed zero cached tokens on sessions
2 through 8.

The extractor therefore sends one user message per earlier session's memory
lines, an explicit `prompt_cache_breakpoint` on the last of those, and the new
session as a final message. Each earlier memory message is byte-identical
from call to call, so the cache read covers all of them and the write covers
only the newest memory message. On the second smoke run sessions 4 through 8
read 27 to 47 percent of their input from cache, rising as memory grows;
sessions 1 through 3 miss because the stable prefix is under the 1,024-token
minimum. Chat Completions accepts the breakpoint field on a content block
without error, verified by a direct probe.

Reasoning effort and the structured-output schema are part of the cached
prefix and must stay constant across calls.

## The extraction unit: sessions, and windows when there are none

Extraction runs once per chunk. The extractor sees the memory so far and the
chunk. It returns only new lines. Nothing from a chunk is in memory until that
chunk has been processed, which is fine, because while a conversation is live
its own turns are in the working context anyway. Memory is only needed for
what happened in earlier conversations.

A chunk is a session when the dataset defines one:

- **LongMemEval** gives each question a list of finished sessions, each with
  one timestamp and about twelve turns. A chunk is one list element. Session
  order is the dataset's order, not clock order; within a day, sessions are
  not always sorted by timestamp, so "newest value wins" means later in the
  list.
- **LoCoMo** gives explicit sessions with a date and time each, up to about
  32 per conversation. Both speakers are people, so atomic keys must carry the
  owner (`Caroline's dog's name`) and narratives must keep speakers apart.

**BEAM has no sessions.** Each conversation is one continuous user and
assistant dialogue from about 100K to 10M tokens. There the chunk is a
predetermined window of a fixed number of turns. The window size is a tuning
parameter, and with no timestamps the extractor can only order facts by
position, which makes the order of values in the chain carry the ordering.

So the unit is "chunk", defined as the dataset session when one exists and a
fixed turn window otherwise. Same loop either way.

In a live product the boundary is a design choice: a new chat thread, an
inactivity gap, or a size cap that triggers extraction so the working context
can be trimmed. The dataset sessions correspond to the first kind. Whatever
the boundary, extraction must also run on disconnect or a timer so a cut-off
conversation still gets written.

## Answering, version one

System prompt, all narrative lines oldest first, the last atomic line per
key, the question date, the question. No retrieval, no ranking. If a store ever exceeds the answer
context, that is a blocked run, the same as prompt-too-large today. Retrieval
is a later layer, added only when store size demands it.

## Where it lives

Inside the run record for each question: the final memory store and every
extraction call with its prompt, output, usage, and cost. The memory-writing
usage fields that the full-history baseline reports as zero are filled. The
Inspect bridge maps all of it into the viewer.

## Models

Extraction: `gpt-5.6-luna`, reasoning effort medium, output allowance
128,000 tokens (the model's cap). Answering and judging unchanged from the
baseline. Relative dates are resolved to absolute dates at write time, when
the session date is known.

## Cost shape

For a full LongMemEval-S question, about 44 sessions of roughly 3k tokens
each against a memory that grows to a few thousand tokens. Without caching
that is on the order of 200k extractor input tokens once per question, then
a few thousand tokens per answer instead of about 110k. With caching most of
the extractor input is the cached memory prefix. Reasoning tokens at medium
effort are billed as output and are small at this scale.

## Adjustments from the literature

See `docs/literature.md` for the evidence. Changes adopted:

- Atomic lines carry the session date and, when the text gives one, the
  event date inside the value.
- The extractor is shown the existing keys and told to reuse a key when the
  fact is the same. "Is this a change to an existing key?" is an explicit
  step in the prompt.
- Every atomic value, or its hard anchor (number, date, name), must appear in
  the session text. A line that fails is a recorded extraction failure.
- An unresolved reference becomes a narrative line, never an atomic line.
- Every line carries its session number as provenance.
- Smoke-test metrics: retain recall (evidence turns produced atomic lines),
  update accuracy (later value superseded the earlier one under the same
  key), read recall (the chain survived into the answer prompt).
- Planned ablation on the five questions: chain view versus flat dated
  append, same extractor and answerer.

## Smoke test

`fixtures/memory_smoke_test.json` is eight sessions cut from the
knowledge-update question 6a1eabeb, with the real question, answer, and
question date. Sessions 2 and 8 hold the evidence (27:12, then 25:50).
Session 4 is a marathon-training distractor. Session 7 opens with a prompt
injection. The design has to pass this before it runs on the five questions.
