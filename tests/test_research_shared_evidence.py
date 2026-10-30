"""Sequential execution with real offline subprocesses and corrupt handoffs."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import sys
import signal
import subprocess
import time
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_runner as runner, research_shared_evidence as shared, research_runtime as runtime
from scripts import research_scheduler as scheduler


def fixture(name):
    spec = importlib.util.spec_from_file_location('_shared_' + name, ROOT/'tests'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parallel = fixture('test_research_parallel')
dsh = fixture('test_research_dsh')


class SharedEvidenceTests(unittest.TestCase):
    def setUp(self):
        parallel.ParallelResearchTests.setUp(self)
        self.request = json.loads(self.request_path.read_text())
        self.request.update(schema_version='stock-research-request/v2', generators=['codex', 'dsh'])
        self.request['tasks'] = self.request['tasks'][:2]
        self.request_path.write_bytes(runner.encode(self.request))
        self.dsh_cli = self.root/'fake-dsh'
        self.dsh_cli.write_text(dsh.build_fake_dsh_cli(parallel.FAKE_CLI))
        self.dsh_cli.chmod(0o700)
        profiles = [runtime.default_profile(g) for g in ('codex', 'dsh')]
        self.config = dict(schema_version=runtime.CONFIG_SCHEMA, profiles=profiles,
                           active={p['producer']:p['profile_id'] for p in profiles})
        # The fake CLI never calls an API; do not depend on developer credentials
        # (including the adapter's local Claude-settings fallback) in offline CI.
        self.extra_env = patch.dict(os.environ, {'DEEPSEEK_API_KEY':'offline-shared-evidence-fixture',
                                                'MOCK_PARALLEL_BARRIER':'0', 'MOCK_PARALLEL_SLEEP':'.05'})
        self.extra_env.start(); self.addCleanup(self.extra_env.stop)

    def prepare(self):
        self.run = runner.prepare_request(self.request_path, self.methods, runtime_config=self.config)
        return self.run

    def execute(self, generator, task=None):
        return runner.run_batch(self.request_path, self.methods, generator=generator,
            cli=str(self.fake if generator=='codex' else self.dsh_cli), timeout=10,
            task_ids=[task or self.request['tasks'][0]['task_id']], runtime_config=self.config)

    def tick(self, timeout=10, **options):
        options.setdefault('max_concurrency', 3)  # Retain the three-slot contention scenarios.
        return scheduler.tick(self.exchange, self.methods, execute=True,
            clis={'codex':str(self.fake), 'dsh':str(self.dsh_cli)}, timeout=timeout, runtime_config=self.config, **options)

    def test_scheduler_orders_each_pair_and_still_parallelizes_stocks(self):
        result = self.tick()
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['used'], 2)
        trace = json.loads(self.trace.read_text())
        self.assertGreaterEqual(trace['maximum'], 2)
        self.assertLessEqual(trace['maximum'], 3)
        for task in self.request['tasks']:
            events = [e for e in trace['events'] if e['task_id']==task['task_id']]
            codex_end = next(e['at'] for e in events if e['generator']=='codex' and e['event']=='end')
            dsh_start = next(e['at'] for e in events if e['generator']=='dsh' and e['event']=='start')
            self.assertLess(codex_end, dsh_start)
        self.prepare()
        task = self.request['tasks'][0]
        dsh_folder = runner.execution_folder(self.run, task, 'dsh')
        payload = (dsh_folder/'jev-runtime-prompt.txt').read_text()
        dependency = json.loads((dsh_folder/'runner/evidence-dependency.json').read_text())
        self.assertIn(dependency['bundle']['sha256'], payload)
        self.assertIn('research_mode=incremental', payload)
        self.assertNotIn('research-codex.md', payload)
        self.assertEqual(json.loads((dsh_folder/'process.json').read_text())['status'], 'completed')

    def test_codex_terminal_failure_never_launches_dsh_for_that_stock(self):
        task = self.request['tasks'][0]['task_id']
        with patch.dict(os.environ, {'MOCK_PARALLEL_FAIL':task+':codex'}):
            self.tick()
        self.prepare()
        folder = runner.execution_folder(self.run, self.request['tasks'][0], 'dsh')
        self.assertFalse((folder/'launched.json').exists())
        entry = json.loads((folder/'entry.json').read_text())
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('Codex dependency', entry['reason'])
        trace = json.loads(self.trace.read_text())['events']
        self.assertFalse(any(e['task_id']==task and e['generator']=='dsh' for e in trace))
        self.assertTrue(any(e['task_id']!=task and e['generator']=='dsh' for e in trace))

    def test_direct_dsh_call_before_codex_does_not_claim_or_launch(self):
        self.prepare()
        result = json.loads(self.execute('dsh').read_text())['results'][0]
        self.assertEqual(result['status'], 'failed')
        self.assertFalse((runner.execution_folder(self.run,self.request['tasks'][0],'dsh')/'launched.json').exists())
        self.assertFalse(self.trace.exists())

    def test_source_tamper_stops_downstream_before_claim(self):
        self.prepare(); self.execute('codex')
        task=self.request['tasks'][0]
        source=runner.execution_folder(self.run,task,'codex')/'runner/shared-evidence/sources/original.txt'
        source.chmod(0o644);source.write_text('tampered')
        result=json.loads(self.execute('dsh').read_text())['results'][0]
        self.assertEqual(result['status'],'failed')
        self.assertIn('hash mismatch',result['reason'])
        self.assertFalse((runner.execution_folder(self.run,task,'dsh')/'launched.json').exists())

    def test_schema_cutoff_quote_and_path_failures_are_not_silently_shared(self):
        self.prepare();self.execute('codex')
        task=self.request['tasks'][0]
        folder=runner.execution_folder(self.run,task,'codex')/'agent/shared-evidence'
        base=json.loads((folder/'bundle.json').read_text())
        mutations=[lambda d:d.update(p1=12), lambda d:d.update(task_id='SH-999999'),
                   lambda d:d['sources'][0].update(published_at='2099-01-01'),
                   lambda d:d['facts'][0].update(quote='invented quotation'),
                   lambda d:d['sources'][0]['original'].update(path='../private.txt'),
                   lambda d:d['facts'][0].update(kind='valuation_assumption')]
        for mutate in mutations:
            doc=deepcopy(base);mutate(doc)
            with self.subTest(doc=doc),self.assertRaises(ValueError):shared.validate(doc,folder,self.request,task)
        original=folder/'sources/original.txt';original.unlink();original.symlink_to(self.request_path)
        with self.assertRaises((ValueError,OSError)):shared.validate(base,folder,self.request,task)

    def test_old_frozen_pair_keeps_original_independent_execution(self):
        self.prepare()
        manifest=self.run/'framework-snapshot/manifest.json'
        snap=json.loads(manifest.read_text());snap.pop('evidence_workflow')
        manifest.chmod(0o644);manifest.write_bytes(runner.encode(snap))
        frames,_=runner.snapshot_hashes(self.run)
        for task in self.request['tasks']:
            for g in self.request['generators']:
                folder=runner.execution_folder(self.run,task,g)
                targets=json.loads((folder/'targets.json').read_text())
                prompt=runner.make_prompt(self.request,task,g,(self.run/task['data_pack']['path']).read_bytes(),
                    self.methods,frames,targets,maintenance=snap['maintenance'],research_validation=snap['research_validation'],
                    delivery=runner.delivery_contract(snap))
                (folder/'prompt.txt').write_bytes(prompt)
                (folder/'input.json').write_bytes(runner.encode(runner.input_record(self.request,
                    self.request_path.read_bytes(),task,g,prompt,frames,targets)))
        self.assertFalse(runner.sequential_research(self.run))
        result=json.loads(self.execute('dsh').read_text())['results'][0]
        self.assertEqual(result['status'],'completed',result['reason'])

    def test_removing_workflow_marker_cannot_downgrade_new_batch(self):
        self.prepare()
        manifest=self.run/'framework-snapshot/manifest.json'
        snap=json.loads(manifest.read_text());snap.pop('evidence_workflow')
        manifest.chmod(0o644);manifest.write_bytes(runner.encode(snap))
        with self.assertRaisesRegex(ValueError,'prompt mismatch'):
            runner.verify_prepared(self.run,self.request_path.read_bytes(),self.methods)

    def test_retry_reuses_same_dependency_and_retains_original_input(self):
        # Uses the existing process/output retry contract; first DSH fails once.
        marker=self.root/'dsh-failed'
        source=parallel.FAKE_CLI.replace("ticker,market=code.split('.')",
            f"marker=Path({str(marker)!r})\nif generator=='dsh' and get('task_id')=='SH-600066' and not marker.exists():\n marker.write_text('failed');sys.exit(3)\nticker,market=code.split('.')")
        self.dsh_cli.write_text(dsh.build_fake_dsh_cli(source))
        self.tick();self.prepare()
        folder=runner.execution_folder(self.run,self.request['tasks'][0],'dsh')
        first=json.loads((folder/'process.json').read_text())
        second=json.loads((folder/'retry-1/process.json').read_text())
        self.assertEqual(second['status'],'completed')
        self.assertEqual(first['shared_evidence_dependency_sha256'],second['shared_evidence_dependency_sha256'])


    def test_missing_codex_packet_is_retryable_and_never_published(self):
        self.fake.write_text(parallel.FAKE_CLI.replace("if generator=='codex' and b'codex-then-dsh-evidence/v1' in payload:",
            "if False:"))
        self.tick();self.prepare()
        task=self.request['tasks'][0]
        folder=runner.execution_folder(self.run,task,'codex')
        self.assertTrue(json.loads((folder/'process.json').read_text())['retryable'])
        self.assertEqual(json.loads((folder/'retry-1/process.json').read_text())['status'],'failed')
        self.assertFalse((runner.execution_folder(self.run,task,'dsh')/'launched.json').exists())
        self.assertFalse(list((self.methods/'research').rglob('*-research-*.md')))

    def test_successful_codex_retry_is_the_only_downstream_source(self):
        marker=self.root/'codex-failed'
        source=parallel.FAKE_CLI.replace("ticker,market=code.split('.')",
            f"marker=Path({str(marker)!r})\nif generator=='codex' and get('task_id')=='SH-600066' and not marker.exists():\n marker.write_text('failed');sys.exit(3)\nticker,market=code.split('.')")
        self.fake.write_text(source)
        self.tick();self.prepare()
        folder=runner.execution_folder(self.run,self.request['tasks'][0],'dsh')
        dependency=json.loads((folder/'runner/evidence-dependency.json').read_text())
        self.assertIn('/codex/retry-1/runner/shared-evidence/',dependency['bundle']['path'])
        self.assertEqual(json.loads((folder/'process.json').read_text())['status'],'completed')

    def test_scheduler_resumes_completed_codex_without_rerunning_it(self):
        original=scheduler.run_provider_entry
        def interrupt_before_dsh(*args,**kwargs):
            if args[1]=='dsh':
                raise RuntimeError('offline scheduler interruption before DSH')
            return original(*args,**kwargs)
        with patch.object(scheduler,'run_provider_entry',side_effect=interrupt_before_dsh):
            self.tick()
        self.tick()
        events=json.loads(self.trace.read_text())['events']
        task=self.request['tasks'][0]['task_id']
        for generator in ('codex','dsh'):
            starts=[e for e in events if e['task_id']==task and e['generator']==generator and e['event']=='start']
            self.assertEqual(len(starts),1)

    def test_dsh_omitting_visible_evidence_binding_is_not_published(self):
        self.prepare();self.execute('codex')
        with patch.dict(os.environ,{'MOCK_MODE':'missing_evidence_binding'}):
            result=json.loads(self.execute('dsh').read_text())['results'][0]
        self.assertEqual(result['status'],'failed')
        self.assertIn('visibly bind',result['reason'])
        self.assertFalse(list((self.methods/'research').rglob('*-research-dsh*.md')))

    def use_four_stocks(self):
        self.request['tasks'] = self.tasks
        self.request_path.write_bytes(runner.encode(self.request))

    def seals(self):
        return [json.loads(p.read_text()) for p in (self.methods/'output/research_queue/sealed').glob('*.json')]

    def scheduler_process(self, log, **environment):
        code = (f'import sys;sys.path.insert(0,{str(ROOT)!r});'
                'from scripts.research_scheduler import tick;'
                f'r=tick({str(self.exchange)!r},{str(self.methods)!r},execute=True,'
                f'clis={{"codex":{str(self.fake)!r},"dsh":{str(self.dsh_cli)!r}}},'
                f'runtime_config={self.config!r},timeout=60,max_concurrency=3);'
                'sys.exit(2 if r.get("failures") else 0)')
        process = subprocess.Popen([sys.executable, '-c', code], stdout=log, stderr=log,
                                   env=dict(os.environ, **environment), start_new_session=True)
        def cleanup():
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=10)
        self.addCleanup(cleanup)
        return process

    def wait_until(self, process, predicate):
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if predicate():
                return
            self.assertIsNone(process.poll(), (self.root/'scheduler.log').read_text())
            time.sleep(.03)
        self.fail('Timed out waiting for offline research progress')

    def test_single_slot_finishes_ready_pair_before_starting_next_stock(self):
        self.use_four_stocks()
        result = self.tick(max_concurrency=1)
        self.assertEqual(result['used'], 4)
        self.assertEqual(result['failures'], [])
        trace = json.loads(self.trace.read_text())
        starts = [(e['task_id'], e['generator']) for e in trace['events'] if e['event']=='start']
        expected = [(t['task_id'], g) for t in self.request['tasks'] for g in ('codex','dsh')]
        self.assertEqual(starts, expected)
        self.assertEqual(trace['maximum'], 1)
        self.assertEqual(len(self.seals()), 4)

    def test_four_stocks_slow_codex_does_not_block_other_pairs_or_exceed_three(self):
        self.use_four_stocks()
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log, MOCK_PARALLEL_HOLD='SH-600066:codex', MOCK_PARALLEL_BARRIER='3')
            self.wait_until(process, lambda: len(self.seals())==3)
            self.assertNotIn('SH-600066', [s['task_id'] for s in self.seals()])
            self.prepare()
            folder = runner.execution_folder(self.run,self.request['tasks'][0],'dsh')
            self.assertFalse((folder/'launched.json').exists())
            trace = json.loads(self.trace.read_text())
            held = next(e for e in trace['events'] if e['task_id']=='SH-600066' and e['event']=='start')
            self.assertTrue(any(e['generator']=='dsh' and e['event']=='start' and e['at']>held['at'] for e in trace['events']))
            (self.root/'release').touch()
            self.assertEqual(process.wait(timeout=12), 0, (self.root/'scheduler.log').read_text())
        trace = json.loads(self.trace.read_text())
        self.assertEqual(trace['maximum'], 3)
        self.assertEqual(trace['active'], [])
        self.assertEqual(len(self.seals()), 4)
        for task in self.request['tasks']:
            folder = runner.execution_folder(self.run,task,'dsh')
            dependency = json.loads((folder/'runner/evidence-dependency.json').read_text())
            bundle = json.loads((self.methods/dependency['bundle']['path']).read_text())
            self.assertEqual(bundle['task_id'],task['task_id'])
            self.assertEqual(bundle['input_pack_sha256'],task['data_pack']['sha256'])

    def test_slow_dsh_never_publishes_partial_seal_while_other_pairs_finish(self):
        self.use_four_stocks()
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log, MOCK_PARALLEL_HOLD='SH-600066:dsh')
            self.wait_until(process, lambda: len(self.seals())==3)
            self.prepare()
            first = self.request['tasks'][0]
            self.assertTrue((runner.execution_folder(self.run,first,'codex')/'accepted.json').exists())
            self.assertFalse((runner.execution_folder(self.run,first,'dsh')/'entry.json').exists())
            self.assertNotIn(first['task_id'],[s['task_id'] for s in self.seals()])
            (self.root/'release').touch()
            self.assertEqual(process.wait(timeout=12),0,(self.root/'scheduler.log').read_text())
        for seal in self.seals():
            self.assertEqual([x['generator'] for x in seal['results']],['codex','dsh'])

    def test_cancel_cleans_codex_groups_and_never_claims_waiting_dsh(self):
        self.use_four_stocks()
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log,MOCK_PARALLEL_SLEEP='30')
            self.wait_until(process,lambda:self.trace.exists() and len(json.loads(self.trace.read_text())['active'])==3)
            with self.assertRaises(BlockingIOError):
                self.tick()
            process.send_signal(signal.SIGTERM)
            self.assertEqual(process.wait(timeout=12),2)
        self.prepare()
        claims = list((self.run/'execution').glob('*/*/launched.json'))
        self.assertEqual(len(claims),3)
        self.assertTrue(all(p.parent.name=='codex' for p in claims))
        for path in (self.run/'execution').glob('*/*/process.json'):
            value = json.loads(path.read_text())
            self.assertEqual(value['status'],'failed')
            self.assertFalse(runner.group_alive(value['pid']))
        self.assertEqual(self.seals(),[])

    def test_codex_timeout_retries_cleanup_without_releasing_its_dsh(self):
        with patch.dict(os.environ,{'MOCK_PARALLEL_SLOW':'SH-600066:codex'}):
            self.tick(timeout=1)
        self.prepare()
        first = self.request['tasks'][0]
        folder = runner.execution_folder(self.run,first,'codex')
        for attempt in (folder,folder/'retry-1'):
            process = json.loads((attempt/'process.json').read_text())
            entry = json.loads((attempt/'entry.json').read_text())
            self.assertEqual(process['status'],'failed')
            self.assertIn('timeout',entry['reason'])
            self.assertFalse(runner.group_alive(process['pid']))
        self.assertFalse((runner.execution_folder(self.run,first,'dsh')/'launched.json').exists())
        second = runner.execution_folder(self.run,self.request['tasks'][1],'dsh')
        self.assertEqual(json.loads((second/'entry.json').read_text())['status'],'completed')

    def test_dsh_can_continue_started_pair_after_midnight_with_original_cutoff(self):
        self.prepare();self.execute('codex')
        later = (datetime.fromisoformat(runner.stamp())+timedelta(days=1)).isoformat()
        with patch.object(runner,'stamp',return_value=later):
            result = runner.run_batch(self.request_path,self.methods,generator='dsh',cli=str(self.dsh_cli),
                timeout=10,task_ids=[self.request['tasks'][0]['task_id']],runtime_config=self.config,launch_date=self.day)
        entry = json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'],'completed',entry['reason'])
        price = json.loads((self.methods/entry['price_map']['path']).read_text())
        self.assertEqual(price['meta']['valuation_date'],self.day)



    def test_ready_dsh_does_not_starve_last_codex_when_multiple_slots_exist(self):
        self.use_four_stocks()
        source = parallel.FAKE_CLI.replace("ticker,market=code.split('.')",
            "if generator=='dsh':\n while not Path(os.environ['MOCK_PARALLEL_RELEASE']).exists(): time.sleep(.02)\nticker,market=code.split('.')")
        self.dsh_cli.write_text(dsh.build_fake_dsh_cli(source))
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log,MOCK_PARALLEL_BARRIER='3')
            self.wait_until(process,lambda:self.trace.exists() and any(
                e['task_id']=='SH-600519' and e['generator']=='codex' and e['event']=='end'
                for e in json.loads(self.trace.read_text())['events']))
            events = json.loads(self.trace.read_text())['events']
            self.assertFalse(any(e['generator']=='dsh' and e['event']=='end' for e in events))
            (self.root/'release').touch()
            self.assertEqual(process.wait(timeout=12),0,(self.root/'scheduler.log').read_text())
        self.assertEqual(len(self.seals()),4)
        self.assertEqual(json.loads(self.trace.read_text())['maximum'],3)



    def test_ready_dsh_uses_free_slot_before_new_stock_when_codex_is_in_flight(self):
        self.use_four_stocks()
        source = parallel.FAKE_CLI.replace("ticker,market=code.split('.')",
            "if generator=='codex' and get('task_id') in ('SH-600066','SH-600276'):\n while not Path(os.environ['MOCK_PARALLEL_RELEASE']).exists(): time.sleep(.02)\nticker,market=code.split('.')")
        self.fake.write_text(source)
        with (self.root/'scheduler.log').open('wb') as log:
            process = self.scheduler_process(log,MOCK_PARALLEL_BARRIER='3')
            self.wait_until(process,lambda:self.trace.exists() and any(
                e['task_id']=='SH-600519' and e['event']=='start'
                for e in json.loads(self.trace.read_text())['events']))
            events = json.loads(self.trace.read_text())['events']
            dsh_end = next(e['at'] for e in events if e['task_id']=='SH-600900' and e['generator']=='dsh' and e['event']=='end')
            last_start = next(e['at'] for e in events if e['task_id']=='SH-600519' and e['event']=='start')
            self.assertLess(dsh_end,last_start)
            (self.root/'release').touch()
            self.assertEqual(process.wait(timeout=12),0,(self.root/'scheduler.log').read_text())
        self.assertEqual(len(self.seals()),4)



    def test_default_four_slots_preserve_same_stock_order(self):
        self.use_four_stocks()
        with patch.dict(os.environ,{'MOCK_PARALLEL_BARRIER':'4'}):
            result = scheduler.tick(self.exchange,self.methods,execute=True,
                clis={'codex':str(self.fake),'dsh':str(self.dsh_cli)},timeout=10,runtime_config=self.config)
        self.assertEqual(result['failures'],[])
        trace = json.loads(self.trace.read_text())
        self.assertEqual(trace['maximum'],4)
        self.assertEqual(trace['active'],[])
        self.assertEqual(len(self.seals()),4)
        for task in self.request['tasks']:
            events = [e for e in trace['events'] if e['task_id']==task['task_id']]
            codex_end = next(e['at'] for e in events if e['generator']=='codex' and e['event']=='end')
            dsh_start = next(e['at'] for e in events if e['generator']=='dsh' and e['event']=='start')
            self.assertLess(codex_end,dsh_start)



if __name__=='__main__':unittest.main()
