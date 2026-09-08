# Research: chunk boundaries, OpenAI prompt caching, and write-time memory cost

Survey date: 2026-09-08. Design under study: extractor LLM sees
`[fixed instructions][entire memory so far][chunk]`, appends new memory lines,
memory is append-only so the prefix is byte-stable and prompt caching hits.

Legend: **[doc]** = primary documentation or paper text, **[vendor]** = vendor
blog / marketing, **[secondary]** = not verified against the primary source in
this survey (network blocked or page unreachable).

---

## 1. Session and chunk boundaries for memory extraction

### Summary of units in use

| System / paper | Write unit | Context given to the extractor | Notes |
|---|---|---|---|
| Mem0 (paper, OSS) | one new message pair (`add()` call) | conversation summary + last m=10 messages | ADD/UPDATE/DELETE/NOOP against top-10 similar memories |
| Mem0 platform (2026 "token-efficient" algorithm) | per `add()` call, async after the agent responds | not disclosed | single add-only LLM call, no overwrite/delete |
| Zep / Graphiti | one message = one episode; docs say add every chat turn | last n=4 messages (two turns) | max 30 messages per `add_messages` call, 4,096 chars/message |
| Letta / MemGPT | no fixed unit; eviction triggered by context fill | recursive summary + evicted messages | warn at ~70%, flush at 100%, evict ~50% (paper examples); Letta default sliding window summarizes oldest 30% |
| LangMem | whole conversation, after an inactivity debounce | entire conversation (OpenAI message format) | `after_seconds` reschedule on each new message; 30–60 min suggested |
| LIGHT (BEAM paper) | every user–assistant turn | current + preceding turn; scratchpad merged iteratively, compressed 30K -> 15K | BEAM has no sessions, only turns |
| Hindsight | per session ("coarse-grained chunking") | the session | "2–5 comprehensive facts per conversation" |
| SelfMem | none fixed; agent reads a SQLite transcript store with SQL tools | agent chooses | memory fully editable, not append-only |
| LongMemEval paper | index granularity study: session vs round vs fact | n/a | round-level values best for reading; fact-only values lose information |
| ES-Mem / HingeMem | LLM-detected event/topic boundaries | local window around candidate boundary | ablation: removing segmentation hurts multi-hop and temporal |

### Sources

**Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory**
https://arxiv.org/abs/2504.19413 (2025) **[doc]**
Extraction runs on each incoming message pair, with "a conversation summary S retrieved from the database" plus "a sequence of recent messages {m_{t-m}, ..., m_{t-2}}", and in the implementation m = 10. The update phase retrieves s = 10 similar memories and the LLM picks ADD / UPDATE / DELETE / NOOP, using GPT-4o-mini. So the write unit is a single turn, and the extractor never sees the whole memory, only a retrieved slice. No ablation on write-unit size is reported.

**Mem0 docs, `add()` operation**
https://docs.mem0.ai/core-concepts/memory-operations/add (2026) **[doc]**
`add()` takes "the ordered list of user/assistant turns you send"; on the platform it returns `PENDING` with an event_id and is processed asynchronously. `infer=True` (default) extracts, `infer=False` stores raw. Guidance is event-driven ("add memory whenever your agent learns something useful"), not session-end batching; no batch-size recommendation is given.

**Mem0, "Introducing The Token-Efficient Memory Algorithm"**
https://mem0.ai/blog/mem0-the-token-efficient-memory-algorithm (2026) **[vendor]**
"The new algorithm collapses extraction into a single LLM call that only adds. Every extracted fact becomes an independent record." Claims ~2x faster extraction and a LongMemEval score of 94.4 with a mean of 6,787 retrieval tokens. Write-side token counts are not published, the model stack is not named, and the post states scores reflect the managed platform with "proprietary optimizations not available in the open-source SDK". Relevant to this project because it is independent confirmation that add-only writes (no UPDATE/DELETE) are viable at the top of the LongMemEval leaderboard.

**Zep: A Temporal Knowledge Graph Architecture for Agent Memory**
https://arxiv.org/abs/2501.13956 (2025) **[doc]**
An episode is one message ("message, text, or JSON"); "the system processes both the current message content and the last n messages to provide context for named entity recognition. For this paper and in Zep's general implementation, n=4, providing two complete conversation turns." Extraction is per message. On LongMemEval the paper reports 115k tokens (full context) vs 1.6k tokens (Zep retrieval) at answer time and 31.3 s vs 3.20 s latency with gpt-4o-mini; no ingestion cost is reported.

