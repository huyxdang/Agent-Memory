from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from adaption_memory.config import PROJECT_ROOT
from adaption_memory.evaluation.pipeline import Coordinator
from adaption_memory.execution.local import FixtureBackend, OpenAIBackend, RoutedBackend
from adaption_memory.inference.openai import BudgetLedger, OpenAITransport, Price
from adaption_memory.presets import load_preset, resolve, selected_items
from adaption_memory.run_store.reporting import write_report


def _backend(preset, budget_usd: float | None):
    if preset.executor == "fixture":
        return FixtureBackend()
    if budget_usd is None or budget_usd <= 0:
        raise ValueError("--budget-usd must be positive for paid execution")
    from openai import OpenAI

    ledger = BudgetLedger(budget_usd)
    answer_price = Price(preset.answer_input_cost, preset.answer_cached_input_cost, preset.answer_output_cost)
    judge_price = Price(preset.judge_input_cost, preset.judge_cached_input_cost, preset.judge_output_cost)
    free_extractor = Price(0.0, 0.0, 0.0)
    evaluation = OpenAIBackend(
        OpenAITransport(OpenAI(max_retries=0, timeout=180), ledger), free_extractor, answer_price, judge_price
    )
    extractor_url = os.getenv("EXTRACTOR_BASE_URL")
    if extractor_url:
        extractor_client = OpenAI(base_url=extractor_url, api_key=os.getenv("EXTRACTOR_API_KEY", "local-only"), max_retries=0, timeout=600)
        extractor = OpenAIBackend(OpenAITransport(extractor_client, ledger), free_extractor, answer_price, judge_price)
    else:
        if preset.system == "memory" and preset.executor == "local":
            raise ValueError("A local memory experiment requires EXTRACTOR_BASE_URL")
        extractor = evaluation
    return RoutedBackend(extractor=extractor, evaluator=evaluation)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m adaption_memory.cli", description="Canonical experiment runner")
    parser.add_argument("--runs", type=Path, default=PROJECT_ROOT / "runs")
    sub = parser.add_subparsers(dest="command", required=True)

    preflight = sub.add_parser("preflight", help="Resolve and validate a frozen experiment without writing or calling models")
    preflight.add_argument("--spec", type=Path, required=True)

    prepare = sub.add_parser("prepare", help="Create an immutable version 2 run")
    prepare.add_argument("--spec", type=Path, required=True)
    prepare.add_argument("--run-id", required=True)

    run = sub.add_parser("run", help="Execute a prepared run")
    run.add_argument("--spec", type=Path, required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--allow-paid", action="store_true")
    run.add_argument("--budget-usd", type=float)
    run.add_argument("--modal-budget-usd", type=float)

    resume = sub.add_parser("resume", help="Resume a non-terminal run or create a retry for a terminal run")
    resume.add_argument("--spec", type=Path, required=True)
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--retry-as")
    resume.add_argument("--allow-paid", action="store_true")
    resume.add_argument("--budget-usd", type=float)
    resume.add_argument("--modal-budget-usd", type=float)
    resume.add_argument("--watch", action="store_true")

    stop = sub.add_parser("stop", help="Stop the Modal sandbox for a prepared run")
    stop.add_argument("--spec", type=Path, required=True)
    stop.add_argument("--run-id", required=True)

    reconcile = sub.add_parser("reconcile", help="Validate a run and report unresolved call outcomes without replaying them")
    reconcile.add_argument("--spec", type=Path, required=True)
    reconcile.add_argument("--run-id", required=True)

    report = sub.add_parser("report", help="Write a report from a strictly validated run")
    report.add_argument("--run-id", required=True)
    report.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    coordinator = Coordinator(args.runs)
    if args.command == "report":
        data = write_report(coordinator.store, args.run_id, args.output)
        print(json.dumps(data, indent=2))
        return 0

    preset = load_preset(args.spec)
    spec = resolve(preset)
    if args.command == "preflight":
        items = selected_items(preset)
        print(json.dumps({
            "name": preset.name,
            "spec_sha256": spec.sha256(),
            "configuration_sha256": spec.configuration_sha256(),
            "questions": len(items),
            "paid_authorized": False,
        }, indent=2))
        return 0
    if args.command == "prepare":
        manifest = coordinator.prepare(args.run_id, preset)
        if preset.executor == "modal":
            from adaption_memory.execution import modal

            modal.prepare(args.runs / args.run_id / "modal", preset)
        print(json.dumps(manifest.to_dict(), indent=2))
        return 0
    if args.command == "reconcile":
        loaded = coordinator.store.load(args.run_id, expected_spec_sha256=spec.sha256())
        unresolved = [
            row["question_id"]
            for row in loaded.results
            if row.get("last_call_state") in {"in_flight", "unknown_outcome"}
        ]
        print(json.dumps({"run_id": args.run_id, "status": loaded.manifest.status.value, "unresolved_question_ids": unresolved, "safe_to_retry": False}, indent=2))
        return 2 if unresolved else 0
    if args.command == "resume" and args.retry_as:
        parent_run_id = args.run_id
        coordinator.retry(parent_run_id, args.retry_as, preset)
        args.run_id = args.retry_as
        if preset.executor == "modal":
            from adaption_memory.execution import modal

            directory = args.runs / args.run_id / "modal"
            modal.prepare(directory, preset)
            if args.modal_budget_usd is None:
                print(json.dumps({"run_id": args.run_id, "status": "prepared", "retry_of": parent_run_id}, indent=2))
                return 0
            if not args.allow_paid:
                raise PermissionError("Modal execution requires --allow-paid")
            print(json.dumps(modal.launch(directory, args.modal_budget_usd), indent=2))
            return 0
    elif args.command == "resume" and coordinator.store.load(args.run_id).manifest.status.terminal:
        raise RuntimeError("Terminal runs require --retry-as with a new run ID")
    if args.command == "stop":
        from adaption_memory.execution import modal

        modal.stop(args.runs / args.run_id / "modal")
        return 0
    if preset.executor == "modal" and args.command == "run":
        if not args.allow_paid:
            raise PermissionError("Modal execution requires --allow-paid")
        if args.modal_budget_usd is None:
            raise ValueError("Modal execution requires --modal-budget-usd")
        from adaption_memory.execution import modal

        record = modal.launch(args.runs / args.run_id / "modal", args.modal_budget_usd)
        print(json.dumps(record, indent=2))
        return 0
    if preset.executor == "modal" and args.command == "resume":
        from adaption_memory.execution import modal

        summary = modal.collect(args.runs / args.run_id / "modal", watch=args.watch)
        if not summary["complete"]:
            print(json.dumps(summary, indent=2))
            return 2
        coordinator.import_modal_memories(args.run_id, preset, args.runs / args.run_id / "modal")
    backend = _backend(preset, args.budget_usd)
    manifest = coordinator.run(args.run_id, preset, backend, allow_paid=args.allow_paid)
    print(json.dumps(manifest.to_dict(), indent=2))
    return 0 if manifest.status.value == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
