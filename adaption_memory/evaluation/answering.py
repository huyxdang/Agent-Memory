from __future__ import annotations

import json
from typing import Any

from adaption_memory.history import sanitize_history


ANSWER_SYSTEM_PROMPT_V1 = (
    "Answer the question using only the complete timestamped conversation history. "
    "Be direct and concise. If the history does not contain enough information, say so."
)
ANSWER_SYSTEM_PROMPT_V2 = """Answer the question using only the complete timestamped conversation history. Each session carries its timestamp; assistant turns record what the assistant itself recommended, listed, or wrote for the user.

- For advice or recommendation questions, tailor the answer to the user's stated preferences, interests, possessions, and past choices, and name the parts of the history you are using. Do not decline over missing incidental details such as the user's location; make reasonable suggestions from what is known.
- For questions that count things or compute dates or durations, first list the relevant turns with their session dates, then do the arithmetic, then give the answer.
- For questions about what the assistant said or recommended earlier, use the assistant turns.
- Otherwise be direct and concise. If the history truly does not contain the information, say so."""
ANSWER_SYSTEM_PROMPTS = {"v1": ANSWER_SYSTEM_PROMPT_V1, "v2": ANSWER_SYSTEM_PROMPT_V2}
ANSWER_PROMPT_FORMAT = (
    "Question date: {question_date}\n\n"
    "Conversation history (chronological JSON):\n{history}\n\n"
    "Question: {question}"
)


def tokenizer(name: str) -> Any:
    import tiktoken

    return tiktoken.get_encoding(name)


def token_count(encoding: Any, *parts: str) -> int:
    return sum(len(encoding.encode(part, disallowed_special=())) for part in parts) + 12


def fit_check(input_tokens: int, max_output_tokens: int, context_window: int) -> dict[str, Any]:
    framing_margin = 256
    total = input_tokens + max_output_tokens + framing_margin
    return {
        "input_tokens_estimated": input_tokens,
        "max_output_tokens": max_output_tokens,
        "framing_margin_tokens": framing_margin,
        "context_window_tokens": context_window,
        "total_reserved_tokens": total,
        "remaining_tokens": context_window - total,
        "fits": total <= context_window,
    }


def context_text_from_prompt(prompt: str) -> str:
    suffix = "\n\nQuestion: "
    for marker in (
        "Conversation history (chronological JSON):\n",
        "earlier sessions (kind | session | date | content):\n",
        "oldest first; date | memory):\n",
    ):
        if marker in prompt:
            return prompt.split(marker, 1)[1].rsplit(suffix, 1)[0]
    raise RuntimeError("Could not isolate the context block from the answer prompt")


def check_no_label_leak(prompt: str) -> None:
    forbidden = ('"has_answer":', '"answer_session_ids":', '"question_type":', '"answer":')
    leaked = [key for key in forbidden if key in prompt]
    if leaked:
        raise RuntimeError(f"Evaluation label leaked into prompt: {leaked}")


def build_full_history_prompt(item: dict[str, Any]) -> tuple[str, dict[str, int]]:
    history = sanitize_history(item)
    history_json = json.dumps(history, ensure_ascii=False, separators=(",", ":"))
    prompt = ANSWER_PROMPT_FORMAT.format(
        question_date=item["question_date"], history=history_json, question=item["question"]
    )
    check_no_label_leak(prompt)
    source_turns = sum(len(session) for session in item["haystack_sessions"])
    clean_turns = sum(len(session["messages"]) for session in history)
    if len(history) != len(item["haystack_sessions"]) or clean_turns != source_turns:
        raise RuntimeError(f"History was not preserved completely for {item['question_id']}")
    return prompt, {"sessions": len(history), "turns": clean_turns}
