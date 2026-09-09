# LongMemEval five-question results

- Run ID: `20260909T005041106821Z_mem0_e2ba6d1`
- System: `mem0`
- Run status: `running`
- Retry of: `none`
- Dataset revision: `locomo`
- Dataset SHA-256: `see sources in manifest`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| source_files_recorded | passed | locomo: 1 files hashed in metadata |
| selected_ids_unique | passed | question_ids_locomo_rerun.json: 2 questions |
| mem0_locomo_judge_prompts_exact | passed | 8ebac1ef60e9ab5caf99079fdaac038b85472e81491ed35e2d2655f3927c76c2 |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |

- Reported system cost (judge excluded): `0.0`
- Total API spend (judge included): `0.0`

## Memory stores

### locomo0_q82

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q15

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|


## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| locomo0_q82 | single-hop | What did the charity race raise awareness for? | mental health | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q15 | single-hop | What pets does Jolene have? | snakes | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'locomo0_q82', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q15', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `2.51177913`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
