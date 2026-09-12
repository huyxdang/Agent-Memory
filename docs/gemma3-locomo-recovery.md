# Gemma LoCoMo recovery

Date: 2026-09-12. This is a diagnostic, not a new benchmark score.

## Verified saved state

| Run | Saved updates | Complete histories | Graded questions | State |
| --- | ---: | ---: | ---: | --- |
| `gemma3-beam-90-003` | 203/203 | 7/7 | 90/90 | Complete; recorded weighted score 0.3657275 |
| `gemma3-locomo-50-003` | 57/272 | 0/10 | 0/50 | Stopped; sandbox exit 137 |
| `gemma3-locomo-50-004` | 84/272 | 0/10 | 0/50 | Stopped; sandbox exit 137 |

The previous handoff's claim that nine histories could already be graded was
incorrect. They were in progress, not complete. Partial grading cannot recover
answers from these two attempts without further extraction. Partial memories
must not be treated as complete histories.

## Changes

- Once the Modal sandbox stops, import available complete memories and answer
  only their questions. Missing or failed memories remain `blocked_memory`.
- Do not fall through to local/OpenAI extraction for blocked memories.
- Validate checkpoint identity and completed-session counts before import.
- Report scored-question coverage and distinguish a scored subset from the
  full frozen selection. Missing outputs are not scored as wrong answers.
- Wait for confirmed stop, record a conservative cost once, and retain its
  basis in imported accounting artifacts and reports.
- Permit collection of historical artifacts after local source changes while
  preserving frozen payload checks. Launch still requires matching source.

## Historical stop accounting

Modal's app-level hourly metering reports **$0.64367187** for the interval
2026-09-12 04:00 through 09:00 UTC for app `ap-Y0WZk5ehYUa1KMiFEmpKgn`.
This covers the two stopped LoCoMo attempts but is not a per-sandbox invoice.
Each ledger conservatively receives the entire interval plus a $0.50 startup
allowance: **$1.14367187 each**. Summing these bounds deliberately overcounts
the shared interval; do not present their sum as actual provider spend.

The original ledgers and metering rows are preserved locally in
`work/gemma-locomo-billing-reconciliation.json`. Exact historical stop timestamps
remain unavailable; the repaired records do not invent them.

## Isolated decoder diagnostic

`tools/replay_extraction.py` replays the saved failed session from LoCoMo 004 in
its original image. The fixture and outputs stay outside benchmark results in
`work/gemma-locomo-schema-replay-001`.

- Model: `google/gemma-3-4b-it`, revision
  `093f9f388b31de276ce2de164bdc2081324b9767`.
- Original worker image: `im-B0tIEIFSLcB1tjnezrulkM`.
- Prompt: 3,446 input tokens; output allowance: 8,192 tokens; context: 65,536.
- Sampling: temperature 0, frequency penalty 0.3, seed 0.
- GPU: one L4, with the original server configuration.
- Checks: a fixed-output JSON-schema sentinel, the original streamed request,
  and an equivalent non-streamed request.
- Modal reservation: $1.10 maximum. No OpenAI answering or judging calls.

This isolated replay retains the concurrency setting but does not recreate
other simultaneous requests. Therefore a successful replay alone would not
prove the original failure impossible or fixed.

### Results

| Check | Actual result |
| --- | --- |
| Fixed schema requiring `{"probe":"grammar-active"}` | Passed: exact object after JSON parsing; normal stop |
| Original request, streaming | Valid memory JSON; normal stop; 724 output tokens |
| Equivalent request, no streaming | Valid memory JSON; normal stop; 724 output tokens |
| Streaming versus non-streaming content | Byte-identical |
| Narrative repetition | Five lines, only three unique; two duplicate entries |
| Sandbox shutdown | Confirmed, exit 0 |

All three calls reported 3,446 input tokens each: **10,338 total input tokens**.
The sentinel used 16 output tokens, for **1,464 total output tokens** across
the three calls. These are diagnostic tokens, not benchmark answering costs.

GPU reservation began at 09:38:57.537614 UTC; shutdown was confirmed at
09:44:42.056196 UTC. The 344.52-second interval includes loading and time until
stop confirmation, not just extraction. Conservative accounted cost including
the startup allowance: **$0.70434086**, within the $1.10 reservation. It is not
a provider invoice. OpenAI calls and spend: zero.

The requested grammar is demonstrably enforced for the sentinel in this
isolated test. The original malformed JSON did **not** reproduce, and streaming
did not change this replay's output. This does not establish stability under
the original concurrent workload or identify the earlier failure's cause.
Repetition remains a separate quality problem; parsing success is not an
accuracy grade. No decoding change or new full benchmark was launched.

Next diagnostic, if pursued: reproduce concurrent request traffic in a small
bounded test before changing grammar settings. Do not infer that disabling
whitespace freedom fixes malformed quotes from the evidence gathered here.

## Verification

- 116 offline tests passed (`python -m unittest discover -q`).
- Regression coverage includes partial grading, blocked extraction, missing
  histories, active-run gating, stopped accounting idempotence, failed stop,
  and historical artifact collection with frozen-identity validation.
- `git diff --check` passed. Existing unrelated worktree edits were preserved.
