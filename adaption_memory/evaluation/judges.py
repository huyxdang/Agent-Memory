from __future__ import annotations

import re
from typing import Any


LONGMEMEVAL_JUDGE_PROMPT = """I will give you a question, a correct answer (or rubric), and a model response. Decide whether the model response is correct.

CORE PRINCIPLE — Semantic equivalence: Judge by MEANING, not exact words. Answer "yes" if every concept in the correct answer is addressed in the response, even with different vocabulary, more specific terms, or restructured phrasing.

IMPORTANT BIAS CHECK: You have a tendency to say "no" too quickly. Before concluding "no", you MUST verify the answer is truly wrong, not just differently worded. When in doubt, lean toward "yes".

Rules:

**Equivalence & Supersets**
- Equivalent or superset responses are correct. Extra details are fine unless proven to be factually wrong. Extra qualifiers are fine unless proven to be wrong. E.g., "a blue dress and a matching necklace" is correct when the answer is "a blue dress."
- If a response captures the most specific part (exact item/place/name) but omits a broader container, it's correct.
- Same factual meaning with different phrasing = correct (e.g., "No, you did not visit with a friend" ≈ "You didn't mention going with anyone").
- Adding scope qualifiers like "regular-season" or "excluding X" is fine as long as the core value is correct. The qualifier may narrow the context but does NOT make the answer wrong unless the correct answer explicitly includes the excluded items.

**Lists & Compound Terms**
- For list answers, match each item by semantic meaning. A concept is covered if restated via synonyms, sub-concepts, or related terms. Adding methodological detail or rewording verbs to near-synonyms is acceptable.
- A broad term like "A and B significance" is covered if the response addresses the topic area through related specific terms, even without naming each component literally.
- If some items as listed as "or"s, "maybe"s and potential answers, it's okay if the answer does not include those.
- If two items in a list achieve the same purpose, listing just one of them is fine.

IMPORTANT: The "anti-preference" items are very specific!
Eg. Someone "not interested in general AI topics" could be very interested in specific AI topics in general AI *conferences*; those are not the same thing and should be accepted! topics != conferences

**Numbers & Precision**
- Hedging ("at least 3", "approximately") is fine if the core number matches. A range that includes the correct answer is correct.
Generally, if the user themself would be satisfied by the response, it is acceptable. Ie. If the answer is conditional on information they would have (eg. their birthday, some hidden dependent information), and would be correct with that information, that is acceptable.
- More precise answers are correct: "22 days" matches "3 weeks"; "over $270" matches "$270."; "9 1/2 months" matches "9 months";

- Rough answers are correct: "about nine months" ≈ "9 months; "8 months and 20 days" matches "9 months";

- Off-by-one errors on days/weeks/months are acceptable.
- Approximate unit conversions are equivalent: "14 weeks" ≈ "3 months", "6 months" ≈ "half a year."
- Round time ranges generously: 7 months and 16 days ≈ 8 months.
- Notes instead of chords are acceptable when justified
- A correct number with added context (e.g., "about 5 months ago (around December 2022)") is correct — the parenthetical date is supplementary, not a contradiction.

**Dates & Temporal**
- Date format variations are equivalent: "February 1st" = "Feb 1, 2023" = "on February 1."
- Same-day event ordering swaps are acceptable.
- Outdated info alongside the correct updated answer is acceptable if the current value is identified.
- "recent" is upto 6 years ago, which means 2017+
- References like "last weekend", "last Wednesday", etc. are imprecise - people sometimes mean the weekend/Wednesday before the latest one if they're near it. "Last 3 months" can include boundary days of the 4th month back. "Last month" includes the current month so far. Be flexible with such timestamps

**Counting Edge Cases**
- If correct answer is "0" or "nothing found," model saying "not enough information" is also correct.
- Similarly, If correct answer is "not enough information", model saying "0" or "nothing found," is also correct.

**Preference/Personalization Rubrics** (apply in order):
1. Correct if the response demonstrates awareness of user's personal context (preferences, habits, interests). Need not satisfy every rubric point.
2. Primary criterion: do main suggestions align with what the user WANTS?
3. Anti-preferences: evaluate the OVERALL thrust, not keyword scanning. If the response largely suggests correct options, minor incidental references to "not-preferred" things are fine.
4. Mentioning a phone app as a MEANS to a preferred activity (e.g., meditation app for sleep) is not "suggesting phone use." Judge by the activity, not delivery mechanism.
5. "May not prefer" = mild preference, not hard prohibition. Secondary/context-dependent inclusion is fine.
6. Explicit acknowledgment of anti-preferences (e.g., "keep screens off") strengthens correctness.
7. Context-dependent suggestions are acceptable (reading is fine on a bus even if rubric flags visual attention activities). Adjacent genres alongside preferred ones are additive, not contradictory.
8. If the rubric mentions specific user resources/tools (e.g., "Suica card", "TripIt app"), the response is correct if it demonstrates awareness of the user's MAIN personal context even if it does not name every specific tool. The rubric is a guide, not a checklist.

**Abstention Matching**
- If correct answer = unanswerable/abstention, ANY phrasing that conveys "I don't have this information" is correct, regardless of what partial context is mentioned or omitted.
- Saying "not enough information" while mentioning partial related context = correct abstention.
- Saying "no record of X" or "only have plans for X, not actual dates" = correct abstention.
- The key test: does the response REFUSE to answer the question? If yes, it matches an abstention ground truth, period.

FINAL CHECK: Before answering "no," you MUST reason through these steps:
1. What is the core factual claim or intent of the correct answer?
2. Does the model response address that same claim, even in different words?
3. Is the response a superset (correct answer + extra details)?
4. For numbers: does the core number match, ignoring hedging/qualifiers?
5. For abstentions: does the response effectively decline to answer?
Only answer "no" if, after this analysis, a core concept is entirely unaddressed or contradicted.

Question: {question}

Correct Answer: {answer}

Model Response: {response}

Think step-by-step in <judge_thinking> tags, then give your final verdict as exactly "yes" or "no" on a new line after the closing tag."""


