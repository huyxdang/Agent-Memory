import json
from pathlib import Path
import tempfile
import unittest

from teacher_traces import Journal, hashes, usage_cost_upper_bound


class TeacherResumeTests(unittest.TestCase):
    def test_usage_pricing_counts_cached_and_reasoning_once(self):
        usage = dict(input_tokens=1000, cached_input_tokens=600, output_tokens=100, reasoning_output_tokens=80)
        self.assertAlmostEqual(usage_cost_upper_bound(usage), .000232)
        self.assertAlmostEqual(usage_cost_upper_bound(dict(input_tokens=300000, output_tokens=100)), .15018)
        with self.assertRaises(ValueError):
            usage_cost_upper_bound(dict(input_tokens=1,cached_input_tokens=2,output_tokens=0))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.config = {'max_output_tokens': 100, 'context_window': 100000}
        self.item = {'haystack_sessions': [[{'role':'user', 'content':'I like tea.'}]],
                     'haystack_dates':['2026-01-01'], 'haystack_session_ids':['s1'],
                     'question':'DO NOT SEND', 'answer':'SECRET'}
        self.response = dict(content='{"narrative":["The user likes tea."],"atomic":[]}',
                             finish_reason='stop', usage={'input_tokens':100,'output_tokens':20})

    def test_completed_resume_does_not_call(self):
        j = Journal(self.path, self.config, 1)
        j.build(self.item, self.config, lambda messages:self.response)
        resumed = Journal(self.path, self.config, 1)
        resumed.build(self.item, self.config, lambda _:self.fail('Duplicate paid call'))
        state = next(iter(resumed.states.values()))
        self.assertEqual(state['sessions_done'], 1)
        self.assertNotIn('SECRET', json.dumps(state))
        self.assertNotIn('DO NOT SEND', json.dumps(state))

    def test_unknown_call_is_not_retried_and_reserve_persists(self):
        j = Journal(self.path, self.config, 1)
        def timeout(_):
            raise TimeoutError()
        j.build(self.item, self.config, timeout)
        used = j.used()
        self.assertGreater(used, 0)
        resumed = Journal(self.path, self.config, 1)
        resumed.build(self.item, self.config, lambda _:self.fail('Unknown call retried'))
        self.assertEqual(resumed.used(), used)
        self.assertEqual(next(iter(resumed.states.values()))['status'], 'needs_reconciliation')

    def test_response_saved_before_crash_is_applied_without_call(self):
        j = Journal(self.path, self.config, 1)
        j.build(self.item, self.config, lambda _:self.response)
        key = hashes(self.item)[0]
        state = j.states[key]
        state.update(lines=[], sessions_done=0, status='running')
        state['calls'][-1]['status'] = 'response_saved'
        j.checkpoint(key)
        resumed = Journal(self.path, self.config, 1)
        resumed.build(self.item, self.config, lambda _:self.fail('Saved response repeated'))
        self.assertEqual(resumed.states[key]['status'], 'complete')

    def test_explicit_abandonment_retains_reserve_and_creates_new_attempt(self):
        j = Journal(self.path, self.config, 1)
        def timeout(_):
            raise TimeoutError()
        j.build(self.item, self.config, timeout)
        state = next(iter(j.states.values()))
        reserved = j.used()
        state['calls'][-1].update(status='abandoned_unknown', resolution='Explicit replacement authorized')
        j.checkpoint(hashes(self.item)[0])
        j.build(self.item, self.config, lambda _: self.response)
        self.assertEqual(state['sessions_done'], 1)
        self.assertEqual(len(state['calls']), 2)
        self.assertEqual(state['calls'][0]['status'], 'abandoned_unknown')
        self.assertGreater(j.used(), reserved)

    def test_budget_blocks_before_call(self):
        j = Journal(self.path, self.config, .00000001)
        j.build(self.item, self.config, lambda _:self.fail('Over-budget call'))
        self.assertEqual(j.used(), 0)
        self.assertEqual(next(iter(j.states.values()))['status'], 'budget_blocked')

    def test_configuration_change_rejected(self):
        Journal(self.path, self.config, 1)
        with self.assertRaises(ValueError):
            Journal(self.path, {**self.config, 'context_window':1}, 1)

    def test_invalid_response_is_preserved_not_applied(self):
        j = Journal(self.path, self.config, 1)
        j.build(self.item, self.config, lambda _:{**self.response, 'content':'not json'})
        state = next(iter(j.states.values()))
        self.assertEqual(state['status'], 'invalid_output')
        self.assertEqual(state['sessions_done'], 0)
        self.assertEqual(state['calls'][0]['response']['content'], 'not json')


if __name__ == '__main__':
    unittest.main()
