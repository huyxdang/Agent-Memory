# Qwen vLLM smoke result

Completed 2026-09-11. Four updates across two fixed histories, no benchmark answering or judging.

| Check | Result |
|---|---|
| Valid extraction updates | 4/4 |
| Histories processed | 2, two sequential updates each |
| Concurrent request allowance | 2 |
| Extraction wall time | 33.66 seconds |
| First engine startup | 349.71 seconds |
| GPU | L40S, BF16 |
| vLLM / Torch / Transformers | 0.21.0 / 2.11.0 / 4.57.6 |
| GPU sandbox shutdown | Confirmed |
| Accounted estimate including overhead allowance | $0.903 |
| Provider invoice | Not verified |

Each history persisted independently to the cloud Volume. The local collector downloaded four completed calls, two progress files, engine metadata and completion status. The GPU did not require laptop acknowledgements. No question or reference answer was supplied to the extractor. JSON schema validation passed for every output; factual correctness was not graded.

| History prefix | Update | Input tokens | Output tokens | Request seconds |
|---|---:|---:|---:|---:|
| 544ece40 | 1 | 15,647 | 503 | 20.50 |
| 544ece40 | 2 | 12,961 | 329 | 8.81 |
| b3e95bff | 1 | 7,063 | 188 | 11.21 |
| b3e95bff | 2 | 8,244 | 293 | 8.12 |

The sum of request times exceeds extraction wall time because requests overlap. This verifies concurrency but is not a controlled old-versus-new speedup measurement: schema constraints and engine changed, generated memories differ, and later prompts depend on those memories. The new checkpoint variant starts from empty memories rather than importing the stopped run's outputs.

The image, model weights and compilation artifacts are cached. Warm-start savings and cloud crash/restart behavior were not fault-injected in this paid test. Offline tests cover duplicate avoidance, response-saved recovery, unknown-outcome blocking and per-history ordering. Full suite: 69 tests passed. The full 90-question optimized baseline has not been launched.

Raw evidence: `work/qwen_vllm_smoke/{configuration,payload,cloud,loaded,finished}.json` and `memories/*.json`. Frozen worker image: `im-AVJnDICbscYGPY2qXmAgIa`. Terminated sandbox: `sb-TOe7GEGuBFzBkcz5goODNl`.
