"""Re-open answer or judge calls that failed before any request reached the provider.

An `APIConnectionError` whose message is the SDK's "Connection error." means the HTTP
connection was never established (TLS handshake reset, DNS, refused); the request was
not transmitted, so the provider cannot have processed or billed it. Such calls are
not `unknown_outcome` in substance, but the transport records them that way, and the
pipeline never replays unknown outcomes on its own. This tool, run by a person with
the evidence in hand, records a reconciliation call state chained to the failed one
and returns the row to `not_dispatched`, so `resume` dispatches a fresh attempt.
Timeouts and any error after dispatch are never touched.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.domain import CallState
from adaption_memory.run_store import RunStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.reconcile_connection_failures")
    parser.add_argument("--runs", type=Path, default=PROJECT_ROOT / "runs")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--window-start", required=True, help="ISO time; only calls started at or after this")
    parser.add_argument("--window-end", required=True, help="ISO time; only calls started at or before this")
    parser.add_argument("--evidence", required=True, help="What established that no request was transmitted")
    parser.add_argument("--apply", action="store_true", help="Write the reconciliation; default is a dry run")
    args = parser.parse_args(argv)
    store = RunStore(args.runs)
    loaded = store.load(args.run_id)
    manifest = loaded.manifest
    if manifest.status.terminal:
        raise RuntimeError("Terminal runs are immutable; retry under a new identity instead")
    refs = {artifact.sha256: artifact for artifact in manifest.artifacts}
    start = datetime.fromisoformat(args.window_start)
    end = datetime.fromisoformat(args.window_end)
    results = [dict(row) for row in loaded.results]
    candidates = []
    for row in results:
        if row.get("last_call_state") != CallState.UNKNOWN_OUTCOME.value:
            continue
        call = store.read_artifact(args.run_id, refs[row["last_call_sha256"]])
        started = call.get("started_at")
        if (call.get("error_type") == "APIConnectionError" and call.get("error") == "Connection error."
                and started and start <= datetime.fromisoformat(started) <= end
                and (call.get("usage") or {}).get("input_tokens") is None):
            candidates.append((row, call))
    print(f"{len(candidates)} unknown-outcome calls are connection failures inside the window")
    for row, call in candidates:
        print(f"  {row['question_id']}  {call['call_id']}  started {call['started_at']}")
    if not args.apply:
        print("dry run; pass --apply to record the reconciliation")
        return 0
    for row, call in candidates:
        revision = refs[row["last_call_sha256"]].implementation_revision
        reconciled = {
            **call,
            "state": CallState.NOT_DISPATCHED.value,
            "ok": False,
            "error_type": "ConnectionFailedBeforeDispatch",
            "error": "Reconciled by a person: the connection was never established, so no request reached the provider",
            "reconciled_from": row["last_call_sha256"],
            "evidence": args.evidence,
        }
        ref = store.put_artifact(args.run_id, "call_state", reconciled, (row["last_call_sha256"],), revision)
        if ref.sha256 not in refs:
            refs[ref.sha256] = ref
            manifest = manifest.with_artifacts((*manifest.artifacts, ref))
        stage = str(call["call_id"]).split(":")[1]
        row.update(status=f"{stage}_{CallState.NOT_DISPATCHED.value}", last_call_state=CallState.NOT_DISPATCHED.value, last_call_sha256=ref.sha256)
    generation = store.checkpoint(manifest, results)
    print(f"recorded {len(candidates)} reconciliations in generation {generation[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
