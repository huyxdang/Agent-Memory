# LongMemEval split feasibility

Offline check of the 100 existing canonical histories, seed `20260910`.
Reserve whole dev histories, then discard every prospective training history
that shares an exact session with dev. No partial histories or mixed trajectories.

| Candidate | Train histories | Train updates | Dev histories | Dev updates | Histories discarded |
|---|---:|---:|---:|---:|---:|
| Fixed 20-history dev | 20 | 938 | 20 | 955 | 60 |
| Fixed 10-history dev | 51 | 2,428 | 10 | 478 | 39 |

Both candidates have zero exact session overlap between train and dev. Existing
split files are unchanged; these are candidates, not adopted training splits.

The earlier connected-component finding was correct, but the train-only outcome
assumed keeping every history. Discarding histories that connect the two sides
makes a split possible.

Across 1,000 diagnostic seeds, reserving 20 dev histories retained 698 to 2,007
training updates, median 1,317.5; 951 trials retained at least 1,000. Reserving 10
retained 1,750 to 3,262, median 2,504; all 1,000 retained at least 1,000. These are
sampled outcomes, not exhaustive bounds. The fixed candidates were not selected
using answer scores or the best search result.

Recommendation: use the 10-history dev candidate as the starting point for trace
quality review. Its 2,428 training updates leave more room for filtering, but only
762 currently have no target warnings. Warnings are heuristics, not verified bad
labels. Neither candidate establishes 1,000 quality-approved examples yet.

Ten dev histories mean only ten independent history-level evaluation units, even
though they contain 478 extraction updates. No independent final LongMemEval set
is reserved here. Discarded histories can still overlap dev and are not a clean
pool for final evaluation. LoCoMo and BEAM assignments were not changed.

Reproduce with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python check_split_feasibility.py`.
Local candidate IDs, update pointers, source hashes and diagnostic trials summary:
`work/longmemeval_split_feasibility/`. The original audit files remain unchanged.

Verification: 22 offline tests passed; saved partitions and script/source hashes
verified; zero exact-session overlap asserted for both candidates. Semantic
near-duplicates and factual quality are not reviewed. No API calls, training,
commit or push.
