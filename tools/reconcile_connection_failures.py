"""Re-open answer or judge calls that failed before any request reached the provider.

An `APIConnectionError` whose message is the SDK's "Connection error." means the HTTP
connection was never established (TLS handshake reset, DNS, refused); the request was
not transmitted, so the provider cannot have processed or billed it. Such calls are
not `unknown_outcome` in substance, but the transport records them that way, and the
pipeline never replays unknown outcomes on its own. This tool, run by a person with
the evidence in hand, records a reconciliation call state chained to the failed one
and returns the row to `not_dispatched`, so `resume` dispatches a fresh attempt.
Timeouts and any error after dispatch are never touched.

With `--after-dispatch`, the tool instead re-opens calls that failed *after* the
request was transmitted: `APITimeoutError` (no response inside the client timeout) and
`InterruptedAfterDispatch` (the operator stopped the process while the call was in
flight). The provider may have processed and billed these, so accounted spend can
undercount by at most those calls, and a fresh attempt may duplicate one. Use it only
when leaving the rows unresolved would otherwise strand the run, and state the bound
in the evidence. An unresolved call forces the run `blocked` at the end of the pass; it can
still be reconciled and resumed, but every question on it stays ungraded until then.
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
    parser.add_argument("--after-dispatch", action="store_true",
                        help="Re-open APITimeoutError and InterruptedAfterDispatch calls, which may already have been billed")
    parser.add_argument("--apply", action="store_true", help="Write the reconciliation; default is a dry run")
    args = parser.parse_args(argv)
    store = RunStore(args.runs)
    loaded = store.load(args.run_id)
    manifest = loaded.manifest
    if manifest.status.settled:
        raise RuntimeError("This run succeeded on every question; retry under a new identity instead")
    refs = {artifact.sha256: artifact for artifact in manifest.artifacts}
    start = datetime.fromisoformat(args.window_start)
    end = datetime.fromisoformat(args.window_end)
    results = [dict(row) for row in loaded.results]
    candidates = []
    for row in results:
        states = {CallState.UNKNOWN_OUTCOME.value}
        if args.after_dispatch:
            # A call left in flight by a process that is no longer running will never have a
            # response saved; the next resume would only relabel it unknown, so treat it here.
            states.add(CallState.IN_FLIGHT.value)
        if row.get("last_call_state") not in states:
            continue
        if not row.get("last_call_sha256"):
            # A question blocked behind another question's failed extraction: it carries the owner's
            # state but no call of its own. Reconciling the owner's call releases it.
            continue
        call = store.read_artifact(args.run_id, refs[row["last_call_sha256"]])
        started = call.get("started_at")
        if args.after_dispatch:
            matches = (call.get("error_type") in {"APITimeoutError", "InterruptedAfterDispatch"}
                       or call.get("state") == CallState.IN_FLIGHT.value)
        else:
            matches = call.get("error_type") == "APIConnectionError" and call.get("error") == "Connection error."
        if (matches and started and start <= datetime.fromisoformat(started) <= end
                and (call.get("usage") or {}).get("input_tokens") is None):
            candidates.append((row, call))
    kind = "failures after dispatch" if args.after_dispatch else "connection failures"
    print(f"{len(candidates)} unknown-outcome calls are {kind} inside the window")
    for row, call in candidates:
        print(f"  {row['question_id']}  {call['call_id']}  started {call['started_at']}")
    if not args.apply:
        print("dry run; pass --apply to record the reconciliation")
        return 0
    for row, call in candidates:
        revision = refs[row["last_call_sha256"]].implementation_revision
        if args.after_dispatch:
            error_type = "FailedAfterDispatch"
            error = ("Reconciled by a person: the request was transmitted but no response was durably saved; "
                     "the provider may have billed it, so accounted spend can undercount by this one call")
        else:
            error_type = "ConnectionFailedBeforeDispatch"
            error = "Reconciled by a person: the connection was never established, so no request reached the provider"
        reconciled = {
            **call,
            "state": CallState.NOT_DISPATCHED.value,
            "ok": False,
            "error_type": error_type,
            "error": error,
            "reconciled_from": row["last_call_sha256"],
            "evidence": args.evidence,
        }
        ref = store.put_artifact(args.run_id, "call_state", reconciled, (row["last_call_sha256"],), revision)
        if ref.sha256 not in refs:
            refs[ref.sha256] = ref
            manifest = manifest.with_artifacts((*manifest.artifacts, ref))
        stage = str(call["call_id"]).split(":")[1]
        row.update(status=f"{stage}_{CallState.NOT_DISPATCHED.value}", last_call_state=CallState.NOT_DISPATCHED.value, last_call_sha256=ref.sha256)
    # A failed extraction parks every other question on that history at `blocked_memory`, and the
    # pipeline skips those rows for the rest of the run. Once the history's own call is reopened the
    # memory will be rebuilt, so return its parked questions to `prepared` or they stay stranded.
    unresolved_histories = {
        row["history_sha256"] for row in results
        # A parked row carries the owner's state but owns no call, so it must not block its own release.
        if row.get("status") != "blocked_memory"
        and row.get("last_call_state") in {CallState.UNKNOWN_OUTCOME.value, CallState.IN_FLIGHT.value}
    }
    released = 0
    for row in results:
        if row.get("status") == "blocked_memory" and row["history_sha256"] not in unresolved_histories:
            row.update(status="prepared", last_call_state=None, last_call_sha256=None)
            released += 1
    generation = store.checkpoint(manifest, results)
    print(f"recorded {len(candidates)} reconciliations and released {released} questions "
          f"blocked behind a reopened extraction, in generation {generation[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
