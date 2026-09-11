# Published LongMemEval split audit

Audited 2026-09-11. No split adopted, training exports changed, or paid calls made.

## Result

Neither repository supplies a verified replacement for our session-disjoint split. BudgetMem publishes row indices without the processed data needed to identify the corresponding questions. LazyMem documents its split but does not include the IDs.

| Source | Published train / dev / test | What we verified | What remains unverified |
|---|---|---|---|
| BudgetMem | 297 / 98 / 105 indices | All indices 0 through 499 occur exactly once. The training loader merges train and val, giving 395 training indices. | Mapping to original question IDs, exact cross-partition session counts, and the authors' actual processed input exposure. |
| LazyMem | 360 / 40 / 100 questions, seed 42 | README protocol; train/val/test ID files absent from the checked revision. No split-generation code found in tracked source. | Actual IDs and exact cross-partition session counts. Seed and sizes alone do not uniquely reproduce the split. |

Pinned sources:

- [BudgetMem split file](https://github.com/ViktorAxelsen/BudgetMem/blob/91c17435f3b7634711a22fe9cb303ec15069a7aa/data/longmemeval_s_splits.json).
- [BudgetMem loader, lines 1539 onward](https://github.com/ViktorAxelsen/BudgetMem/blob/91c17435f3b7634711a22fe9cb303ec15069a7aa/train/train_longmemeval.py#L1539). It indexes `longmemeval_s.json`, whose records use `sample_id` and `qa`. That processed dataset is absent. We did not apply its indices to our cleaned JSON and pretend the ordering was verified.
- [LazyMem data protocol](https://github.com/allacnobug/LazyMem/blob/af4109960aacb90d6dba994e9103a36a165cc380/README.md#L205). The repository ignores `data/`, including its split files.

## What the complete dataset proves independently

We connected two histories whenever they share an exact session. We then counted connected groups, including indirect connections such as A sharing with B and B sharing with C.

| Matching method | Histories checked | Connected groups | Largest group | Distinct sessions found in multiple histories |
|---|---:|---:|---:|---:|
| Exact role/content sequence | 500 | 1 | 500 | 4,366 |
| Dataset session ID | 500 | 1 | 500 | 3,932 |

The text check found 18,464 distinct sessions overall. It strips evaluation annotations and ignores timestamps, using the same sanitized role/content fields as our extraction pipeline. It does not alter whitespace or detect paraphrases. Session IDs provide a separate corroborating check, with 19,195 distinct IDs overall.

Because all histories belong to one connected group, **any partition using all 500 complete histories in two or more nonempty sets must have at least one shared session across sets**. Otherwise each connected group could only belong to one set.

This does not mean every pair shares a session. It also does not show that either paper trained on held-out answers. Shared background sessions are different from shared answer evidence, and the authors may train on selected windows rather than complete histories. Our concern is the stricter requirement for our question-blind, full-history extractor.

## Implication for our experiment

Adopting a published question-level split does not remove the need for our source-session audit. To retain zero exact-session overlap, we must exclude enough overlapping whole histories, or obtain new source conversations. If we instead permit shared background sessions, that is a different evaluation rule requiring an explicit decision.

The current 51-history training / 10-history dev Copy 2 remains unchanged. Final IDs remain unfrozen. This audit does not adopt the previously discussed exploratory 50-question final candidate.

## Reproduce

Use clean checkouts of the pinned revisions linked above. The script only reads those repositories; it does not execute their code, install their dependencies, or make network requests.

From this project:

```sh
.venv/bin/python audit_published_split.py \
  --budgetmem /path/to/BudgetMem \
  --lazymem /path/to/LazyMem \
  --output work/published_split_audit/report.json

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -q
```

The script requires cleaned LongMemEval-S revision `98d7416c24c778c2fee6e6f3006e7a073259d48f`, SHA-256 `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`. The saved JSON records source revisions, all tracked public-source file hashes, local code hashes, and current training/dev artifact hashes. It contains aggregate results, not benchmark answers or memory traces.

Verification: all 41 local tests passed, including three new split-audit checks. The full suite's displayed API spend is mocked test output, not paid usage. Exact author split overlap remains explicitly unverified because the required mappings are absent.
