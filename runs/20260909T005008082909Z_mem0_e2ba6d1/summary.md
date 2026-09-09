# LongMemEval five-question results

- Run ID: `20260909T005008082909Z_mem0_e2ba6d1`
- System: `mem0`
- Run status: `running`
- Retry of: `none`
- Dataset revision: `beam`
- Dataset SHA-256: `see sources in manifest`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| source_files_recorded | passed | beam: 16 files hashed in metadata |
| selected_ids_unique | passed | question_ids_beam_50.json: 50 questions |
| mem0_beam_judge_prompts_exact | passed | a1c2a4822898411f90ab2915a72d2b2031f97437bdcc1b3ac2008fe93653267b |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 3817722 | 157830 | 50542 | 107288 | 0.45049726 | 2229.7318 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |

- Reported system cost (judge excluded): `0.45049726`
- Total API spend (judge included): `0.45049726`

## Memory stores

### beam100K_1_abstention_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90460 | 69074 | 3799 | 1106 | NOT RUN | 0.01051194 | 51.9483 |
| 2 | 91663 | 68481 | 4352 | 1282 | NOT RUN | 0.01147506 | 54.8634 |
| 3 | 91610 | 68481 | 3972 | 1295 | NOT RUN | 0.01101054 | 55.4532 |
| 4 | 29619 | 22827 | 1116 | 470 | NOT RUN | 0.00321494 | 17.1705 |
| 5 | 92149 | 68481 | 3591 | 1447 | NOT RUN | 0.01066014 | 53.5434 |
| 6 | 81342 | 60872 | 2892 | 892 | NOT RUN | 0.0089965 | 44.1716 |

### beam100K_1_contradiction_resolution_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90774 | 68481 | 3904 | 1217 | NOT RUN | 0.01080736 | 56.2909 |
| 2 | 91761 | 68481 | 4449 | 1072 | NOT RUN | 0.01161692 | 56.2284 |
| 3 | 91835 | 68481 | 3880 | 1047 | NOT RUN | 0.01094776 | 54.6591 |
| 4 | 29548 | 22827 | 1237 | 315 | NOT RUN | 0.0033502 | 17.2367 |
| 5 | 92519 | 68481 | 3760 | 1283 | NOT RUN | 0.01094256 | 59.5128 |
| 6 | 81680 | 60872 | 3044 | 1076 | NOT RUN | 0.00924744 | 43.0137 |

### beam100K_1_event_ordering_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90604 | 69074 | 3661 | 1238 | NOT RUN | 0.01037184 | 54.0755 |
| 2 | 92113 | 68481 | 4133 | 1282 | NOT RUN | 0.01130148 | 54.8413 |
| 3 | 92385 | 68481 | 4068 | 1331 | NOT RUN | 0.01128178 | 52.1216 |
| 4 | 29649 | 22827 | 1062 | 325 | NOT RUN | 0.00315682 | 14.8155 |
| 5 | 92734 | 68481 | 3702 | 1144 | NOT RUN | 0.01091666 | 52.6927 |
| 6 | 81770 | 60872 | 3074 | 850 | NOT RUN | 0.00930422 | 48.4094 |

### beam100K_1_information_extraction_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90599 | 69074 | 3628 | 1077 | NOT RUN | 0.01033292 | 49.0739 |
| 2 | 91553 | 68481 | 4146 | 1420 | NOT RUN | 0.01120256 | 55.0779 |
| 3 | 91559 | 68481 | 3703 | 1256 | NOT RUN | 0.01067444 | 50.6154 |
| 4 | 29522 | 22827 | 1324 | 485 | NOT RUN | 0.00344814 | 19.8916 |
| 5 | 91985 | 68481 | 3566 | 1354 | NOT RUN | 0.01059808 | 50.7573 |
| 6 | 81448 | 60872 | 3051 | 980 | NOT RUN | 0.00921074 | 46.7375 |

### beam100K_1_instruction_following_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90554 | 69074 | 3838 | 1155 | NOT RUN | 0.01057686 | 52.2721 |
| 2 | 91278 | 68481 | 3934 | 987 | NOT RUN | 0.01089446 | 50.2086 |
| 3 | 91289 | 68481 | 3622 | 1149 | NOT RUN | 0.01052308 | 54.4517 |
| 4 | 29459 | 22827 | 1167 | 422 | NOT RUN | 0.0032462 | 19.0846 |
| 5 | 91590 | 68481 | 3492 | 1169 | NOT RUN | 0.01043182 | 53.3673 |
| 6 | 81110 | 60872 | 3314 | 1124 | NOT RUN | 0.00945916 | 53.7002 |

