# Qwen decoding probe, 2026-09-11

The exact previously failing LoCoMo history 5, session 23 completed after changing
the sampling bundle. This is a one-case generation diagnostic, not a benchmark
accuracy result or a controlled isolation of one sampling parameter.

| Check | Result |
| --- | --- |
| Model | Qwen/Qwen3.5-9B, revision c202236235762e1c871ad0ccb60c8ee5ba337b9a |
| GPU / runtime | L40S, vLLM 0.21.0, BF16, thinking disabled |
| Original prompt hash | Exact match |
| Input tokens | 14,624, tokenizer and API agree |
| Output allowance | 50,912, unchanged and not reached |
| API output tokens | 307 |
| Request elapsed | 13.469 seconds including diagnostic persistence |
| Extraction phase wall time | 16.392 seconds |
| Finish reason / JSON | stop / valid |
| New completed updates | Exactly 1 |
| Duplicate narrative / atomic entries | 0 / 0 |
| Warmup after server launch | 229.270 seconds |
| Conservative accounting | $1.141364 against $1.25 reservation; invoice unverified |
| Answering / judging | Not run; $0 new OpenAI calls |

Sampling: temperature 0.7, top_p 0.8, top_k 20, min_p 0,
presence_penalty 1.5, repetition_penalty 1. Seed, prompt, JSON constraints,
model revision, context window and output allowance stayed unchanged.
The diagnostic had a 180-second request deadline. It finished normally well
before that deadline, rather than ending through timeout or truncation.

The former greedy run produced repeated strings and did not finish; its final
API output usage is unknown. Do not calculate a benchmark speedup from this
single repaired request. Initial allocation-to-worker delay also differs from
generation latency. Sandbox termination was confirmed after this probe.

## Quality caveat

A manual source check found the main selected activities and conditional future
tattoo statement supported. However, successful generation does not establish
full extractor quality. There are five new automatic warning records, including
a chain-tail mismatch for an existing weekend-plan key. Atomic values include
paraphrases and plans despite stricter prompt rules, and a narrative retains
"last Tuesday" instead of resolving the date. The source itself inconsistently
mentions Tuesday and Friday for board games; the date chosen by the output is
not a resolution of that source contradiction. No target was repaired, filtered,
or promoted into the final evaluation.

## Provenance

- Run: qwen-2a2fcabfa6ff70fb.
- Sandbox: sb-nuPklNfWogzQJP9a6SKQX4.
- Local raw artifacts: work/qwen_locomo_decoding_probe, excluded from publication.
- Configuration preserves source provenance, exact hashes and sampling settings.
- One-update preparation: prepare_qwen_decoding_probe.py.
- Full checkout suite passed 106 tests before launch; five streaming tests
  passed again afterward. Offline rehearsal verified exactly one new call and
  identical prompt hash from the actual prepared checkpoint.
- Official sampling reference: https://huggingface.co/Qwen/Qwen3.5-9B#best-practices

The smoke scope intentionally leaves five question outputs missing. The full
LoCoMo final evaluation still has its original 45 valid question results; this
diagnostic does not complete the remaining five questions.
