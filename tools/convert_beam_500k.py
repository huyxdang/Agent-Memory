"""Convert BEAM 500K chats from the HuggingFace parquet into work/beam/500K/<id>/, the layout the adapter reads.

Chats already on disk are reconverted first and must come out identical; nothing is written otherwise.
Reads work/beam/hf/500K.parquet with pyarrow (installed in the environment, not a runtime dependency).
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

from adaption_memory.config import PROJECT_ROOT

PARQUET = PROJECT_ROOT / "work" / "beam" / "hf" / "500K.parquet"
TARGET = PROJECT_ROOT / "work" / "beam" / "500K"


def convert_chat(batches: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Each batch's flat message list becomes [user, assistant] turns; null fields are dropped."""
    out = []
    for number, batch in enumerate(batches, start=1):
        messages = [{key: value for key, value in message.items() if value is not None} for message in batch]
        anchor = next((message["time_anchor"] for message in messages if message.get("time_anchor")), "")
        out.append({
            "batch_number": number,
            "turns": [messages[index:index + 2] for index in range(0, len(messages), 2)],
            "time_anchor": anchor,
        })
    return out


def chat_files(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "chat.json": convert_chat(row["chat"]),
        "topic.json": row["conversation_seed"],
        "probing_questions/probing_questions.json": ast.literal_eval(row["probing_questions"]),
    }


def load_rows() -> dict[str, dict[str, Any]]:
    import pyarrow.parquet as pq

    return {str(row["conversation_id"]): row for row in pq.read_table(PARQUET).to_pylist()}


def verify_existing(rows: dict[str, dict[str, Any]]) -> list[str]:
    verified = []
    for directory in sorted((path for path in TARGET.iterdir() if path.is_dir() and path.name.isdigit()), key=lambda p: int(p.name)):
        for name, value in chat_files(rows[directory.name]).items():
            if json.loads((directory / name).read_text()) != value:
                raise ValueError(f"Conversion does not reproduce {directory.name}/{name}")
        verified.append(directory.name)
    return verified


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.convert_beam_500k")
    parser.add_argument("--chats", type=int, nargs="+", required=True, help="500K conversation ids to convert")
    args = parser.parse_args(argv)
    rows = load_rows()
    verified = verify_existing(rows)
    written = []
    for chat in args.chats:
        directory = TARGET / str(chat)
        if directory.exists():
            continue
        for name, value in chat_files(rows[str(chat)]).items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        written.append(chat)
    print(json.dumps({"verified": verified, "written": written, "categories": {
        str(chat): rows[str(chat)]["conversation_seed"].get("category") for chat in args.chats}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
