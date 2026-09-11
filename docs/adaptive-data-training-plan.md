# Adaptive Data plan for BEAM extractor training

## Correction after API verification, 2026-09-11

The proposed seeded Augment workflow below is **not supported by the verified
Augment endpoint**. The official OpenAPI spec describes POST
`/api/v1/datasets/{dataset_id}/augment` as retrieving rows from a curated pool,
not generating task-specific new examples from our traces. `domain_rows` selects
rows from matching topics; `general_rows` selects other topics. The response
combines original and retrieved rows in a new dataset. SDK 0.12.0 agrees.

There is no custom generation prompt or extractor-schema control in that
endpoint's typed request. Topic-matched instruction examples do not establish
compatibility with our prior-memory + session -> JSON-update training task.
Do not execute the earlier 32/600-row proposal through Augment as if it were
trace-based synthesis. User direction is needed on curated-pool augmentation
versus investigating a task-specific generation route. No upload, estimate,
augmentation or training was started during this verification.

Source: [official OpenAPI specification](https://github.com/adaptionlabs/adaption-api-docs/blob/main/spec/openapi.json).
The generated Augment page failed to fetch; the official raw spec was retrieved
successfully and checked against installed SDK types and method documentation.

2026-09-11. Proposed plan, awaiting user confirmation. No upload, estimate API
request, generation, or training was performed to prepare this plan.

## Objective and frozen inputs

Build a synthetic-augmented Qwen3.5-9B extractor training set with at least 1,000
accepted rows, using only the approved BEAM training histories. The source is
`work/beam_teacher_sft/e18563c1a02ce127/`: 588 original updates, 564 fitting the
65,536-token SFT window, and 24 oversized updates preserved outside training.
The 564 are candidates, not quality-approved examples; 366 of all 588 have
heuristic warnings. Preserve this source snapshot unchanged.

Adaptive Data produces data. AutoScientist performs fine-tuning. Modal runs the
extractor. This plan does not change those roles or authorize paid execution.

## Recommended sequence

| Stage | Work | Exit condition |
|---|---|---|
| 1. Seed review | Review source faithfulness, attribution, temporal updates and coverage. Sample four fitting examples per history, covering warning statuses and early/late updates where available; prioritize broader review where defects appear. | At least two reviewed seeds per history, with source-backed targets and a recorded review trail. Flagged and unflagged examples are both checked. |
| 2. Prepare adapter and quote | Verify installed SDK and current augmentation schema; round-trip canonical messages through the provider mapping without losing roles, timestamps or JSON targets. Prepare the frozen request and obtain pilot/full estimates and available-credit information. | Exact fields, estimated cost and credit reservation presented for approval. |
| 3. Pilot | Generate 32 new candidates, targeting two per source history/family. Inspect every pilot example, not just the provider quality score. | No systemic format/attribution failure; at least 26/32 accepted before expanding. Otherwise report defects and revise the specification on training data only, with a new cost quote. |
| 4. Expand | Target 600 new candidates total, including the pilot, in separately checkpointed batches. Initial planning mix balances the 100K/500K source families and topics. | Stop when enough accepted rows exist; do not automatically exceed the quoted batch allocation. |
| 5. Validate and freeze | Validate every row mechanically; review semantic support, deduplicate and check held-out overlap. Select originals and synthetics under the same quality rules. | At least 1,000 accepted, fitting rows, with counts, hashes, provenance and exclusions recorded. |
| 6. Training handoff | Prepare the AutoScientist input and explicit training settings, check credits and obtain a training estimate. | Separate training approval; no automatic training triggered by data completion. |

The 64-row source spot-check is diagnostic, not a certification of all originals.
Every retained original and synthetic row needs source-consistency checks; use
reviewed seeds only for generation. Where review rejects a teacher target, keep
the original and any repaired version separate and record the reason.

The 600-row target is a planning number, not a guaranteed usable yield. If all
564 originals survived, it would produce 1,164 candidates before synthetic
filtering. Let R be retained originals and S accepted synthetics: readiness is
R + S >= 1,000. More original exclusions increase the synthetic shortfall.
Report any deficit and seek approval for another quoted batch. Do not pad counts
by duplicating rows or count retries as new examples.

## Generation task

Each example is an extractor update, not a benchmark question/answer:

`fixed extractor instruction + prior memory + timestamped new conversation window -> narrative/atomic JSON update`

Preserve the exact inference instruction and output schema. New examples should
change the source situation coherently, not just rephrase the target. Rebuild
prior memory, source messages, timestamps and target together whenever facts
change. Never pair an unchanged source with an invented incompatible target.
Use the existing eight-pair extraction boundary and metadata conventions; include
early empty-memory cases and later accumulated-memory cases.

Cover new preferences, corrected preferences, future plans versus completed
events, assistant suggestions versus user decisions, chronological updates,
irrelevant conversation, no-new-fact updates, and selective concise retention.
Maintain topic and source-family diversity; inspect actual token-length
distributions to avoid making every synthetic prompt much shorter than deployment.
Do not add generic question-answering or general-purpose augmentation rows.

The desired target is visible JSON only, not reasoning prose or explanations.
Disable reasoning-trace generation and web-search grounding where supported:
correctness means support in the supplied conversation, not outside knowledge.
Do not transform source material through automatic translation/localization.
Verify these controls on the actual selected endpoint rather than passing fields
that belong to another endpoint.

## Which Adaptive Data route

Use dataset augmentation seeded by reviewed training examples for the first
experiment. The [run API](https://docs.adaptionlabs.ai/api/resources/datasets/methods/run)
states that adaptation improves existing rows without increasing their count and
directs additional-row generation to augmentation. Its `max_rows` is a processing
cap, not the number of additional rows to invent.

The [augmentation reference](https://docs.adaptionlabs.ai/api/resources/datasets/methods/augment)
could not be fetched during planning. Before implementation, verify its current
SDK/request schema, estimate support, controls, source preservation and lineage
fields. Do not assume the adaptation endpoint's blueprint or recipe fields also
work on augmentation. If the endpoint cannot enforce this coupled input/target
task, stop and present the alternative before spending.

[Invent](https://docs.adaptionlabs.ai/api/resources/datasets/methods/invent)
supports domain-based generation, a task description, a row target, estimates and
idempotency keys. It is a possible separate experiment, not the default here:
invented rows have no original source-row parent. Do not claim they were derived
from our traces. A generic domain instruction dataset would not meet our task.

## Isolation and quality gates

- No dev/final source conversations, memories, benchmark questions, reference
  answers or evidence go to Adaptive Data. Held-out hashes may be used locally
  for overlap detection, not to guide generation content.
- All children of a training seed/family remain training-only. Do not split
  synthetic siblings into dev. The four existing BEAM dev conversations and
  seven final conversations retain their exact question selections.
- Preserve role boundaries; freeze the system prompt locally after parsing the
  provider output into validated source fields. Do not accept a provider rewrite
  of the extractor instruction as equivalent without an explicit new experiment.
- Parse target JSON using the current strict schema; replay updates with the
  actual memory implementation; reject malformed, truncated or unsupported
  targets. Replay consistency alone does not prove semantic faithfulness.
- Measure the entire Qwen training sequence including chat template and target.
  Reject overlength rows from the fitting export without truncating stored data.
- Check speaker attribution, temporal certainty, contradictions, update-chain
  semantics, important-fact coverage and concision against the supplied source.
  A provider score or a lack of existing heuristic warnings is not sufficient.
- Deduplicate exact and near-duplicate prompts/targets, retain source-family IDs,
  and audit cross-split overlap. Report semantic-overlap limitations honestly.
- Keep rejected rows and reasons outside the training payload; keep API usage and
  provenance in sidecars, not in model input. No hidden reasoning is distilled.

## Cost, interruption and artifacts

First estimate the exact pilot and expansion requests. Use verified existing
Adaption credits only, preserving a stated reserve for AutoScientist and review.
No prices are assumed in this plan. If credits or a bounded reservation cannot be
verified, obtain a numeric cap before generation. No purchases, top-ups, overage,
or changes to the $30 Modal cap are authorized. If semantic review uses another
paid provider, quote and allocate that cost separately.

Persist request configuration, source hashes, dataset IDs, job IDs, idempotency
keys, requested/delivered/accepted counts, estimates, actual credits when returned,
and timestamps before proceeding to the next stage. Poll existing jobs after an
interruption; never blindly submit a duplicate generation request. Download and
validate completed or recoverable partial results before deciding on another job.

Save separate seed manifest, pilot, batch exports, quality-review records,
accepted-original, accepted-synthetic and combined training manifests under a new
gitignored `work/` directory. Publish only code and aggregate documentation.

## What comparison this enables

This creates the synthetic-data arm, starting from the same Qwen base model.
It does not solve eligibility for the no-synthetic arm: that arm still has at
most 564 currently fitting original candidates and needs additional real teacher
updates or a separately approved training-service change. Neither duplicating
rows nor calling generated targets original data is an acceptable workaround.

Pin the base model, extractor contract, serving output policy, answerer, judge,
and evaluation selections across arms. Disable hidden extra AutoScientist
augmentation. Use completion-only loss for the extractor targets after verifying
the API settings. Choose checkpoints on dev, never on the ongoing final run.
Any comparison to the mixed-output-cap baseline must retain that limitation;
an observed gain does not establish that synthetic data alone caused it without
the real-only fine-tuned control.

## Confirmation requested

Approve this staged plan: review seeds and verify the adapter; present exact
credit quotes; then, after cost approval, run the 32-row pilot and expand toward
600 candidates if it passes, targeting at least 1,000 accepted combined rows.
Training remains a separate approval. No paid data work has started.
