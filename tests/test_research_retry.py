"""Bounded retry proved through real offline CLI processes and durable artifacts."""
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_runner as runner
from scripts import research_scheduler as scheduler

_spec = importlib.util.spec_from_file_location("_retry_parallel_fixture", ROOT / "tests/test_research_parallel.py")
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)

RETRY_OBSERVER = r'''
key=get('task_id')+':'+generator
starts=[event for event in json.loads(trace_path.read_text())['events']
        if event['event']=='start' and event['task_id']==get('task_id') and event['generator']==generator]
attempt=len(starts)
print(json.dumps({'type':'system','subtype':'init','model':f'offline-retry-model-{attempt}'})
      if generator=='claude' else json.dumps({'type':'turn.started','model':f'offline-retry-model-{attempt}'}))
captures=Path(os.environ['MOCK_RETRY_CAPTURES'])
captures.mkdir(exist_ok=True)
(captures/f'{os.getpid()}.json').write_text(json.dumps({
 'task_id':get('task_id'),'generator':generator,'batch_id':batch,
 'code':code,'valuation_date':day,'input_pack_sha256':sha,
 'attempt':attempt,'payload':payload.decode()}))
if key==os.environ.get('MOCK_RETRY_TIMEOUT_FIRST','') and attempt==1: time.sleep(30)
if key==os.environ.get('MOCK_RETRY_ONCE','') and attempt==1: sys.exit(3)
if key==os.environ.get('MOCK_RETRY_ALWAYS',''): sys.exit(3)
if key==os.environ.get('MOCK_RETRY_FORMAT','') and attempt==1:
 print(json.dumps({'type':'result','subtype':'success','is_error':False,'structured_output':{}}))
 sys.exit(0)
if key==os.environ.get('MOCK_RETRY_HOLD_SECOND','') and attempt==2:
 deadline=time.monotonic()+15
 while not Path(os.environ['MOCK_PARALLEL_RELEASE']).exists():
  if time.monotonic()>deadline: sys.exit(8)
  time.sleep(.02)
'''
FAKE_CLI = _fixture.FAKE_CLI.replace(
    "ticker,market=code.split('.')", RETRY_OBSERVER + "\nticker,market=code.split('.')"
).replace(
    "(staged/price).write_text(json.dumps(doc))",
    "if mode in ('frozen','rejected'):\n doc['price_map'].update(mode=mode,p1=None)\n"
    "(staged/price).write_text(json.dumps(doc))"
)


