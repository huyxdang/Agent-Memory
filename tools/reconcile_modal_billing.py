"""Reconcile stopped runs using a saved, shared app billing interval as an upper bound."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from adaption_memory.execution.files import save
from adaption_memory.execution.modal import cloud, reconcile_stopped_states


def reconcile(directories, object_id, start, end, output):
    modal, _ = cloud()
    records = [json.loads((directory / "cloud.json").read_text()) for directory in directories]
    for record in records:
        started = datetime.fromisoformat(record["gpu_started_at"])
        if not start <= started < end:
            raise ValueError("Billing interval does not cover run start")
        if modal.Sandbox.from_id(record["sandbox_id"]).poll() is None:
            raise ValueError("Cannot reconcile a running sandbox")
    rows = [asdict(row) for row in modal.Workspace.from_context().billing.report(
        start=start, end=end, resolution="h") if row.object_id == object_id]
    if not rows:
        raise ValueError("No provider billing evidence for the selected app and interval")
    shared_cost = sum(float(row["cost"]) for row in rows)
    observed = datetime.now(timezone.utc).isoformat()
    evidence = dict(observed_at=observed, object_id=object_id, start=start.isoformat(),
        end=end.isoformat(), provider_metered_usd=shared_cost,
        rows=json.loads(json.dumps(rows, default=str)), original_ledgers=records,
        note="App-level metering does not allocate cost between sandboxes. Each run is conservatively assigned the whole interval plus its startup allowance. No exact termination time or invoice is inferred.")
    if output.exists():
        raise ValueError("Use a new billing evidence path")
    save(output, evidence)
    for directory, record in zip(directories, records):
        if record.get("termination") == "confirmed" and record.get("accounted_usd") is not None:
            continue
        record.update(status="stopped", termination="confirmed", reconciled_at=observed,
            accounted_usd=min(record["reserved_usd"], shared_cost + .50),
            accounting_basis="shared_app_interval_upper_bound_plus_startup_allowance",
            billing_evidence=str(output.resolve()), finished_at=None,
            termination_time_note="Exact provider termination timestamp unavailable.")
        save(directory / "cloud.json", record)
        payload = json.loads((directory / "configuration.json").read_text())["payload"]
        reconcile_stopped_states(directory, payload)
    print(json.dumps({"shared_provider_metered_usd": shared_cost,
        "per_run_conservative_bound_usd": shared_cost + .50, "evidence": str(output)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--start", required=True, type=datetime.fromisoformat)
    parser.add_argument("--end", required=True, type=datetime.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    reconcile(args.directories, args.object_id, args.start, args.end, args.output)
