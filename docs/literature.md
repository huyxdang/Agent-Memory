# Literature: write-time memory, supersession, chunking, and caching

Curated on 2026-09-08 from two research passes. The raw survey notes, with
per-source detail and skepticism flags, are in `docs/research/`. This file is
the short version: what the field has demonstrated, what it only claims, and
what we change in our design because of it.

The Adaption Labs article itself was read directly earlier in the project.
Both research passes found the site unreachable, so their notes on the article
come from search snippets and `docs/memory-design.md`.

## Bottom line for our design

1. **Append-only wins on knowledge updates, empirically.** On LongMemEval-S,
   every system that keeps the old fact scores 92 to 96 on the knowledge-update
   category: ADD-only Mem0 (93.6), Hindsight (94.9), Honcho (94.9), Eywa
   (96.2), Memanto (93.6). The two that let an LLM adjudicate updates in place
   at write time score 74 to 83: Zep (83.3 with gpt-4o, 74.4 with mini) and the
   old Mem0 (79.5). Mem0 abandoned in-place UPDATE and DELETE in April 2026,
   saying the reconciliation step "was where context got destroyed".
2. **But plain append leaves the old value unmarked.** Mem0's own caveat after
   going ADD-only: knowledge update is now their weakest category because "a
   semantically similar prior fact can surface alongside a newer one". Our
   arrow line, `25:50 <- 27:12` appended as a new line, is exactly the missing
   marker. Nobody in
   the survey renders supersession to the reader; MemStrata's `superseded_by`
   and Zep's `t_invalid` both hide the old value instead.
3. **Rewriting a compact state block loses updates even with frontier
   models.** The Supersede paper measures gpt-5.4 at 92% with full context
   versus 77% with a self-maintained notes field, and 24 times more memory
   budget does not recover it. LIGHT's summarized scratchpad scores near zero
   on BEAM's contradiction-resolution category. This is the argument for
   writing a chain extension as a new line rather than editing the old one.
4. **Fact-only memory is lossy.** LongMemEval's authors found facts-as-values
   hurt QA. TriMem quantifies 14.5% information loss from fact extraction.
   "Fidelity Before Structure" reports 45.4% for extracted artifacts versus
   67.4% for verbatim chunks on LongMemEval-S, and session-level extraction
   did not close the gap. Three 2026 papers (TriMem, AtomMem, Amory)
   independently arrive at atomic plus narrative, so the two-form split is
   sound but not novel. What is distinctive in our design is that the
   narrative layer is append-only and the current-state view is derived.
5. **Embedding similarity cannot find contradictions.** MemStrata shows cosine
   similarity separates contradictions from paraphrases at 0.59 AUROC, so
   "retrieve similar memories and let the LLM decide" is handicapped at the
   retrieval step. Supersession has to be decided by something that sees the
   old value explicitly. Our extractor sees the whole memory, which is a
   structural advantage. The hard skill becomes emitting the same key for the
   same fact across sessions; MemStrata's extraction reliability drops to
   about 44% on messy natural-language contradictions.
6. **Supersession is only as good as the first extraction.** HaluMem finds
   every tested system below 26% update accuracy with over 50% omission,
   mostly because the pre-update fact was never extracted. MemTrace documents
   "timestamp reassignment" bugs caused by in-place updates, which append-only
   cannot produce.
7. **Write-time versus retrieval-time is claimed, not isolated.** Every top
   system also has a heavy retrieval layer, and Memanto reaches 93.6 on
   knowledge update with no write-time LLM at all. No paper ablates write-time
   supersession marking against plain timestamped append on the same stack.
   That ablation, arrow chains versus flat append with the same extractor and
   answerer, is the experiment this reproduction can actually contribute.

## Systems at a glance