VALIDATION_CASES = (
    {
        "question_id": "e47becba",
        "question": "What degree did I graduate with?",
        "reference_answer": "Business Administration",
        "cases": (
            ("known_correct", "Business Administration", "yes"),
            ("correct_paraphrase", "I graduated with a degree in Business Administration.", "yes"),
            ("clearly_wrong", "I graduated with a Computer Science degree.", "no"),
        ),
    },
    {
        "question_id": "6a1eabeb",
        "question": "What was my personal best time in the charity 5K run?",
        "reference_answer": "25 minutes and 50 seconds (or 25:50)",
        "cases": (
            ("known_correct", "25 minutes and 50 seconds", "yes"),
            ("correct_paraphrase", "My best was 25:50.", "yes"),
            ("clearly_wrong", "My personal best was 31 minutes.", "no"),
        ),
    },
)


def parse_locomo_label(raw: str) -> str:
    match = re.search(r'"label"\s*:\s*"(CORRECT|WRONG)"', raw, re.I)
    if not match:
        found = re.findall(r"\b(CORRECT|WRONG)\b", raw)
        if len(set(found)) != 1:
            return "invalid"
        label = found[-1]
    else:
        label = match.group(1)
    return "yes" if label.upper() == "CORRECT" else "no"


def parse_beam_score(raw: str) -> float | None:
    match = re.search(r'"score"\s*:\s*([0-9.]+)', raw)
    if not match:
        return None
    try:
        score = float(match.group(1))
    except ValueError:
        return None
    return min((0.0, 0.5, 1.0), key=lambda level: abs(level - score))


def parse_yes_no(raw: str) -> str:
    text = raw.strip()
    if not text:
        return "invalid"
    after_reasoning = re.split(r"</judge_thinking>|</thinking>", text, flags=re.IGNORECASE)
    verdict_region = after_reasoning[-1].strip() if after_reasoning else text
    verdict_lines = [line.strip().lower() for line in verdict_region.splitlines() if line.strip()]
    for line in reversed(verdict_lines):
        if line in {"yes", "no"}:
            return line
    matches = re.findall(r"\b(yes|no)\b", verdict_region.lower())
    if matches:
        return matches[-1]
    lowered = text.lower()
    if lowered.startswith("yes"):
        return "yes"
    if lowered.startswith("no"):
        return "no"
    return "invalid"


def judge_explanation(raw: str) -> str | None:
    match = re.search(r"<(?:judge_thinking|thinking)>(.*?)</(?:judge_thinking|thinking)>", raw, re.I | re.S)
    return match.group(1).strip() if match else None


def judge_prompt(item: dict[str, Any], response: str) -> tuple[str, str]:
    return judge_requests(item, response)[0]


def judge_requests(item: dict[str, Any], response: str) -> list[tuple[str, str]]:
    judge = item.get("judge", "longmemeval")
    if judge == "longmemeval":
        return [("", LONGMEMEVAL_JUDGE_PROMPT.format(
            question=item["question"], answer=str(item["answer"]), response=response
        ))]
    if judge == "locomo":
        from third_party.mem0 import locomo_prompts

        prompt = locomo_prompts.get_judge_prompt(
            question=item["question"],
            answer=str(item["answer"]),
            response=response,
        )
        return [(locomo_prompts.JUDGE_SYSTEM_PROMPT, prompt)]
    if judge == "beam":
        from third_party.mem0 import beam_prompts

        rubric = item.get("rubric") or (str(item["answer"]),)
        return [
            (
                beam_prompts.BEAM_JUDGE_SYSTEM_PROMPT,
                beam_prompts.get_beam_nugget_judge_prompt(item["question"], nugget, response),
            )
            for nugget in rubric
        ]
    raise ValueError(f"Unsupported judge: {judge!r}")


def parse_judge(judge: str, raw: str) -> tuple[str, float | None]:
    if judge == "longmemeval":
        verdict = parse_yes_no(raw)
        return verdict, 1.0 if verdict == "yes" else 0.0 if verdict == "no" else None
    if judge == "locomo":
        verdict = parse_locomo_label(raw)
        return verdict, 1.0 if verdict == "yes" else 0.0 if verdict == "no" else None
    if judge == "beam":
        score = parse_beam_score(raw)
        return "invalid" if score is None else "yes" if score == 1.0 else "partial" if score == 0.5 else "no", score
    raise ValueError(f"Unsupported judge: {judge!r}")
