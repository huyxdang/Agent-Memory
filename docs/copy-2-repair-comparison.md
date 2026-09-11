# Copy 2 repair comparison

The completed repair snapshot is `work/training_copies_v2/copy_2_repaired/`.
Its manifest status is `scoped_repair_complete`, verified on 2026-09-10.
All six final-context checks and all 30 offline tests passed. This closes the
repair pass below; it does not certify every teacher target in the corpus as
correct.

| Property | Copy 1 control | Copy 2 repaired |
|---|---:|---:|
| Training examples | 2,428 | 2,428, same IDs/order |
| Training histories | 51 | Same 51 |
| Dev examples / histories | 478 / 10 | Byte-identical |
| Targets changed versus control | 0 | 33 |
| Prior-memory inputs changed | 0 | 155 |
| Source sessions / system prompts | Original | Unchanged |

Copy 1 remains at `work/training_copies_v1/copy_1_original/`. The earlier
six-repair pilot remains at `work/training_copies_v1/copy_2_repaired_pilot/`.
Nothing in either snapshot was overwritten. V2 adds 27 accepted target repairs
to the original six and changes 113 later inputs relative to the pilot.

## What was reviewed

Sol and two Terra agents reviewed the 155 pending downstream examples, grouped
by whole history. The saved reviews cover each queue ID exactly once:
120 keep, 28 proposed repairs and seven uncertain. Root checked proposed changes
against source evidence and accepted 27. One proposed deletion was rejected:
an earlier recommendation of the same book does not justify removing it from
the actual list recommended in a later session.

Repairs address speaker attribution, unsupported completion/success claims,
invented date precision, tentative plans stored as settled facts, malformed
keys and a stale history chain exposed by an earlier repair. The builder replays
all memory updates, rather than editing later prompt strings manually.

Seven source/contract ambiguities remain unchanged and flagged in the review
and decision files. These include inconsistent dates, uncertain attribution,
and conflicting game-completion records. No rows were silently dropped or
declared factually clean because a detector passed.

This is an assistant-reviewed repair experiment, not independent human labeling
or an exhaustive audit of all 2,428 examples. The review set was selected from
affected histories; its repair fraction is not a corpus-wide error estimate.
Unchanged dev targets are teacher outputs, not gold factual annotations.

## Verification and provenance

`finalize_repaired_copy.py` rejects missing/duplicate reviews, malformed targets,
changed proposal hashes and incomplete adjudications. Its verification command
reconstructs the exported training rows and requires exact equality, preserving
IDs, order, source sessions and prompt boundaries. Final-context reviews bind
to the content hash of each of the six affected exported histories before the
snapshot can be sealed.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python verify_training_copies.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python finalize_repaired_copy.py verify
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

V2 saves reviews, proposals, root decisions, the change log and content hashes.
The manifest links the frozen pilot manifest and the builder code hash. The
builder refuses to overwrite an existing output directory. Raw examples and
review evidence stay local and Git-ignored.

## How to compare

Use these two data copies with the same student checkpoint, prompt, training
settings, seed, ordering, step budget and frozen evaluation protocol. Record
actual token exposure because repaired targets and memory inputs differ in
length. Keep synthetic augmentation separate. Reserve independent final
histories before claiming held-out benchmark performance.

No training, synthetic generation or benchmark evaluation was run for this
repair pass. Whether the repairs improve final accuracy is still unverified.
