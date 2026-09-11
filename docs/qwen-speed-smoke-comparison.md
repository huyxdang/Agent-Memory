# Qwen concurrency smoke comparison

Measured 2026-09-11 at commit `c44663174196425427f8fbb64f2f20e1e751a167`.
Two fresh runs processed the first two updates of the same two fixed BEAM
histories. No answering, judging, training or synthetic-data calls were made.

| Metric | One active request | Two active requests |
|---|---:|---:|
| Valid updates | 4/4 | 4/4 |
| Extraction wall seconds, including checkpoint work | 46.197 | 47.661 |
| Valid updates per minute | 5.195 | 5.036 |
| Engine startup seconds | 279.484 | 299.830 |
| Observed launch-to-stop seconds | 405.190 | 433.957 |
| Accounted USD, including overhead allowance | 0.844 | 0.876 |
| GPU shutdown confirmed | Yes | Yes |

Two-request extraction was 3.17% slower, a speed ratio of 0.969x. This smoke
does not demonstrate a concurrency speedup. The earlier two-request smoke took
33.658 seconds, showing that one small trial is not a stable throughput estimate.
Do not project these early updates directly onto full, growing memories.

Both runs used one L40S, Qwen/Qwen3.5-9B revision
`c202236235762e1c871ad0ccb60c8ee5ba337b9a`, BF16, thinking disabled, temperature
zero, seed zero, schema-constrained JSON, a 65,536-token window and 2,048-token
output allowance. Image `im-AVJnDICbscYGPY2qXmAgIa` used vLLM 0.21.0,
Torch 2.11.0 and Transformers 4.57.6. Only concurrency and the corresponding
server max-num-seqs setting changed. The one-request trial ran first.

The first prompt in each history matched exactly across runs. All four outputs
differed, so second-update prompts also differed. This compares the same source
workload under two scheduling configurations, not identical token workloads.
Output validity is not factual accuracy; memories were not quality-graded.

| History prefix | Update | C1 input/output tokens | C2 input/output tokens | C1 request seconds | C2 request seconds |
|---|---:|---:|---:|---:|---:|
| 544ece40 | 1 | 15,647 / 481 | 15,647 / 504 | 17.604 | 20.060 |
| 544ece40 | 2 | 12,944 / 557 | 12,965 / 553 | 14.209 | 14.067 |
| b3e95bff | 1 | 7,063 / 188 | 7,063 / 216 | 5.004 | 11.904 |
| b3e95bff | 2 | 8,244 / 293 | 8,268 / 265 | 7.581 | 6.930 |

Request durations exclude semaphore queue waits. Extraction wall time includes
tokenization, queueing, inference and checkpoint commits. The whole observed
interval includes image lookup/build, GPU provisioning, startup, shutdown and
collector polling delay. It is an upper-bound observed interval, not precise
provider-billed GPU time. Summed request durations are not wall time.

Combined accounted cost is $1.720018, including two $0.50 overhead allowances;
provider invoices remain unverified. Both launches reserved at most $1.25 each
and had 821-second sandbox limits. The prior baseline and vLLM runs plus these
smokes account for $5.790603 of the existing $10 baseline allocation, leaving
$4.209397. This is not the account's remaining credit balance.

No full 90-question optimized baseline was launched in this comparison.
The old mixed A100/L40S Transformers run is not a matched speed control: its
first four corresponding calls included an invalid result, used unconstrained
decoding and lacked a comparable four-update wall-time measurement.

Local, ignored evidence:

- `work/qwen_vllm_speed_c1/`: configuration, payload, loaded, finished, cloud and memories.
- `work/qwen_vllm_speed_c2/`: the same artifacts for concurrency two.
- Run IDs: `qwen-29d755fd0bc8602f`, `qwen-c806ab4b32dacac6`.
- Terminated sandboxes: `sb-s667J2jkCoRntvjZJMueWF`, `sb-zTAnF56JhUeLZxeCzwIQT2`.

Cached model weights were reused. The second run explicitly loaded compiled
graphs from cache, which still took 67 seconds. Cache persistence follows the
[Modal Volume lifecycle](https://modal.com/docs/guide/sandbox-files).
