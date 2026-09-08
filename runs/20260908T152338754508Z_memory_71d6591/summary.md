# LongMemEval five-question results

- Run ID: `20260908T152338754508Z_memory_71d6591`
- System: `memory`
- Run status: `blocked_missing_paid_config`
- Retry of: `none`
- Dataset revision: `98d7416c24c778c2fee6e6f3006e7a073259d48f`
- Dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| fixture_sha256 | passed | memory_smoke_test.json abfef225e8eb89071582009f45a0e613acead2648ffc25495355a166efae9da0 |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | checked when the memory prompt is built |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |

- Reported system cost (judge excluded): `0.0`
- Total API spend (judge included): `0.0`

## Memory stores

### 6a1eabeb

- Sessions written: 0 of 8
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|


## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| 6a1eabeb | knowledge-update | What was my personal best time in the charity 5K run? | 25 minutes and 50 seconds (or 25:50) | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:known_correct | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:correct_paraphrase | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:clearly_wrong | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:known_correct | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:correct_paraphrase | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:clearly_wrong | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|
| e47becba:known_correct | Business Administration | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| e47becba:correct_paraphrase | I graduated with a degree in Business Administration. | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| e47becba:clearly_wrong | I graduated with a Computer Science degree. | no | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:known_correct | 25 minutes and 50 seconds | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:correct_paraphrase | My best was 25:50. | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:clearly_wrong | My personal best was 31 minutes. | no | NOT RUN | NOT RUN | not_run | No paid API call was made. |

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': '6a1eabeb', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `1.56776614`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
