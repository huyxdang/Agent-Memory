# LongMemEval five-question results

- Run ID: `20260909T042205080808Z_memory_5af8086`
- System: `memory`
- Run status: `blocked_spending_limit`
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
| selected_ids_unique | passed | question_ids_locomo_154.json: 154 questions |
| mem0_locomo_judge_prompts_exact | passed | 8ebac1ef60e9ab5caf99079fdaac038b85472e81491ed35e2d2655f3927c76c2 |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q19 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q61 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q62 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q17 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q39 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q63 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q25 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q40 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q91 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q64 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q33 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q41 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q92 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q49 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q43 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q94 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q58 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q44 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q95 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q59 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q45 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q96 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

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

### locomo0_q0

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q1

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q2

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q3

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q4

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q82

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q83

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q0

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q1

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q2

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q3

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q4

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q5

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q0

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q2

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q8

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q65

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q66

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q0

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q1

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q2

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q88

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q89

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q0

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q3

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q6

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q71

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q72

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q0

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q2

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q19

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q61

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q62

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q0

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q1

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q2

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q67

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q68

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q0

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q1

- Sessions written: 0 of 30
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

### locomo7_q16

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q0

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q4

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q83

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q84

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q0

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q1

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q71

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q72

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q5

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q6

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q1

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q3

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q10

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q1

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q4

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q2

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q9

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q2

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q6

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q7

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q4

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q6

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q12

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q4

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q10

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q3

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q12

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q8

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q14

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q14

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q4

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q5

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q7

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q9

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q3

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q5

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q1

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q3

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q3

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q6

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q1

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q3

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q11

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q17

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q6

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q10

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q2

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q9

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q84

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q39

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q67

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q90

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q73

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q63

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q69

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q25

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q85

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q73

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q85

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q40

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q68

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q91

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q74

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q64

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q70

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q33

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q86

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q74

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q86

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q41

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q69

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q92

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q75

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q65

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q71

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q42

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q87

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q75

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q87

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q42

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q70

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q93

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q76

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q66

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q72

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q49

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q88

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q76

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q88

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q43

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q71

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q94

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q77

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q67

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q73

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q58

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q89

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q77

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q89

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q44

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q72

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q95

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo4_q78

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo5_q68

- Sessions written: 0 of 28
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo6_q74

- Sessions written: 0 of 31
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo7_q59

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo8_q90

- Sessions written: 0 of 25
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo9_q78

- Sessions written: 0 of 30
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo0_q90

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo1_q45

- Sessions written: 0 of 19
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo2_q73

- Sessions written: 0 of 32
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|

### locomo3_q96

- Sessions written: 0 of 29
- Lines: 0; flagged lines: 0

```text
(empty)
```

| Session | Input tokens | Cached input | Output tokens (inclusive) | Reasoning subset | New lines | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|


## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| locomo0_q0 | temporal | When did Caroline go to the LGBTQ support group? | 7 May 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q1 | temporal | When did Melanie paint a sunrise? | 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q2 | open-domain | What fields would Caroline be likely to pursue in her educaton? | Psychology, counseling certification | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q3 | multi-hop | What did Caroline research? | Adoption agencies | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q4 | multi-hop | What is Caroline's identity? | Transgender woman | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q82 | single-hop | What did the charity race raise awareness for? | mental health | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q83 | single-hop | What did Melanie realize after the charity race? | self-care is important | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q0 | temporal | When Jon has lost his job as a banker? | 19 January, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q1 | temporal | When Gina has lost her job at Door Dash? | January, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q2 | single-hop | How do Jon and Gina both like to destress? | by dancing | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q3 | multi-hop | What do Jon and Gina both have in common? | They lost their jobs and decided to start their own businesses. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q4 | single-hop | Why did Jon decide to start his dance studio? | He lost his job and decided to start his own business to share his passion. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q5 | multi-hop | What Jon thinks the ideal dance studio should look like? | By the water, with natural light and Marley flooring | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q0 | temporal | Who did Maria have dinner with on May 3, 2023? | her mother | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q2 | multi-hop | What martial arts has John done? | Kickboxing, Taekwondo | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q8 | open-domain | What might John's financial status be? | Middle-class or wealthy | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q65 | single-hop | What is John's main focus in local politics? | Improving education and infrastructure | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q66 | single-hop | What sparked John's interest in improving education and infrastructure in the community? | Seeing how lack of education and crumbling infrastructure affected his neighborhood while growing up. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q0 | open-domain | Is it likely that Nate has friends besides Joanna? | Yesteammates on hisvideo game team. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q1 | multi-hop | What kind of interests do Joanna and Nate share? | Watching movies, making desserts | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q2 | temporal | When did Joanna first watch "Eternal Sunshine of the Spotless Mind? | 2019 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q88 | single-hop | What is one of Joanna's favorite movies? | "Eternal Sunshineof the Spotless Mind" | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q89 | single-hop | What color did Nate choose for his hair? | purple | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q0 | multi-hop | what are John's goals with regards to his basketball career? | improve shooting percentage, win a championship | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q3 | open-domain | Would Tim enjoy reading books by C. S. Lewis or John Greene? | C. S.Lewis | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q6 | temporal | In which month's game did John achieve a career-high score in points? | June 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q71 | single-hop | Which team did John sign with on 21 May, 2023? | The Minnesota Wolves | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q72 | single-hop | What is John's position on the team he signed with? | shooting guard | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q0 | temporal | Which year did Audrey adopt the first three of her dogs? | 2020 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q2 | multi-hop | What kind of indoor activities has Andrew pursued with his girlfriend? | boardgames, volunteering at pet shelter, wine tasting, growing flowers | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q19 | open-domain | What is an indoor activity that Andrew would enjoy doing while make his dog happy? | cook dog treats | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q61 | single-hop | Which specific type of bird mesmerizes Andrew? | Eagles | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q62 | single-hop | What did Andrew express missing about exploring nature trails with his family's dog? | The peaceful moments | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q0 | open-domain | What are John's suspected health problems? | Obesity | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q1 | temporal | Which recreational activity was James pursuing on March 16, 2022? | bowling | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q2 | multi-hop | Which places or events have John and James planned to meet at? | VR Club, McGee's, baseball game | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q67 | single-hop | What programming languages has James worked with? | Python and C++ | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q68 | single-hop | What type of mobile application does James plan to build with John? | An app for dog walking and pet care | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q0 | temporal | What kind of project was Jolene working on in the beginning of January 2023? | electricity engineering project | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q1 | multi-hop | Which of Deborah`s family and friends have passed away? | mother, father, her friend Karlie | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q15 | single-hop | What pets does Jolene have? | snakes | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q16 | single-hop | What are the names of Jolene's snakes? | Susie, Seraphim | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q0 | multi-hop | What kind of car does Evan drive? | Prius | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q4 | temporal | Which hobby did Sam take up in May 2023? | painting | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q83 | single-hop | What type of car did Evan get after his old Prius broke down? | new Prius | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q84 | single-hop | How did Evan get into watercolor painting? | friend's advice | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q0 | temporal | When did Calvin first travel to Tokyo? | between 26 March and 20 April 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q1 | multi-hop | What items did Calvin buy in March 2023? | mansion in Japan, luxury car Ferrari 488 GTB | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q71 | single-hop | How long did Calvin plan to stay in Japan? | A few months | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q72 | single-hop | Which band was Dave's favorite at the music festival in April 2023? | Aerosmith | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q5 | temporal | When did Melanie run a charity race? | The sunday before 25 May 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q6 | temporal | When is Jon's group performing at a festival? | February, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q1 | temporal | When did Maria donate her car? | 21 December 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q3 | temporal | When did Nate win his first video game tournament? | the week before 21Janury, 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q10 | temporal | When was John in Seattle for a game? | early August, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q1 | temporal | When did Andrew start his new job as a financial analyst? | The week before March 27, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q4 | temporal | When did John resume playing drums in his adulthood? | February 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q2 | temporal | When did Deborah`s mother pass away? | a few years before 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q9 | temporal | When did Evan go to Jasper with his family? | weekend before May 24, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q2 | temporal | When did Dave see Aerosmith perform live? | on the weekend before March 26, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q6 | temporal | When is Melanie planning on going camping? | June 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q7 | temporal | When did Gina launch an ad campaign for her store? | 29 January, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q4 | temporal | When did John join the online support group? | The week before 1 January 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q6 | temporal | How long has Nate had his first two turtles? | three years | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q12 | temporal | What year did John start surfing? | 2018 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q4 | temporal | When did Audrey make muffins for herself? | The week of April 3rd to 9th | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q10 | temporal | When did James adopt Ned? | first week of April 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q3 | temporal | When did Jolene`s mother pass away? | in 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q12 | temporal | When did Sam first go to the doctor and find out he had a weight problem? | A few days before May 24, 2023. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q8 | temporal | When did Dave start his car maintenance shop? | May 1, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q14 | open-domain | Would Caroline still want to pursue counseling as a career if she hadn't received support growing up? | Likely no | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q14 | open-domain | Would John be considered a patriotic person? | Yes | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q4 | open-domain | What pets wouldn't cause any discomfort to Joanna? | Hairless cats or pigs,since they don't have fur, which is one of the main causes of Joanna's allergy. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q5 | open-domain | Based on Tim's collections, what is a shop that he would enjoy visiting in New York city? | House of MinaLima | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q7 | multi-hop | What is Caroline's relationship status? | Single | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q9 | multi-hop | Which city have both Jean and John visited? | Rome | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q3 | multi-hop | What type of volunteering have John and Maria both done? | Volunteering at a homeless shelter | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q5 | multi-hop | What are Joanna's hobbies? | Writing, watchingmovies, exploringnature, hanging withfriends. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q1 | multi-hop | What are John's goals for his career that are not related to his basketball skills? | get endorsements, build his brand, do charity work | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q3 | multi-hop | What kind of places have Andrew and his girlfriend checked out around the city? | cafes, new places to eat, open space for hikes, pet shelter, wine tasting event, park | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q3 | multi-hop | Do both James and John have pets? | No | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q6 | multi-hop | What symbolic gifts do Deborah and Jolene have from their mothers? | pendants | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q1 | multi-hop | What kinds of things did Evan have broken? | His old Prius and his new Prius. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q3 | multi-hop | Which bands has Dave enjoyed listening to? | Aerosmith, The Fireworks | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q11 | multi-hop | Where did Caroline move from 4 years ago? | Sweden | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q17 | multi-hop | Why did Gina decide to start her own clothing store? | She always loved fashion trends and finding unique pieces and she lost her job so decided it was time to start her own business. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q6 | multi-hop | Where has Maria made friends? | homeless shelter, gym, church | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q10 | multi-hop | What emotions is Joanna feeling about  the screenplay she submitted? | Relief, excitement,worry, hope,anxiety. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q2 | multi-hop | What items does John collect? | sneakers, fantasy movie DVDs, jerseys | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q9 | multi-hop | What kind of classes or groups has Audrey joined to take better care of her dogs? | positive reinforcement training workshop to bond with pets, dog training course, agility training course, grooming course, dog-owners group | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q84 | single-hop | How does Melanie prioritize self-care? | by carving out some me-time each day for activities like running, reading, or playing the violin | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q39 | single-hop | What is Gina's favorite style of dance? | Contemporary | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q67 | single-hop | How did the extra funding help the school shown in the photo shared by John? | Enabled needed repairs and renovations, making the learning environment safer and more modern for students. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q90 | single-hop | What is Nate's favorite movie trilogy? | Lord of the Rings | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q73 | single-hop | What challenge did John encounter during pre-season training? | fitting into the new team's style of play | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q63 | single-hop | What kind of pastries did Andrew and his girlfriend have at the cafe? | croissants, muffins, and tarts | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q69 | single-hop | How does James plan to make his dog-sitting app unique? | By allowing users to customize their pup's preferences/needs | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q25 | single-hop | What are Jolene's favorite books? | Sapiens, Avalanche by Neal Stephenson | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q85 | single-hop | What did Evan start doing a few years back as a stress-buster? | watercolor painting | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q73 | single-hop | Where did Calvin attend a music festival in April 2023? | Tokyo | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q85 | single-hop | What are Caroline's plans for the summer? | researching adoption agencies | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q40 | single-hop | What is Jon's favorite style of dance? | Contemporary | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q68 | single-hop | What type of workout class did Maria start doing in December 2023? | aerial yoga | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q91 | single-hop | What is Nate's favorite book series about? | dragons | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q74 | single-hop | What aspects of the Harry Potter universe will be discussed in John's fan project collaborations? | characters, spells, magical creatures | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q64 | single-hop | What kind of flowers does Audrey have a tattoo of? | sunflowers | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q70 | single-hop | What has John mostly found with the metal detector so far? | bottle caps | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q33 | single-hop | How long have Jolene and her partner been together? | for three years | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q86 | single-hop | What advice did Evan give Sam about finding a passion? | keep trying new things until something sparks excitement | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q74 | single-hop | What advice did Calvin receive from the producer at the music festival? | to stay true to himself and sound unique | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q86 | single-hop | What type of individuals does the adoption agency Caroline is considering support? | LGBTQ+ individuals | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q41 | single-hop | What was Gina's favorite dancing memory? | Winning first place at a regionals dance competition | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q69 | single-hop | What did Maria donate to a homeless shelter in December 2023? | old car | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q92 | single-hop | What kind of lighting does Nate's gaming room have? | red and purple lighting | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q75 | single-hop | What forum did Tim join recently? | fantasy literature forum | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q65 | single-hop | What does Audrey do during dog playdates in the park? | chat with people while dogs make new friends | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q71 | single-hop | What did James offer to do for John regarding pets? | help find the perfect pet | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q42 | single-hop | What music pieces does Deborah listen to during her yoga practice? | Savana, Sleep | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q87 | single-hop | Where did Evan take his family for a road trip on 24 May, 2023? | Jasper | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q75 | single-hop | What is Dave's new business venture as of 1 May, 2023? | Car maintenance shop | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q87 | single-hop | Why did Caroline choose the adoption agency? | because of their inclusivity and support for LGBTQ+ individuals | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q42 | single-hop | What kind of dance piece did Gina's team perform to win first place? | "Finding Freedom" | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q70 | single-hop | What kind of meal did John and his family make together in the photo shared by John? | pizza | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q93 | single-hop | What game was the second tournament that Nate won based on? | Street Fighter | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q76 | single-hop | What kind of picture did Tim share as part of their Harry Potter book collection? | MinaLima's creation from the Harry Potter films | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q66 | single-hop | What type of dog was Andrew looking to adopt based on his living space? | smaller dog | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q72 | single-hop | What instrument is John learning to play as of 27 March, 2022? | Drums | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q49 | single-hop | How long has Jolene been doing yoga and meditation? | about 3 years | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q88 | single-hop | What did Evan find relaxing about his road trip to Jasper? | fresh air, peacefulness, cozy cabin surrounded by mountains and forests | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q76 | single-hop | What type of cars does Dave work on at his shop? | all kinds of cars, from regular maintenance to full restorations of classic cars | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q88 | single-hop | What is Caroline excited about in the adoption process? | creating a family for kids who need one | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q43 | single-hop | What do the dancers in the photo represent? | They are performing at the festival | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q71 | single-hop | What kind of online group did John join? | service-focused online group | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q94 | single-hop | What is Joanna's third screenplay about? | loss, identity, and connection | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q77 | single-hop | What was the highest number of points John scored in a game recently? | 40 points | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q67 | single-hop | Where does Andrew want to live to give their dog a large, open space to run around? | near a park or woods | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q73 | single-hop | How long has John been playing the drums as of 27 March, 2022? | One month | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q58 | single-hop | What games does Jolene recommend for Deborah? | Zelda BOTW for Switch , Animal Crossing: New Horizons, Overcooked 2 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q89 | single-hop | What habit is Sam trying to change in terms of diet? | consuming soda and candy | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q77 | single-hop | What did Calvin receive as a gift from another artist? | a gold necklace with a diamond pendant | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q89 | single-hop | What does Melanie think about Caroline's decision to adopt? | she thinks Caroline is doing something amazing and will be an awesome mom | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q44 | single-hop | What does Gina say about the dancers in the photo? | They look graceful | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q72 | single-hop | What kind of activities did John and his mates from the online group do as part of their service efforts? | gave out food and supplies at a homeless shelter, organized a toy drive for kids in need | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q95 | single-hop | What is Nate's favorite video game? | Xenoblade Chronicles | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q78 | single-hop | What did John celebrate at a restaurant with teammates? | a tough win | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q68 | single-hop | Why did Audrey sign up for a workshop about bonding with pets? | Strengthen the bond with her pets | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q74 | single-hop | What game did John play in an intense tournament at the gaming convention in March 2022? | CS:GO | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q59 | single-hop | What do Deborah and her husband do together? | play detective games together, spend time outdoors and explore nature | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q90 | single-hop | What new suggestion did Evan give to Sam regarding his soda and candy consumption? | try flavored seltzer water and dark chocolate with high cocoa content | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q78 | single-hop | What was the necklace Calvin received meant to remind him of? | why he keeps hustling as a musician | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q90 | single-hop | How long have Mel and her husband been married? | Mel and her husband have been married for 5 years. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q45 | single-hop | What is Jon's attitude towards being part of the dance festival? | Glad | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q73 | single-hop | Who inspired Maria to start volunteering? | Her aunt | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q96 | single-hop | What type of movies does Nate enjoy watching the most? | action and sci-fi | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q19 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q61 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q62 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q17 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q39 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q63 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q25 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q40 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q91 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q64 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q33 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q41 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q92 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q49 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q43 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q94 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q58 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q44 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q95 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q59 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q45 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q96 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q19 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q61 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q62 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q12 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q14 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q11 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q17 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q10 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q39 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q63 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q25 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q85 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q40 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q91 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q64 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q33 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q86 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q41 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q69 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q92 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q75 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q87 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q42 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q49 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q76 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q43 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q94 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q58 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q44 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q95 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q74 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q59 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q78 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q90 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q45 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q73 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q96 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'locomo0_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q82', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q83', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q5', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q8', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q65', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q66', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q88', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q89', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q19', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q61', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q62', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q67', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q68', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q15', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q16', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q83', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q84', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q5', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q10', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q9', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q7', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q12', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q10', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q12', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q8', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q14', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q14', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q5', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q7', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q9', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q5', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q11', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q17', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q10', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q9', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q84', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q39', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q67', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q90', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q73', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q63', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q69', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q25', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q85', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q73', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q85', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q40', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q68', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q91', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q74', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q64', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q70', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q33', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q86', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q74', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q86', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q41', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q69', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q92', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q75', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q65', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q42', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q87', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q75', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q87', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q42', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q70', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q93', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q76', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q66', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q49', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q88', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q76', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q88', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q43', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q94', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q77', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q67', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q73', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q58', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q89', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q77', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q89', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q44', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q95', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q78', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q68', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q74', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q59', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q90', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q78', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q90', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q45', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q73', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q96', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `659.36917006`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