class ResearchRetryTests(unittest.TestCase):
    setUp_fixture = _fixture.ParallelResearchTests.setUp
    run_tick = _fixture.ParallelResearchTests.run_tick
    run_scheduled_tick = _fixture.ParallelResearchTests.run_scheduled_tick
    observation = _fixture.ParallelResearchTests.observation
    seals = _fixture.ParallelResearchTests.seals
    result_entries = _fixture.ParallelResearchTests.result_entries
    scheduler_process = _fixture.ParallelResearchTests.scheduler_process

    def setUp(self):
        self.setUp_fixture()
        self.fake.write_text(FAKE_CLI)
        self.captures = self.root / 'captures'
        self.retry_env = patch.dict(os.environ, {
            'MOCK_RETRY_CAPTURES': str(self.captures), 'MOCK_RETRY_ONCE': '',
            'MOCK_RETRY_ALWAYS': '', 'MOCK_RETRY_FORMAT': '', 'MOCK_RETRY_HOLD_SECOND': '',
            'MOCK_RETRY_TIMEOUT_FIRST': ''})
        self.retry_env.start()
        self.addCleanup(self.retry_env.stop)

    @property
    def run_root(self):
        return self.methods/'output/runs/investment'/self.day/('a'*32)

    def starts(self, task='SH-600066', generator='claude'):
        return [event for event in self.observation()['events']
                if event['event']=='start' and event['task_id']==task and event['generator']==generator]

    def attempt_folder(self, attempt=1, task='SH-600066', generator='claude'):
        folder = self.run_root/'execution'/task/generator
        return folder if attempt==1 else folder/'retry-1'

    def retry_endpoint(self):
        run = runner.prepare_request(self.request_path, self.methods)
        request, raw, _ = runner.read_request(self.request_path)
        return run, request, raw, request['tasks'][0]

    def execute_endpoint(self, context, attempt):
        run, request, raw, task = context
        return runner.run_provider(run, request, raw, task, 'claude', str(self.fake),
                                   self.methods, 10, threading.Event(), attempt=attempt)

    def test_one_failed_attempt_recovers_without_repeating_successful_peer_or_input(self):
        event_log = self.root/'unified-events.jsonl'
        with patch.dict(os.environ, {'MOCK_RETRY_ONCE': 'SH-600066:claude'}):
            result = self.run_tick(event_log=event_log)
        self.assertEqual(result['failures'], [])
        self.assertEqual(len(self.starts()), 2)
        self.assertEqual(len(self.starts(generator='codex')), 1)
        self.assertEqual(self.observation()['maximum'], 3)
        first = json.loads((self.attempt_folder()/'entry.json').read_text())
        second = json.loads((self.attempt_folder(2)/'entry.json').read_text())
        self.assertEqual([first['status'], second['status']], ['failed', 'completed'])
        for attempt in (1, 2):
            process = json.loads((self.attempt_folder(attempt)/'process.json').read_text())
            self.assertEqual(process['attempt'], attempt)
            self.assertTrue((self.attempt_folder(attempt)/'events.jsonl').exists())
            self.assertTrue((self.attempt_folder(attempt)/'stderr.log').exists())
        self.assertTrue(json.loads((self.attempt_folder()/'process.json').read_text())['retryable'])
        selected = next(seal for seal in self.seals() if seal['task_id']=='SH-600066')
        receipt = next(item for item in selected['results'] if item['generator']=='claude')
        self.assertIn('/retry-1/queue-result.json', receipt['manifest'])
        self.assertEqual(receipt['actual_model'], 'offline-retry-model-2')
        events = [json.loads(line) for line in event_log.read_text().splitlines()]
        retries = [event for event in events if event['event']=='provider_retry_scheduled']
        self.assertEqual(len(retries), 1)
        self.assertEqual(retries[0]['details']['attempt'], 2)
        self.assertEqual(retries[0]['details']['max_attempts'], 2)
        finishes = [event for event in events if event['event']=='provider_finished'
                    and event['task_id']=='SH-600066' and event['generator']=='claude']
        self.assertEqual([event['details']['attempt'] for event in finishes], [1, 2])
        self.assertEqual([event['details']['actual_model'] for event in finishes],
                         ['offline-retry-model-1', 'offline-retry-model-2'])
        captured = sorted((json.loads(path.read_text()) for path in self.captures.glob('*.json')
                           if json.loads(path.read_text())['task_id']=='SH-600066'
                           and json.loads(path.read_text())['generator']=='claude'), key=lambda doc: doc['attempt'])
        self.assertEqual(len(captured), 2)
        for key in ('task_id', 'generator', 'batch_id', 'code', 'valuation_date', 'input_pack_sha256'):
            self.assertEqual(captured[0][key], captured[1][key], f'Retry changed binding {key}')
        original_pack = (self.request_path.parent/self.tasks[0]['data_pack']['path']).read_text()
        for document in captured:
            self.assertIn(original_pack, document['payload'])
        state = json.loads((self.methods/'output/research_queue/state.json').read_text())
        self.assertEqual(len(state['days'][self.day]), 4)
        first_start = min(json.loads((self.attempt_folder(a)/'process.json').read_text())['launched_at']
                          for a in (1, 2))
        codex_start = json.loads((self.attempt_folder(generator='codex')/'process.json').read_text())['launched_at']
        self.assertEqual(state['last_started']['SH-600066']['started_at'], min(first_start, codex_start))

    def test_permanent_failure_stops_after_two_and_preserves_other_seven_results(self):
        with patch.dict(os.environ, {'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            result = self.run_tick()
            before = self.trace.read_bytes()
            again = self.run_tick()
        self.assertEqual(result['failures'], [])
        self.assertEqual(again['failures'], [])
        self.assertEqual(len(self.starts()), 2)
        self.assertEqual(self.trace.read_bytes(), before, 'A sealed round restarted a failed provider')
        statuses = {(entry['task_id'], entry['generator']): entry['status']
                    for seal in self.seals() for entry in self.result_entries(seal)}
        self.assertEqual(statuses.pop(('SH-600066', 'claude')), 'failed')
        self.assertEqual(list(statuses.values()), ['completed']*7)
        self.assertEqual(self.observation()['maximum'], 3)
        self.assertFalse((self.attempt_folder()/'retry-2').exists())

    def test_invalid_model_receipt_retries_once_and_recovers(self):
        with patch.dict(os.environ, {'MOCK_RETRY_FORMAT': 'SH-600066:claude'}):
            result = self.run_tick()
        self.assertEqual(result['failures'], [])
        self.assertEqual(len(self.starts()), 2)
        self.assertEqual(json.loads((self.attempt_folder(2)/'entry.json').read_text())['status'], 'completed')

    def test_timed_out_process_is_cleaned_before_the_single_retry(self):
        run, request, raw, task = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_PARALLEL_SLEEP': '.01',
                                     'MOCK_RETRY_TIMEOUT_FIRST': 'SH-600066:claude'}):
            first = runner.run_provider(run, request, raw, task, 'claude', str(self.fake),
                                        self.methods, 2, threading.Event(), attempt=1)
            self.assertEqual(first['status'], 'failed')
            self.assertIn('timeout', first['reason'])
            process = json.loads((self.attempt_folder()/'process.json').read_text())
            self.assertTrue(process['retryable'])
            self.assertFalse(runner.group_alive(process['pid']))
            # SIGTERM skips the fake's atexit observer. Remove that stale PID only
            # after the independent process-group death check above.
            observed = self.observation()
            observed['active'] = []
            self.trace.write_text(json.dumps(observed))
            second = runner.run_provider(run, request, raw, task, 'claude', str(self.fake),
                                         self.methods, 10, threading.Event(), attempt=2)
        self.assertEqual(second['status'], 'completed')
        self.assertEqual(len(self.starts()), 2)
        self.assertEqual(self.observation()['maximum'], 1)

    def test_valid_buy_refusal_is_completed_research_and_never_retried(self):
        with patch.dict(os.environ, {'MOCK_MODE': 'rejected'}):
            result = self.run_tick()
        self.assertEqual(result['failures'], [])
        self.assertEqual(len([event for event in self.observation()['events'] if event['event']=='start']), 8)
        self.assertEqual(list(self.run_root.glob('execution/*/*/retry-1')), [])
        for seal in self.seals():
            self.assertEqual([entry['status'] for entry in self.result_entries(seal)], ['completed', 'completed'])
            for entry in self.result_entries(seal):
                doc = json.loads((self.methods/entry['price_map']['path']).read_text())
                self.assertEqual(doc['price_map']['mode'], 'rejected')
                self.assertIsNone(doc['price_map']['p1'])

    def test_runner_requires_failed_first_attempt_and_refuses_duplicate_or_third_attempt(self):
        context = self.retry_endpoint()
        with self.assertRaises(ValueError):
            self.execute_endpoint(context, 2)
        self.assertFalse(self.trace.exists())
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
            self.assertEqual(self.execute_endpoint(context, 2)['status'], 'failed')
            with self.assertRaises(ValueError):
                self.execute_endpoint(context, 2)
            with self.assertRaises(ValueError):
                self.execute_endpoint(context, 3)
        self.assertEqual(len(self.starts()), 2)

    def test_changed_frozen_input_between_attempts_prevents_a_second_child(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ONCE': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
            (self.run_root/'packs/SH-600066.md').write_text('tampered frozen pack')
            try:
                result = self.execute_endpoint(context, 2)
            except (ValueError, OSError):
                pass
            else:
                self.assertEqual(result['status'], 'failed')
        self.assertEqual(len(self.starts()), 1, 'Tampered retry input reached a model')
        process_path = self.attempt_folder(2)/'process.json'
        if process_path.exists():
            process = json.loads(process_path.read_text())
            self.assertFalse(process.get('retryable', False))
            self.assertIsNone(process.get('pid'))

    def test_legacy_failed_record_without_retryability_is_not_reopened(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
        process_path = self.attempt_folder()/'process.json'
        process = json.loads(process_path.read_text())
        process.pop('retryable', None)
        process_path.write_text(json.dumps(process))
        records, rejected = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records[:1], self.now)
        admitted = scheduler.reserve(state, self.now)[0]
        admitted['status'] = 'interrupted'
        queue = self.methods/'output/research_queue'
        queue.mkdir(parents=True)
        (queue/'state.json').write_text(json.dumps(state))
        result = self.run_tick()
        self.assertEqual(result['failures'], [])
        self.assertEqual(len(self.starts()), 1)
        self.assertFalse(self.attempt_folder(2).exists())
        sealed = next(seal for seal in self.seals() if seal['task_id']=='SH-600066')
        self.assertEqual([entry['status'] for entry in self.result_entries(sealed)], ['completed', 'failed'])

    def test_restart_after_retry_entry_before_seal_reuses_both_attempts(self):
        with patch.dict(os.environ, {'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.run_tick()['failures'], [])
            state_path = self.methods/'output/research_queue/state.json'
            state = json.loads(state_path.read_text())
            entry = state['entries']['SH-600066']
            seal_path = Path(entry.pop('sealed'))
            expected_seal = seal_path.read_bytes()
            seal_path.unlink()
            state['completed_events'].pop(entry['event_key'])
            entry['status'] = 'interrupted'
            state_path.write_text(json.dumps(state))
            before = self.trace.read_bytes()
            self.assertEqual(self.run_tick()['failures'], [])
        self.assertEqual(self.trace.read_bytes(), before, 'Crash recovery launched a third attempt')
        self.assertEqual(len(self.starts()), 2)
        self.assertEqual(seal_path.read_bytes(), expected_seal)

    def test_live_retry_group_blocks_admission_before_daily_check(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
        records, rejected = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records[:1], self.now)
        entry = scheduler.reserve(state, self.now)[0]
        entry['status'] = 'interrupted'
        queue = self.methods/'output/research_queue'
        queue.mkdir(parents=True)
        state_path = queue/'state.json'
        state_path.write_text(json.dumps(state))
        baseline = state_path.read_bytes()
        observed = self.trace.read_bytes()
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
        try:
            folder = self.attempt_folder(2)
            folder.mkdir(parents=True)
            stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
            (folder/'launched.json').write_text(json.dumps(dict(claimed_at=stamp,
                                                               request_sha256=runner.sha(context[2]))))
            (folder/'process.json').write_text(json.dumps(dict(task_id=entry['task_id'],generator='claude',
                status='running',pid=child.pid,started_at=stamp,launched_at=stamp,attempt=2,retryable=False)))
            self.assertTrue(runner.group_alive(child.pid))
            with self.assertRaises(RuntimeError):
                self.run_scheduled_tick()
            self.assertEqual(state_path.read_bytes(), baseline)
            self.assertFalse((queue/'daily-check.json').exists())
            self.assertEqual(self.trace.read_bytes(), observed, 'New providers started beside an orphaned retry')
        finally:
            os.killpg(child.pid, signal.SIGTERM)
            child.wait(timeout=5)

    def test_terminal_failed_entry_with_live_group_still_blocks_all_new_admission(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
        process = json.loads((self.attempt_folder()/'process.json').read_text())
        self.assertTrue(process['retryable'])
        records, rejected = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records[:1], self.now)
        entry = scheduler.reserve(state, self.now)[0]
        entry['status'] = 'interrupted'
        queue = self.methods/'output/research_queue'
        queue.mkdir(parents=True)
        state_path = queue/'state.json'
        state_path.write_text(json.dumps(state))
        baseline = state_path.read_bytes()
        observed = self.trace.read_bytes()
        with patch.object(scheduler, 'group_alive', side_effect=lambda pid: pid==process['pid']), \
             patch.object(runner, 'group_alive', side_effect=lambda pid: pid==process['pid']):
            with self.assertRaises(RuntimeError):
                self.run_scheduled_tick()
        self.assertEqual(state_path.read_bytes(), baseline)
        self.assertEqual(self.trace.read_bytes(), observed)
        self.assertFalse((queue/'daily-check.json').exists())
        self.assertFalse((self.attempt_folder(2)/'launched.json').exists())
        self.assertEqual(self.seals(), [])

    def test_terminal_retry_entry_with_live_group_is_not_returned_or_restarted(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
            self.assertEqual(self.execute_endpoint(context, 2)['status'], 'failed')
        entry_path = self.attempt_folder(2)/'entry.json'
        preserved_entry = entry_path.read_bytes()
        observed = self.trace.read_bytes()
        record = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))[0][0]
        record['budget_date'] = self.day
        run, request, raw, _ = context
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
        try:
            process_path = self.attempt_folder(2)/'process.json'
            process = json.loads(process_path.read_text())
            process['pid'] = child.pid
            process_path.write_text(json.dumps(process))
            self.assertTrue(runner.group_alive(child.pid))
            with self.assertRaises(RuntimeError):
                scheduler.run_provider_entry(record, 'claude', request, raw, run, self.methods,
                    {'codex': str(self.fake), 'claude': str(self.fake)}, 10, threading.Event())
            self.assertEqual(entry_path.read_bytes(), preserved_entry, 'Live terminal evidence was replaced')
            self.assertEqual(self.trace.read_bytes(), observed, 'A live terminal retry launched a third attempt')
            self.assertEqual(len(self.starts()), 2)
            self.assertFalse((self.attempt_folder()/'retry-2').exists())
            self.assertEqual(self.seals(), [])
        finally:
            os.killpg(child.pid, signal.SIGTERM)
            child.wait(timeout=5)

    def test_cancel_between_first_failure_and_retry_keeps_provider_unsealed(self):
        run, request, raw, task = self.retry_endpoint()
        record = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))[0][0]
        record['budget_date'] = self.day
        cancelled = threading.Event()
        original = scheduler.run_provider
        def finish_and_cancel(*args, **kwargs):
            result = original(*args, **kwargs)
            cancelled.set()
            return result
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}), \
             patch.object(scheduler, 'run_provider', side_effect=finish_and_cancel):
            with self.assertRaisesRegex(RuntimeError, 'cancelled'):
                scheduler.run_provider_entry(record, 'claude', request, raw, run, self.methods,
                    {'codex': str(self.fake), 'claude': str(self.fake)}, 10, cancelled)
        self.assertEqual(json.loads((self.attempt_folder()/'entry.json').read_text())['status'], 'failed')
        self.assertTrue(json.loads((self.attempt_folder()/'process.json').read_text())['retryable'])
        self.assertEqual(len(self.starts()), 1)
        self.assertFalse((self.attempt_folder(2)/'launched.json').exists())
        self.assertEqual(self.seals(), [])

    def test_cancel_in_launch_check_gap_keeps_unclaimed_endpoint_pending(self):
        for attempt in (1, 2):
            with self.subTest(attempt=attempt):
                run, request, raw, task = self.retry_endpoint()
                if attempt == 2:
                    with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ALWAYS': 'SH-600066:claude'}):
                        self.assertEqual(self.execute_endpoint((run, request, raw, task), 1)['status'], 'failed')
                record = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))[0][0]
                record['budget_date'] = self.day
                cancelled = threading.Event()
                original = scheduler.run_provider
                def cancel_just_before_runner(*args, **kwargs):
                    cancelled.set()
                    return original(*args, **kwargs)
                with patch.object(scheduler, 'run_provider', side_effect=cancel_just_before_runner):
                    with self.assertRaisesRegex(RuntimeError, 'cancelled'):
                        scheduler.run_provider_entry(record, 'claude', request, raw, run, self.methods.resolve(),
                            {'codex': str(self.fake), 'claude': str(self.fake)}, 10, cancelled)
                folder = self.attempt_folder(attempt)
                self.assertFalse((folder/'launched.json').exists())
                self.assertFalse((folder/'entry.json').exists())
                self.assertEqual(self.seals(), [])

    def test_retry_uses_verified_pack_snapshot_if_files_change_after_verification(self):
        context = self.retry_endpoint()
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_RETRY_ONCE': 'SH-600066:claude'}):
            self.assertEqual(self.execute_endpoint(context, 1)['status'], 'failed')
            pack_path = self.run_root/'packs/SH-600066.md'
            expected_pack = pack_path.read_bytes()
            replacement_pack = expected_pack+b'\nMUTATED BODY AFTER VERIFY\n'
            original = runner.verify_prepared
            def verify_then_replace(*args, **kwargs):
                verified = original(*args, **kwargs)
                document = json.loads((self.run_root/'request.json').read_text())
                document['tasks'][0]['data_pack']['sha256'] = hashlib.sha256(replacement_pack).hexdigest()
                pack_path.write_bytes(replacement_pack)
                (self.run_root/'request.json').write_text(json.dumps(document, ensure_ascii=False))
                return verified
            with patch.object(runner, 'verify_prepared', side_effect=verify_then_replace):
                result = self.execute_endpoint(context, 2)
        self.assertEqual(result['status'], 'failed', 'Post-run input validation must catch changed disk inputs')
        documents = [json.loads(path.read_text()) for path in self.captures.glob('*.json')]
        second = next(document for document in documents if document['task_id']=='SH-600066'
                      and document['generator']=='claude' and document['attempt']==2)
        self.assertIn(expected_pack.decode(), second['payload'])
        self.assertNotIn('MUTATED BODY AFTER VERIFY', second['payload'])
        self.assertEqual(second['input_pack_sha256'], hashlib.sha256(expected_pack).hexdigest())
        self.assertEqual(len(self.starts()), 2)

    def test_stock_is_unsealed_until_retry_finishes(self):
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log, MOCK_RETRY_ONCE='SH-600066:claude',
                                              MOCK_RETRY_HOLD_SECOND='SH-600066:claude')
            try:
                deadline = time.monotonic()+10
                while time.monotonic()<deadline:
                    if self.trace.exists() and len(self.starts())==2 and self.seals():
                        break
                    self.assertIsNone(process.poll(), (self.root/'scheduler.log').read_text())
                    time.sleep(.03)
                else:
                    self.fail('Retry never started while independent stocks completed')
                self.assertNotIn('SH-600066', [seal['task_id'] for seal in self.seals()],
                                 'Writeback can consume an unfinished retry')
                self.assertTrue((self.attempt_folder(generator='codex')/'entry.json').exists())
                (self.root/'release').touch()
                self.assertEqual(process.wait(timeout=10), 0, (self.root/'scheduler.log').read_text())
            finally:
                if process.poll() is None:
                    process.send_signal(signal.SIGTERM)
                    process.wait(timeout=10)
        self.assertEqual(len(self.seals()), 4)
        self.assertEqual(len(self.starts()), 2)

    def test_sigterm_does_not_trigger_retry_and_cleans_live_groups(self):
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log, MOCK_PARALLEL_SLEEP='30')
            try:
                deadline = time.monotonic()+10
                while time.monotonic()<deadline:
                    if self.trace.exists() and len(self.observation()['active'])==3:
                        break
                    self.assertIsNone(process.poll(), (self.root/'scheduler.log').read_text())
                    time.sleep(.03)
                else:
                    self.fail('Three processes did not start')
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=10)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        self.assertEqual(len([event for event in self.observation()['events'] if event['event']=='start']), 3)
        self.assertEqual(list(self.run_root.glob('execution/*/*/retry-1')), [])
        for path in self.run_root.glob('execution/*/*/process.json'):
            document = json.loads(path.read_text())
            self.assertEqual(document['status'], 'failed')
            self.assertFalse(document.get('retryable', False))
            self.assertFalse(runner.group_alive(document['pid']))


if __name__ == '__main__':
    unittest.main()
