# LongMemEval five-question results

- Run ID: `20260908T221159879763Z_mem0_753dd29`
- System: `mem0`
- Run status: `complete_with_failures`
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
| selected_ids_unique | passed | question_ids_852ce960.json: 1 questions |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| 852ce960 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 1000256 | 30446 | 10575 | 19871 | 0.09278676 | 520.9989 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 9140 | 1864 | 1728 | 136 | 0.020561 | 31.7629 |

- Reported system cost (judge excluded): `0.09278676`
- Total API spend (judge included): `0.11334776`

## Memory stores

### 852ce960

- Sessions written: 20 of 39
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 49790 | 45654 | 1133 | 498 | NOT RUN | 0.00313066 | 25.7024 |
| 2 | 56414 | 45654 | 1609 | 531 | NOT RUN | 0.00507844 | 26.8099 |
| 3 | 57251 | 45654 | 1953 | 779 | NOT RUN | 0.00566328 | 32.639 |
| 4 | 57200 | 45654 | 1585 | 618 | NOT RUN | 0.005223 | 31.1144 |
| 5 | 57479 | 45654 | 1771 | 582 | NOT RUN | 0.00551154 | 28.5033 |
| 6 | 37004 | 30436 | 988 | 291 | NOT RUN | 0.00315104 | 17.9757 |
| 7 | 57473 | 38045 | 2333 | 629 | NOT RUN | 0.00754896 | 34.0951 |
| 8 | 64057 | 53263 | 1929 | 703 | NOT RUN | 0.00559974 | 33.2529 |
| 9 | 13812 | 7609 | 440 | 124 | NOT RUN | 0.00202556 | 6.3416 |
| 10 | 56418 | 45654 | 1720 | 707 | NOT RUN | 0.00520954 | 28.3177 |
| 11 | 46543 | 38045 | 2272 | 410 | NOT RUN | 0.00525394 | 27.7596 |
| 12 | 63016 | 53263 | 1338 | 544 | NOT RUN | 0.00466308 | 26.0688 |
| 13 | 57172 | 45654 | 2058 | 484 | NOT RUN | 0.00578332 | 32.0432 |
| 14 | 57426 | 45654 | 2268 | 717 | NOT RUN | 0.00608986 | 32.6647 |
| 15 | 46016 | 38045 | 1202 | 566 | NOT RUN | 0.00384072 | 24.5566 |
| 16 | 63577 | 53263 | 1484 | 721 | NOT RUN | 0.00495246 | 29.9367 |
| 17 | 56945 | 45654 | 1643 | 624 | NOT RUN | 0.00521956 | 29.7112 |
| 18 | 37007 | 30436 | 829 | 307 | NOT RUN | 0.0029467 | 17.9357 |
| 19 | 9201 | 7609 | 244 | 96 | NOT RUN | 0.00077218 | 4.5111 |
| 20 | 56455 | 45654 | 1647 | 644 | NOT RUN | 0.00512318 | 31.0593 |
| 21 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |


## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| 852ce960 | knowledge-update | What was the amount I was pre-approved for when I got my mortgage from Wells Fargo? | $400,000 | NOT RUN | NOT RUN | NOT RUN | extraction_api_error |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| 852ce960 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| 852ce960 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:known_correct | 1510 | 330 | 320 | 10 | 0.0036035 | 8.0742 | gpt-5-2025-08-07 |
| validation:e47becba:correct_paraphrase | 1516 | 202 | 192 | 10 | 0.002331 | 4.0977 | gpt-5-2025-08-07 |
| validation:e47becba:clearly_wrong | 1515 | 330 | 320 | 10 | 0.00360975 | 5.1897 | gpt-5-2025-08-07 |
| validation:6a1eabeb:known_correct | 1533 | 266 | 256 | 10 | 0.00299225 | 3.9552 | gpt-5-2025-08-07 |
| validation:6a1eabeb:correct_paraphrase | 1533 | 534 | 448 | 86 | 0.00567225 | 6.7372 | gpt-5-2025-08-07 |
| validation:6a1eabeb:clearly_wrong | 1533 | 202 | 192 | 10 | 0.00235225 | 3.7089 | gpt-5-2025-08-07 |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|
| e47becba:known_correct | Business Administration | yes | yes | True | success |  |
| e47becba:correct_paraphrase | I graduated with a degree in Business Administration. | yes | yes | True | success |  |
| e47becba:clearly_wrong | I graduated with a Computer Science degree. | no | no | True | success |  |
| 6a1eabeb:known_correct | 25 minutes and 50 seconds | yes | yes | True | success |  |
| 6a1eabeb:correct_paraphrase | My best was 25:50. | yes | yes | True | success |  |
| 6a1eabeb:clearly_wrong | My personal best was 31 minutes. | no | no | True | success |  |

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': '852ce960', 'status': 'extraction_api_error', 'detail': "Session 21 LLMError: LLM extraction failed: Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-5.6-luna in organization org-j4LMInT9tBdrua7ISYaTApRE on tokens per min (TPM): Limit 2000000, Used 2000000, Requested 10489. Please try again in 314ms. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}"}]`
- Projected maximum cost: `1.08919414`
- Reported system cost, excluding judge: `0.09278676`
- Internal judging cost: `0.020561`
- Total API spend: `0.11334776`