**Zep docs, Adding messages**
https://help.getzep.com/adding-messages (2026) **[doc]**
"You can add at most 30 messages in a single `thread.add_messages` call"; "Each message can contain 4,096 characters by default". The recommendation is to "add chat history to Zep on every chat turn ... as you receive them and in the order that the messages were created". Ingestion is asynchronous; callers poll message UUIDs.

**MemGPT: Towards LLMs as Operating Systems**
https://arxiv.org/abs/2310.08560 (2023; ar5iv HTML used) **[doc]**
"When the prompt tokens exceed the 'warning token count' ... (e.g. 70% of the context window), the queue manager inserts a system message ... warning the LLM of an impending queue eviction." "When the prompt tokens exceed the 'flush token count' (e.g. 100% ...), the queue manager ... evicts a specific count of messages (e.g. 50% of the context window), generates a new recursive summary using the existing recursive summary and evicted messages." The write trigger is context pressure, not a semantic boundary; the agent is expected to move facts to core/archival memory before eviction.

**Letta docs, Compaction (summarization)**
https://docs.letta.com/guides/core-concepts/messages/compaction/ (2026) **[doc]**
"When an agent's conversation history grows too long to fit in its context window, Letta automatically compacts (summarizes) older messages." Default mode `sliding_window` with `sliding_window_percentage` 0.3 (oldest ~30% summarized, ~70% kept), summary limit 50,000 characters, provider-specific summarizer (e.g. claude-haiku-4-5). "Self-compact" variants include the system prompt and tool definitions in the summarizer request specifically "to improve cache hit rates" by keeping an identical prefix. This is the only vendor doc found that ties chunk/eviction policy to prompt-cache reuse.

**LangMem, Delayed Background Memory Processing**
https://langchain-ai.github.io/langmem/guides/delayed_processing/ (2025) **[doc]**
Pattern: "Wait 30 minutes before processing. If new messages arrive before then: 1. Cancel pending processing task 2. Reschedule with new messages included"; "in practice would choose longer (30-60 min) depending on app context". The memory manager receives the whole conversation in OpenAI message format, i.e. unit = one conversation, boundary = inactivity timeout. Motivation stated as avoiding "redundant work when messages arrive in quick succession" and "unnecessary token consumption".

**LangMem conceptual guide (hot path vs background)**
https://github.com/langchain-ai/langmem/blob/main/docs/docs/concepts/conceptual_guide.md (2025) **[doc]**
"Subconscious memory formation refers to the technique of prompting an LLM to reflect on a conversation after it occurs (or after it has been inactive for some period)". Hot-path formation "adds perceptible latency"; background formation has "none" latency, "delayed" update speed, and is claimed to "ensure higher recall of extracted information" (no measurement given).

**Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs (BEAM / LIGHT)**
https://arxiv.org/abs/2510.27246 (Oct 2025, rev. Feb 2026) **[doc]**
BEAM: "100 conversations ranging from 100K to 10M tokens each, accompanied by 2000 probing questions"; conversations are flat turn sequences with no session structure. LIGHT writes memory per turn: "After each user–assistant turn ... we apply Qwen2.5-32B-AWQ ... to extract key–value pairs and a summary" for the episodic store, and "for each dialogue pair ... reason over the current and preceding turn and extract salient content" into a scratchpad that "is iteratively merged with earlier versions" and, "once content exceeds a 30K-token threshold ... is compressed into a 15K-token summary". Working memory is the last z turns (z not stated in the text retrieved). Retrieval k=15 was best among {5,10,15,20}. Baselines are long-context and turn-level RAG only (no Mem0/Zep); no cost numbers. Note the scratchpad is exactly the pattern the current design uses (whole memory as prompt context, iteratively extended), but LIGHT rewrites it rather than appending, which would break prefix caching.

**Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects**
https://arxiv.org/abs/2512.12818 (Dec 2025) **[doc]**
Retain uses "coarse-grained chunking, extracting 2–5 comprehensive facts per conversation"; "each fact is intended to cover an entire exchange rather than a single utterance, be narrative and self-contained". Retain involves several LLM calls (fact extraction with temporal normalization, entity resolution, optional background "observations"). The paper reports retrieval token budgets but no retain-side token or cost numbers.

**Hindsight blog, "Hindsight Is #1 on BEAM"**
https://hindsight.vectorize.io/blog/2026/04/02/beam-sota (Apr 2026) **[vendor]**
Claims 73.4% / 71.1% / 73.9% / 64.1% at 100K / 500K / 1M / 10M, "next-best published result is 40.6%". No chunk size, no model, no ingestion cost or latency, no per-tier token counts are disclosed in the post; the benchmarks repo (https://github.com/vectorize-io/hindsight-benchmarks) only holds LongMemEval and LoCoMo tables, not BEAM. Treat the BEAM numbers as unaudited.

**SelfMem: Self-Optimizing Memory for AI Agents**
https://arxiv.org/abs/2607.03726 (Jul 2026) **[doc]**
No fixed chunking: the raw transcript is a read-only SQLite store and the agent "decide[s] which parts of the history are worth inspecting, rather than forcing a fixed chunking or summarization policy." Memory is editable (add, replace, merge, refine, archive, delete). Reported BEAM scores 0.504 / 0.487 / 0.454 at 100K / 500K / 1M. Table 1 memory-construction cost for a 1M-token conversation: SelfMem $2.004, Mem0 $18.830 (25,779 embedding requests), MemGPT $12.264. No ablation on chunk size.

**LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory**
https://arxiv.org/abs/2410.10813 (Oct 2024, ICLR 2025); dataset README https://github.com/xiaowu0162/LongMemEval **[doc]**
LongMemEval_S: 500 questions, "roughly consumes 115k tokens (~40 history sessions) for Llama 3"; `haystack_sessions` is a list of sessions, each a list of `{role, content}` turns. Section 5.2 compares value granularity (whole session vs round vs extracted facts): decomposing sessions into rounds "significantly enhances reading performance with GPT-4o as the reader", and "replacing sessions or rounds with extracted summaries or facts negatively impacts QA performance due to information loss", except that fact decomposition helps multi-session reasoning. This is the clearest published evidence that a purely lossy fact store underperforms verbatim rounds on this benchmark; the paper studies retrieval indexing, not write-once memory, so it is indirect evidence for this project.

**Fidelity Before Structure: Verbatim Chunks Beat Lossy Artifact Extraction in Long-Conversation LLM Memory**
https://arxiv.org/abs/2601.00821 (Dec 2025, rev. Jul 2026) **[doc]**
Same retrieve-rerank-reason pipeline, two stores: verbatim chunks (512 chars, 100 overlap) vs LLM-extracted typed artifacts. LongMemEval-S: 67.4% vs 45.4%; LoCoMo: 43.9% vs 28.0%. A control with session-level extraction (29.2% on LoCoMo) did not close the gap, i.e. changing the extraction unit from chunk to session did not help; the loss is attributed to "lossy distillation, not structure per se". Cost on LoCoMo10: extraction $0.14, generation $2.78 (artifacts) vs $3.84 (chunks); per 1,000 correct answers $12.50 (chunks) vs $14.90 (artifacts). Directly relevant risk for a fact-only memory.

**ES-Mem: Event Segmentation-Based Memory for Long-Term Dialogue Agents**
https://arxiv.org/abs/2601.07582 (Jan 2026) **[doc]**
Two-stage boundary detection: per-turn topic vectors, mutual information between adjacent turns, candidate boundaries at the bottom 35% quantile, then an LLM classifies each candidate with intent labels and a 0.75 confidence threshold. LongMemEval-S overall 72.40 (vs LightMem 69.81); LoCoMo F1 45.56. Ablation "w/o es" shows "significant degradation in Multi Hop and Temporal tasks". Per-query tokens 2,925 vs LightMem 815. This is the strongest evidence found that boundary choice matters, but it is measured through a retrieval pipeline, not a write-time whole-memory extractor.

**HingeMem: Boundary Guided Long-Term Memory with Query Adaptive Retrieval**
https://arxiv.org/abs/2604.06845 (Apr 2026) **[doc]**
Writes a segment whenever "person, time, location, and topic" change (event segmentation theory). Claims ~20% relative improvement over baselines and 68% lower QA token cost than HippoRAG2. No comparison against per-session writes.

**When F1 Fails: Granularity-Aware Evaluation for Dialogue Topic Segmentation**
https://arxiv.org/abs/2512.17083 (Dec 2025) **[doc]**
Argues topic segmentation is a granularity-selection problem, and notes LLM systems "increasingly rely on segmentation to manage conversation history beyond fixed context windows". Useful only as a caution that there is no ground-truth "right" boundary; segmentation quality is annotator-granularity dependent.

**A Simple Yet Strong Baseline for Long-Term Conversational Memory of LLM Agents**
https://arxiv.org/abs/2511.17208 (Nov 2025) **[doc]**
Decomposes each session into "self-contained statements with normalized entities and source turn attributions" (EDUs) in a heterogeneous graph; matches or beats baselines on LoCoMo and LongMemEval-S "with much shorter QA contexts". Unit = session, output = many atomic statements with turn provenance. No cost numbers in the abstract.

### What the evidence says about unit choice

- Every production system that writes per turn (Mem0, Zep) feeds the extractor only a short window (10 messages / 4 messages) plus retrieved memories, never the whole store. Systems that write per session or per conversation (Hindsight, LangMem, the EDU baseline) give the extractor the full unit. No paper found ablates "per turn vs per session vs fixed window" for a whole-memory-in-prompt extractor; the closest are ES-Mem (semantic boundaries beat fixed turns in retrieval) and the verbatim-chunks paper (session-level extraction did not rescue a lossy store).
- LongMemEval's own analysis says round-level verbatim values beat session-level values and beat fact-only values for reading. For a system that stores only extracted lines, the risk is the 20-point gap in 2601.00821, which is a representation problem, not a boundary problem. Keeping atomic lines verbatim ("key: value" with exact strings) is the mitigation the design already has.
- For BEAM (no sessions) the LIGHT authors chose a one-turn write unit with a 30K/15K scratchpad compression, and Hindsight chose session-sized coarse chunks; neither reports a sweep over window size.

---

## 2. OpenAI prompt caching mechanics (as of September 2026)

Primary page: **Prompt caching | OpenAI API**, https://developers.openai.com/api/docs/guides/prompt-caching **[doc]**. Azure mirror with more explicit wording: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/prompt-caching (updated 2026-08-11) **[doc]**. Model page: https://developers.openai.com/api/docs/models/gpt-5.6-luna **[doc]**. Pricing: https://developers.openai.com/api/docs/pricing **[doc]**.

The rules split by model generation. The project's extractor is gpt-5.6-luna, so the GPT-5.6 column is what matters.

| Rule | GPT-5.6 and later (incl. gpt-5.6-luna) | GPT-5.5 and earlier |
|---|---|---|
| Automatic? | Yes by default (`prompt_cache_options.mode: implicit`); can be turned off with `mode: explicit` and no breakpoints | Yes, always on, cannot be disabled |
| Minimum cacheable prefix | 1,024 tokens (hidden OpenAI system content does not count) | 1,024 on Azure wording; OpenAI page says "2,048 visible input tokens; some models may cache shorter prefixes" |
| Match granularity | "exact eligible boundary"; implicit breakpoint "at the end of the latest eligible user or tool message"; explicit breakpoints via `prompt_cache_breakpoint: {"mode":"explicit"}` on a content block | prefix hits counted in 128-token increments after the first 1,024 (2,048-token spacing quoted for GPT-5.5) |
| Breakpoint limits | up to 4 new cache writes per request (3 explicit + 1 implicit in implicit mode); earlier-turn breakpoints are read-only; reads consider the latest 50 breakpoints | n/a |
| Lifetime | `prompt_cache_options.ttl` = `"30m"` (only value, default): "remains eligible for reuse for 30 minutes after its most recent write or reuse"; may be kept longer | `prompt_cache_retention`: `in_memory` "around 5 to 10 minutes of inactivity, up to one hour"; `24h` "typically ... around 30 minutes and ... up to 24 hours" (gpt-5.5 defaults to 24h; `prompt_cache_retention` is deprecated on 5.6) |
| Cache write price | 1.25x the uncached input rate, on both implicit and explicit writes | free |
| Cache read price | 0.1x uncached input | model-dependent, mostly 0.1x for gpt-5.x, 0.25x for gpt-4.1 |
| Routing | hash of the initial tokens (after hidden content) + optional `prompt_cache_key`; "Cached states live on individual machines, where traffic above 15 requests per minute can lead to overflow routing"; keys "do not pin requests to a machine or guarantee a cache read hit" | same |
| Usage reporting | `usage.input_tokens_details.cached_tokens` and `usage.input_tokens_details.cache_write_tokens` (Responses); `prompt_tokens_details.cached_tokens` / `cache_write_tokens` (Chat Completions) | `cached_tokens` only |

Other documented points:
- What is cached: "the model's full rendered context including OpenAI-provided instructions, developer messages, tool definitions, and conversation history containing text, images, documents, and supported audio." Azure lists Structured Outputs explicitly: "Structured output schema is appended as a prefix to the system message." So a `text.format` JSON schema is part of the prefix, and changing it invalidates the cache.
- Request settings whose change resets the cacheable prefix: `model`, `tools`, `parallel_tool_calls`, `text.format`, `reasoning.effort`, `text.verbosity`, `context_management`. Keep reasoning effort constant across extractor calls.
- Reasoning models: caching applies to the rendered input; reasoning tokens are output. The reasoning guide notes that "GPT-5.6 models instead default to rendering available reasoning from earlier turns" into later samples in multi-step conversations (`reasoning.context: all_turns` vs `current_turn`). This only matters for multi-turn Responses chains; a single-shot extractor call per chunk is unaffected.
- Documented best practices: "Preserve conversation history by appending, not rewriting"; keep stable instructions first; place explicit breakpoints after stable content; group `prompt_cache_key` by user/session; monitor `cached_tokens` vs `cache_write_tokens`.
- Caches are not shared across organizations or regions.

Pricing (standard tier, per 1M tokens, from the pricing page, 2026-09):

| Model | Input | Cached input | Output |
|---|---|---|---|
| gpt-5.6-luna | $0.20 | $0.02 | $1.20 |
| gpt-5.6-terra | $2.00 | $0.20 | $12.00 |
| gpt-5.6-sol | $4.00 | $0.40 | $20.00 |
| gpt-5.5 | $5.00 | $0.50 | $30.00 |
| gpt-5.4 | $2.50 | $0.25 | $15.00 |
| gpt-5.4-mini | $0.75 | $0.075 | $4.50 |
| gpt-5.2 | $1.75 | $0.175 | $14.00 |
| gpt-5.1 / gpt-5 | $1.25 | $0.125 | $10.00 |
| gpt-5-mini | $0.25 | $0.025 | $2.00 |
| gpt-5-nano | $0.05 | $0.005 | $0.40 |
| gpt-4.1 | $2.00 | $0.50 | $8.00 |

gpt-5.6-luna specifics: 1,050,000-token context; reasoning model with `reasoning.effort` none/low/medium/high/xhigh/max; cache writes 1.25x ($0.25/M); "prompts with >272K input tokens are priced at 2x input and 1.5x output for the full request".

Implication for the design: with GPT-5.6, an append-only prefix costs 1.25x once when written and 0.1x on every later hit, so the break-even is one reuse. Because each extractor call adds new lines at the tail, each call re-writes only the delta (the new memory lines and the chunk) as long as the request lands on the same machine within 30 minutes and the prefix is unchanged. Put an explicit breakpoint after the fixed instructions and, if the memory block is large, a second one at the end of the memory block; leave the chunk after the last breakpoint. Do not change `reasoning.effort` or the structured-output schema between calls. Run chunks for one question sequentially (or at most a few in flight) to stay under the ~15 rpm per-prefix routing limit.

Consumer-facing summaries such as Effloow / TheRouter / AIHubMix (found in search) restate these rules; they are **[secondary]** and were not used as sources of fact.

### Anthropic, for contrast

**Prompt caching**, https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching (2026) **[doc]**
Explicit `cache_control` breakpoints (up to 4 per request) or a single top-level `cache_control` that "automatically applies the cache breakpoint to the last cacheable block and moves it forward as conversations grow". Minimum cacheable length is model dependent: 512 tokens (Fable 5.1, Mythos 5.1, Opus 5, Fable 5, Mythos 5), 1,024 (Sonnet 4.x/5, Opus 4/4.1/4.8), 2,048 (Opus 4.7, Mythos Preview), 4,096 (Opus 4.5/4.6, Haiku 4.5). TTL 5 minutes default, 1 hour optional. Writes 1.25x (5-min) or 2x (1-hour) base input; reads 0.1x (0.025x on Fable 5.1 / Mythos 5.1). Usage reports `cache_creation_input_tokens`, `cache_read_input_tokens`, `input_tokens`. Lookback for explicit breakpoints is 20 blocks. Net: OpenAI GPT-5.6 has converged on Anthropic's explicit-breakpoint, paid-write model, with a longer default TTL (30 min vs 5 min) and no 1-hour tier.

---

## 3. Cost arithmetic for write-time memory

Baseline sizes: LongMemEval_S is 500 questions, ~115k tokens and ~40 sessions per history (README); the local design notes say ~44 sessions of ~3k tokens each for the cleaned dataset, and full-history answering at ~110k input tokens per question.

**Beyond the Context Window: A Cost-Performance Analysis of Fact-Based Memory vs. Long-Context LLMs for Persistent Agents**
https://arxiv.org/abs/2603.04814 (Mar 2026) **[doc]**
Mem0-based fact memory vs long-context inference on LongMemEval, LoCoMo, PersonaMemv2 with GPT-5-mini and GPT-OSS-120B. Write cost: "$21.76 in total ($0.0435 per conversation)" to extract 500 LongMemEval conversations (~101,600 tokens each compressed to ~2,909 memory tokens per user) plus $0.037 of embeddings for 103,183 records. Read cost: "roughly $0.0013 per query" for memory vs "$0.0293 per request" for full context with GPT-5-mini. Break-even in interaction turns at which memory becomes cheaper: 13 (30k context), 10 (100k), 9 (200k), 9 (500k). Accuracy: long-context GPT-5-mini 82.40% vs memory 49.00% on LongMemEval, so the paper is also a warning that lossy fact extraction can give back the whole accuracy gain. This is the only paper found that reports an explicit per-conversation write cost on LongMemEval.

**Fidelity Before Structure (2601.00821)** — see Section 1. Reports LoCoMo10 extraction $0.14 vs generation $2.78–$3.84 per query set, i.e. write cost was roughly 4–5% of read cost in that pipeline, and artifacts reduced completion length 5.1x but lost accuracy.

**SelfMem (2607.03726)** — Table 1: memory construction for a 1M-token BEAM conversation costs SelfMem $2.004, Mem0 $18.830, MemGPT $12.264 (models and prices as configured by the authors). Scaled linearly, Mem0-style per-turn extraction on a 115k-token LongMemEval history would be on the order of $2, versus $0.0435 in 2603.04814; the two papers use different Mem0 configurations and models, so only the order-of-magnitude spread (extraction can cost 2–50x more than the raw token count suggests when it makes many small calls) is the takeaway.

**Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads**
https://arxiv.org/abs/2606.06448 (Jun 2026) **[doc]**
Phase-aware profiling of ten systems: "Construction energy dominates the agent lifecycle: for LLM-mediated agent memory systems, construction energy exceeds total query-phase energy across 300 queries." On a 1.8M-token LongMemEval_S slice with 300 queries, end-to-end energy ranges from 582 kJ (BM25) to 15,429 kJ (Letta), a 26.7x spread. "Construction is dominated by embedding and LLM prefill ... the LLM construction path reads a window or chunk and emits a compact structured output"; median decode share of construction tokens is 4.6%. Per-session construction wall time ~10 s for Mem0/MIRIX with tails over 100 s. Consequence for this design: extraction cost is prefill-dominated, which is exactly the part prompt caching discounts.

**Mem0 paper (2504.19413)** — LoCoMo, answer-time tokens per conversation: full context 26,031, Mem0 ~7k, Mem0g ~14k, Zep >600k (the Zep figure reflects Mem0's harness and is disputed by Zep). p95 total latency 1.44 s vs 17.1 s. No write-side cost.

**Zep paper (2501.13956)** — LongMemEval answer-time: 115k tokens (full context) vs 1.6k (Zep), 31.3 s vs 3.20 s with gpt-4o-mini. No write-side cost.

**Mem0 docs, Memory Evaluation** https://docs.mem0.ai/core-concepts/memory-evaluation (2026) **[vendor doc]** — mean retrieval tokens: 6,956 (LoCoMo), 6,787 (LongMemEval), 6,719 (BEAM 1M); "Conversation enters the pipeline asynchronously (after the agent responds)". No ingest-stage numbers. "All benchmarks run on the same production-representative model stack", unnamed.

**Mem0, "LoCoMo, LongMemEval & BEAM Leaderboard ... 2026"** https://mem0.ai/blog/ai-memory-benchmarks-in-2026 **[vendor]** — restates 6.7–7.0k retrieval tokens, "roughly 3-4x lower token cost" than 25k+ full-context queries, P50 latency at or under 1.1 s. No ingest numbers for any system.

**Hindsight** — paper, benchmarks repo, and BEAM post publish no retain-side token or cost numbers. A Zep comparison page (https://www.getzep.com/vectorize-hindsight-alternative/, **[vendor]**) states Hindsight's 91.4% LongMemEval score is measured at an 8,192-token retrieval budget vs ~4,408 tokens for Zep's 90.2%.

**Adaption Labs, "Better Agent Memory Starts Before Retrieval"**
https://adaptionlabs.ai/blog/agent-memory-write-time (Aug 13 2026) **[secondary: domain blocked by network policy during this survey; WebFetch reset, curl returned an empty body, Wayback blocked]**
From the search snippet: "Adaptive memory offers a trade-off where you spend a small amount once to shape what was learned, then reuse it without repeatedly processing the full history", and the thesis that "the bottleneck is what gets written into memory in the first place". From this repository's own notes (docs/memory-design.md): LongMemEval full history 60.6%, their system 90.6%, Mem0 OSS 71.6%; the post withholds extraction prompts, schemas, and model names. No per-session extraction token or dollar figures were recoverable; treat any cost claim from the post as unverified until the page can be read directly.

### Worked arithmetic for this design (gpt-5.6-luna extractor, LongMemEval_S)

Assumptions: 44 sessions x 3k tokens; fixed instructions ~1.5k tokens; memory grows linearly to ~4k tokens; extractor output ~150 tokens per session plus medium-effort reasoning (~500 tokens); prices from the table above.

- Uncached extractor input: sum over sessions of (1.5k + memory_so_far + 3k) ~ 44 x 4.5k + 44 x 2k avg = ~286k tokens = $0.057. Output 44 x 650 = ~29k tokens = $0.034. Total ~ $0.09 per question without caching.
- With caching: the ~4.5k stable prefix per call (instructions + memory so far) is written once at 1.25x and read at 0.1x on the next call; only the ~3k chunk and the new lines are uncached. Roughly 44 x 3k = 132k uncached ($0.026) + ~100k cached reads ($0.002) + writes ($0.005) + output ($0.034) ~ $0.07. Caching saves ~20–25% here because the chunk, not the memory, dominates input at this memory size; the saving grows as the memory grows relative to the chunk (e.g. BEAM at 1M tokens with a 50k-token memory).
- Answer-time saving: ~110k input tokens ($0.022 on luna, $0.55 on gpt-5.5) replaced by ~5k tokens per question. On luna the extraction cost (~$0.07) exceeds the answer-time saving (~$0.02) for a single question; it pays off only if the same memory serves several questions or the answer model is expensive. This matches 2603.04814's finding that break-even is around 10 reads per history at 100k context.
- The minimum-prefix rule (1,024 tokens) is met from the first call only if instructions alone exceed 1,024 tokens; otherwise the first few sessions get no cache benefit.

Caveats: nobody in the literature reports a whole-memory-in-prompt append-only extractor, so the numbers above are derived, not cited. The two published per-conversation write costs on LongMemEval (2603.04814: $0.0435 with Mem0/GPT-5-mini era pricing; SelfMem Table 1: $18.83 for Mem0 on a 1M-token BEAM conversation) differ by more than an order of magnitude after scaling, so the project's own run records should be the source of truth.
