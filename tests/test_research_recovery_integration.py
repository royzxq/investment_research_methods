"""Real frozen requests, failed seats and synthetic DSH recovery, without APIs."""
from copy import deepcopy
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tests'))
import test_research_runner as runner_fixture
import test_research_dsh as dsh_fixture
from scripts import research_coze as coze
from scripts import research_exchange as exchange
from scripts import research_recovery as recovery
from scripts import research_runner as runner
from scripts import research_runtime as runtime
from scripts import research_scheduler as scheduler


class RecoveryIntegrationTests(unittest.TestCase):
    def setUp(self):
        f = self.f = runner_fixture.ResearchRunnerTests('runTest')
        f.setUp(); self.addCleanup(f.doCleanups)
        for name in ('root', 'methods', 'exchange', 'pack', 'request_path', 'fake', 'capture'):
            setattr(f, name, getattr(f, name).resolve())
        day = runner.stamp()[:10]
        f.raw_pack = f.raw_pack.replace('20261006', day.replace('-', ''))
        f.pack.write_text(f.raw_pack)
        f.request.update(schema_version=exchange.REQUEST_SCHEMA_V2,
                         created_at=day+'T00:00:00+08:00', valuation_date=day,
                         generators=['codex', 'dsh'])
        task = f.request['tasks'][0]
        task['data_pack']['sha256'] = f.sha(f.pack)
        task['data_pack_meta']['research_trigger'] = dict(event_key='frozen-parent-event')
        f.write_request()
        self.config = runtime.load_config()
        profile = runtime.default_profile('dsh')
        self.config['profiles'].append(profile)
        self.config['active']['dsh'] = profile['profile_id']
        self.dsh_cli = f.root/'fake-dsh'
        self.dsh_cli.write_text(dsh_fixture.build_fake_dsh_cli())
        self.dsh_cli.chmod(0o700)
        env = patch.dict(os.environ, {'DEEPSEEK_API_KEY':'offline-recovery-fixture'})
        env.start(); self.addCleanup(env.stop)
        codex_result = runner.run_batch(f.request_path, f.methods, generator='codex',
            cli=str(f.fake), timeout=5, runtime_config=self.config)
        with patch.dict(os.environ, {'MOCK_MODE':'nonzero'}):
            dsh_result = runner.run_batch(f.request_path, f.methods, generator='dsh',
                cli=str(self.dsh_cli), timeout=5, runtime_config=self.config)
        self.assertEqual(recovery.read(codex_result)['results'][0]['status'], 'completed')
        self.assertEqual(recovery.read(dsh_result)['results'][0]['status'], 'failed')
        self.parent_run = codex_result.parent
        self.original_folder = self.parent_run/'execution/SH-600066/dsh'
        # Production scheduler seals an endpoint's final manifest next to its
        # matching terminal process. No original manifest or process is edited.
        final_dsh = self.original_folder/'results.json'
        runner.write_new(final_dsh, dsh_result.read_bytes())
        self.base = f.methods/'output/research_queue/sealed'/('a'*32+'-SH-600066.json')
        seal = dict(schema_version=exchange.seal_schema(f.request), task_id=task['task_id'],
            batch_id=f.request['batch_id'], event_key='frozen-parent-event', request=str(f.request_path),
            request_sha256=f.sha(f.request_path), budget_date=day, results=[dict(generator=g,
                manifest=p.relative_to(f.methods).as_posix(), manifest_sha256=f.sha(p), actual_model=None)
                for g, p in [('codex', codex_result), ('dsh', final_dsh)]])
        runner.write_new(self.base, runner.encode(seal))
        self.protected = {p:p.read_bytes() for p in f.methods.rglob('*') if p.is_file()}

    def prepare(self, **kwargs):
        options = dict(authorization='explicit human request: recover only failed DSH seat',
            authorized_at=runner.stamp(), recovery_id='b'*32, max_attempts=1, timeout_seconds=5)
        options.update(kwargs)
        return recovery.prepare([self.base], self.f.exchange, self.f.methods, **options)

    def execute(self, intent):
        return recovery.execute(intent, self.f.exchange, self.f.methods, cli=str(self.dsh_cli))

    def refresh_intent_binding(self, path, value):
        path.write_bytes(runner.encode(value))
        descriptor = recovery.descriptor(path, self.f.methods)
        for parent in value['parents']:
            recovery.intent_claim(self.f.methods, parent).write_bytes(runner.encode(descriptor))

    def test_real_recovery_preserves_original_and_reuses_only_dsh_on_reexecution(self):
        intent = self.prepare()
        value, child_request, _ = recovery.load_intent(intent, self.f.methods, self.f.exchange)
        run = self.f.methods/'output/runs/investment'/self.f.request['valuation_date']/value['recovery_id']
        parent_plan = recovery.read(self.parent_run/'framework-snapshot/execution-plan.json')
        child_plan = recovery.read(run/'framework-snapshot/execution-plan.json')
        self.assertEqual(child_plan['profiles'], {'dsh':parent_plan['profiles']['dsh']})
        self.assertEqual(recovery.read(child_request)['tasks'], self.f.request['tasks'])
        self.assertFalse((run/'execution/SH-600066/codex').exists())
        with patch.object(runner, 'run_provider', wraps=runner.run_provider) as launched:
            first = self.execute(intent)
            second = self.execute(intent)
        self.assertEqual(launched.call_count, 1)
        self.assertEqual(first, second)
        self.assertEqual(first[0]['status'], 'completed')
        wrapper = Path(first[0]['supplement'])
        base_path, private, document = recovery.load_supplement(wrapper, self.f.methods, self.f.exchange)
        self.assertEqual(base_path, self.base)
        self.assertEqual(document['results'], recovery.read(self.base)['results'])
        self.assertFalse(private.is_relative_to(self.f.methods/'output/research_queue/sealed'))
        effective = coze.load_base(wrapper, self.f.methods, self.f.exchange)
        self.assertEqual(set(effective['documents']), {'codex', 'dsh'})
        self.assertEqual(effective['request']['batch_id'], self.f.request['batch_id'])
        self.assertEqual({p:p.read_bytes() for p in self.protected}, self.protected)

    def test_recovery_claim_is_unique_and_cannot_authorize_a_second_paid_attempt_set(self):
        intent = self.prepare()
        before = {p:p.read_bytes() for p in self.f.methods.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError, 'already authorized'):
            self.prepare(recovery_id='c'*32)
        self.assertEqual({p:p.read_bytes() for p in before}, before)
        self.assertFalse((self.f.exchange/'recoveries'/('c'*32)).exists())
        recovery.load_intent(intent, self.f.methods, self.f.exchange)

    def assert_cross_day_recovery(self, intent):
        state = scheduler.new_state()
        day = self.f.request['valuation_date']
        state['days'] = {day:{'SH-600066':{'immutable':'reservation'}}}
        scheduler.sync_started(state, self.f.methods)
        before = deepcopy(state)
        first = self.execute(intent)
        self.assertEqual(first[0]['status'], 'completed')
        with patch.object(runner, 'run_provider') as launched:
            self.assertEqual(self.execute(intent), first)
        launched.assert_not_called()
        _, child_path, _ = recovery.load_intent(intent, self.f.methods, self.f.exchange)
        child = recovery.read(child_path)
        self.assertEqual(child['valuation_date'], day)
        self.assertEqual(child['tasks'], self.f.request['tasks'])
        self.assertEqual(child['generators'], ['dsh'])
        recovery.load_supplement(first[0]['supplement'], self.f.methods, self.f.exchange)
        scheduler.sync_started(state, self.f.methods)
        self.assertEqual(state, before)
        self.assertEqual({p:p.read_bytes() for p in self.protected}, self.protected)

    def test_authorized_recovery_prepared_and_started_after_original_day(self):
        tomorrow = (datetime.fromisoformat(runner.stamp()) + timedelta(days=1)).isoformat()
        with patch.object(runner, 'stamp', return_value=tomorrow):
            self.assert_cross_day_recovery(self.prepare())

    def test_authorized_recovery_prepared_before_midnight_can_start_next_day(self):
        intent = self.prepare()
        tomorrow = (datetime.fromisoformat(runner.stamp()) + timedelta(days=1)).isoformat()
        with patch.object(runner, 'stamp', return_value=tomorrow):
            self.assert_cross_day_recovery(intent)

    def test_intent_request_and_claim_tampering_fail_before_launch(self):
        intent = self.prepare()
        value = recovery.read(intent)
        child = Path(value['request']['path'])
        claim = recovery.intent_claim(self.f.methods, value['parents'][0])
        for target in (intent, child, claim):
            original = target.read_bytes()
            if target == claim:
                changed = recovery.read(target)
                changed['sha256'] = '0'*64
                target.write_bytes(runner.encode(changed))
            else:
                target.write_bytes(original+b' ')
            with self.subTest(target=target.name), patch.object(runner, 'run_provider') as launched:
                with self.assertRaises(ValueError):
                    self.execute(intent)
                launched.assert_not_called()
            target.write_bytes(original)

    def test_exact_frozen_task_date_pack_and_event_cannot_be_changed_by_rehashing(self):
        intent = self.prepare()
        value = recovery.read(intent)
        child = Path(value['request']['path'])
        original_request = child.read_bytes()
        original_intent = intent.read_bytes()
        claim = recovery.intent_claim(self.f.methods, value['parents'][0])
        original_claim = claim.read_bytes()
        mutations = [lambda x:x['tasks'][0].update(name='different company'),
                     lambda x:x['tasks'][0]['data_pack_meta']['research_trigger'].update(event_key='other-event'),
                     lambda x:x['tasks'][0].update(code='600900.SH', task_id='SH-600900'),
                     lambda x:x.update(valuation_date='2000-01-01')]
        for mutate in mutations:
            request = json.loads(original_request)
            mutate(request)
            child.write_bytes(runner.encode(request))
            changed = deepcopy(value)
            changed['request']['sha256'] = recovery.sha(child)
            self.refresh_intent_binding(intent, changed)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                recovery.load_intent(intent, self.f.methods, self.f.exchange)
            child.write_bytes(original_request); intent.write_bytes(original_intent); claim.write_bytes(original_claim)
        pack = child.parent/self.f.request['tasks'][0]['data_pack']['path']
        raw = pack.read_bytes(); pack.write_bytes(raw+b'changed')
        with self.assertRaises(ValueError):
            recovery.load_intent(intent, self.f.methods, self.f.exchange)

    def test_current_model_configuration_cannot_replace_frozen_parent_profile(self):
        intent = self.prepare()
        value = recovery.read(intent)
        run = self.f.methods/'output/runs/investment'/self.f.request['valuation_date']/value['recovery_id']
        plan_path = run/'framework-snapshot/execution-plan.json'
        plan = recovery.read(plan_path)
        plan['profiles']['dsh']['models']['main']['model'] = 'different-model'
        plan_path.chmod(0o644); plan_path.write_bytes(runtime.canonical_bytes(plan))
        manifest_path = run/'framework-snapshot/manifest.json'
        manifest = recovery.read(manifest_path)
        manifest['execution_plan']['sha256'] = recovery.sha(plan_path)
        manifest_path.chmod(0o644); manifest_path.write_bytes(runner.encode(manifest))
        with patch.object(runner, 'run_provider') as launched, self.assertRaises(ValueError):
            self.execute(intent)
        launched.assert_not_called()

    def test_original_completed_dsh_seat_cannot_be_recovered(self):
        # A genuine completed opinion is never treated as failed even when its
        # price/control conclusion is inconvenient. Use the real shared runner.
        new_batch = deepcopy(self.f.request)
        new_batch['batch_id'] = 'd'*32
        path = self.f.exchange/'completed/request.json'
        runner.write_new(path.parent/new_batch['tasks'][0]['data_pack']['path'], self.f.pack.read_bytes())
        runner.write_new(path, runner.encode(new_batch))
        codex = runner.run_batch(path, self.f.methods, generator='codex', cli=str(self.f.fake),
                                 timeout=5, runtime_config=self.config)
        self.assertEqual(recovery.read(codex)['results'][0]['status'], 'completed')
        result = runner.run_batch(path, self.f.methods, generator='dsh', cli=str(self.dsh_cli),
                                  timeout=5, runtime_config=self.config)
        entry = recovery.read(result)['results'][0]
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        with self.assertRaisesRegex(ValueError, 'explicit failed'):
            recovery.require_failed(entry)

    def test_history_reconstruction_keeps_original_round_and_daily_budget(self):
        state = scheduler.new_state()
        state['days'] = {self.f.request['valuation_date']:{'SH-600066':{'immutable':'reservation'}}}
        scheduler.sync_started(state, self.f.methods)
        before = deepcopy(state)
        intent = self.prepare()
        self.execute(intent)
        scheduler.sync_started(state, self.f.methods)
        self.assertEqual(state, before)
        self.assertEqual(state['last_started']['SH-600066']['batch_id'], self.f.request['batch_id'])

    def test_original_failure_process_must_match_before_authorization(self):
        path = self.original_folder/'process.json'
        value = recovery.read(path)
        value['status'] = 'completed'
        path.write_bytes(runner.encode(value))
        with self.assertRaisesRegex(ValueError, 'terminal process'):
            self.prepare()
        self.assertFalse((self.f.exchange/'recoveries').exists())

    def test_published_child_cannot_outlive_failed_native_or_process_terminal(self):
        intent = self.prepare()
        first = self.execute(intent)
        wrapper = Path(first[0]['supplement'])
        private = recovery.read(first[0]['private_seal'])
        folder = (self.f.methods/private['results'][0]['manifest']).parent
        process_path = folder/'process.json'
        original_process = process_path.read_bytes()
        process = recovery.read(process_path)
        process.update(status='failed', reason='supervisor cancelled')
        process_path.write_bytes(runner.encode(process))
        with self.assertRaises(ValueError):
            recovery.load_supplement(wrapper, self.f.methods, self.f.exchange)
        process_path.write_bytes(original_process)
        events_path = folder/'events.jsonl'
        raw = events_path.read_text()
        events_path.write_text(raw.replace('"kind": "completed"', '"kind": "aborted"'))
        with self.assertRaises(ValueError):
            recovery.load_supplement(wrapper, self.f.methods, self.f.exchange)

    def test_persisted_jev_runtime_configuration_cannot_drift_after_success(self):
        intent = self.prepare()
        first = self.execute(intent)
        private = recovery.read(first[0]['private_seal'])
        folder = (self.f.methods/private['results'][0]['manifest']).parent
        config = folder/'jev/config.json'
        config.write_bytes(config.read_bytes()+b' ')
        with self.assertRaises(ValueError):
            recovery.load_supplement(first[0]['supplement'], self.f.methods, self.f.exchange)

    def test_incomplete_attempt_is_preserved_without_duplicate_launch(self):
        intent = self.prepare()
        value = recovery.read(intent)
        run = self.f.methods/'output/runs/investment'/self.f.request['valuation_date']/value['recovery_id']
        folder = run/'execution/SH-600066/dsh'
        runner.write_new(folder/'launched.json', runner.encode(dict(
            claimed_at=runner.stamp(), request_sha256=value['request']['sha256'])))
        with patch.object(runner, 'run_provider') as launched, \
             self.assertRaisesRegex(ValueError, 'incomplete recovery attempt'):
            self.execute(intent)
        launched.assert_not_called()
        self.assertTrue((folder/'launched.json').exists())
        self.assertFalse((folder/'entry.json').exists())

    def test_finite_failed_recovery_preserves_both_attempts_and_never_creates_wrapper(self):
        intent = self.prepare(max_attempts=2)
        with patch.dict(os.environ, {'MOCK_MODE':'nonzero'}), \
             patch.object(runner, 'run_provider', wraps=runner.run_provider) as launched:
            first = self.execute(intent)
            second = self.execute(intent)
        self.assertEqual(launched.call_count, 2)
        self.assertEqual(first, second)
        self.assertEqual(first[0]['status'], 'failed')
        self.assertIsNone(first[0]['supplement'])
        folder = self.f.methods/'output/runs/investment'/self.f.request['valuation_date']/('b'*32)/'execution/SH-600066/dsh'
        self.assertEqual(recovery.read(folder/'entry.json')['status'], 'failed')
        self.assertEqual(recovery.read(folder/'retry-1/entry.json')['status'], 'failed')
        self.assertEqual(recovery.read(first[0]['private_seal'])['results'][0]['generator'], 'dsh')
        self.assertEqual({p:p.read_bytes() for p in self.protected}, self.protected)

    def test_existing_manifest_cannot_mask_changed_terminal_entry_on_execute(self):
        intent = self.prepare()
        first = self.execute(intent)
        private = recovery.read(first[0]['private_seal'])
        folder = (self.f.methods/private['results'][0]['manifest']).parent
        entry_path = folder/'entry.json'
        changed = recovery.read(entry_path)
        changed['completed_at'] = changed['started_at']
        entry_path.write_bytes(runner.encode(changed))
        with patch.object(runner, 'run_provider') as launched, self.assertRaises(ValueError):
            self.execute(intent)
        launched.assert_not_called()

    def test_failed_final_seal_does_not_hide_still_running_previous_parent_attempt(self):
        # A final retry seal is insufficient proof that every original attempt
        # has settled. Preserve the original first attempt and create a genuine
        # matching final failure, then make that prior process nonterminal.
        seal = recovery.read(self.base)
        final = self.original_folder/'retry-1'
        for name in ('process.json', 'entry.json', 'launched.json', 'results.json'):
            runner.write_new(final/name, (self.original_folder/name).read_bytes())
        descriptor = next(x for x in seal['results'] if x['generator'] == 'dsh')
        descriptor['manifest'] = (final/'results.json').relative_to(self.f.methods).as_posix()
        descriptor['manifest_sha256'] = recovery.sha(final/'results.json')
        self.base.write_bytes(runner.encode(seal))
        process = recovery.read(self.original_folder/'process.json')
        process.update(status='running', completed_at=None, reason=None)
        (self.original_folder/'process.json').write_bytes(runner.encode(process))
        with self.assertRaises((ValueError, RuntimeError)):
            self.prepare()
        self.assertFalse((self.f.exchange/'recoveries').exists())

    def test_completed_codex_manifest_does_not_hide_nonterminal_parent_process(self):
        folder = self.parent_run/'execution/SH-600066/codex'
        path = folder/'process.json'
        process = recovery.read(path)
        process.update(status='running', completed_at=None, reason=None)
        path.write_bytes(runner.encode(process))
        with self.assertRaises((ValueError, RuntimeError)):
            self.prepare()
        self.assertFalse((self.f.exchange/'recoveries').exists())

    def test_now_terminal_parent_cannot_finish_after_original_seal_evidence(self):
        seal = recovery.read(self.base)
        cutoff = max(datetime.fromisoformat(recovery.read(self.f.methods/item['manifest'])['created_at'])
                     for item in seal['results'])
        late = (cutoff+timedelta(seconds=1)).isoformat()
        folder = self.parent_run/'execution/SH-600066/codex'
        for name in ('process.json', 'entry.json'):
            path = folder/name
            value = recovery.read(path)
            value['completed_at'] = late
            path.write_bytes(runner.encode(value))
        with self.assertRaisesRegex(ValueError, 'chronology|seal|terminal'):
            self.prepare()
        self.assertFalse((self.f.exchange/'recoveries').exists())


if __name__ == '__main__':
    unittest.main()
