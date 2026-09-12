# Gemma 3 4B extractor smoke

Date: 2026-09-12

## Scope

- Model: `google/gemma-3-4b-it`
- Revision: `093f9f388b31de276ce2de164bdc2081324b9767`
- Runtime: vLLM 0.21.0 on one Modal L4, BF16, 65,536-token context
- Workload: the first two frozen LoCoMo histories, first two updates per history
- Extraction only. No answers or judge calls were run.
- Prompt text was unchanged. Gemma requires alternating chat roles, so the existing
  ordered user prompt blocks were joined with two newlines into one user message.

## Result

The corrected smoke completed all four calls with valid JSON and `stop` finish
reasons. There was no whitespace runaway or repeated generation loop.

| Metric | Result |
|---|---:|
| Successful updates | 4 / 4 |
| Input tokens | 8,168 |
| Output tokens | 1,119 |
| Mean inference time | 14.26 s |
| Sum of call time | 57.03 s |
| Concurrent extraction wall time | 40.47 s |
| Corrected attempt accounted cost | $0.7406 |
| Failed integration attempt accounted cost | $0.7195 |
| Total smoke accounting | $1.4600 |

The first attempt produced no model output. Gemma's native chat template rejected
the extractor's consecutive user messages. The corrected envelope preserved their
content and order and passed 112 offline tests.

## Quality assessment

Gemma 3 4B is coherent enough to continue testing. It is materially better than
the fine-tuned Qwen 0.8B smoke: all outputs were readable, grounded in the source
conversation, and structurally complete. It is not yet a reliable extractor.

Observed problems:

- Relative event dates remained relative instead of becoming absolute dates.
- Atomic keys were not consistently lower-case or stable.
- One official-looking business name, `Dance Studio`, was inferred from a generic
  description rather than stated as a name.
- `Gina's location = Paris` was wrong. Jon visited Paris; Gina said she had never
  visited Paris and had visited Rome.
- Several attributes shared one repeated key instead of using a precise value or
  narrative, and one unchanged meetup date was repeated in the next update.
- Some atomic values paraphrased the conversation instead of preserving its exact
  wording.

Verdict: pass the basic usability smoke, fail strict extraction fidelity. A larger
untuned baseline or fine-tuning run should follow only after a small direct quality
evaluation is defined and these rule failures are measured consistently.

Artifacts are local under `work/gemma3_locomo_smoke_c2_v2/`. The failed integration
attempt remains under `work/gemma3_locomo_smoke_c2/`.