### beam100K_1_knowledge_update_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90627 | 69074 | 3881 | 1118 | NOT RUN | 0.01064466 | 55.4307 |
| 2 | 91508 | 68481 | 4314 | 1228 | NOT RUN | 0.01140056 | 55.0584 |
| 3 | 92020 | 68481 | 4345 | 1302 | NOT RUN | 0.01154566 | 56.2628 |
| 4 | 29663 | 22827 | 1171 | 343 | NOT RUN | 0.00329228 | 17.9612 |
| 5 | 92369 | 68481 | 3554 | 1269 | NOT RUN | 0.01066172 | 53.8906 |
| 6 | 81652 | 60872 | 3215 | 969 | NOT RUN | 0.00945 | 49.5928 |

### beam100K_1_multi_session_reasoning_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90363 | 61465 | 3867 | 1180 | NOT RUN | 0.01194338 | 56.0022 |
| 2 | 91423 | 68481 | 3884 | 1064 | NOT RUN | 0.0108634 | 51.8026 |
| 3 | 91802 | 68481 | 4430 | 1612 | NOT RUN | 0.01160062 | 55.0773 |
| 4 | 29530 | 22827 | 1135 | 476 | NOT RUN | 0.00322024 | 16.3119 |
| 5 | 92035 | 68481 | 3274 | 1293 | NOT RUN | 0.0102544 | 52.4288 |
| 6 | 81506 | 60872 | 3342 | 1190 | NOT RUN | 0.00957212 | 47.9816 |

### beam100K_1_preference_following_0

- Sessions written: 6 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 90451 | 61465 | 3451 | 1152 | NOT RUN | 0.01145598 | 49.8876 |
| 2 | 91596 | 68481 | 4167 | 1213 | NOT RUN | 0.0112394 | 53.6365 |
| 3 | 91672 | 68481 | 3682 | 1095 | NOT RUN | 0.01067426 | 49.6949 |
| 4 | 29467 | 22827 | 1162 | 512 | NOT RUN | 0.00323984 | 15.6544 |
| 5 | 92380 | 68481 | 3407 | 1203 | NOT RUN | 0.01048658 | 51.1526 |
| 6 | 81497 | 60872 | 3068 | 1073 | NOT RUN | 0.00923954 | 45.6188 |

### beam100K_1_summarization_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_1_temporal_reasoning_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_abstention_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_contradiction_resolution_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_event_ordering_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_information_extraction_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_instruction_following_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_knowledge_update_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_multi_session_reasoning_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_preference_following_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_summarization_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_4_temporal_reasoning_0

- Sessions written: 0 of 12
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_abstention_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_contradiction_resolution_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_event_ordering_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_information_extraction_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_instruction_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_knowledge_update_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_multi_session_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_preference_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_summarization_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_6_temporal_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_abstention_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_contradiction_resolution_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_event_ordering_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_information_extraction_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_instruction_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_knowledge_update_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_multi_session_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_preference_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_summarization_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_13_temporal_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_abstention_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_contradiction_resolution_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_event_ordering_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_information_extraction_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_instruction_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_knowledge_update_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_multi_session_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_preference_following_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_summarization_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### beam100K_16_temporal_reasoning_0

- Sessions written: 0 of 15
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|


## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| beam100K_1_abstention_0 | abstention | How did the user feedback influence the UI/UX improvements I made before the public launch? | Based on the provided chat, there is no information related to how user feedback influenced UI/UX improvements. | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_contradiction_resolution_0 | contradiction_resolution | Have I worked with Flask routes and handled HTTP requests in this project? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of developing my personal budget tracker throughout our conversations, in order? Mention ONLY and ONLY three items. |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_information_extraction_0 | information_extraction | When does my first sprint end? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_instruction_following_0 | instruction_following | Could you show me how to implement a login feature? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_knowledge_update_0 | knowledge_update | What is the average response time of the dashboard API? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_multi_session_reasoning_0 | multi_session_reasoning | How many new columns did I want to add to the transactions table across my requests? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_preference_following_0 | preference_following | I'm planning to add user login, income and expense tracking, and some basic analytics to my Flask app. What libraries or tools would you suggest I use to implement these features? |  | NOT RUN | NOT RUN | NOT RUN | memory_in_progress |
| beam100K_1_summarization_0 | summarization | Can you provide a comprehensive summary of how my budget tracker project has progressed, including the key features implemented, the development timeline, security enhancements, and documentation efforts? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_temporal_reasoning_0 | temporal_reasoning | How many weeks do I have between finishing the transaction management features and the final deployment deadline? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_abstention_0 | abstention | What specific criteria did I consider when choosing between angle-based or side-based classification strategies? | Based on the provided chat, there is no information related to the specific criteria considered for choosing classification strategies. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_contradiction_resolution_0 | contradiction_resolution | Have I ever worked on triangle classification problems before? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of classifying triangles throughout our conversations, including how I first approached understanding their types, then moved on to calculating areas, identifying key characteristics, comparing types, and finally applying these concepts to more complex problems, in order? Mention ONLY and ONLY nine items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_information_extraction_0 | information_extraction | What approach did I outline to demonstrate that two triangles with matching angle pairs and a connecting segment are identical, and how did I organize the information to support this? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_instruction_following_0 | instruction_following | How can I find the area of a triangle using medians and altitudes? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_knowledge_update_0 | knowledge_update | What is my accuracy percentage in solving area calculation problems after completing 15 problems? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_multi_session_reasoning_0 | multi_session_reasoning | How many triangle classification problems have I completed in total across all sessions where I mentioned my progress? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_preference_following_0 | preference_following | Can you show me how to calculate the area of this triangle using different methods and also help me find the length of the median? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_summarization_0 | summarization | Can you give me a clear summary of everything we've covered about triangles, including how to verify right angles, calculate areas, and understand medians? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_temporal_reasoning_0 | temporal_reasoning | Which improvement happened first: my quiz score increasing from 65% to 82% after focusing on triangle side classifications, or my test score rising from 80% to 92% on congruence proofs and similarity calculations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_abstention_0 | abstention | What specific advice did Bryan give about updating the LinkedIn profile in April 2024? | Based on the provided chat, there is no information related to the specific advice Bryan gave about updating the LinkedIn profile. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_contradiction_resolution_0 | contradiction_resolution | Have I ever enrolled in any courses or training programs on ATS optimization? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of improving my professional profile and resume throughout our conversations in order? Mention ONLY and ONLY six items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_information_extraction_0 | information_extraction | How much does my subscription to the service I’m using for my resume cost each month? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_instruction_following_0 | instruction_following | How should I organize the information about my past jobs? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_knowledge_update_0 | knowledge_update | How many interviews have I secured for executive producer roles during the recent period? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_multi_session_reasoning_0 | multi_session_reasoning | How many different areas have I focused on updating or improving based on my messages about my resume, portfolio, and salary negotiation? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_preference_following_0 | preference_following | I'm updating my portfolio and want to include some samples. What types of content would you suggest I add? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_summarization_0 | summarization | Can you give me a summary of how I worked on improving my resume and job application strategy over time? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_temporal_reasoning_0 | temporal_reasoning | How many days do I have between the deadline to tailor my resume for film, television, and digital media and the date I want to be ready to apply confidently for executive producer roles? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_abstention_0 | abstention | What was the atmosphere like during the February 20 book club discussion on 'The Poppy War' hosted by Kelly and I? | Based on the provided chat, there is no information related to the atmosphere during the February 20 book club discussion on 'The Poppy War'. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_contradiction_resolution_0 | contradiction_resolution | Have I ever met Kelly at any book club or library event? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of my book club activities throughout our conversations in order? Mention ONLY and ONLY five items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_information_extraction_0 | information_extraction | How many series did I say were on my reading list, and what was the total page count? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_instruction_following_0 | instruction_following | Can you suggest some good audiobooks for me to listen to? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_knowledge_update_0 | knowledge_update | How many books am I aiming to read in my winter reading challenge? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_multi_session_reasoning_0 | multi_session_reasoning | How many different book series or genres have I mentioned wanting to explore across my conversations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_preference_following_0 | preference_following | I'm looking to add some new books to my collection and also want something easy to carry around. What would you suggest? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_summarization_0 | summarization | Can you summarize how my reading goals and strategies have developed over time based on our conversations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_temporal_reasoning_0 | temporal_reasoning | How many days did it take me to finish reading the trilogy after I downloaded it? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_abstention_0 | abstention | What are Alexis’s specific plans and strategies for launching the freelance design business in January 2025? | Based on the provided chat, there is no information related to Alexis’s specific plans or strategies for launching the freelance design business. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_contradiction_resolution_0 | contradiction_resolution | Have U been using Excel to track my daily expenses? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_event_ordering_0 | event_ordering | Can you walk me through the order in which I brought up different financial planning topics during our chats, in order? Mention ONLY and ONLY four items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_information_extraction_0 | information_extraction | What monthly amount did I say I’m currently paying for my place on Bay Street? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_instruction_following_0 | instruction_following | How much am I allowed to spend on my holiday plans? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_knowledge_update_0 | knowledge_update | What is the monthly grocery budget Alexis and I have agreed on? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_multi_session_reasoning_0 | multi_session_reasoning | How much money had I saved in total by the time I reached 60% of my emergency fund goal? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_preference_following_0 | preference_following | I want to set up a system to track my monthly expenses and stick to a dining out budget of $200 starting next month. How would you suggest I organize this? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_summarization_0 | summarization | Can you summarize how my approach to managing finances with Alexis has developed over time? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_temporal_reasoning_0 | temporal_reasoning | How many days had I been tracking my daily expenses before I felt frustrated enough to consider stopping? |  | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'beam100K_1_abstention_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_contradiction_resolution_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_event_ordering_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_information_extraction_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_instruction_following_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_knowledge_update_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_multi_session_reasoning_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_preference_following_0', 'status': 'memory_in_progress', 'detail': ''}, {'question_id': 'beam100K_1_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `28.58119927`
- Reported system cost, excluding judge: `0.45049726`
- Internal judging cost: `0.0`
- Total API spend: `0.45049726`
