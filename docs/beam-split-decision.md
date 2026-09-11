# BEAM train, dev and final split decision

Approved by the user on 2026-09-11. This is the authoritative split decision and supersedes the earlier six-history and eight-history training proposals, the two-conversation 100K final proposal, and the proposal to expand 100K final to all available questions.

| Purpose | BEAM 100K | BEAM 500K | Use |
|---|---|---|---|
| Train | 8 new conversations | 8 new conversations | Generate teacher traces for extractor fine-tuning and synthetic-data seeds |
| Dev | 2 other new conversations | 2 other new conversations | Choose checkpoints and settings using downstream question accuracy |
| Final | All 5 existing conversations, original 50 questions | Both existing conversations, original 40 questions | Compare frozen models with the existing baselines |

Train and dev use new histories, not the existing evaluation histories. They must not overlap each other or final, including shared source windows or message pairs. Keep every conversation's updates together. Do not use dev/final histories, memories, traces, questions or answers for training or synthetic generation.

## Exact BEAM final selections

- 100K: conversation IDs 1, 4, 6, 13 and 16. Use the exact 50 question IDs in `question_ids_beam_50.json`, ten previously evaluated questions per conversation.
- 500K: conversation IDs 1 and 13. Use the exact 40 question IDs in `question_ids_beam_500k_40.json`, twenty questions per conversation.
- Total: seven conversations and 90 questions. Scale is part of the conversation identity; equal numeric IDs across tiers do not establish identical histories.
- Do not select only two 100K conversations. Do not add the other ten available questions per 100K conversation. The original question sets are intentional, to preserve comparability with Mem0 and other saved baselines.

These are previously inspected evaluation sets, held out from the new training/dev data, not untouched tests. Use identical questions across the new model arms. Record differences from historical runs, including shared-memory reuse, rather than claiming a fully controlled historical comparison.

Each Qwen arm builds its own memory once per conversation, then answers that conversation's selected questions from the completed memory. Saved GPT memories are historical reference artifacts, not inputs to Qwen extractor evaluation. Keep the existing eight-pair extraction boundaries and no question-based retrieval.

LongMemEval and LoCoMo remain additional final evaluations at the previously intended 100 and 50 questions respectively. This decision does not select new IDs for those benchmarks or certify their overlap checks. Their data must also remain outside training and tuning.

## Implementation status

The active sixteen-history train, four-history dev and original ninety-question BEAM final manifests are saved under `work/beam_split_v2/`. See [the rebalanced split](beam-split-rebalanced.md) for exact IDs, counts and limitations. The earlier `work/beam_split/` and candidate directories are preserved historical checkpoints, not the active split. No teacher traces have been generated for the new split.

Next: budget the full three-arm inference workload, verify available credits, then generate and review teacher traces from the frozen training manifest before fitting models. The Modal cap remains $30 total; other provider spending remains bounded by verified available credits under the experiment plan. Do not silently reduce final questions to fit the budget.
