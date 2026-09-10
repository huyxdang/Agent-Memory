# Experiment rules

Read this file before planning or running experiments in this repository.

## Shared-memory speed experiment

- The goal is to measure **observed historical speedup**, not claim a controlled causal speedup from async scheduling alone.
- A is the recorded original pipeline: each question independently built memory, answered and judged. Different question jobs already ran concurrently. Do not describe A as globally serial.
- B builds each unique history once, finishes all building, then answers its questions. C builds each history once and starts answering from its completed memory while other histories are still building. Distinguish reuse savings from scheduling overlap. If only A and C are measured, report their combined improvement; do not invent a B result.
- Do not rerun A or launch any paid experiment without explicit authorization and an agreed spending cap.
- Preserve the selected histories, questions, extraction semantics, answerer and judge settings for the historical comparison. Record any differences, including concurrency, provider conditions, cache behavior and code/model versions. Historical comparisons are not controlled experiments.
- Build memory once per unique sanitized history and extraction configuration. Keep updates sequential within each history. Questions sharing that history must use the same completed, immutable memory artifact, identified by ID and hash. Never answer from a still-changing memory in this experiment.
- For a full-pipeline comparison, start new runs without completed memories for those histories. Label runs using previously built memories as answer-only reuse runs, not full-pipeline speed measurements.

## Required timing and accounting

- Measure total elapsed wall time for the entire workload, from run start before memory building through the final judge result and finalization. Use UTC start/finish timestamps and a monotonic elapsed timer. Keep timing boundaries consistent with the historical run interval; disclose any differences.
- Record time to first graded answer and time to all graded answers. Record building, answering and judging timings separately, plus retries and rate-limit waits when available.
- Sum of API-call durations is not wall-clock duration when calls overlap. Do not substitute one for the other or add overlapping stage durations as total time.
- Record unique histories, selected questions, valid outputs, calls, token usage and costs by stage. Include failed attempts explicitly; unknown usage is unknown, not zero.
- Speedup = historical elapsed seconds / new elapsed seconds. Elapsed-time reduction = 1 - new elapsed seconds / historical elapsed seconds. Report the underlying durations, workload and completion counts alongside both numbers.
- Do not claim completion speedup for a run that omitted or failed questions as if it completed the same workload. Report incomplete runs separately.
- Report performance and memory-size changes alongside speed. Shared-memory evaluation differs from independently generated memory per question; do not silently treat historical accuracy as the same experimental condition.
- Publish code and aggregate reports only. Keep credentials, raw responses and memory artifacts local. Preserve original run records and their historical settings.

## Historical A timings, verified from saved manifests

These are our memory-system runs, not full-history answer-only runs or Mem0 reruns. Duration is manifest finished_at minus started_at, including extraction, answering, judging and run overhead within that interval.

| Benchmark | Questions | Unique histories | Start UTC | Finish UTC | Elapsed seconds | Human duration | Run ID |
|---|---:|---:|---|---|---:|---|---|
| LoCoMo shared 50 | 50 | 10 | 2026-09-08 19:05:59.396590 | 2026-09-08 19:20:38.772866 | 879.376276 | 14m 39.38s | 20260908T190559396590Z_memory_6a360f8 |
| BEAM 500K | 40 | 2 | 2026-09-09 06:43:05.432208 | 2026-09-09 07:51:00.589248 | 4075.157040 | 67m 55.16s | 20260909T064305432208Z_memory_e66fa47 |

Both manifests report complete. Their durations sum to 4954.533316 seconds, or 82m 34.53s. This is the sum of two separate job durations, not a measured combined-job wall time. Concurrency is not recorded in these manifests' metadata.execution field; do not infer it from these timestamps.

Source files: runs/<run-id>/manifest.json, with duplicate-history and extraction-call counts checked against the corresponding local results.jsonl files. The original runs recorded 1,332 extraction calls for LoCoMo and 2,680 for BEAM; one build per history requires 272 and 134 update steps respectively with the same boundaries. Call-count reduction is not an observed runtime or dollar saving.
