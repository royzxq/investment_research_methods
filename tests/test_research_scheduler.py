import copy
from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile
from pathlib import Path
import unittest
import json
import subprocess
import sys
from unittest.mock import patch

from scripts.research_scheduler import reserve, new_state, merge_candidates, load_state, queue_lock, tick

NOW = datetime(2026, 10, 7, 8, tzinfo=ZoneInfo('Asia/Shanghai'))


def candidates():
    return [dict(task_id=f'SH-{600001+i}', event_key=str(i)*64, priority=p,
                 request=f'/requests/{i}/request.json', request_sha256='a'*64,
                 valuation_date='2026-10-07', created_at=NOW.isoformat(), batch_id=str(i)*32)
            for i, p in enumerate([4, 3, 2, 1, 1, 3, 4])]


class SchedulerTests(unittest.TestCase):
    def test_service_runs_at_five_without_load_or_interval_trigger(self):
        from scripts.install_research_service import service
        plist=service(sys.executable,sys.executable,sys.executable)
        self.assertEqual(plist['StartCalendarInterval'], {'Hour':5,'Minute':0})
        self.assertNotIn('StartInterval',plist)
        self.assertFalse(plist.get('RunAtLoad',False))
        self.assertEqual(plist['EnvironmentVariables']['TZ'],'Asia/Shanghai')

    def test_schedule_replacement_waits_for_active_run(self):
        from scripts import install_research_service as installer
        from types import SimpleNamespace
        import plistlib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            target=root/'Library/LaunchAgents'/f'{installer.LABEL}.plist'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'old-plist')
            calls=[]; prints=iter(['  pid = 123\n','  state = waiting\n'])
            def command(args,**kwargs):
                calls.append(args)
                if args[1]=='print':return SimpleNamespace(stdout=next(prints),returncode=0)
                return SimpleNamespace(returncode=0)
            args=['install','--python',sys.executable,'--codex-cli',sys.executable,
                  '--claude-cli',sys.executable,'--install','--replace-when-idle']
            with patch.object(installer,'ROOT',root),patch.object(installer.Path,'home',return_value=root),\
                 patch.object(installer.subprocess,'run',side_effect=command),\
                 patch.object(installer.time,'sleep') as sleep,patch('scripts.research_scheduler.journal'),\
                 patch.dict(sys.modules,{'research_scheduler':sys.modules['scripts.research_scheduler']}),patch.object(sys,'argv',args):
                installer.main()
            sleep.assert_called_once_with(30)
            self.assertEqual([c[1] for c in calls],['print','print','bootout','enable','bootstrap'])
            self.assertEqual(target.with_suffix('.plist.bak').read_bytes(),b'old-plist')
            self.assertEqual(plistlib.loads(target.read_bytes())['StartCalendarInterval'],{'Hour':5,'Minute':0})

    def test_scheduled_empty_check_is_durable_and_not_repeated(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            result=tick(root/'exchange',root,execute=True,clis={},once_daily=True,event_log=root/'events.jsonl')
            self.assertEqual(result['used'],0)
            self.assertTrue((root/'output/research_queue/daily-check.json').exists())
            with patch('scripts.research_scheduler.scan_requests',side_effect=AssertionError('second scan')):
                again=tick(root/'exchange',root,execute=True,clis={},once_daily=True,event_log=root/'events.jsonl')
            self.assertEqual(again['status'],'already_checked')
            phases=[json.loads(line)['event'] for line in (root/'events.jsonl').read_text().splitlines()]
            self.assertIn('no_research',phases)
            self.assertIn('already_checked',phases)

    def test_corrupt_daily_marker_stops_before_reserving(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); queue=root/'output/research_queue'; queue.mkdir(parents=True)
            (queue/'daily-check.json').write_text(json.dumps({'checked_on':123,'checked_at':NOW.isoformat()}))
            with self.assertRaisesRegex(ValueError,'daily research check'):
                tick(root/'exchange',root,execute=True,clis={},once_daily=True,event_log=root/'events.jsonl')
            self.assertFalse((queue/'state.json').exists())

    def test_manual_handoff_blocks_same_event_but_allows_new_evidence(self):
        state = new_state()
        record = candidates()[3]
        held = {(record['task_id'], record['event_key'])}
        merge_candidates(state, [record], NOW)
        self.assertEqual(reserve(state, NOW, held=held), [])
        fresh = dict(record, valuation_date='2026-10-08', created_at=NOW.replace(day=8).isoformat())
        merge_candidates(state, [fresh], NOW.replace(day=8))
        self.assertEqual(reserve(state, NOW.replace(day=8), held=held), [])
        fresh['event_key'] = 'f'*64
        merge_candidates(state, [fresh], NOW.replace(day=8))
        self.assertEqual(len(reserve(state, NOW.replace(day=8), held=held)), 1)

    def test_held_interrupted_task_does_not_resume_or_require_clis(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue = root/'output/research_queue'
            queue.mkdir(parents=True)
            state = new_state()
            merge_candidates(state, [candidates()[3]], NOW)
            entry = reserve(state, NOW)[0]
            entry['status'] = 'interrupted'
            (queue/'state.json').write_text(json.dumps(state))
            hold = dict(event_key=entry['event_key'], reason='user manually started both providers', created_at=NOW.isoformat())
            (queue/'manual_holds.json').write_text(json.dumps(dict(schema_version='research-manual-holds/v1', tasks={entry['task_id']:hold})))
            result = tick(root/'exchange', root, execute=True, clis={})
            self.assertEqual(result['manual_held'], [entry['task_id']])
            self.assertEqual(result['failures'], [])
            saved = json.loads((queue/'state.json').read_text())
            self.assertEqual(saved['days']['2026-10-07'], state['days']['2026-10-07'])
            self.assertEqual(json.loads((queue/'refresh-needed.json').read_text()), [])

    def test_manual_hold_is_applied_to_plan_and_corruption_stops_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue = root/'output/research_queue'
            queue.mkdir(parents=True)
            now = datetime.now(ZoneInfo('Asia/Shanghai'))
            record = dict(candidates()[3], valuation_date=now.date().isoformat(), created_at=now.isoformat())
            hold = dict(event_key=record['event_key'], reason='manual research', created_at=NOW.isoformat())
            path = queue/'manual_holds.json'
            path.write_text(json.dumps(dict(schema_version='research-manual-holds/v1', tasks={record['task_id']:hold})))
            with patch('scripts.research_scheduler.scan_requests', return_value=([record], [])):
                result = tick(root/'exchange', root)
            self.assertEqual(result['manual_held'], [record['task_id']])
            self.assertEqual(result['selected'], [])
            self.assertFalse((queue/'state.json').exists())
            path.unlink()
            with patch('scripts.research_scheduler.scan_requests', return_value=([record], [])):
                self.assertEqual(len(tick(root/'exchange', root)['selected']), 1)
            hold['event_key'] = 'invalid'
            path.write_text(json.dumps(dict(schema_version='research-manual-holds/v1', tasks={record['task_id']:hold})))
            with self.assertRaisesRegex(ValueError, 'manual hold'):
                tick(root/'exchange', root, execute=True, clis={})

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
