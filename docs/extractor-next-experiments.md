# Extractor experiments after Gemma recovery

Updated 2026-09-12. Recovery commit `f291c54` is pushed to `origin/main`.
This plan does not authorize additional training or raise existing budgets.

## Gemma final evaluation in progress

- Keep the completed BEAM final-90 result from `gemma3-beam-90-003`.
- New LoCoMo final-50 attempt: `gemma3-locomo-50-005`. Same 10 histories,
  272 extraction updates, questions, prompts, model revision, and decoding as
  the previous final-50 specification. One L4, four concurrent histories.
- Fresh extraction is explicit. No partial memory is used for answering and
  no unknown-outcome call from an earlier run is silently retried.
- Modal reservation $2.50, maximum sandbox lifetime 3,371 seconds. Answering
  and judging allocation $1.45. The previous BEAM report's $3.16501245 is total
  accounted spend, including $1.62692025 Modal, not OpenAI spend alone.
  Its OpenAI calls cost $1.5380922; adding $1.45 remains under the previously
  approved $3 OpenAI allocation.
- The unchanged 128K judge output allowance requires a large worst-case call
  reservation. The remaining budget may block grading before actual spend
  reaches its cap. Report this explicitly; do not silently lower the allowance
  or increase the budget.
- Do not stop all histories when one returns invalid output. Preserve the
  failure, finish unaffected histories, and grade only complete memories.
- LongMemEval final-100 is not launched. Its 4,803 updates need a separate
  runtime and cost estimate after LoCoMo; no larger allocation is assumed.

## Task 1: GPT-5.6 Sol extractor comparison

The user approved **$20 total OpenAI spend** on 2026-09-12 for this comparison.
Treat this as one shared cap including extraction, answering, judging, smoke
checks, and unresolved reservations, not $20 per benchmark or invocation.
No Sol inference has started. Standard-rate historical extraction proxies are
$15.06 to $18.33 for BEAM final-90 and $12.13 for LoCoMo final-50, excluding
answering/judging. LongMemEval is additional and not yet estimated. These are
workload proxies, not quotes or guarantees; actual Sol memory lengths, tokens,
caching and cache-write premiums differ. Choose which benchmark to prioritize
before spending the cap. Reproduce with `python -m tools.estimate_sol_budget`.

Read-only model retrieval succeeded for `gpt-5.6-sol` with the existing key.
No Sol inference has run. Use Sol as the **extractor**, not the answerer or judge.
Keep the Luna answerer, benchmark judges, no question-based retrieval, frozen
question selections, extraction rules, and history sharing unchanged.

Use reasoning `none` for the first comparison to avoid adding a reasoning
setting change to the extractor-model comparison. Record input, cached input,
total output, reasoning output, cost, latency, failures, and memory size.
Reprice saved unique-history calls as a workload estimate, then obtain a
separate OpenAI cap before executing. The cloud runner currently targets vLLM
models; check the canonical OpenAI extraction path and its nonzero extractor
pricing before adding a Sol preset. Do not call Sol with a free extractor price.

[Official Sol documentation](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
lists $4 per million input tokens and $20 per million output tokens, with
different pricing above 272K input tokens. Actual Sol-generated memory lengths
and cache hits will differ from the historical workload estimate.

Matching observed Qwen-9B and Luna scores is not proof that the extractors are
equivalent. Report paired question outcomes and coverage; retain disclosed
differences in historical prompts, limits, and memory reuse.

## Task 2: Fine-tuning review and next experiment

Authenticated read-only AutoScientist inspection found two relevant runs on
dataset `86b6f09f-d658-4fb2-9800-13c1d0fceb80`, named `agent-memory`.

| Model | Run ID | Best internal win rate | Iterations | Target reached |
| --- | --- | ---: | ---: | --- |
| Gemma 3 4B Instruct | `e9bbffe5-dbed-4291-b133-773ad2402b5b` | 45.57% | 3/3 | No, target 70% |
| Qwen 3.5 0.8B | `9909ea8f-7e49-4536-9642-aa39a6054e51` | 56.32% | 3/3 | No, target 70% |

Both succeeded and have downloadable checkpoints. Gemma's best recipe used
LoRA rank 16, alpha 32, one epoch, learning rate 1e-5, and completion-only loss.
The runs used `original_prompt` and `original_completion` with instruction
training. Dataset metadata reports 564 source rows, chat column `messages`,
and adaptation-quality scores 10 before and 7 after, a reported 30% decline.
Because training selected original columns, that adaptation decline cannot
by itself explain the fine-tuning result.

Adaption's [interpretation guide](https://docs.adaptionlabs.ai/autoscientist/interpreting-results/)
defines win rate as comparisons against the base model on evaluations derived
from the dataset. It is not downstream benchmark accuracy. Gemma underperformed
on this internal metric. The local fine-tuned Qwen smoke completed 19/20 updates
and produced no final-question grades; the untuned run graded only 32/50. There
is no complete local paired comparison establishing final-accuracy degradation.

### Next steps before another training charge

1. Reuse the existing Gemma checkpoint. Pin its base, adapter, tokenizer, and
   template and first test JSON stability and extraction quality on dev. Do not
   start another training run simply because the platform's win rate is low.
2. Audit the exact exported training columns and targets, including attribution,
   dates, changed values, duplicate lines, and preserved previous-memory inputs.
   Dataset quality grades are not a replacement for source-faithfulness checks.
3. Confirm Gemma's **training** sequence limit. The
   [supported-models page](https://docs.adaptionlabs.ai/autoscientist/supported-models/)
   explicitly leaves Gemma 3 limits unpublished, warns that overlong rows are
   truncated, and distinguishes serving context from training context. The API's
   131,072 context value does not establish a safe training window. Our existing
   sequence measurements use Qwen tokenization, not Gemma's.
4. Verify effective training row count and augmentation. The documentation says
   1,000 effective SFT rows, but source metadata shows 564 and successful jobs.
   Available run metadata does not establish whether augmentation or a different
   historical policy explains this. Do not infer that only 564 rows were trained.
5. For a new controlled run, pin `model="google/gemma-3-4b-it"`, use explicit
   instruction prompt/completion mapping and `train_on_inputs=False`, and keep
   external dev histories separate. Leave unrelated hyperparameters platform-
   selected unless the experiment requires a fixed recipe. Record resolved
   settings and evaluate the best downloaded checkpoint on our own dev metrics.
6. Separate original-data and synthetic-data arms. AutoScientist's
   [create API](https://docs.adaptionlabs.ai/api/python/resources/autoscientist/methods/create)
   exposes augmentation counts, model choice, mapping, training strategy, and
   iteration limits. Changing both the data and automatically selected recipe
   compares whole training workflows, not the causal effect of synthetic data.

No Adaptive Data or AutoScientist job was started during this review. Relevant
API evidence is saved locally in `work/adaption-training-review-20260912.json`.
Training-context handling, exact effective dataset composition, and a matched
downstream fine-tuned Gemma result remain unverified.
