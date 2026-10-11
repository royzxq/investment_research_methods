import copy
import hashlib
from datetime import datetime, timedelta
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
    def test_service_wakes_clock_gate_without_load_or_interval_trigger(self):
        from scripts.install_research_service import service
        plist=service(sys.executable,sys.executable,sys.executable)
        self.assertEqual(plist['StartCalendarInterval'], [{'Minute': m} for m in (0, 15, 30, 45)])
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
            self.assertEqual(plistlib.loads(target.read_bytes())['StartCalendarInterval'], [{'Minute': m} for m in (0, 15, 30, 45)])

    def test_scheduled_empty_check_is_durable_and_not_repeated(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with patch('scripts.research_scheduler.datetime', wraps=datetime) as clock:
                clock.now.return_value = NOW  # 08:00 Shanghai, after the daily 05:00 gate.
                result=tick(root/'exchange',root,execute=True,clis={},once_daily=True,event_log=root/'events.jsonl')
                self.assertEqual(result['used'],0)
                self.assertTrue((root/'output/research_queue/daily-check.json').exists())
                with patch('scripts.research_scheduler.scan_requests',side_effect=AssertionError('second scan')):
                    again=tick(root/'exchange',root,execute=True,clis={},once_daily=True,event_log=root/'events.jsonl')
            self.assertEqual(again['status'],'already_checked')
            phases=[json.loads(line)['event'] for line in (root/'events.jsonl').read_text().splitlines()]
            self.assertIn('no_research',phases)
            self.assertIn('already_checked',phases)

    def test_calendar_wakeups_only_scan_once_from_shanghai_five(self):
        from scripts.install_research_service import service
        from scripts import research_scheduler as scheduler
        alarms = service(sys.executable, sys.executable, sys.executable)['StartCalendarInterval']
        for host in ('America/Los_Angeles', 'Europe/London', 'Asia/Kathmandu', 'Pacific/Chatham'):
            for day in (datetime(2026, 1, 9, tzinfo=ZoneInfo('Asia/Shanghai')),
                        datetime(2026, 7, 9, tzinfo=ZoneInfo('Asia/Shanghai'))):
                with self.subTest(host=host, day=day), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    due = day.replace(hour=5)
                    local_due = due.astimezone(ZoneInfo(host))
                    self.assertTrue(any(alarm.get('Minute') == local_due.minute
                                        and ('Hour' not in alarm or alarm['Hour'] == local_due.hour)
                                        for alarm in alarms))
                    with patch.object(scheduler, 'datetime') as clock, \
                         patch.object(scheduler, 'scan_requests', return_value=([], [])) as scan:
                        instant = due - timedelta(seconds=1)
                        clock.now.side_effect = lambda zone: instant.astimezone(zone)
                        before = tick(root/'exchange', root, execute=True, clis={}, once_daily=True)
                        self.assertEqual(before['status'], 'not_due')
                        self.assertFalse((root/'output').exists())
                        scan.assert_not_called()
                        instant = due
                        at_five = tick(root/'exchange', root, execute=True, clis={}, once_daily=True)
                        self.assertEqual(at_five['used'], 0)
                        scan.assert_called_once()
                        instant += timedelta(minutes=15)
                        after = tick(root/'exchange', root, execute=True, clis={}, once_daily=True)
                        self.assertEqual(after['status'], 'already_checked')
                        scan.assert_called_once()

    def test_late_wakeup_catches_up_and_next_day_still_waits_until_five(self):
        from scripts import research_scheduler as scheduler
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(scheduler, 'datetime') as clock, \
                 patch.object(scheduler, 'scan_requests', return_value=([], [])) as scan:
                clock.now.return_value = NOW.replace(hour=10)
                tick(root/'exchange', root, execute=True, clis={}, once_daily=True)
                scan.assert_called_once()
                marker = root/'output/research_queue/daily-check.json'
                before = marker.read_bytes()
                clock.now.return_value = (NOW+timedelta(days=1)).replace(hour=4)
                self.assertEqual(tick(root/'exchange', root, execute=True, clis={}, once_daily=True)['status'], 'not_due')
                self.assertEqual(marker.read_bytes(), before)
                clock.now.return_value = (NOW+timedelta(days=1)).replace(hour=5)
                tick(root/'exchange', root, execute=True, clis={}, once_daily=True)
                self.assertEqual(scan.call_count, 2)
                self.assertEqual(json.loads(marker.read_text())['checked_on'], '2026-10-08')

    def test_stopped_unlaunched_held_entries_allow_fresh_evidence(self):
        from scripts import research_scheduler as scheduler
        for status in ('reserved', 'running', 'interrupted'):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                queue = root/'output/research_queue'
                queue.mkdir(parents=True)
                state = new_state()
                old = candidates()[3]
                merge_candidates(state, [old], NOW)
                entry = reserve(state, NOW)[0]
                entry['status'] = status
                (queue/'state.json').write_text(json.dumps(state))
                hold = dict(event_key=old['event_key'], reason='manual handoff', created_at=NOW.isoformat())
                (queue/'manual_holds.json').write_text(json.dumps(dict(schema_version='research-manual-holds/v1',
                                                                     tasks={entry['task_id']: hold})))
                fresh = dict(old, event_key='f'*64, batch_id='c'*32, request_sha256='c'*64,
                             created_at=(NOW+timedelta(minutes=1)).isoformat())
                with patch.object(scheduler, 'datetime') as clock, \
                     patch.object(scheduler, 'scan_requests', return_value=([fresh], [])):
                    clock.now.return_value = NOW+timedelta(minutes=2)
                    result = tick(root/'exchange', root)
                self.assertEqual([e['batch_id'] for e in result['selected']], ['c'*32])
                self.assertEqual(result['manual_held'], [])
                self.assertEqual(json.loads((queue/'state.json').read_text()), state, 'Plan must remain read-only')
                # The same held evidence still cannot re-enter after retirement.
                with patch.object(scheduler, 'datetime') as clock, \
                     patch.object(scheduler, 'scan_requests', return_value=([old], [])):
                    clock.now.return_value = NOW+timedelta(minutes=2)
                    self.assertEqual(tick(root/'exchange', root)['selected'], [])

    def test_unheld_active_entry_is_not_replaced_by_fresh_evidence(self):
        state = new_state()
        old = candidates()[3]
        merge_candidates(state, [old], NOW)
        reserve(state, NOW)[0]['status'] = 'interrupted'
        fresh = dict(old, event_key='f'*64, batch_id='c'*32, request_sha256='c'*64,
                     created_at=(NOW+timedelta(minutes=1)).isoformat())
        merge_candidates(state, [fresh], NOW+timedelta(minutes=2))
        self.assertEqual(state['entries'][old['task_id']]['batch_id'], old['batch_id'])

    def test_corrupt_daily_marker_stops_before_reserving(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); queue=root/'output/research_queue'; queue.mkdir(parents=True)
            (queue/'daily-check.json').write_text(json.dumps({'checked_on':123,'checked_at':NOW.isoformat()}))
            with patch('scripts.research_scheduler.datetime', wraps=datetime) as clock:
                clock.now.return_value = NOW  # Reach marker validation regardless of the CI run hour.
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
            self.assertEqual(saved['days']['2026-10-07'], {})
            self.assertEqual(saved['entries'][entry['task_id']]['status'], 'pending')
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


class CooldownTests(unittest.TestCase):
    def history(self, started=NOW):
        return dict(started_at=started.isoformat(), batch_id='a'*32, request_sha256='b'*64)

    def prior_run(self, root, task='SH-600004', *, pid=321, generator='codex', started=NOW, exact=True):
        run = root/'output/runs/investment/2026-10-07'/('a'*32)
        pack = run/'packs'/f'{task}.md'
        pack.parent.mkdir(parents=True, exist_ok=True)
        market, code = task.split('-')
        pack.write_text(f'# {code}.{market} 量价与基本面数据包\n')
        request = dict(schema_version='stock-research-request/v1', batch_id='a'*32,
                       created_at=NOW.isoformat(), valuation_date='2026-10-07', generators=['codex','claude'],
                       tasks=[dict(task_id=task, code=f'{code}.{market}', name='fixture', sources=['monitor'],
                                   data_pack=dict(path=f'packs/{task}.md', sha256=hashlib.sha256(pack.read_bytes()).hexdigest()),
                                   data_pack_meta={})])
        raw = json.dumps(request).encode()
        (run/'request.json').write_bytes(raw)
        folder = run/'execution'/task/generator
        folder.mkdir(parents=True, exist_ok=True)
        (folder/'launched.json').write_text(json.dumps(dict(claimed_at=NOW.isoformat(), request_sha256=hashlib.sha256(raw).hexdigest())))
        (folder/'process.json').write_text(json.dumps(dict(task_id=task, generator=generator, status='failed',
            started_at=started.isoformat(), completed_at=(started+timedelta(minutes=1)).isoformat(), pid=pid, exit_code=3,
            **({'launched_at':started.isoformat()} if exact and pid is not None else {}))))
        return run, hashlib.sha256(raw).hexdigest()

    def test_new_event_and_batch_cannot_bypass_exact_seven_days(self):
        state = new_state()
        state['last_started'] = {'SH-600004': self.history()}
        fresh = dict(candidates()[3], created_at=(NOW+timedelta(days=7)).isoformat(),
                     valuation_date='2026-10-14', event_key='f'*64, batch_id='c'*32)
        merge_candidates(state, [fresh], NOW+timedelta(days=7))
        before = NOW+timedelta(days=7)-timedelta(microseconds=1)
        self.assertEqual(reserve(copy.deepcopy(state), before), [])
        self.assertEqual([e['task_id'] for e in reserve(state, NOW+timedelta(days=7))], ['SH-600004'])

    def test_filter_before_priority_limit_and_a_h_are_separate(self):
        state = new_state()
        state['last_started'] = {'SH-600004': self.history()}
        tomorrow = NOW+timedelta(days=1)
        fresh = [dict(e, valuation_date='2026-10-08', created_at=tomorrow.isoformat()) for e in candidates()]
        merge_candidates(state, fresh+[dict(fresh[3], task_id='HK-60004', priority=1)], tomorrow)
        chosen = reserve(state, tomorrow)
        self.assertEqual([e['task_id'] for e in chosen], ['HK-60004','SH-600005','SH-600003','SH-600002'])
        self.assertEqual(state['entries']['SH-600004']['status'], 'pending')

    def test_legacy_state_plan_uses_failed_process_start_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.prior_run(root)
            queue = root/'output/research_queue'; queue.mkdir(parents=True)
            state = new_state(); state.pop('last_started', None)
            state['days']['2026-10-07'] = {'SH-600004':'e'*64}
            path = queue/'state.json'; path.write_text(json.dumps(state)); before = path.read_bytes()
            fresh = dict(candidates()[3], valuation_date='2026-10-08', created_at=(NOW+timedelta(days=1)).isoformat())
            with patch('scripts.research_scheduler.datetime') as clock, patch('scripts.research_scheduler.scan_requests',return_value=([fresh], [])):
                clock.now.return_value = NOW+timedelta(days=1)
                result = tick(root/'exchange', root)
            self.assertEqual(result['selected'], [])
            self.assertEqual(result['cooldown_skipped'][0]['next_eligible_at'], '2026-10-14T08:00:00+08:00')
            self.assertEqual(path.read_bytes(), before)

    def test_pure_preflight_failure_does_not_start_cooldown(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.prior_run(root, pid=None)
            fresh = dict(candidates()[3], valuation_date='2026-10-08', created_at=(NOW+timedelta(days=1)).isoformat())
            with patch('scripts.research_scheduler.datetime') as clock, patch('scripts.research_scheduler.scan_requests',return_value=([fresh], [])):
                clock.now.return_value = NOW+timedelta(days=1)
                result = tick(root/'exchange', root)
            self.assertEqual(len(result['selected']), 1)
            self.assertEqual(result['cooldown_skipped'], [])

    def test_two_providers_use_first_start_and_run_saves_migration_without_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.prior_run(root)
            self.prior_run(root, generator='claude', started=NOW+timedelta(hours=2))
            queue = root/'output/research_queue'; queue.mkdir(parents=True)
            state = new_state(); state.pop('last_started', None)
            state['days']['2026-10-07'] = {'SH-600004':'e'*64}
            (queue/'state.json').write_text(json.dumps(state))
            with patch('scripts.research_scheduler.datetime') as clock:
                clock.now.return_value = NOW+timedelta(days=1)
                tick(root/'exchange', root, execute=True, clis={})
            saved = load_state(queue/'state.json')
            self.assertEqual(saved['last_started']['SH-600004']['started_at'], NOW.isoformat())
            self.assertEqual(saved['days'], state['days'])

    def test_unlaunched_reservation_respects_history_and_releases_slot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.prior_run(root)
            queue = root/'output/research_queue'; queue.mkdir(parents=True)
            now = NOW+timedelta(days=1)
            record = dict(candidates()[3], valuation_date='2026-10-08', created_at=now.isoformat(), batch_id='c'*32)
            state = new_state(); merge_candidates(state, [record], now); reserve(state, now)
            (queue/'state.json').write_text(json.dumps(state))
            with patch('scripts.research_scheduler.datetime') as clock:
                clock.now.return_value = now
                result = tick(root/'exchange', root, execute=True, clis={})
            self.assertEqual(result['used'], 0)
            self.assertEqual(result['failures'], [])
            self.assertEqual(load_state(queue/'state.json')['entries'][record['task_id']]['status'], 'pending')

    def test_started_same_round_resume_is_allowed_and_does_not_move_start(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); run, digest = self.prior_run(root)
            queue = root/'output/research_queue'; queue.mkdir(parents=True)
            record = dict(candidates()[3], request=str(run/'request.json'), batch_id='a'*32, request_sha256=digest)
            state = new_state(); merge_candidates(state, [record], NOW); entry = reserve(state, NOW)[0]
            entry['status'] = 'interrupted'; (queue/'state.json').write_text(json.dumps(state))
            def finish(entry, *args):
                entry.update(status='failed', sealed='fixture')
            with patch('scripts.research_scheduler.datetime') as clock, patch('scripts.research_scheduler.check_codex_cli'), \
                 patch('scripts.research_scheduler.prepare_entry', return_value=({'generators':['codex','claude']},b'',run)), \
                 patch('scripts.research_scheduler.run_provider_entry', return_value=('failed',{})) as dispatch, \
                 patch('scripts.research_scheduler.seal_entry', side_effect=finish):
                clock.now.return_value = NOW+timedelta(days=1)
                tick(root/'exchange', root, execute=True, clis={'codex':sys.executable,'claude':sys.executable})
            self.assertEqual(dispatch.call_count,2)
            saved = load_state(queue/'state.json')
            self.assertEqual(saved['last_started'][entry['task_id']]['started_at'], NOW.isoformat())
            self.assertEqual(saved['days']['2026-10-07'], state['days']['2026-10-07'])
            self.assertEqual(len(saved['days'].get('2026-10-08', {})), 0)

    def test_corrupt_start_history_is_not_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'state.json'; state = new_state()
            state['last_started'] = {'SH-600004':dict(self.history(), started_at='bad')}
            path.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, 'start|timestamp'):
                load_state(path)


    def test_all_trigger_priorities_defer_and_log_without_requiring_clis(self):
        for priority in range(1, 5):
            with self.subTest(priority=priority), tempfile.TemporaryDirectory() as temp:
                root = Path(temp); self.prior_run(root)
                now = NOW+timedelta(days=1)
                record = dict(candidates()[3], priority=priority, valuation_date='2026-10-08',
                              created_at=now.isoformat(), batch_id='d'*32, event_key='f'*64)
                with patch('scripts.research_scheduler.datetime') as clock, \
                     patch('scripts.research_scheduler.scan_requests', return_value=([record], [])):
                    clock.now.return_value = now
                    result = tick(root/'exchange', root, execute=True, clis={}, event_log=root/'events.jsonl')
                self.assertEqual(result['used'], 0)
                events = [json.loads(line) for line in (root/'events.jsonl').read_text().splitlines()]
                skipped = [event for event in events if event['event']=='cooldown_skipped']
                self.assertEqual(len(skipped), 1)
                self.assertEqual(skipped[0]['details']['next_eligible_at'], '2026-10-14T08:00:00+08:00')
                state = load_state(root/'output/research_queue/state.json')
                self.assertEqual(state['entries'][record['task_id']]['status'], 'pending')
                self.assertEqual(json.loads((root/'output/research_queue/refresh-needed.json').read_text())[0]['task_id'], record['task_id'])

    def test_dispatch_preflight_error_releases_reservation_without_start_history(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); record = candidates()[3]
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests', return_value=([record], [])), \
                 patch('scripts.research_scheduler.check_codex_cli'), \
                 patch('scripts.research_scheduler.prepare_entry', side_effect=OSError('prepare failed')):
                clock.now.return_value = NOW
                result = tick(root/'exchange', root, execute=True, clis={'codex':sys.executable,'claude':sys.executable})
            self.assertEqual(result['used'], 0)
            self.assertIn('prepare failed', result['failures'][0]['reason'])
            saved = load_state(root/'output/research_queue/state.json')
            self.assertEqual(saved['last_started'], {})
            self.assertEqual(saved['entries'][record['task_id']]['status'], 'pending')

    def test_dispatch_failure_after_launch_keeps_quota_and_survives_new_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); run, digest = self.prior_run(root)
            folder = run/'execution/SH-600004/codex'
            (folder/'launched.json').unlink(); (folder/'process.json').unlink()
            record = dict(candidates()[3], request=str(run/'request.json'), batch_id='a'*32, request_sha256=digest)
            def fail_after_launch(*args):
                self.prior_run(root)
                raise RuntimeError('cancelled after launch')
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests', return_value=([record], [])), \
                 patch('scripts.research_scheduler.check_codex_cli'), \
                 patch('scripts.research_scheduler.prepare_entry', side_effect=fail_after_launch):
                clock.now.return_value = NOW
                result = tick(root/'exchange', root, execute=True, clis={'codex':sys.executable,'claude':sys.executable})
            self.assertEqual(result['used'], 1)
            state = load_state(root/'output/research_queue/state.json')
            self.assertEqual(state['last_started'][record['task_id']]['started_at'], NOW.isoformat())
            state['entries'][record['task_id']]['status'] = 'failed'
            (root/'output/research_queue/state.json').write_text(json.dumps(state))
            fresh = dict(record, batch_id='c'*32, event_key='f'*64, valuation_date='2026-10-08',
                         created_at=(NOW+timedelta(days=1)).isoformat(), request_sha256='c'*64)
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests', return_value=([fresh], [])):
                clock.now.return_value = NOW+timedelta(days=1)
                result = tick(root/'exchange', root)
            self.assertEqual(result['selected'], [])
            self.assertEqual(len(result['cooldown_skipped']), 1)


    def test_held_started_round_can_retain_new_event_without_refunding_or_bypassing_cooldown(self):
        from scripts import research_scheduler as scheduler
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run, digest = self.prior_run(root)
            old = dict(candidates()[3], batch_id='a'*32, request_sha256=digest,
                       request=str(run/'request.json'))
            queue = root/'output/research_queue'
            queue.mkdir(parents=True)
            state = new_state()
            merge_candidates(state, [old], NOW)
            reserve(state, NOW)[0]['status'] = 'interrupted'
            (queue/'state.json').write_text(json.dumps(state))
            hold = dict(event_key=old['event_key'], reason='manual handoff', created_at=NOW.isoformat())
            (queue/'manual_holds.json').write_text(json.dumps(dict(schema_version='research-manual-holds/v1',
                                                                 tasks={old['task_id']: hold})))
            tomorrow = NOW+timedelta(days=1)
            fresh = dict(old, event_key='f'*64, batch_id='c'*32, request_sha256='c'*64,
                         created_at=tomorrow.isoformat(), valuation_date='2026-10-08')
            process = run/'execution'/old['task_id']/'codex/process.json'
            original_process = process.read_bytes()
            with patch.object(scheduler, 'datetime') as clock, \
                 patch.object(scheduler, 'scan_requests', return_value=([fresh], [])), \
                 patch.object(scheduler, 'group_alive', return_value=False):
                clock.now.return_value = tomorrow
                result = tick(root/'exchange', root, execute=True, clis={})
            self.assertEqual(result['failures'], [])
            self.assertEqual(result['cooldown_skipped'][0]['batch_id'], 'c'*32)
            saved = load_state(queue/'state.json')
            self.assertEqual(saved['entries'][old['task_id']]['event_key'], 'f'*64)
            self.assertEqual(saved['entries'][old['task_id']]['status'], 'pending')
            self.assertEqual(saved['days']['2026-10-07'], state['days']['2026-10-07'])
            self.assertEqual(saved['last_started'][old['task_id']]['started_at'], NOW.isoformat())
            self.assertEqual(process.read_bytes(), original_process)
            fresh['valuation_date'] = '2026-10-14'
            fresh['created_at'] = (NOW+timedelta(days=7, seconds=1)).isoformat()
            with patch.object(scheduler, 'datetime') as clock, \
                 patch.object(scheduler, 'scan_requests', return_value=([fresh], [])):
                clock.now.return_value = NOW+timedelta(days=7, seconds=1)
                self.assertEqual([e['batch_id'] for e in tick(root/'exchange', root)['selected']], ['c'*32])

    def test_live_or_uncertain_held_round_blocks_replacement(self):
        from scripts import research_scheduler as scheduler
        for live in (True, None):
            with self.subTest(live=live), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                run, digest = self.prior_run(root)
                old = dict(candidates()[3], batch_id='a'*32, request_sha256=digest,
                           request=str(run/'request.json'))
                queue = root/'output/research_queue'
                queue.mkdir(parents=True)
                state = new_state()
                merge_candidates(state, [old], NOW)
                reserve(state, NOW)[0]['status'] = 'interrupted'
                path = queue/'state.json'
                path.write_text(json.dumps(state))
                before = path.read_bytes()
                hold = dict(event_key=old['event_key'], reason='manual handoff', created_at=NOW.isoformat())
                (queue/'manual_holds.json').write_text(json.dumps(dict(schema_version='research-manual-holds/v1',
                                                                     tasks={old['task_id']: hold})))
                if live is None:
                    (run/'execution'/old['task_id']/'codex/process.json').unlink()
                fresh = dict(old, event_key='f'*64, batch_id='c'*32, request_sha256='c'*64,
                             created_at=(NOW+timedelta(minutes=1)).isoformat())
                with patch.object(scheduler, 'datetime') as clock, \
                     patch.object(scheduler, 'scan_requests', return_value=([fresh], [])), \
                     patch.object(scheduler, 'group_alive', return_value=True):
                    clock.now.return_value = NOW+timedelta(minutes=2)
                    with self.assertRaises(RuntimeError):
                        tick(root/'exchange', root)
                self.assertEqual(path.read_bytes(), before)

    def test_entry_start_is_used_if_process_was_archived(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); run, _ = self.prior_run(root)
            folder=run/'execution/SH-600004/codex'; (folder/'process.json').unlink()
            started=NOW+timedelta(seconds=1)
            (folder/'entry.json').write_text(json.dumps(dict(task_id='SH-600004',generator='codex',status='failed',
                reason='CLI failed', started_at=started.isoformat(), completed_at=(started+timedelta(minutes=1)).isoformat(),
                report=None, price_map=None)))
            fresh=dict(candidates()[3],valuation_date='2026-10-08',created_at=(NOW+timedelta(days=1)).isoformat())
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests',return_value=([fresh], [])):
                clock.now.return_value=NOW+timedelta(days=1)
                result=tick(root/'exchange',root)
            self.assertEqual(result['cooldown_skipped'][0]['next_eligible_at'],'2026-10-14T08:01:01+08:00')

    def test_ambiguous_claim_cannot_silently_refund_or_start_new_round(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); run, _ = self.prior_run(root)
            (run/'execution/SH-600004/codex/process.json').unlink()
            fresh=dict(candidates()[3],valuation_date='2026-10-08',created_at=(NOW+timedelta(days=1)).isoformat())
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests',return_value=([fresh], [])):
                clock.now.return_value=NOW+timedelta(days=1)
                result=tick(root/'exchange',root)
            self.assertEqual(result['selected'],[])
            self.assertEqual(len(result['cooldown_skipped']),1)


    def test_one_daily_check_admits_fresh_pack_after_old_unlaunched_reservation(self):
        for execute in (False, True):
            with self.subTest(execute=execute), tempfile.TemporaryDirectory() as temp:
                root=Path(temp); queue=root/'output/research_queue'; queue.mkdir(parents=True)
                state=new_state(); merge_candidates(state,[candidates()[3]],NOW); reserve(state,NOW)
                (queue/'state.json').write_text(json.dumps(state))
                tomorrow=NOW+timedelta(days=1)
                fresh=dict(candidates()[3],valuation_date='2026-10-08',created_at=tomorrow.isoformat(),
                           batch_id='c'*32,request_sha256='c'*64)
                def finish(entry,*args): entry['status']='failed'
                with patch('scripts.research_scheduler.datetime') as clock, \
                     patch('scripts.research_scheduler.scan_requests',return_value=([fresh],[])), \
                     patch('scripts.research_scheduler.check_codex_cli'), \
                     patch('scripts.research_scheduler.prepare_entry',return_value=({'generators':['codex','claude']},b'',root)), \
                     patch('scripts.research_scheduler.run_provider_entry',return_value=('failed',{})) as dispatch, \
                     patch('scripts.research_scheduler.seal_entry',side_effect=finish):
                    clock.now.return_value=tomorrow
                    result=tick(root/'exchange',root,execute=execute,once_daily=execute,
                                clis={'codex':sys.executable,'claude':sys.executable})
                if execute:
                    self.assertEqual(dispatch.call_count,2)
                    self.assertEqual(dispatch.call_args.args[0]['batch_id'],'c'*32)
                    saved=load_state(queue/'state.json')
                    self.assertEqual(saved['days']['2026-10-07'],{})
                else:
                    self.assertEqual([e['batch_id'] for e in result['selected']],['c'*32])

    def test_legacy_precheck_timestamp_uses_completion_and_advances_old_history(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); run,digest=self.prior_run(root,exact=False)
            path=run/'execution/SH-600004/codex/process.json'
            process=json.loads(path.read_text()); process['completed_at']=(NOW+timedelta(hours=4)).isoformat()
            path.write_text(json.dumps(process))
            queue=root/'output/research_queue'; queue.mkdir(parents=True)
            state=new_state(); state['last_started']={'SH-600004':dict(self.history(),request_sha256=digest)}
            (queue/'state.json').write_text(json.dumps(state))
            now=NOW+timedelta(days=7,hours=1)
            fresh=dict(candidates()[3],valuation_date='2026-10-14',created_at=now.isoformat(),batch_id='c'*32)
            with patch('scripts.research_scheduler.datetime') as clock, \
                 patch('scripts.research_scheduler.scan_requests',return_value=([fresh],[])):
                clock.now.return_value=now
                result=tick(root/'exchange',root)
            self.assertEqual(result['selected'],[])
            self.assertEqual(result['cooldown_skipped'][0]['next_eligible_at'],'2026-10-14T12:00:00+08:00')
