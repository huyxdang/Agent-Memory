# Extractor audit and human review, 2026-09-13

This is an exploratory audit, not a validated extractor metric or training reward. The original benchmark results remain unchanged.

## Matched comparisons

Coverage uses preserved=1, partial=0.5, absent/contradicted=0, averaged within questions and then across questions. Questions without a usable source checklist are excluded and counted, not scored as extractor failures.

| Cohort | Model | Usable paired questions | Proposed coverage | Existing downstream rubric mean on the same subset |
|---|---|---:|---:|---:|
| Dev | Gemma base | 11 | 22.16% | 14.14% |
| Dev | Gemma fine-tuned | 11 | 27.27% | 18.18% |
| Historical reference | Gemma base | 8 | 12.15% | 21.53% |
| Historical reference | Luna | 8 | 82.99% | 77.78% |

These are different cohorts, not a three-way same-data ranking. Selection began with 20 questions in each cohort, across four histories each and five question types. No matched Luna dev traces were available.

All 80 candidate outcomes were recorded once: 38 scored and 42 explicitly excluded, covering 19 usable and 21 excluded questions. No missing or duplicate outcomes.

The separate faithfulness sample covered 160 memory lines and 268 claims. Twelve supported-label/error-tag conflicts and additional AI-review disagreements remain. Its rates are not calibrated hallucination rates.

## Controls, usage and limits

- Current coverage controls: 8/8; faithfulness: 5/5; source acceptance/rejection: 2/2; premise-only dates: 1/1.
- An earlier verifier stress test remains 2/3. The calculated-duration case failed; this failure was preserved.
- Judge: gpt-5.6-luna, reasoning none. 180 calls including rejected iterations.
- Input: 25,046,834 tokens. Output: 87,794 tokens. Reasoning: 0 reported.
- Conservative upper-accounted cost: $12.681446 of the authorized $20. This is not the provider invoice.
- No unknown usage, unknown outcomes or reserved exposure remained.
- First-to-last-call horizon: 1,257.35 seconds, including inspection gaps. Summed call durations are not wall time.
- Completed audit resume was tested offline with API dispatch forbidden: zero new requests and identical outcomes.

## AI first pass, then human review

The user chose AI preparation followed by human approval. The review packet covers ten dev questions, two per type across all four histories, with 20 anonymous memories and 28 proposed facts.

Six cases need a checklist or grading-rule decision; four are simpler spot-checks. Eight have saved AI coverage results and two preserve checklist exclusions. Every human decision remains pending.

The AI pass reviewed checklists and cited evidence with targeted source/memory checks, not every claim in every complete history. It flags speaker attribution, plans versus completed actions, target versus achieved values, and discussion order versus event dates. Evidence links are not proof of entailment.

The offline tools in `tools/extractor_review/` produce the packet and verify artifact integrity. They keep human decisions separate and preserve edits on rerun. Raw histories, memories, model answers, per-question grades and human review notes are intentionally not committed.

## Next experiment

Approve or repair the dev rubric first. Use confirmed error categories to review and repair separate training histories. Do not copy these dev examples into training. Compare a controlled SFT run with the base and previous checkpoint under fixed inference settings; retain coverage, faithfulness, format, size and downstream accuracy as separate measures. Repeatedly inspected historical test sets are historical comparisons, not fresh held-out evidence.

## Publication checks

The published tools were run against a disposable copy of the saved local audit: 10 cases, 20 candidate outcomes, 28 source citations, 30 memory citations, 20 recomputed token counts and 51 valid local links. Thirty input hashes were unchanged. A repeated build was byte-identical and preserved a simulated human edit. Both CLI help commands passed. No paid calls were made.

The clean-worktree repository suite ran 118 tests with 21 errors because local dataset fixtures were absent and dataset downloads could not resolve the network host. It is not reported as a passing full suite. The initial pytest command was unavailable; the repository's documented runner is unittest. No unrelated runtime code was changed to work around these conditions.
