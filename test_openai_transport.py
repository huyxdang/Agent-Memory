import unittest
from types import SimpleNamespace

from adaption_memory.inference.openai import BudgetLedger, ChatRequest, OpenAITransport, Price


def response(content="answer", finish_reason="stop"):
    usage = SimpleNamespace(
        prompt_tokens=10,
        completion_tokens=2,
        total_tokens=12,
        prompt_tokens_details=SimpleNamespace(cached_tokens=3),
        completion_tokens_details=SimpleNamespace(reasoning_tokens=1),
    )
    return SimpleNamespace(
        id="response-1",
        model="resolved",
        system_fingerprint="fp",
        usage=usage,
        choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason=finish_reason)],
    )


class FakeCompletions:
    def __init__(self, action):
        self.action = action

    def create(self, **kwargs):
        if isinstance(self.action, Exception):
            raise self.action
        return self.action


class SequenceCompletions:
    def __init__(self, actions):
        self.actions = iter(actions)

    def create(self, **kwargs):
        action = next(self.actions)
        if isinstance(action, Exception):
            raise action
        return action


def client(action):
    return SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(action)))


def request():
    return ChatRequest(
        call_id="call-1",
        model="gpt-5.6-luna",
        system="system",
        user_messages=({"role": "user", "content": "question"},),
        max_output_tokens=32,
        price=Price(1.0, 0.1, 2.0),
    )


class OpenAITransportTests(unittest.TestCase):
    def test_response_is_observed_before_completion(self):
        states = []
        transport = OpenAITransport(client(response()), BudgetLedger(1), lambda call: states.append(call["state"]))

        result = transport.chat(request())

        self.assertEqual(states, ["in_flight", "response_saved", "complete"])
        self.assertTrue(result["ok"])
        self.assertEqual(transport.budget.unknown_or_reserved_exposure_usd, 0)

    def test_transport_error_is_unknown_and_keeps_reservation(self):
        transport = OpenAITransport(client(TimeoutError("late")), BudgetLedger(1), rate_limit_error=KeyError)

        result = transport.chat(request())

        self.assertEqual(result["state"], "unknown_outcome")
        self.assertGreater(transport.budget.unknown_or_reserved_exposure_usd, 0)

    def test_length_output_is_saved_then_invalid(self):
        states = []
        transport = OpenAITransport(client(response("partial", "length")), BudgetLedger(1), lambda call: states.append(call["state"]))

        result = transport.chat(request())

        self.assertEqual(result["state"], "invalid_output")
        self.assertEqual(states[-2:], ["response_saved", "invalid_output"])

    def test_budget_rejection_never_dispatches(self):
        transport = OpenAITransport(client(response()), BudgetLedger(0.000001))

        result = transport.chat(request())

        self.assertEqual(result["state"], "not_dispatched")
        self.assertEqual(result["error_type"], "RuntimeError")

    def test_rate_limit_rejection_is_durable_and_retryable(self):
        class RateLimited(Exception):
            pass

        states = []
        fake = SimpleNamespace(
            chat=SimpleNamespace(completions=SequenceCompletions([RateLimited(), response()]))
        )
        transport = OpenAITransport(
            fake,
            BudgetLedger(1),
            lambda call: states.append(call["state"]),
            sleep=lambda _: None,
            rate_limit_error=RateLimited,
        )

        result = transport.chat(request())

        self.assertTrue(result["ok"])
        self.assertEqual(states[:3], ["in_flight", "not_dispatched", "in_flight"])


if __name__ == "__main__":
    unittest.main()
