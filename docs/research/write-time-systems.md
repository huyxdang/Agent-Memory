# Write-time extraction and fact updates in agent memory systems — literature survey

Compiled 2026-09-08 for the Adaption-memory reproduction. Scope: what each system does at
**write time**, how it handles a **changed fact**, and what that implies for our design
(per-session LLM extractor; atomic `key: value` lines + narrative lines; append-only with
`(was X)` supersession; read-time chain view `Rex <- Max`; evaluated on LongMemEval,
LoCoMo, BEAM).

Access notes: adaptionlabs.ai returned 503/connection-reset on every path (direct, curl,
reader proxy, browser); the article's claims below come from search-engine snippets and the
repo's `docs/memory-design.md`. GitHub raw/blob fetches also failed intermittently, so the
Mem0 and Graphiti prompt texts are described from the papers, not quoted from source.

Legend for the "Stance" line: **agrees** / **disagrees** / **borrow** relative to our design.

---

## 0. The target: Adaption Labs, "Better Agent Memory Starts Before Retrieval" (Aug 2026)

- URL: https://adaptionlabs.ai/blog/agent-memory-write-time (not fetchable today)
- Write time: memory is written in two forms. "Narrative memories preserve causal context
  (the reasoning behind decisions or changes), while atomic memories preserve exact facts
  that need to survive verbatim." Motivating example: an account switching from monthly to
  annual billing after a new VP consolidated vendors (narrative) vs a renewal date or
  contract value (atomic). "Forcing both into a single representation always cost
  something: rich summaries lost precise figures, and bare facts lost the context."
- Changed facts: append with supersession rather than overwrite (per the repo design doc,
  which is our spec of record).
- Claimed results (from `docs/memory-design.md`): LongMemEval full history 60.6%, their
  system 90.6%, Mem0 OSS 71.6%. Headline claim: "The largest gains came not from
  retrieving more, but from writing better representations of what mattered."
- Skeptical note: the post withholds prompts, schemas, model names, and per-category
  numbers. The 90.6 vs 60.6 comparison is against a *full-context* baseline, and every
  system below that does any extraction also beats full context by 20-40 points on
  LongMemEval-S (Zep, Hindsight, Mem0, Honcho, Eywa all sit at 88-94). So the number is
  consistent with the field but does not by itself isolate "write-time" as the cause.

---

## 1. Mem0 — "Building Production-Ready AI Agents with Scalable Long-Term Memory" (2025)

