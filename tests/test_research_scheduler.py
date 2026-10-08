import copy
from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile
from pathlib import Path
import unittest
import json
import subprocess
import sys

from scripts.research_scheduler import reserve, new_state, merge_candidates, load_state, queue_lock, tick

NOW = datetime(2026, 10, 7, 8, tzinfo=ZoneInfo('Asia/Shanghai'))


def candidates():
    return [dict(task_id=f'SH-{600001+i}', event_key=str(i)*64, priority=p,
                 request=f'/requests/{i}/request.json', request_sha256='a'*64,
                 valuation_date='2026-10-07', created_at=NOW.isoformat(), batch_id=str(i)*32)
            for i, p in enumerate([4, 3, 2, 1, 1, 3, 4])]


class SchedulerTests(unittest.TestCase):
    def test_corrupt_or_missing_durable_budget_is_not_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'initialized.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'missing'):
                load_state(root/'state.json')
            state = new_state()
            state['days']['2026-10-07'] = []
            (root/'state.json').write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, 'budget'):
                load_state(root/'state.json')

    def test_concurrent_process_cannot_reserve_again(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with queue_lock(root):
                result = subprocess.run([sys.executable, '-c',
                    'import fcntl,sys; f=open(sys.argv[1],"a"); fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)',
                    str(root/'queue.lock')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'BlockingIOError', result.stderr)

    def test_no_work_does_not_require_models(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = tick(root/'exchange', root, execute=True, clis={})
            self.assertEqual(result['used'], 0)
            self.assertEqual(result['failures'], [])

    def test_four_in_priority_order_and_remaining_wait(self):
        state = new_state()
        merge_candidates(state, candidates(), NOW)
        chosen = reserve(state, NOW)
        self.assertEqual([r['task_id'] for r in chosen],
                         ['SH-600004', 'SH-600005', 'SH-600003', 'SH-600002'])
        self.assertEqual(reserve(copy.deepcopy(state), NOW), [])
        self.assertEqual(len([e for e in state['entries'].values() if e['status']=='pending']), 3)

    def test_five_and_six_also_cap_at_four(self):
        for n in (5, 6):
            state = new_state()
            merge_candidates(state, candidates()[:n], NOW)
            self.assertEqual(len(reserve(state, NOW)), 4)

    def test_failure_does_not_refund_and_new_batch_same_security_cannot_bypass(self):
        state = new_state()
        merge_candidates(state, candidates(), NOW)
        selected = reserve(state, NOW)
        for entry in selected:
            entry['status'] = 'failed'
        changed = candidates()
        changed[0]['event_key'] = 'f'*64
        merge_candidates(state, changed, NOW)
        self.assertEqual(reserve(state, NOW), [])

    def test_next_day_requires_new_input_and_preserves_waiting_order(self):
        state = new_state()
        merge_candidates(state, candidates(), NOW)
        tomorrow = NOW.replace(day=8)
        self.assertEqual(reserve(state, tomorrow), [])
        fresh = candidates()
        for entry in fresh:
            entry['valuation_date'] = '2026-10-08'
            entry['created_at'] = tomorrow.isoformat()
        merge_candidates(state, fresh, tomorrow)
        self.assertEqual(len(reserve(state, tomorrow)), 4)
        self.assertTrue(all(e['first_seen']==NOW.isoformat() for e in state['entries'].values()))
