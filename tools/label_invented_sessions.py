"""Label invented single-session conversations with the Luna extractor, producing SFT rows.

Input rows come from an Adaption Invent dataset export. Only the generated conversation is used;
the generator's completion is discarded. Each session is labelled with the repo's own extraction
prompt (empty prior memory, session 1 of 1) and schema, so targets match inference exactly.
"""
from __future__ import annotations

import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

from adaption_memory import memory
from adaption_memory.config import PROJECT_ROOT
from adaption_memory.inference.openai import BudgetLedger, ChatRequest, OpenAITransport, Price
from adaption_memory.inference.vllm import output_valid

SUBJECT = "one user, built from their past conversations with an assistant"
LUNA = Price(0.2, 0.02, 1.2)
DATE_RE = re.compile(r"dated\s+([^\n]+?)(?:\.|\n|$)")


def parse_session(text: str) -> tuple[str, list[dict[str, str]]] | None:
    """Recover (timestamp, turns) from a generated prompt; None when the row is unusable."""
    match = DATE_RE.search(text)
    start = text.find("[")
    if start < 0:
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "[":
            depth += 1
        elif text[index] == "]":
            depth -= 1
            if depth == 0:
                candidate = text[start:index + 1]
                break
    else:
        return None
    try:
        turns = json.loads(candidate)
    except ValueError:
        return None
    if not isinstance(turns, list) or len(turns) < 4:
        return None
    clean = []
    for turn in turns:
        if not isinstance(turn, dict) or turn.get("role") not in {"user", "assistant"} or not isinstance(turn.get("content"), str):
            return None
        clean.append({"role": turn["role"], "content": turn["content"].strip()})
    if not any(t["role"] == "assistant" for t in clean) or not any(t["role"] == "user" for t in clean):
        return None
    timestamp = match.group(1).strip() if match else "2024/03/15 (Fri) 10:00"
    return timestamp, clean


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.label_invented_sessions")
    parser.add_argument("--input", type=Path, required=True, help="JSONL export from datasets.download")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget-usd", type=float, required=True)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    args = parser.parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")
    from openai import OpenAI

    ledger = BudgetLedger(args.budget_usd)
    transport = OpenAITransport(OpenAI(max_retries=0, timeout=300), ledger, reservation_wait_seconds=600.0)
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    lock = threading.Lock()
    out = args.output.open("w")
    stats = {"rows": len(rows), "unparsable": 0, "labelled": 0, "invalid": 0, "failed": 0}

    def label(index: int, row: dict) -> None:
        text = row.get("enhanced_prompt") or row.get("prompt") or ""
        parsed = parse_session(text)
        if parsed is None:
            with lock:
                stats["unparsable"] += 1
            return
        timestamp, turns = parsed
        parts = memory.extraction_parts([], 1, 1, timestamp, turns)
        request = ChatRequest(
            call_id=f"invent:{index}", model="gpt-5.6-luna", system=memory.extraction_system_prompt(SUBJECT),
            user_messages=tuple(memory.extraction_messages(parts)), max_output_tokens=args.max_output_tokens,
            price=LUNA, reasoning_effort="low", response_format=memory.EXTRACTION_RESPONSE_FORMAT,
        )
        call = transport.chat(request)
        if call.get("state") != "complete":
            with lock:
                stats["failed"] += 1
            return
        content = call["content"]
        if not output_valid(content):
            with lock:
                stats["invalid"] += 1
            return
        messages = [{"role": "system", "content": memory.extraction_system_prompt(SUBJECT)}] + [
            {"role": "user", "content": part} for part in parts] + [{"role": "assistant", "content": content}]
        with lock:
            out.write(json.dumps({"messages": messages, "source": "invented", "invent_index": index,
                                  "usage": call.get("usage"), "cost_usd": call.get("cost_usd")}, ensure_ascii=False) + "\n")
            stats["labelled"] += 1

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        list(pool.map(lambda pair: label(*pair), enumerate(rows)))
    out.close()
    stats["known_spend_usd"] = ledger.known_spend_usd
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
