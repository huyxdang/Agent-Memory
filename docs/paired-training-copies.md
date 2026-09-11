# Original versus repaired training copies

This page describes the preserved v1 pilot. See
[the v2 repair comparison](copy-2-repair-comparison.md) for the subsequent
33-target repair snapshot and its verification status.

Two self-contained copies are saved locally in `work/training_copies_v1/`.

| Copy | Training examples | Dev examples | Changes |
|---|---:|---:|---|
| `copy_1_original` | 2,428 across 51 histories | 478 across 10 histories | Original teacher outputs and reconstructed original inputs |
| `copy_2_repaired_pilot` | Same IDs and ordering | Byte-identical to copy 1 | Six reviewed target repairs; 155 later memory inputs rebuilt |

Each copy contains `train.jsonl` and `dev.jsonl`. Rows carry the full system/user/
assistant messages plus example IDs, history hashes and original-call provenance.
These are auditable, provider-neutral exports; a provider-specific training upload
may need to strip metadata. Provider prompt-cache hints are omitted from both
copies; prompt text and message boundaries are preserved. Hidden reasoning text
is neither available nor included.

Copy 1 is the control. It was reconstructed against original prompt hashes, and
its assistant target strings match the saved teacher outputs exactly. Source run
files are unchanged. The builder refuses to overwrite an existing snapshot;
checksums detect subsequent edits.

## Repair scope

The pilot applies six reviewed corrections, without changing prompts or the
detector: separate keys for distinct trips/games, remove unsupported completion
and attributed preferences, preserve uncertainty and contemplated plans, avoid
inferred protocol labels, normalize an approximate future date, and attribute
assistant-proposed actions to the assistant.

All other targets are untouched. The six corrections change later memory inputs,
so those inputs are rebuilt by replaying the repaired targets. All 155 affected
later rows are explicitly pending semantic dependency review. None directly
reuses an edited atomic key, but that mechanical check does not prove its entire
target remains appropriate after the context changes.

**Copy 2 is a repair pilot, not a fully cleaned or training-ready dataset.** The
unreviewed examples remain unreviewed. Six changed targets are too small a change
to assume a measurable downstream gain. No filtering, paid API calls, fine-tuning
or benchmark comparison has been performed.

## Comparison controls

After repairs and dependency review are finished, train two copies of the same
student checkpoint with the same prompt, example IDs/order, optimizer settings,
seed and number of training steps. Record token exposure, actual compute/cost and
target-length differences rather than assuming identical token counts.

Evaluate the untuned student and both trained variants using the same answerer,
judge, no-retrieval policy and frozen evaluation histories. Keep synthetic-data
augmentation separate. A new independent final set still needs to be reserved.
Unchanged dev teacher targets are not independent factual gold labels.

Local `manifest.json` records artifact/source hashes and readiness. The
`changes.jsonl` file records each edit and propagated input change;
`dependency_review_queue.jsonl` lists pending checks; `repair_spec.json` preserves
the exact repair operations and reasons; `frozen_split.json` records assignments.

Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python verify_training_copies.py` to check
both copies without changing them. Verified 2,428 aligned training IDs, 478
identical dev rows, six expected target changes, 155 logged input changes,
unaltered source sessions/system prompts, source hashes and original-target
fidelity. All 25 offline tests and the whitespace check passed.

Raw data and repair payloads remain local and gitignored. No commit or push.
