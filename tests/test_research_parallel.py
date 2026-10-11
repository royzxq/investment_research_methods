"""Bounded provider concurrency proved with real offline CLI subprocesses."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_scheduler import tick
from scripts import research_scheduler as scheduler
from scripts.research_runner import group_alive
from scripts import research_runner as runner

_spec = importlib.util.spec_from_file_location("_parallel_cli_fixture", ROOT / "tests/test_research_runner.py")
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)

# Instrument the existing contract-valid fake. The flock trace is an independent
# observation of live child processes, not a copy of the scheduler algorithm.
TRACE_CODE = r'''
import atexit,fcntl
trace_path=Path(os.environ['MOCK_PARALLEL_TRACE'])
def trace(event):
 with trace_path.with_suffix('.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  state=json.loads(trace_path.read_text()) if trace_path.exists() else {'active':[], 'maximum':0, 'events':[]}
  if event=='start': state['active'].append(os.getpid())
  elif os.getpid() in state['active']: state['active'].remove(os.getpid())
  state['maximum']=max(state['maximum'],len(state['active']))
  state['events'].append({'event':event,'pid':os.getpid(),'task_id':get('task_id'),'generator':generator,'at':time.monotonic_ns()})
  temporary=trace_path.with_suffix('.partial')
  temporary.write_text(json.dumps(state)); temporary.replace(trace_path)
trace('start')
atexit.register(trace,'end')
barrier=int(os.environ.get('MOCK_PARALLEL_BARRIER','0'))
deadline=time.monotonic()+5
while barrier and json.loads(trace_path.read_text())['maximum']<barrier:
 if time.monotonic()>deadline: sys.exit(9)
 time.sleep(.02)
time.sleep(float(os.environ.get('MOCK_PARALLEL_SLEEP','.2')))
if get('task_id')+':'+generator==os.environ.get('MOCK_PARALLEL_SLOW',''):
 time.sleep(30)
if get('task_id')+':'+generator==os.environ.get('MOCK_PARALLEL_HOLD',''):
 deadline=time.monotonic()+15
 while not Path(os.environ['MOCK_PARALLEL_RELEASE']).exists():
  if time.monotonic()>deadline: sys.exit(8)
  time.sleep(.02)
if get('task_id')+':'+generator==os.environ.get('MOCK_PARALLEL_FAIL',''): sys.exit(3)
'''
FAKE_CLI = _fixture.FAKE_CLI.replace(
    "ticker,market=code.split('.')", TRACE_CODE + "\nticker,market=code.split('.')"
).replace(
    "{'600066.SH':'宇通客车','600900.SH':'长江电力'}[code]",
    "{'600066.SH':'宇通客车','600900.SH':'长江电力','600276.SH':'恒瑞医药','600519.SH':'贵州茅台'}[code]",
)


class ParallelResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.methods = self.root / 'methods'
        self.methods.mkdir()
        for name in ('investment_framework.md', 'investment_framework_compact.md'):
            path = self.methods / 'framework' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('offline framework')
        self.exchange = self.root / 'exchange'
        self.now = datetime.now(ZoneInfo('Asia/Shanghai'))
        self.day = self.now.date().isoformat()
        self.request_path = self.exchange / 'requests' / ('a' * 32) / 'request.json'
        self.request_path.parent.mkdir(parents=True)
        self.tasks = []
        for index, (code, name) in enumerate((('600066', '宇通客车'), ('600900', '长江电力'),
                                            ('600276', '恒瑞医药'), ('600519', '贵州茅台'))):
            relative = f'packs/SH-{code}.md'
            pack = self.request_path.parent / relative
            pack.parent.mkdir(exist_ok=True)
            pack.write_text(f'# {code}.SH 量价与基本面数据包\n- 最新收盘: 25.30\n- 最新成交量(手): 12345\n完整原始资料\n')
            evidence = {'review': index}
            identity = dict(market='A', code=code, sources=['candidate_review'], evidence=evidence)
            event_key = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False,
                                                  allow_nan=False).encode()).hexdigest()
            trigger = dict(schema_version='research-trigger/v1', priority=index+1,
                           event_key=event_key, evidence=evidence)
            self.tasks.append(dict(task_id=f'SH-{code}', code=f'{code}.SH', name=name,
                                   sources=['candidate_review'],
                                   data_pack=dict(path=relative, sha256=hashlib.sha256(pack.read_bytes()).hexdigest()),
                                   data_pack_meta={'research_trigger': trigger}))
        request = dict(schema_version='stock-research-request/v1', batch_id='a'*32,
                       created_at=self.now.isoformat(), valuation_date=self.day,
                       generators=['codex', 'claude'], tasks=self.tasks)
        self.request_path.write_text(json.dumps(request, ensure_ascii=False))
        self.fake = self.root / 'fake-research-cli'
        self.fake.write_text(FAKE_CLI)
        self.fake.chmod(0o700)
        self.trace = self.root / 'trace.json'
        self.env = patch.dict(os.environ, {'MOCK_INPUT': str(self.root/'stdin.txt'),
                                          'MOCK_MODE': 'success', 'MOCK_PARALLEL_TRACE': str(self.trace),
                                          'MOCK_PARALLEL_BARRIER': '3', 'MOCK_PARALLEL_SLEEP': '.2',
                                          'MOCK_PARALLEL_HOLD': '',
                                          'MOCK_PARALLEL_SLOW': '',
                                          'MOCK_PARALLEL_RELEASE': str(self.root/'release'),
                                          'MOCK_PARALLEL_FAIL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_tick(self, **options):
        return tick(self.exchange, self.methods, execute=True,
                    clis={'codex': str(self.fake), 'claude': str(self.fake)}, timeout=10, **options)

    def observation(self):
        return json.loads(self.trace.read_text())

    def seals(self):
        return [json.loads(path.read_text()) for path in (self.methods/'output/research_queue/sealed').glob('*.json')]

    def result_entries(self, seal):
        return [json.loads((self.methods/item['manifest']).read_text())['results'][0] for item in seal['results']]

    def scheduler_process(self, log, **environment):
        code = (f'import sys;sys.path.insert(0,{str(ROOT)!r});'
                'from scripts.research_scheduler import tick;'
                f'r=tick({str(self.exchange)!r},{str(self.methods)!r},execute=True,'
                f'clis={{"codex":{str(self.fake)!r},"claude":{str(self.fake)!r}}},timeout=60);'
                'sys.exit(2 if r.get("failures") else 0)')
        return subprocess.Popen([sys.executable, '-c', code], stdout=log, stderr=log,
                                env=dict(os.environ, **environment), start_new_session=True)

    def test_real_children_reach_three_and_pair_runs_overlap(self):
        result = self.run_tick()
        self.assertEqual(result['failures'], [])
        observed = self.observation()
        self.assertEqual(observed['maximum'], 3)
        self.assertEqual(observed['active'], [])
        self.assertEqual(len([item for item in observed['events'] if item['event']=='start']), 8)
        intervals = {}
        for item in observed['events']:
            intervals.setdefault((item['task_id'], item['generator']), {})[item['event']] = item['at']
        codex = intervals[('SH-600066', 'codex')]
        claude = intervals[('SH-600066', 'claude')]
        self.assertLess(max(codex['start'], claude['start']), min(codex['end'], claude['end']))
        sealed = self.seals()
        self.assertEqual(len(sealed), 4)
        for seal in sealed:
            self.assertEqual([item['generator'] for item in seal['results']], ['codex', 'claude'])
            self.assertEqual([item['status'] for item in self.result_entries(seal)], ['completed', 'completed'])
        before = self.trace.read_bytes()
        again = self.run_tick()
        self.assertEqual(again['failures'], [])
        self.assertEqual(self.trace.read_bytes(), before, 'Completed providers must not launch again')

    def test_one_failed_provider_keeps_other_seven_results_and_complete_seal(self):
        with patch.dict(os.environ, {'MOCK_PARALLEL_FAIL': 'SH-600066:claude'}):
            result = self.run_tick()
        self.assertEqual(result['failures'], [])
        sealed = self.seals()
        self.assertEqual(len(sealed), 4)
        statuses = {(entry['task_id'], entry['generator']): entry['status']
                    for seal in sealed for entry in self.result_entries(seal)}
        self.assertEqual(statuses.pop(('SH-600066', 'claude')), 'failed')
        self.assertEqual(list(statuses.values()), ['completed']*7)
        self.assertEqual(self.observation()['maximum'], 3)

    def test_reduced_concurrency_is_respected(self):
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0', 'MOCK_PARALLEL_SLEEP': '.04'}):
            result = self.run_tick(max_concurrency=1)
        self.assertEqual(result['failures'], [])
        self.assertEqual(self.observation()['maximum'], 1)
        self.assertEqual(len(self.seals()), 4)

    def test_invalid_concurrency_does_not_create_budget_or_launch(self):
        for invalid in (0, 4, 1.5):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                self.run_tick(max_concurrency=invalid)
        self.assertFalse(self.trace.exists())
        self.assertFalse((self.methods/'output/research_queue/state.json').exists())

    def test_atomic_provider_claim_prevents_duplicate_real_child(self):
        run = runner.prepare_request(self.request_path, self.methods)
        request, raw, _ = runner.read_request(self.request_path)
        barrier = threading.Barrier(2)
        cancelled = threading.Event()
        def launch():
            barrier.wait(timeout=5)
            return runner.run_provider(run, request, raw, request['tasks'][0], 'claude',
                                       str(self.fake), self.methods, 10, cancelled)
        completed, rejected = [], []
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0'}), ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(launch) for _ in range(2)]
            for future in futures:
                try:
                    completed.append(future.result())
                except (ValueError, OSError) as error:
                    rejected.append(error)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]['status'], 'completed')
        self.assertEqual(len(rejected), 1)
        starts = [item for item in self.observation()['events'] if item['event']=='start']
        self.assertEqual(len(starts), 1, 'Concurrent consumers launched a duplicate CLI')
        saved = json.loads((run/'execution/SH-600066/claude/entry.json').read_text())
        self.assertEqual(saved['status'], 'completed')

    def test_claim_is_invisible_to_cooldown_reader_until_complete_atomic_publication(self):
        run = runner.prepare_request(self.request_path, self.methods)
        request, raw, _ = runner.read_request(self.request_path)
        claim = run/'execution/SH-600066/codex/launched.json'
        expected = runner.encode(dict(claimed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                                      request_sha256=runner.sha(raw)))
        ready, release = threading.Event(), threading.Event()
        original = runner.os.fsync
        def blocked_fsync(fd):
            original(fd)
            ready.set()
            if not release.wait(timeout=5):
                raise OSError('offline claim barrier not released')
        with patch.object(runner.os, 'fsync', side_effect=blocked_fsync), ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(runner.write_new, claim, expected)
            try:
                self.assertTrue(ready.wait(timeout=5))
                self.assertFalse(claim.exists(), 'A reader can see a claim before its bytes are durably complete')
                state = scheduler.new_state()
                self.assertEqual(scheduler.sync_started(state, self.methods), {})
                self.assertEqual(state['last_started'], {})
            finally:
                release.set()
            future.result(timeout=5)
        self.assertEqual(claim.read_bytes(), expected)
        state = scheduler.new_state()
        rounds = scheduler.sync_started(state, self.methods)
        self.assertIn(('SH-600066', request['batch_id'], runner.sha(raw)), rounds)
        self.assertEqual(state['last_started']['SH-600066']['request_sha256'], runner.sha(raw))

    def test_prior_actual_launch_allows_next_day_pair_but_preflight_claim_does_not(self):
        yesterday = self.now-timedelta(days=1)
        document = json.loads(self.request_path.read_text())
        document.update(created_at=yesterday.isoformat(), valuation_date=yesterday.date().isoformat())
        self.request_path.write_text(json.dumps(document, ensure_ascii=False))
        run = runner.prepare_request(self.request_path, self.methods)
        request, raw, _ = runner.read_request(self.request_path)
        cancelled = threading.Event()
        folder = run/'execution/SH-600900/codex'
        (folder/'launched.json').write_text(json.dumps(dict(claimed_at=yesterday.isoformat(),
                                                          request_sha256=runner.sha(raw))))
        (folder/'process.json').write_text(json.dumps(dict(task_id='SH-600900', generator='codex',
                                                         status='failed', pid=None,
                                                         started_at=yesterday.isoformat(), completed_at=yesterday.isoformat())))
        with self.assertRaisesRegex(ValueError, 'reservation expired'):
            runner.run_provider(run, request, raw, request['tasks'][1], 'claude', str(self.fake),
                                self.methods, 10, cancelled, launch_date=yesterday.date().isoformat())
        self.assertFalse((run/'execution/SH-600900/claude/launched.json').exists())
        self.assertFalse(self.trace.exists())
        with patch.dict(os.environ, {'MOCK_PARALLEL_BARRIER': '0'}):
            with patch.object(runner, 'stamp', return_value=yesterday.isoformat()):
                first = runner.run_provider(run, request, raw, request['tasks'][0], 'codex', str(self.fake),
                                            self.methods, 10, cancelled, launch_date=yesterday.date().isoformat())
            second = runner.run_provider(run, request, raw, request['tasks'][0], 'claude', str(self.fake),
                                         self.methods, 10, cancelled, launch_date=yesterday.date().isoformat())
        self.assertEqual([first['status'], second['status']], ['completed', 'completed'])
        process = json.loads((run/'execution/SH-600066/codex/process.json').read_text())
        self.assertEqual(process['launched_at'], yesterday.isoformat())
        self.assertEqual(len([item for item in self.observation()['events'] if item['event']=='start']), 2)

    @patch.object(scheduler, 'datetime', wraps=datetime)
    def test_live_prior_group_blocks_new_admission_without_state_changes(self, clock):
        clock.now.return_value = self.now.replace(hour=6, minute=0, second=0, microsecond=0)
        run = runner.prepare_request(self.request_path, self.methods)
        _, raw, _ = runner.read_request(self.request_path)
        records, rejected = scheduler.scan_requests(self.exchange, datetime.now(ZoneInfo('Asia/Shanghai')))
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records[:1], self.now)
        old = scheduler.reserve(state, self.now)[0]
        old['status'] = 'interrupted'
        queue = self.methods/'output/research_queue'
        queue.mkdir(parents=True)
        state_path = queue/'state.json'
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        baseline = state_path.read_bytes()
        process = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'],
                                   start_new_session=True)
        try:
            folder = run/'execution'/old['task_id']/'claude'
            stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
            (folder/'launched.json').write_text(json.dumps(dict(claimed_at=stamp,
                                                              request_sha256=runner.sha(raw))))
            (folder/'process.json').write_text(json.dumps(dict(task_id=old['task_id'], generator='claude',
                                                             status='running', pid=process.pid,
                                                             started_at=stamp, launched_at=stamp)))
            self.assertTrue(group_alive(process.pid))
            with self.assertRaises(RuntimeError):
                self.run_tick(once_daily=True)
            self.assertEqual(state_path.read_bytes(), baseline)
            self.assertFalse((queue/'daily-check.json').exists(), 'Blocked admission must not consume the daily check')
            self.assertFalse(self.trace.exists(), 'New candidates started while an old research group survived')
            self.assertEqual(len(list(run.glob('execution/*/*/launched.json'))), 1)
        finally:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)

    def test_state_write_failure_cancels_slow_children_without_dispatching_waiters(self):
        state_path = (self.methods/'output/research_queue/state.json').resolve()
        original = scheduler.atomic_json
        failures = []
        def fail_after_seal(path, value):
            if Path(path).resolve()==state_path and self.seals():
                failures.append(str(path))
                raise OSError('offline durable state write failure')
            return original(path, value)
        started = time.monotonic()
        with patch.dict(os.environ, {'MOCK_PARALLEL_SLOW': 'SH-600900:codex'}), \
             patch.object(scheduler, 'atomic_json', side_effect=fail_after_seal):
            with self.assertRaisesRegex(OSError, 'durable state write failure'):
                tick(self.exchange, self.methods, execute=True,
                     clis={'codex': str(self.fake), 'claude': str(self.fake)}, timeout=60)
        self.assertLess(time.monotonic()-started, 8, 'Coordinator failure waited for the slow CLI instead of cancelling it')
        self.assertGreaterEqual(len(failures), 2, 'Fault injection must remain active through error persistence')
        execution = self.methods/'output/runs/investment'/self.day/('a'*32)/'execution'
        slow = json.loads((execution/'SH-600900/codex/process.json').read_text())
        self.assertEqual(slow['status'], 'failed')
        self.assertIn('cancelled', slow['reason'])
        for path in execution.glob('*/*/process.json'):
            status = json.loads(path.read_text())
            if status.get('pid'):
                self.assertFalse(group_alive(status['pid']), 'Coordinator failure leaked a CLI process group')
        for task in ('SH-600276', 'SH-600519'):
            self.assertEqual(list((execution/task).glob('*/launched.json')), [],
                             'Coordinator failure launched a waiting provider')

    def test_transient_state_write_failure_also_stops_admission_and_cleans_children(self):
        state_path = (self.methods/'output/research_queue/state.json').resolve()
        original = scheduler.atomic_json
        faults = []
        def fail_once_after_seal(path, value):
            if Path(path).resolve()==state_path and self.seals() and not faults:
                faults.append(str(path))
                raise OSError('offline transient durable state write failure')
            return original(path, value)
        with patch.dict(os.environ, {'MOCK_PARALLEL_SLOW': 'SH-600900:codex'}), \
             patch.object(scheduler, 'atomic_json', side_effect=fail_once_after_seal):
            result = tick(self.exchange, self.methods, execute=True,
                          clis={'codex': str(self.fake), 'claude': str(self.fake)}, timeout=1)
        self.assertEqual(len(faults), 1)
        self.assertTrue(any('transient durable state write failure' in row['reason'] for row in result['failures']))
        execution = self.methods/'output/runs/investment'/self.day/('a'*32)/'execution'
        for task in ('SH-600276', 'SH-600519'):
            self.assertEqual(list((execution/task).glob('*/launched.json')), [],
                             'A recovered state-write error still admitted a waiting provider')
        for path in execution.glob('*/*/process.json'):
            process = json.loads(path.read_text())
            if process.get('pid'):
                self.assertFalse(group_alive(process['pid']))

    @patch.object(scheduler, 'datetime', wraps=datetime)
    def test_uncertain_popen_record_blocks_admission_without_consuming_daily_check(self, clock):
        clock.now.return_value = self.now.replace(hour=6, minute=0, second=0, microsecond=0)
        run = runner.prepare_request(self.request_path, self.methods)
        records, rejected = scheduler.scan_requests(self.exchange, self.now)
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records[:1], self.now)
        entry = scheduler.reserve(state, self.now)[0]
        entry['status'] = 'interrupted'
        queue = self.methods/'output/research_queue'
        queue.mkdir(parents=True)
        state_path = queue/'state.json'
        state_path.write_text(json.dumps(state))
        original_state = state_path.read_bytes()
        folder = run/'execution'/entry['task_id']/'claude'
        stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
        (folder/'launched.json').write_text(json.dumps(dict(claimed_at=stamp,
            request_sha256=runner.sha(self.request_path.read_bytes()))))
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=True)
        try:
            (folder/'process.json').write_text(json.dumps(dict(task_id=entry['task_id'], generator='claude',
                status='starting', pid=None, started_at=stamp, completed_at=None, exit_code=None)))
            with self.assertRaisesRegex(RuntimeError, 'uncertain'):
                self.run_tick(once_daily=True)
            self.assertEqual(state_path.read_bytes(), original_state)
            self.assertFalse((queue/'daily-check.json').exists())
            self.assertFalse(self.trace.exists())
            self.assertFalse((folder/'entry.json').exists())
            (folder/'process.json').unlink()
            with self.assertRaisesRegex(RuntimeError, 'uncertain'):
                self.run_tick(once_daily=True)
            self.assertEqual(state_path.read_bytes(), original_state)
            self.assertFalse((queue/'daily-check.json').exists())
        finally:
            os.killpg(child.pid, signal.SIGTERM)
            child.wait(timeout=5)

    def test_stock_waits_for_both_providers_while_other_stocks_can_seal(self):
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log, MOCK_PARALLEL_HOLD='SH-600066:claude')
            try:
                deadline = time.monotonic()+10
                while time.monotonic()<deadline:
                    if self.seals():
                        break
                    self.assertIsNone(process.poll(), (self.root/'scheduler.log').read_text())
                    time.sleep(.03)
                else:
                    self.fail('Other stocks were blocked by the held provider')
                run = self.methods/'output/runs/investment'/self.day/('a'*32)
                self.assertTrue((run/'execution/SH-600066/codex/entry.json').exists())
                self.assertFalse((run/'execution/SH-600066/claude/entry.json').exists())
                self.assertNotIn('SH-600066', [seal['task_id'] for seal in self.seals()],
                                 'A completed Codex must not seal a still-running Claude pair')
                (self.root/'release').touch()
                self.assertEqual(process.wait(timeout=10), 0, (self.root/'scheduler.log').read_text())
            finally:
                if process.poll() is None:
                    process.send_signal(signal.SIGTERM)
                    process.wait(timeout=10)
        self.assertEqual(len(self.seals()), 4)

    def test_sigterm_cleans_active_groups_and_leaves_waiting_providers_unlaunched(self):
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
                    self.fail('Three real research processes did not start')
                with self.assertRaises(BlockingIOError):
                    self.run_tick()
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=10)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        execution = self.methods/'output/runs/investment'/self.day/('a'*32)/'execution'
        self.assertEqual(len(list(execution.glob('*/*/launched.json'))), 3,
                         'Waiting providers must remain unclaimed after cancellation')
        for path in execution.glob('*/*/process.json'):
            status = json.loads(path.read_text())
            self.assertEqual(status['status'], 'failed')
            self.assertFalse(group_alive(status['pid']), 'Cancellation left a research process group alive')
        for seal in self.seals():
            self.assertEqual(len(seal['results']), 2, 'Cancellation must not publish a one-provider seal')


if __name__ == '__main__':
    unittest.main()
