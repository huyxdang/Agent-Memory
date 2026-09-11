# Qwen extraction streaming diagnostics

The LoCoMo recovery was stopped by user request after session 23 again generated
for minutes without completing. Its preceding 22 updates averaged 369 output
tokens, maximum 605. Server logs showed about 41 generated tokens/second. This
suggests excessive generation, but repetition is unconfirmed: the old request
was non-streaming and no partial response text was returned to the worker.

New workers use streaming completions with final API usage enabled. Prompts,
sampling, structured-output schema and maximum remaining-context output allowance
are unchanged. Streaming is instrumentation, not a fix for generation behavior.

- Each call records `stream_key`, the hash of its input token IDs.
- Partial snapshots go to `streams/<stream_key>.json` inside that run's directory
  on the Modal volume. The local collector mirrors active and terminal snapshots.
- Snapshots preserve accumulated response text, response ID, chunk count, elapsed
  time, time to first text, save timestamp, finish reason, and usage when provided.
- The first chunk, each ten-second interval with new chunks, and termination
  trigger a snapshot. A frozen stream retains its last snapshot; a killed process
  may lose the most recent unsaved chunks. No old partial text can be recovered.
- Chunks and characters are not token counts. Output tokens remain unknown until
  API usage arrives. Final usage is required, including an exact input-token check.
- A wall-clock request deadline remains enforced even if chunks keep arriving.
  Disconnects/timeouts preserve the available diagnostic text and fail the call.
- Partial or truncated text never becomes memory. Existing finish-reason and JSON
  validation still gate applying an update. Diagnostics do not trigger retries.
- Stream artifacts contain private source-derived text. Keep them local/untracked,
  like raw answers and memories; do not commit them.

Reference: [vLLM 0.21.0 streaming completions](https://docs.vllm.ai/en/v0.21.0/api/vllm/entrypoints/openai/completion/serving/).

## Verification and remaining work

Offline tests cover exact text assembly, final token usage, missing usage, input
count mismatch, disconnected streams, and the wall-clock deadline. No new GPU
run has been launched to test this implementation. Before another retry, prepare
a separate diagnostic run with the new code hashes and explicit retry provenance.
Do not silently replay the stopped in-flight request.