| System | Write unit | Changed fact | LongMemEval-S knowledge update | Relation to our design |
|---|---|---|---|---|
| Mem0 (paper, 2025) | message pair, last 10 msgs | LLM picks ADD/UPDATE/DELETE in place | 79.5 | disagrees; later reversed |
| Mem0 (ADD-only, 2026) | per add call, async | append, no marker | 93.6 | agrees, lacks our marker |
| Zep / Graphiti | one message, last 4 for context | LLM invalidates contradicted edge, sets `t_invalid`, keeps history | 83.3 / 74.4 | agrees on keep-history, disagrees on mechanism |
| Letta / MemGPT | context pressure, not boundaries | block overwrite, "last write wins" | not reported | disagrees |
| A-Mem | per interaction | metadata evolves, content immutable, no supersession | not reported | partial |
| Generative Agents | per event, append-only | none; recency in retrieval | n/a | ancestor of narrative lines |
| LangMem | whole conversation after inactivity debounce | patch or delete document | not reported | disagrees |
| Hindsight | per session, 2 to 5 narrative facts | keep all; confidence at belief layer | 94.9 | agrees, no explicit marker |
| LIGHT (BEAM paper) | per turn; scratchpad rewritten, 30K to 15K compression | implicit, lossy | BEAM CR near 0 | cautionary tale |
| Eywa | per turn; deterministic signal extraction plus validated LLM facts | superseded marked at write, `valid_from/until` | 96.2 (BEAM KU 70.0) | closest relative |
| MemIR | typed atoms with span provenance | read-time bundle selection | BEAM-100K KU 58.4 | agrees on typing |
| EMBER | learned retention policy, verbatim capsules | learned overwrite | n/a | agrees on verbatim, disagrees on overwrite |
| MemStrata | (S,R,O) triples | same key, new value supersedes; bi-temporal ledger | n/a | agrees exactly on keyed supersession |
| MemReader | trained add/search/buffer/ignore | add after searching existing memory | 91.0 | agrees; borrow "defer incomplete" |
| Memanto | no LLM at write | conflict flagged to agent | 93.6 | counterexample |

## Extraction units

No published system uses our exact shape: whole memory in the prompt,
append-only, one call per session. Production per-turn writers (Mem0, Zep)
give the extractor a short window plus a retrieved slice, never the full
store. Per-session and per-conversation writers (Hindsight, LangMem, the EDU
baseline in 2511.17208) give the whole unit. No paper ablates turn versus
session versus fixed window for a whole-memory extractor.

The indirect evidence says the risk is representation, not boundary
placement. ES-Mem shows LLM-detected event boundaries beat fixed turns inside
a retrieval pipeline, with multi-hop and temporal questions hurt most when
segmentation is removed. "Are We Ready For An Agent-Native Memory System?"
finds heuristic topic segmentation beating LLM segmentation, and lighter
extraction retaining more detail. Using the dataset's own sessions avoids that
whole question on LongMemEval and LoCoMo.

For BEAM, which has no sessions, LIGHT writes per turn and Hindsight uses
session-sized coarse chunks. Neither reports a sweep over window size, and
neither publishes chunk size or cost for BEAM. Letta's compaction docs are the
only vendor source that ties chunk policy to prompt caching: their
self-compact mode keeps the prefix identical "to improve cache hit rates".

## Prompt caching rules that constrain the extractor

From OpenAI's prompt-caching guide and the gpt-5.6-luna model page, as of
September 2026, for the GPT-5.6 family:

- Caching is automatic. Minimum cacheable prefix is 1,024 tokens. Matching is
  at exact eligible boundaries, with an implicit breakpoint at the end of the
  latest user message and optional explicit breakpoints.
- Cache lifetime is 30 minutes after the last write or reuse. Cache writes
  bill at 1.25 times the input rate, reads at 0.1 times.
- Changing any of `model`, `tools`, `text.format`, `reasoning.effort`, or
  `text.verbosity` resets the cacheable prefix. A structured-output schema is
  rendered into the prefix. So the extractor's reasoning effort and output
  schema must be identical across calls.
- Routing is by prefix hash plus an optional `prompt_cache_key`. Above about
  15 requests per minute on one prefix, traffic can overflow to other
  machines. Run one question's chunks sequentially.
- Usage reports `cached_tokens` and `cache_write_tokens` under
  `prompt_tokens_details` on Chat Completions.
- gpt-5.6-luna prices per million tokens: input 0.20, cached input 0.02,
  cache write 0.25, output 1.20. Prompts over 272K input tokens bill at
  double input and 1.5 times output.

OpenAI's own best-practice line is the design rule: "Preserve conversation
history by appending, not rewriting."

## Cost arithmetic

Only one paper reports a per-conversation write cost on LongMemEval:
2603.04814 measures $0.0435 per roughly 101k-token conversation for Mem0-style
extraction with GPT-5-mini, $0.0013 per memory query against $0.0293 per
full-context query, and break-even at about 10 reads per history. It also
reports memory accuracy of 49.0% against 82.4% for full context, so it doubles
as a warning that lossy extraction can give back the whole gain. Construction
is prefill-dominated (2606.06448 puts the median decode share at 4.6%), which
is exactly what caching discounts.

For our design on gpt-5.6-luna, derived not cited: about 44 sessions of
roughly 3k tokens against a memory that grows to a few thousand tokens is on
the order of $0.09 per question without caching and $0.07 with it, since the
chunk rather than the memory dominates input at this memory size. Answer-time
saving is about $0.02 per question on the same model. On five questions the
economics are a rounding error; accuracy is what we are measuring. The
caching benefit grows with memory size relative to chunk size, which is the
BEAM regime.

## Adjustments adopted into the design