- arXiv 2504.19413. https://arxiv.org/abs/2504.19413 ; code https://github.com/mem0ai/mem0
- **Write time (paper version):** two phases per message pair. *Extraction* sees a rolling
  conversation summary S plus the last m messages and emits candidate facts. *Update*
  retrieves the top-s similar existing memories for each candidate and has the LLM pick
  one of ADD / UPDATE / DELETE / NOOP ("rather than using a separate classifier, we leverage
  the LLM's reasoning capabilities to directly select the appropriate operation").
- **Changed fact:** UPDATE rewrites the stored memory text in place (a history table keeps
  `old_memory` / `new_memory` rows for audit: GET /v1/memories/{id}/history); DELETE removes
  memories "contradicted by new information". Mem0-graph adds an edge-invalidation step.
- **Results (LoCoMo, LLM-judge, gpt-4o-mini):** Mem0 66.88 overall (single-hop 67.13,
  multi-hop 51.15, open-domain 72.93, temporal 55.51); Mem0-graph 68.44; Zep 41.35 multi-hop
  / 49.31 temporal; LangMem 23.43 temporal; full-context 72.90 overall. No ablation on the
  update mechanism.
- **What happened next (important):** Mem0's April-2026 "token-efficient algorithm" post
  (https://mem0.ai/blog/mem0-the-token-efficient-memory-algorithm) *dropped UPDATE/DELETE
  at write time* and moved to "single-pass ADD-only extraction": "The old algorithm
  extracted memories in two LLM passes... That reconciliation step was slow, and it was
  where context got destroyed." "ADD-only extraction preserves the full history of state
  changes, so the system can reason about how things evolved, not just where they landed."
  LongMemEval per-category, old -> new: SS-user 94.3 -> 98.6; SS-assistant 46.4 -> 98.2;
  SS-preference 76.7 -> 96.7; knowledge-update 79.5 -> 93.6; temporal 51.1 -> 97.0;
  multi-session 70.7 -> 88.0; overall 94.4 at ~6,787 tokens/query. Their own caveat
  (https://mem0.ai/blog/ai-memory-benchmarks-in-2026): "Knowledge update, at 93.6, is the
  category most affected by the additive, ADD-only architecture: older facts are preserved
  rather than overwritten, so a semantically similar prior fact can surface alongside a
  newer one."
- **Independent evidence on the paper-era UPDATE path:** HaluMem (sec. 20) measured Mem0
  update accuracy < 26% with > 50% omission; MemTrace found "timestamp reassignment during
  updates, where content remains unchanged but its time is modified"; GitHub issue #3945
  reports updates failing because "the system cannot find the old memory".
- **Stance:** strongly **agrees** with append-only. The most-used OSS memory system tried
  LLM-adjudicated in-place UPDATE/DELETE and retreated to ADD-only, and reports that
  knowledge-update is now its weakest category *because nothing marks the old value as
  old*. Our `(was X)` line plus chain view is exactly the piece Mem0 is missing.
  **Borrow:** keep a per-key history (Mem0's history table) — we get this for free from
  append-only. **Disagrees** on granularity: Mem0 extracts per message pair, we extract per
  session; HaluMem/MemTrace show fine-grained extraction drops details either way.

---

## 2. Zep / Graphiti — "Zep: A Temporal Knowledge Graph Architecture for Agent Memory" (2025)

- arXiv 2501.13956. https://arxiv.org/abs/2501.13956 ; code https://github.com/getzep/graphiti
- **Write time:** episodes (messages + 4 prior for context) -> LLM entity extraction with a
  reflection pass -> entity dedup by embedding + full-text -> LLM fact (edge) extraction ->
  edge dedup per entity pair -> community detection (label propagation) with summaries.
  Relative dates ("two weeks ago") are resolved against the episode's reference timestamp
  into ISO-8601 at write time.
- **Changed fact — bi-temporal model:** every edge carries `t_valid`/`t_invalid` (world
  time) and `t'_created`/`t'_expired` (transaction time). At ingest, "the LLM compares it
  against semantically related existing edges to identify contradictions... When the system
  identifies temporally overlapping contradictions, it invalidates the affected edges by
  setting their t_invalid to the t_valid of the invalidating edge." Old edges are kept, not
  deleted: "automatic fact invalidation with temporal history preserved."
- **Results (LongMemEval-S, per type, full-context vs Zep):** gpt-4o: SS-user 81.4 -> 92.9;
  SS-assistant 94.6 -> 80.4 (-17.7%); SS-preference 20.0 -> 56.7; multi-session 44.3 -> 57.9;
  **knowledge-update 78.2 -> 83.3 (+6.5%)**; temporal 45.1 -> 62.4. gpt-4o-mini:
  **knowledge-update 76.9 -> 74.4 (-3.4%)**; SS-assistant 81.8 -> 75.0. Zep is honest that
  assistant-side and KU are its weak spots. MemReader (2026) re-ran Zep on LongMemEval and
  got KU 74.4, temporal 54.1.
- **Skeptical note:** the LLM invalidation step is the fragile part — it relies on
  similarity retrieval to even surface the contradicted edge, then an LLM judgment. The KU
  numbers (83/74) are *lower* than ADD-only Mem0's 93.6 and Hindsight's 92-95, i.e. the
  most elaborate write-time invalidation in the field does not win the category it was
  built for.
- **Stance:** **agrees** on "never delete, mark superseded, keep history"; **disagrees** on
  mechanism (LLM edge-vs-edge contradiction search vs our extractor seeing the whole memory
  and emitting `(was X)`). **Borrow:** (a) resolve relative dates to absolute at write time
  using the session timestamp (we already do); (b) the distinction between *when the fact
  became true* and *when we learned it* — our lines carry the session date (learned-at);
  for LongMemEval temporal questions the extractor should also write the event date into
  the value when the text gives one.

---

## 3. Letta / MemGPT — core memory edits; sleep-time compute

- MemGPT paper arXiv 2310.08560; Letta docs https://docs.letta.com/guides/agents/memory-blocks ;
  "Sleep-time Compute" arXiv 2504.13171 https://arxiv.org/abs/2504.13171
- **Write time:** the agent itself edits labeled in-context "memory blocks" via tool calls
  (`core_memory_append`, `core_memory_replace`, later `memory_replace`, `memory_insert`,
  `memory_rethink`), plus `archival_memory_insert` for an external vector store. Blocks have
  character limits (default ~2,000-5,000).
- **Changed fact:** in-place overwrite. Docs: "Setting `value` completely replaces the
  entire block content — it is not an append operation"; "last write wins and overwrites
  all earlier changes." `memory_rethink` rewrites the whole block. The sleep-time agent
  "replaces the current context" and is instructed to "Replace outdated information with
  the most likely truths, avoiding redundancy with original memories." No history is kept
  inside the block; the raw transcript remains in recall storage.
- **Evidence:** the sleep-time paper shows ~5x less test-time compute and +13-18% on
  stateful GSM/AIME variants; it does not evaluate knowledge updates. On LoCoMo (A-Mem
  paper, gpt-4o-mini) MemGPT F1: single-hop 41.0, multi-hop 26.7, temporal 25.5.
- **Stance:** the canonical **disagreement**. Letta is the overwrite/"rethink" model; the
  Supersede paper (sec. 16) shows exactly this bounded, self-maintained notes design losing
  15 points to full context on knowledge updates even with gpt-5.4. **Borrow:** the idea of
  a *separately* maintained compact block for "current state" is what our chain view
  provides at read time without giving up the append-only store.

---

## 4. A-Mem — "Agentic Memory for LLM Agents" (NeurIPS 2025)

- arXiv 2502.12110. https://arxiv.org/abs/2502.12110
- **Write time:** each interaction becomes a Zettelkasten-style note with content, timestamp,
  LLM-generated keywords, tags, contextual description, embedding, and links. Top-k similar
  notes are retrieved and an LLM decides which links to create.
- **Changed fact — "memory evolution":** for each neighbor note the LLM decides "whether to
  update its context, keywords, and tags"; the evolved note "replaces the original memory
  m_j in the memory set." The verbatim *content* is not rewritten; only the metadata /
  contextual description is. The paper has **no** discussion of contradictions or fact
  updates.
- **Results (LoCoMo, gpt-4o-mini, F1):** single-hop 44.65, multi-hop 27.02, temporal 45.85,
  open-domain 12.14, adversarial 50.03 (LoCoMo baseline 69.23 on adversarial). Mem0's
  re-run of A-Mem gave much lower judge scores (single-hop 39.8, multi-hop 18.9).
- **Stance:** **agrees** that verbatim content should be immutable and only derived
  context evolves; that is close to our "narratives never supersede, atomics chain".
  **Disagrees** by having no supersession at all. Nothing concrete to borrow beyond the
  reminder that LLM-driven metadata rewriting is expensive (one LLM call per neighbor per
  new note) and unproven on KU.

---

## 5. Generative Agents (Park et al., 2023) — memory stream + reflection

- arXiv 2304.03442. https://arxiv.org/abs/2304.03442
- **Write time:** every perceived event is appended to a memory stream as a natural-language
  observation with a creation timestamp and last-access timestamp. Nothing is ever edited or
  deleted. Reflection fires "when the sum of the importance scores for the latest events
  perceived by the agents exceeds a threshold (150)": generate the 3 most salient questions
  from the last 100 memories, retrieve, and write insight statements with citations
  ("Klaus Mueller is dedicated to his research on gentrification (because of 1, 2, 8, 15)").
  Reflections are themselves memories and can cite reflections.
- **Changed fact:** not handled; the stream is append-only and retrieval scoring (recency
  decay 0.995/hour, LLM importance 1-10, embedding relevance, equal weights) is expected to
  favor the newer observation.
- **Stance:** the ancestor of our narrative line and of append-only. **Borrow:** the
  citation convention — a narrative line that says *which atomic lines it rests on*, or an
  atomic supersession line that names the old value, is the same "because of 1, 5, 3" idea.
  It is also the origin of "reflection = periodic higher-level rewrite", which we
  deliberately do *not* do (we never regenerate old lines).

---

## 6. LangMem (LangChain, 2025)

- Docs https://langchain-ai.github.io/langmem/ ; conceptual guide
  https://langchain-ai.github.io/langmem/concepts/conceptual_guide/ ; extraction guide
  https://langchain-ai.github.io/langmem/guides/extract_semantic_memories/
- **Write time:** semantic memory as either a *collection* (many small documents) or a
  *profile* (one document representing current state, patched in place). "Conscious"
  (hot-path) vs "subconscious" (background, after the conversation) formation. The manager
  prompts an LLM with parallel tool calls to insert new memories, patch existing ones (same
  id), or emit `RemoveDoc(json_doc_id=...)`; flags `enable_inserts`, `enable_updates`,
  `enable_deletes`.
- **Changed fact:** worked example: "Bob now leads the ML team" -> RemoveDoc for "Alice
  manages the ML team", patch Bob's memory in place. Old value is gone from the collection.
- **Evidence:** none from LangChain. Mem0's LoCoMo re-run: LangMem temporal 23.43, multi-hop
  47.92, single-hop 62.23. HaluMem did not test it.
- **Stance:** **disagrees** (delete/patch). **Borrow:** the *profile vs collection*
  split is a useful frame: our chain view *is* the profile, derived from the collection,
  rather than a second LLM-maintained object that can drift.

---

## 7. Hindsight (Vectorize, Dec 2025 paper; BEAM SOTA Apr 2026)

- Paper arXiv 2512.12818 https://arxiv.org/abs/2512.12818 ; code
  https://github.com/vectorize-io/hindsight ; BEAM post
  https://hindsight.vectorize.io/blog/2026/04/02/beam-sota
- **Write time ("retain"):** LLM converts input into "narrative facts with temporal
  ranges" — each fact has narrative text, embedding, occurrence interval (t_s, t_e), mention
  timestamp, fact type, confidence. Deliberately **coarse-grained: "extracting 2-5
  comprehensive facts per conversation"** rather than sentence-level atoms. Four networks:
  World (objective), Experience (first-person), Opinion (text, confidence in [0,1],
  timestamp), Observation (entity summaries synthesized from many facts, background job).
- **Changed fact:** "Old facts are retained; the system doesn't delete them." Conflict is
  resolved at the *belief* layer: opinions get reinforce (+a), weaken (-a), contradict (-2a)
  confidence updates; observations are "refined rather than overwritten when new evidence
  arrives, so new information strengthens, weakens or extends an existing belief," each
  keeping exact-quote evidence and proof counts. A background merge for user-provided
  biographical info "resolves direct conflicts in favor of the new information when
  appropriate."
- **Results:** LongMemEval (Gemini-3 / OSS-120B / OSS-20B): **knowledge-update 94.9 / 92.3 /
  84.6**; SS-preference 80.0 / 86.7 / 66.7; temporal 91.0 / 85.7 / 79.7; multi-session
  87.2 / 81.2 / 79.7; overall 91.4 / 89.0 / 83.6 vs full-context gpt-4o 60.2. LoCoMo overall
  89.61 (Gemini-3). BEAM overall (Hindsight vs Honcho vs LIGHT vs RAG): 10M 64.1 / 40.6 /
  26.6 / 24.9; 1M 73.9 / 63.1 / 33.6 / 30.7; 100K 73.4 / 63.0 / 35.8 / 32.3. No BEAM
  per-category breakdown published; no ablations in the paper.
- **Skeptical note:** the +44.6-point gain is vs a weak full-context OSS-20B baseline; the
  paper credits retrieval (TEMPR) for most of it. The "narrative facts" are paraphrases, not
  verbatim — Hindsight's own docs admit they layered a verbatim-quote evidence field into
  observations later.
- **Stance:** **agrees** on never deleting and on a narrative form with temporal ranges;
  its 2-5-facts-per-conversation granularity is closest to our per-session narrative line.
  **Disagrees**: no explicit supersession pointer; the "current value" is reconstructed at
  recall/reflect time via time-aware retrieval and confidence, which is an LLM-heavy read
  path. **Borrow:** store *both* mention time and occurrence interval on a line when the
  text supplies them (our dated lines carry mention time only).

---

## 8. BEAM benchmark and LIGHT (Oct 2025)

- arXiv 2510.27246 https://arxiv.org/abs/2510.27246
- **Benchmark:** 100 conversations, 2,000 validated questions, lengths 100K-10M tokens; ten
  abilities: abstention, contradiction resolution ("detect and reconcile inconsistent
  statements"), event ordering, information extraction, instruction following, **knowledge
  update ("revising stored facts as new ones appear")**, multi-hop, **preference following
  ("personalized responses that adapt to evolving preferences")**, summarization, temporal
  reasoning. No session boundaries — one continuous dialogue.
- **LIGHT write time:** three stores. *Episodic*: after each turn, Qwen2.5-32B extracts
  "key-value pairs and a summary of the interaction," embedded into a vector DB. *Scratchpad*:
  "reason over the current and preceding turn and extract salient content," merged
  iteratively; when it exceeds 30K tokens it is compressed to a 15K summary; at inference
  the scratchpad is filtered against the question. *Working memory*: last z turns.
- **Changed fact:** handled implicitly — the scratchpad is rewritten/merged and periodically
  summarized (lossy), the episodic KV store is append-only with no supersession.
- **Results (nugget score):** 1M tokens, Llama vanilla -> LIGHT: **knowledge update 0.164 ->
  0.414**, preference 0.535 -> 0.610, **contradiction resolution 0.046 -> 0.042**; Qwen KU
  0.064 -> 0.357, CR 0.035 -> 0.021. 10M: Llama KU 0.100 -> 0.325, preference 0.291 ->
  0.483, CR 0.025 -> 0.000. Overall +3.5-12.7% over strongest baselines. Hindsight later
  scored LIGHT at 26.6-35.9% overall on BEAM.
- **Stance:** LIGHT is the cautionary tale: a periodically *summarized* scratchpad gets
  contradiction resolution essentially to zero — compression destroys the old value needed
  to *notice* a contradiction. That is a direct argument for our rule "never rewrite old
  lines". **Borrow:** BEAM's contradiction-resolution vs knowledge-update distinction: KU
  asks for the new value; CR asks the model to *see both* and reconcile. Our chain view
  `Rex <- Max` serves both, which nothing else in this survey does explicitly.
  **Design note for BEAM:** no timestamps, no sessions — as our design doc says, the `(was
  X)` phrasing has to carry ordering; the window size becomes a first-class hyperparameter.

---

## 9. Eywa — "Provenance-Grounded Long-Term Memory for AI Agents" (May 2026)

- arXiv 2605.30771 https://arxiv.org/abs/2605.30771
- **Write time:** "evidence before belief." Raw turns stored as "immutable source
  material: the original user turn, assistant proposal, observation, timestamp, role, and
  metadata." Typed signals (dates, entities, money, versions, identifiers, URLs) are
  extracted *deterministically* without an LLM. An LLM proposes candidate facts, each
  validated by V = support-overlap AND hard-value-accuracy AND subject-appears AND
  polarity-preserved; in a 143-sample audit 67.4% of candidates had no hard anchor and
  were checked by the softer rules. Retrieval runs with zero LLM calls.
- **Changed fact:** facts carry `valid_from` / `valid_until`; the write path "represents
  updates, corrections, rejections, approvals, and superseding facts rather than treating
  all memories as flat, timeless assertions." The read-side "preservation floor assumes
  the write path has already marked outdated state facts as superseded."
- **Results:** LongMemEval-S 88.2 overall: SS-user 100, SS-preference 90.0, **knowledge
  update 96.2 (78 q)**, SS-assistant 73.2, multi-session 84.2, temporal 87.2. LoCoMo 90.19.
  BEAM (700 q subset): overall mean 81.45%; **knowledge update 70.00% (lowest technical
  category)**, contradiction resolution 93.21, preference 79.05, temporal 90.0, abstention
  92.86. Failure buckets on LongMemEval: 27 fact-not-retrieved, 12 lost-before-final-context,
  12 fact-not-extracted. Authors name KU "one of the clearest next memory-improvement
  targets."
- **Skeptical note:** BEAM was evaluated on a 700-question subset, not the full 2,000; the
  BEAM KU gap (70%) vs LongMemEval KU (96%) suggests session-less, long-range supersession
  is much harder than LongMemEval's.
- **Stance:** closest published relative of our design — immutable evidence, explicit
  superseding facts marked at write time, validity intervals, cheap read path.
  **Borrow:** (a) a deterministic validator on atomic lines: the value must appear (or
  its hard anchor — number/date/name — must appear) in the session text, negation
  preserved; (b) their failure-bucket taxonomy (not extracted / extracted but lost /
  retrieved but misused) for our smoke test.

---

## 10. MemIR — "Mitigating Provenance-Role Collapse via Typed Memory Representation" (May 2026)

- arXiv 2605.25869 https://arxiv.org/abs/2605.25869
- **Write time:** seven atom types. Evidence atoms (Page, Span) keep verbatim text and
  boundaries; cue atoms (Handle, Time, Pivot) are LLM-extracted access keys; Claim atoms are
  LLM-generated "source-grounded" statements and "the only truth-bearing components," with
  a strict support constraint back to a Span. "Provenance-role collapse" = flat text memory
  lets the model confuse *who said it / when / whether it is evidence or inference*, e.g.
  overcounting "temporally distributed mentions as distinct objects rather than stages of a
  single referent."
- **Changed fact:** no write-time supersession. Conflicts are resolved at read time by
  bundle selection with time cues: "an earlier 3 PM plan from Page 13 and a later 4 PM
  update from Page 23" -> C23:01 as direct evidence, C13:01 "only as historical contrast."
- **Results (gpt-4.1-mini):** LoCoMo judge: single-hop 89.5, temporal 84.6, multi-hop 70.2.
  BEAM-100K: **knowledge update 58.40, contradiction resolution 32.30**, temporal 38.50,
  average 48.26, beating Mem0, SimpleMem, NEMORI.
- **Stance:** **agrees** on typing (evidence vs claim mirrors our atomic-verbatim vs
  narrative-inference split) and on the failure mode — a narrative line that restates a
  fact must not be mistaken for the atomic line that grounds it. **Borrow:** make each
  narrative line reference the session it came from (we date lines; a session id would let
  the answerer trace provenance), and consider tagging *speaker* on LoCoMo where both
  parties are people (the design doc already puts the owner in the key).

---

## 11. EMBER (Jun 2026)

- arXiv 2606.05894 https://arxiv.org/abs/2606.05894
- **Write time:** a *learned* retention policy (RL, 14B) that keeps "evidence capsules:
  verbatim source excerpts paired with retrieval keys and update metadata" under a fixed
  token budget. Capsules = (bounded source excerpt, retrieval keys = entities + intent
  descriptors, token cost).
- **Changed fact:** an `update_mode` field with insert / merge / overwrite / skip. Merge
  "appends new facts and deduplicates; the title, entities, and retrieval keys are
  replaced" while optionally keeping the original excerpt; overwrite "replaces the target
  capsule entirely" when facts are "stale or superseded." So supersession is a *learned
  overwrite*, not a chain.
- **Results (LongMemEval-RR, 8,192-token budget):** EMBER-14B 0.3017 F1 vs 0.1765 for the
  best non-EMBER budgeted baseline; summary-only baseline 0.1156; oracle 0.4499.
  Retain-Recall 0.3215, Read-Recall 0.3112.
- **Stance:** **agrees** on verbatim atomic content ("summary-only" loses badly);
  **disagrees** on overwrite-on-supersede. **Borrow:** their Retain-Recall / Read-Recall
  split is a clean way to instrument our pipeline — did the evidence get written, and did
  it survive to the answer prompt. Their reward design (answer correctness gates evidence
  rewards) is out of scope but explains why they can afford overwrite: the policy is
  trained to know when it is safe.

---

## 12. LongMemEval (Wu et al., ICLR 2025) — the benchmark's own write-time findings

- arXiv 2410.10813 https://arxiv.org/abs/2410.10813
- Question types (500 total): single-session-user, single-session-assistant,
  single-session-preference (30), multi-session (133), **knowledge-update (78)** "recognizing
  changes in the user's personal information," temporal-reasoning (133), plus 30 abstention
  variants. Long-context and commercial assistants show a ~30% drop.
- **Write-time findings:** *value granularity* — decomposing sessions into rounds helps
  reading with GPT-4o; storing extracted **facts alone hurts overall QA** but improves
  multi-session reasoning. *Key expansion* — indexing rounds by extracted user facts gives
  "an average improvement of 9.4% in recall@k and 5.4% in final accuracy." *Time-aware
  query expansion* helps temporal questions.
- **Stance:** the benchmark authors found fact-only memory is lossy — the same result as
  TriMem (sec. 18) and the reason for our narrative line. **Borrow:** their evidence-session
  labels (already used in our Inspect bridge) are the right ground truth for a
  Retain-Recall metric on our extractor.

---

## 13. Honcho (Plastic Labs, 2026)

- https://plasticlabs.ai/blog/research/Benchmarking-Honcho ; https://github.com/plastic-labs/honcho
- **Write time:** "small fine-tuned models capture all latent information & save it as a
  'Representation' of the author" per message; a background "dream" process "prune[s]
  excess information, consolidate[s] duplicated information, create[s] deductions."
  Conclusions are traceable to premises ("dialectic" agent walks conclusion -> premises).
- **Changed fact:** not described beyond consolidation/pruning during dreaming.
- **Results:** LongMemEval-S 90.4: SS-assistant 96.4, **knowledge update 94.9**, SS-user
  94.3, SS-preference 90.0, temporal 88.7, multi-session 85.0. BEAM 100K 0.630, 500K 0.649,
  1M 0.631, 10M 0.406 (Hindsight later reported 64.1 at 10M).
- **Stance:** a representation-centric (profile) design that keeps premises. Not much to
  borrow beyond the reminder that keeping the conclusion -> premise link is what lets a
  reader audit a supersession.

---

## 14. MemStrata — "Temporal Validity in Retrieval Memory" (Jun 2026)

- arXiv 2606.26511 https://arxiv.org/html/2606.26511v1
- **Write time:** LLM extracts a (subject, relation, object) triple only when a statement
  has "a single concrete value that could change." Deterministic rule: same (S,R), different
  O -> newer supersedes older, "independent of how similar their embeddings are." Bi-temporal
  ledger with `valid_from`, `valid_to`, `superseded_by`; retired facts are kept but hidden
  from retrieval. Non-triple prose goes to an LLM gate (duplicate/merge/contradict/novel).
  No LLM on the read path.
- **Key demonstration:** on 98 labeled pairs, cosine similarity separates contradictions
  from duplicates at only **0.59 AUROC** — contradictions are *more* similar to the original
  than paraphrases are. So "retrieve similar memories, then let the LLM decide UPDATE" (Mem0
  paper, Zep) is structurally handicapped at the retrieval step.
- **Results:** RAG serves the stale value 15-40% of the time on four evolving benchmarks;
  MemStrata ~0% (accuracy 0.95-1.00 vs RAG 0.20-0.47), equal on static sets. Admitted
  limits: extraction reliability ~97% on structured input, **~44% on natural-language
  contradictions with multi-value sentences**; ingestion order stands in for real time; tiny
  benchmarks; 7B model.
- **Stance:** **agrees** exactly with our key-based supersession (`key:` is the (S,R), the
  value is O) and with keeping retired values. Its ~44% figure is the honest warning: the
  hard part is getting the extractor to emit the *same key* for the same fact across
  sessions. **Borrow:** treat key normalization as the core extractor skill (show the
  existing keys in the prompt — our extractor already sees the whole memory, which is a
  structural advantage over MemStrata's per-statement extraction).

---

## 15. Supersede — "Diagnosing and Training the Memory-Update Gap" (Jun 2026)

- arXiv 2606.27472 https://arxiv.org/abs/2606.27472
- Setup: agent keeps a bounded (300-char) self-maintained notes field updated after each
  session, never re-reading raw sessions; compared to full context. Failure modes: updated
  fact "compressed away", "not overwritten" (old value persists), or absent.
- **Results:** gpt-5.4 full-context 92% vs bounded-memory 77% (p=0.0033); accuracy falls
  68% -> 28% over 24x longer conversations and 24x more memory budget does not recover it;
  GRPO on Qwen2.5-3B lifts held-out accuracy 9.0% -> 16.7%. Conclusion: "supersession is
  best understood not as a capability the next model will absorb, but as a behavior that
  must be optimized for."
- **Stance:** the strongest evidence that the *rewrite-a-compact-block* pattern (Letta,
  LIGHT scratchpad) fails on updates even with frontier models. It does not test an
  append-with-annotation design like ours, so it neither confirms nor refutes it — but it
  says the extractor prompt must treat "is this a change to an existing key?" as an
  explicit step, not hope the model notices.

---

## 16. MemReader (Apr 2026)

- arXiv 2604.07877 https://arxiv.org/abs/2604.07877
- **Write time:** a 4B model trained (SFT+GRPO) to choose among add_memory, search_memory
  (retrieve context to resolve references), buffer_memory (defer incomplete info),
  ignore_memory. Entries: key (short unique title), memory_type (LongTermMemory /
  UserMemory), value (self-contained, references resolved), tags.
- **Changed fact:** handled by add + the fact that the model can search existing memory
  first; the paper stresses "effective memory updating and temporal reasoning" as the
  differentiator.
- **Results (LongMemEval):** **knowledge update 91.03 vs Mem0 66.67 and Zep 74.40**;
  temporal 84.21 vs Mem0 72.18 / Zep 54.10; overall 83.0. HaluMem-Medium updates: 94.55%
  correct with 5.12% omission, vs Mem0 56.80 F1.
- **Stance:** **agrees** that the extractor must *see existing memory* before writing
  (their search_memory action; our whole-memory-in-prompt). Their key/value entry schema is
  essentially our atomic line. **Borrow:** the "defer incomplete input" action maps to
  "do not write an atomic line for an unresolved reference; write a narrative line
  instead."

---

## 17. Memanto (Apr 2026)

- arXiv 2604.22085 https://arxiv.org/html/2604.22085v1
- **Write time:** no LLM at ingest; raw content committed with automatic typing into 13
  categories (fact, preference, decision, commitment, goal, event, instruction,
  relationship, context, learning, observation, error, artifact), tags, timestamps,
  conflict detection.
- **Changed fact:** on a detected conflict the system "notifies the agent, requesting
  explicit resolution before the contradiction is persisted" — supersede / retain /
  annotate. Temporal versioning supports as-of, changed-since, current-only queries.
- **Results:** LongMemEval 89.8 (**knowledge update 93.6**, SS-assistant 100, multi-session
  81.2, temporal 88.0); LoCoMo 87.1. Also reports that raising retrieval limit 10 -> 40
  chunks adds +20.4 points on LongMemEval — a reminder that retrieval budget dominates
  when memory is raw.
- **Stance:** interesting counterexample — no write-time LLM, yet KU 93.6, the same as
  ADD-only Mem0. Suggests LongMemEval-S KU is largely solvable by *keeping everything with
  timestamps and letting a good answerer pick the newest*; the write-time supersession
  marker matters more at BEAM scale (Eywa's 96 vs 70). **Borrow:** the "current-only" vs
  "as-of" view distinction — our chain view is the "current-only + history" rendering.

---

## 18. Narrative vs atomic: TriMem, AtomMem, Amory

- **TriMem** — "Rethinking How to Remember: Beyond Atomic Facts" (arXiv 2605.19952,
  https://arxiv.org/abs/2605.19952). Keeps three granularities: raw segments with source
  ids, atomic facts for retrieval, synthesized profiles. Quantifies the loss: fact
  extraction "loss 14.5% more information than original dialogue"; fact-only systems
  "completely lack ... deep comprehension towards entity semantic portraits." LoCoMo (GPT-4o)
  F1 avg 50.23 vs SimpleMem; profiles are incrementally updated. **Stance:** strongest
  published case *for* a second, non-atomic form; **disagrees** in that its profile is an
  LLM-rewritten object.
- **AtomMem** (arXiv 2606.19847, https://arxiv.org/abs/2606.19847). SFT "Atomic Fact
  Extractor" emits self-contained facts with participants, keywords, temporal anchors; facts
  are grouped into Episodic Events (narrative blocks) and Persistent Profiles; the profile
  layer "maintains historical versions to preserve past states while adapting to preference
  shifts" — previous state is copied into history on change. LoCoMo judge: single-hop 78.48,
  multi-hop 68.44, temporal 66.98, open-domain 64.58; LongMemEval SS-user F1 80.70,
  multi-session 57.50, temporal 42.10. AtomMem-Flat uses 722.75K tokens vs Mem0's 55,300K.
  **Stance:** **agrees** on atomic + narrative + versioned profile; **borrow** the
  "temporal anchor" field on each fact (event date, distinct from session date).
- **Amory** (arXiv 2601.06282, https://arxiv.org/abs/2601.06282). Episodic memory as
  narratives, "peripheral facts" semanticized; momentum-aware consolidation; retrieval by
  narrative coherence. Claims LoCoMo parity with full context at half the latency; no
  statement on changed facts.
- **Adaption Labs' framing is therefore not novel** — three 2026 papers independently
  arrive at "atomic facts alone lose 10-15% of the information; keep a narrative/profile
  layer too." What is distinctive in our design is that the narrative layer is
  *append-only* and the profile is a *derived view*, not a third LLM-maintained object.

---

## 19. Are We Ready For An Agent-Native Memory System? (Jun 2026) — extraction ablations

- arXiv 2606.24775 https://arxiv.org/html/2606.24775
- Controlled write-time variants inside MemoChat, MemOS, LightMem. LongMemEval (substring
  EM / ROUGE-L): MemOS Fast 20.7/26.1 vs Fine 22.3/30.2; LightMem user-only raw 26.0/31.4
  vs hybrid raw 25.3/31.4; MemoChat heuristic topic 10.7/18.6 beats LLM topic 7.3/15.9.
  Conclusion: "Coverage-preserving write-time extraction provides the most stable balance
  between factual retrieval and downstream reasoning"; lighter memorization "is more
  likely to retain details."
- **Stance:** supports "extract more, compress less" — consistent with Hindsight's coarse
  facts, EMBER's verbatim, TriMem's loss figure. Also a warning that LLM-driven
  segmentation can be *worse* than a heuristic; our chunk = dataset session avoids that.

---

## 20. Write-time error measurement: HaluMem, MemTrace, TrustMem

- **HaluMem** (arXiv 2511.03506, https://arxiv.org/abs/2511.03506). First operation-level
  benchmark: memory extraction (recall, accuracy, false-memory resistance), **memory
  updating (update accuracy, hallucination rate, omission rate)**, and QA. Results
  (Medium): Mem0 extraction recall 42.91 / accuracy 60.86; Mem0-graph 43.28 / 61.86;
  Supermemory 41.53 / 60.83; Memobase 14.55 / 32.29. On Long, Mem0 recall falls to 3.23%
  while Supermemory over-extracts (24,483 memory points). **Updating: all systems below
  26% correct with omission above 50%**, mainly because "when the pre-update memories are
  not extracted, related updates cannot be properly processed"; "the extraction and
  updating stages lack stable linkage." **Stance:** the single most relevant negative
  result for our design: supersession is only as good as the *first* extraction of the
  key. Borrow the three metrics for our smoke test.
- **MemTrace** (arXiv 2605.28732, https://arxiv.org/html/2605.28732). Error taxonomy:
  annotation, extraction, update, deletion, retrieval, response, judge. On Mem0/LoCoMo:
  extraction "tends to keep high-level user information while dropping fine-grained
  details"; "timestamp reassignment during updates, where content remains unchanged but
  its time is modified"; "no deletion errors, likely because deletion is only supported by
  Mem0 and is rarely tested." Retrieval and response errors are frequent for every
  system. **Stance:** the timestamp-reassignment bug is precisely what in-place UPDATE
  causes and what append-only cannot cause.
- **TrustMem** (arXiv 2606.25161, https://arxiv.org/abs/2606.25161). Trains a consolidation
  policy with a Memory Transition Verifier scoring capture / preservation / groundedness;
  +12.14 F1 on HaluMem extraction, -40.1% omissions, -79.1% corruptions, -50.0%
  hallucinations. **Stance:** those three verifier criteria are a good rubric for judging
  our extractor's output diffs even without training.

---

## Cross-cutting: per-category numbers on LongMemEval-S knowledge-update (KU) and preference

| System | KU | SS-preference | Write-time update mechanism |
|---|---|---|---|
| Full context gpt-4o (Zep paper) | 78.2 | 20.0 | none |
| Zep gpt-4o / mini (2025) | 83.3 / 74.4 | 56.7 / 53.3 | LLM edge invalidation, bi-temporal |
| Mem0 old (UPDATE/DELETE) | 79.5 | 76.7 | LLM ADD/UPDATE/DELETE in place |
| Mem0 new ADD-only (Apr 2026) | 93.6 | 96.7 | append only, no marker |
| Mem0 as re-run by MemReader | 66.7 | – | (older config) |
| MemReader-4B-GRPO | 91.0 | – | trained add/search/buffer/ignore |
| Hindsight Gemini-3 / 120B / 20B | 94.9 / 92.3 / 84.6 | 80.0 / 86.7 / 66.7 | keep all, confidence at belief layer |
| Honcho | 94.9 | 90.0 | representation + dream consolidation |
| Eywa | 96.2 | 90.0 | superseded marked at write, valid_from/until |
| Memanto | 93.6 | – | no LLM at write; conflict flagged to agent |

Reading: on LongMemEval-S, KU clusters at 92-96 for every system that *keeps* the old fact
(ADD-only Mem0, Hindsight, Honcho, Eywa, Memanto) and sits at 74-83 for the two that
adjudicate updates with an LLM at write time (Zep, old Mem0). Preference questions (30 q)
are noisier but reward systems that keep the user's phrasing (Mem0 new 96.7, Honcho/Eywa
90). On BEAM, KU is much harder (Eywa 70%, MemIR 58, LIGHT 0.33-0.41) and contradiction
resolution collapses for summary-based memory (LIGHT ~0.0-0.04).

## What is demonstrated vs claimed

- Demonstrated: in-place LLM update/delete underperforms and is error-prone (Mem0's own
  reversal; HaluMem <26% update accuracy; MemTrace timestamp bug; Zep KU < ADD-only).
- Demonstrated: fact-only memory loses information (LongMemEval facts-as-values hurt;
  TriMem 14.5%; EMBER summary-only 0.12 vs 0.30 F1) — supports a narrative layer.
- Demonstrated: embedding similarity cannot detect contradictions (MemStrata 0.59 AUROC),
  so supersession must be decided by something that sees the old value explicitly.
- Demonstrated: rewriting a compact state block loses updates at scale (Supersede, LIGHT).
- Claimed, not isolated: that "write-time" per se beats "retrieval-time" optimization.
  Every top system also has a heavy retrieval layer (Hindsight TEMPR, Mem0 multi-signal
  ranking, Eywa deterministic planner), and Memanto gets KU 93.6 with *no* write-time LLM.
  No paper ablates write-time supersession marking against plain append with timestamps
  on the same retrieval stack. That ablation is the experiment our reproduction can
  actually contribute: chain view vs flat append-only, same extractor, same answerer.
- Nobody publishes a `(was X)` / chain rendering; the nearest are MemStrata's
  `superseded_by` and Zep's `t_invalid`, both hidden from the reader rather than shown.
