# Training trace audit, 2026-09-10

Audited 39 saved our-memory run manifests and 630 trace occurrences, without API
calls. Chose one fully reconstructible trajectory per exact full source history.
Selection uses the latest eligible run, then lowest question ID, never answer
accuracy. Alternate generations remain inventoried but are not independent data.

| Source | Train histories | Dev histories | Train updates | Dev updates |
|---|---:|---:|---:|---:|
| LongMemEval | 100 | 0 | 4,803 | 0 |
| LoCoMo | 8 | 2 | 217 | 55 |
| BEAM 100K | 3 | 2 | 39 | 30 |
| BEAM 500K | 1 | 1 | 53 | 81 |
| Total | 112 | 5 | 5,112 | 166 |

An update is one existing-memory-plus-session input and its teacher output, not
an evaluation question. These are trace indexes, not yet fine-tuning payloads.
The selected teacher configuration is GPT-5.6 Luna, low reasoning, 128,000-token
output cap. Each original prompt version and call remains traceable.

## Split limitations

The intended ratio was 80/20, using seed `extractor-train-dev-v1-20260910`.
However, all 100 LongMemEval histories form one connected component through
identical session content. Splitting those histories would leak sessions across
train/dev. The entire component is assigned to train. **There is no LongMemEval
dev set in this split**, and the aggregate ratio is not 80/20.

BEAM 100K and 500K variants with the same source chat ID stay together, even when
their complete-history hashes differ. Small strata prevent an exact 80/20 ratio.
All 10 local LoCoMo conversations are assigned to train/dev; new questions on
these conversations cannot form an independent final evaluation.

All selected histories and connected sessions must be excluded from future final
evaluation. No new final set was selected or paid run launched. Exact-session
deduplication ignores timestamps; semantic near-duplicate detection was not run.

## Trace validity and quality

468 trace occurrences were fully reconstructible. Exclusions were 100 reused
copies, 21 incomplete histories, 30 missing/retried call sequences, and 11 partial
source or synthetic fixtures. Original artifacts are unchanged and exclusions
are listed individually in the local inventory.

For each selected trajectory, verified every original prompt hash, sequential
session coverage, reconstructed history hash, successful stop finish reason and
target-to-stored-line consistency. Only one intact trajectory is selected per
history; no mixing steps from different generations.

This proves recoverability, not factual accuracy. Saved heuristic warnings flag
3,509 of 5,278 updates. There are 1,727 train and 42 dev updates without target
flags; only 178 train and 7 dev updates also have no flags in their prior memory.
Flags are not human labels, and unflagged outputs are not guaranteed correct.
Do not call all 5,112 train updates quality-approved fine-tuning examples.

## Local artifacts and reproduction

Under `work/training_trace_audit/`, which is gitignored:

- `audit.json`: source-file hashes, run snapshots, policy, exclusions, connected
  components and quality counts.
- `histories.jsonl`, `train_histories.json`, `dev_histories.json`: frozen history
  assignments and canonical trace references.
- `train_updates.jsonl`, `dev_updates.jsonl`: stable example IDs, source call
  pointers, prompt/target hashes and quality flags. No question or answer text is
  supplied as extractor training input.
- `occurrences.jsonl`: all trace candidates, including exclusions and variants.
- `summary.md`: generated aggregate report.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python audit_training_traces.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

The audit regenerates derived files, never source runs. Adding new traces may
change canonical selections or group assignments; preserve this split snapshot
before beginning model training.

Checks passed: 20 offline tests; 117 unique canonical history IDs; 5,278 unique
update IDs; complete partition; zero cross-split exact-history/session overlap;
all inventoried original run files unchanged; audit source hash matches output;
whitespace validation. No API spend, training, commit or push.
