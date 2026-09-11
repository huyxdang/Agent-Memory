# Teacher trace quality spot-check

Reviewed eight training updates from the fixed 10-history-dev candidate. Two
examples each were selected from disjoint warning groups, with eight different
histories. Seed: `trace-quality-review-v1-20260910`. No dev examples, benchmark
answers, new API calls or training were used.

The 2,428-update training population has 1,630 value-only warning examples,
29 date/number warning examples, 7 memory-update warning examples and 762
unflagged examples. Groups use priority update > date/number > value > unflagged.
This intentionally oversamples rare warnings. It is not a prevalence estimate.

## Findings

| Review | Warning group | Finding | Disposition |
|---|---|---|---|
| R01 | Memory update | Supported new fact, but a reused key drops its previous-value chain; joined lists also cause string warnings. | Repair update semantics. |
| R02 | Memory update | Liking a game becomes completing it; assistant descriptions become user preferences; previous value is dropped. | Repair factual attribution and update semantics. |
| R03 | Date/number | Resolving last year is supported, but tentative recollection and a contemplated choice become firmer claims. | Keep normalized date, restore uncertainty. |
| R04 | Date/number | Port mapping numbers are supported despite changed notation; protocol label is inferred rather than stated. | Neutral key and explicit formatting policy. |
| R05 | Value | Joined recommendation lists are supported; exact-string warning is misleading. Some earlier recommendations are omitted. | Retain for further review; coverage is not certified. |
| R06 | Value | Paraphrased facts and visit date are supported; future date remains an offset rather than an approximate absolute month. | Format repair, not rejection as invented content. |
| R07 | Unflagged | Narrative accurately summarizes the request and response in the inspected session. | No material issue found in reviewed scope. |
| R08 | Unflagged | Assistant-proposed actions become the user's endorsed positions. Narrative-only output evades atomic checks. | Repair speaker attribution. |

## What this changes

Do not use `has warning` as an automatic discard rule, or `no warning` as an
approval rule. The current check primarily compares strings and numeric anchors
and checks update tails; it does not establish semantic support, speaker
attribution, preserved uncertainty, or narrative quality.

Keep three separate review dimensions:

1. Source faithfulness: support, speaker, event, uncertainty and date correctness.
2. Extractor contract: key identity, update chains, date/value formatting.
3. Coverage and size: missing useful facts and unnecessary length.

An assistant statement in the source can be retained as something the assistant
said without claiming it is true in the real world. This review did not browse to
verify historical recommendations or general-knowledge claims.

The next data-preparation step should repair or exclude demonstrated defects,
then review a broader training-only sample before choosing the quality gate.
Fixing only the warning detector would not fix the factual or attribution errors
in the teacher targets. Changing the prompt contract should be an explicit
separate decision, not a way to make old targets pass.

No detector thresholds, original targets, split assignments or training-row
filters were changed. We still cannot claim 1,000 quality-approved examples.

## Evidence and reproduction

`sample_trace_review.py` rebuilds the same diagnostic sample from saved pointers.
Local, gitignored `work/trace_quality_review/` contains `sample.json`, eight source
packets and `review_annotations.json`, with source/target excerpts and proposed
actions. Original run IDs, sessions and hashes remain attached.

This is a Codex assistant qualitative review, not independent human annotation or
an API judge score. Each current session and target was read in full, alongside
prior same-key lines. Targeted prior-memory keyword checks were added for R02 and
R08. Entire preceding source histories were not manually reread; global
contradictions, exhaustive coverage and inherited memory quality remain unverified.

Checks passed: 23 offline tests; eight distinct training histories; sample and
input hashes; one annotation per sample; literal source/target evidence presence;
whitespace validation. These mechanical checks do not validate the reviewer's
semantic judgments. No API spend, training, commit or push.