- **Event date as well as session date.** Zep, Hindsight, and AtomMem all
  separate when a fact became true from when it was mentioned. An atomic line
  keeps the session date and, when the text gives one, the event date inside
  the value.
- **Key normalization is the core extractor skill.** The prompt shows the
  existing keys and instructs the extractor to reuse a key when the fact is
  the same, and to treat "is this a change to an existing key?" as an explicit
  step, per the Supersede paper's conclusion that supersession must be
  optimized for rather than assumed.
- **A deterministic check on atomic lines**, borrowed from Eywa: the value, or
  its hard anchor such as a number, date, or name, must appear in the session
  text. Lines that fail are recorded as extraction failures, not silently
  dropped.
- **Unresolved references go to narrative, not atomic**, borrowed from
  MemReader's defer action. A pronoun without a referent does not become a
  `key: value` line.
- **Provenance on every line.** Each line carries its session number, so a
  narrative restatement can never be mistaken for the atomic line that
  grounds it, the failure MemIR calls provenance-role collapse.
- **Smoke-test metrics**, borrowed from HaluMem and EMBER: did the evidence
  turns produce atomic lines (retain recall), did the later value supersede
  the earlier one under the same key (update accuracy), and did the final
  chain survive into the answer prompt (read recall). LongMemEval's evidence
  labels, already used by the Inspect bridge, are the ground truth.
- **The ablation we can contribute.** Same extractor, same answerer, two
  memory formats: arrow chains versus flat dated append with no marker. Run on the five
  questions once the smoke test passes.

## Sources

Primary papers and docs, by section of the raw surveys:

- Adaption Labs, Better Agent Memory Starts Before Retrieval (2026): https://adaptionlabs.ai/blog/agent-memory-write-time
- Mem0 paper (2025): https://arxiv.org/abs/2504.19413 ; token-efficient ADD-only algorithm (2026): https://mem0.ai/blog/mem0-the-token-efficient-memory-algorithm ; benchmark caveats: https://mem0.ai/blog/ai-memory-benchmarks-in-2026
- Zep (2025): https://arxiv.org/abs/2501.13956
- MemGPT (2023): https://arxiv.org/abs/2310.08560 ; Letta compaction docs: https://docs.letta.com/guides/core-concepts/messages/compaction/ ; Sleep-time compute: https://arxiv.org/abs/2504.13171
- A-Mem (2025): https://arxiv.org/abs/2502.12110
- Generative Agents (2023): https://arxiv.org/abs/2304.03442
- LangMem docs: https://langchain-ai.github.io/langmem/
- Hindsight (2025): https://arxiv.org/abs/2512.12818 ; BEAM post: https://hindsight.vectorize.io/blog/2026/04/02/beam-sota
- BEAM and LIGHT (2025): https://arxiv.org/abs/2510.27246
- Eywa (2026): https://arxiv.org/abs/2605.30771
- MemIR (2026): https://arxiv.org/abs/2605.25869
- EMBER (2026): https://arxiv.org/abs/2606.05894
- LongMemEval (2024): https://arxiv.org/abs/2410.10813
- Honcho benchmarks: https://plasticlabs.ai/blog/research/Benchmarking-Honcho
- MemStrata (2026): https://arxiv.org/html/2606.26511v1
- Supersede (2026): https://arxiv.org/abs/2606.27472
- MemReader (2026): https://arxiv.org/abs/2604.07877
- Memanto (2026): https://arxiv.org/html/2604.22085v1
- TriMem (2026): https://arxiv.org/abs/2605.19952 ; AtomMem: https://arxiv.org/abs/2606.19847 ; Amory: https://arxiv.org/abs/2601.06282
- Agent-native memory ablations (2026): https://arxiv.org/html/2606.24775
- HaluMem (2025): https://arxiv.org/abs/2511.03506 ; MemTrace (2026): https://arxiv.org/html/2605.28732 ; TrustMem (2026): https://arxiv.org/abs/2606.25161
- Fidelity Before Structure (2025): https://arxiv.org/abs/2601.00821
- ES-Mem (2026): https://arxiv.org/abs/2601.07582 ; HingeMem (2026): https://arxiv.org/abs/2604.06845
- Simple strong baseline, EDU graph (2025): https://arxiv.org/abs/2511.17208
- SelfMem (2026): https://arxiv.org/abs/2607.03726
- Cost-performance analysis of fact memory vs long context (2026): https://arxiv.org/abs/2603.04814
- Agent memory workload characterization (2026): https://arxiv.org/abs/2606.06448
- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching ; gpt-5.6-luna: https://developers.openai.com/api/docs/models/gpt-5.6-luna ; pricing: https://developers.openai.com/api/docs/pricing
- Anthropic prompt caching, for contrast: https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching
