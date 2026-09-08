# LongMemEval five-question results

- Run ID: `20260908T080034843663Z_full-history_d581a9b`
- System: `full-history`
- Run status: `preflight_only`
- Retry of: `none`
- Dataset revision: `98d7416c24c778c2fee6e6f3006e7a073259d48f`
- Dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| dataset_sha256 | passed | d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442 |
| dataset_500_unique_questions | passed | validated while loading |
| five_fixed_unique_ids | passed | question_ids.json |
| complete_history_and_no_labels | passed | validated while building every answer prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | 110325 | 110400 | 1024 | 256 | 1050000 | 938320 | True |
| 8a2466db | 111417 | 111499 | 1024 | 256 | 1050000 | 937221 | True |
| 0a995998 | 111429 | 111514 | 1024 | 256 | 1050000 | 937206 | True |
| gpt4_59149c77 | 108763 | 108864 | 1024 | 256 | 1050000 | 939856 | True |
| 6a1eabeb | 109643 | 109725 | 1024 | 256 | 1050000 | 938995 | True |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |

- Reported system cost (judge excluded): `0.0`
- Total API spend (judge included): `0.0`

## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| e47becba | single-session-user | What degree did I graduate with? | Business Administration | NOT RUN | NOT RUN | NOT RUN | not_run |
| 8a2466db | single-session-preference | Can you recommend some resources where I can learn more about video editing? | The user would prefer responses that suggest resources specifically tailored to Adobe Premiere Pro, especially those that delve into its advanced settings. They might not prefer general video editing resources or resources related to other video editing software. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 0a995998 | multi-session | How many items of clothing do I need to pick up or return from a store? | 3 | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_59149c77 | temporal-reasoning | How many days passed between my visit to the Museum of Modern Art (MoMA) and the 'Ancient Civilizations' exhibit at the Metropolitan Museum of Art? | 7 days. 8 days (including the last day) is also acceptable. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6a1eabeb | knowledge-update | What was my personal best time in the charity 5K run? | 25 minutes and 50 seconds (or 25:50) | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 8a2466db | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0a995998 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59149c77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 8a2466db | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0a995998 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59149c77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
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

- All five questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'e47becba', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '8a2466db', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0a995998', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_59149c77', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6a1eabeb', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `0.59733563`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
