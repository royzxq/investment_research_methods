"""Frozen scheduler profiles exercised through contract-valid offline CLIs."""
from copy import deepcopy
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_runner as runner
from scripts import research_runtime as runtime
from scripts import research_scheduler as scheduler
from scripts import research_harness as harness

_spec = importlib.util.spec_from_file_location('_scheduler_profiles_fixture', ROOT/'tests/test_research_parallel.py')
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)

PROFILE_OBSERVATION = r'''
profile_capture=Path(os.environ['MOCK_PROFILE_CAPTURES'])
profile_capture.mkdir(exist_ok=True)
(profile_capture/f'{os.getpid()}.json').write_text(json.dumps({
 'generator':generator,'argv':args,'executable':sys.argv[0],
 'subagent_model':os.environ.get('CLAUDE_CODE_SUBAGENT_MODEL')}))
print(json.dumps({'type':'turn.started','model':'observed-codex'}) if generator=='codex'
      else json.dumps({'type':'system','subtype':'init','model':'observed-claude'}),flush=True)
retry_marker=profile_capture/f'{generator}-first-failed'
if os.environ.get('MOCK_PROFILE_RETRY')==generator and not retry_marker.exists():
 retry_marker.write_text('first failure')
 Path(os.environ['MOCK_PROFILE_CONFIG']).write_text('invalid current configuration during retry')
 sys.exit(3)
'''
PROFILE_CLI = _fixture.FAKE_CLI.replace(
    "if '--help' in args:\n", "if '--help' in args:\n print('  --model <MODEL>\\n  --effort <EFFORT>')\n",
).replace("ticker,market=code.split('.')", PROFILE_OBSERVATION + "\nticker,market=code.split('.')")


class SchedulerProfileTests(unittest.TestCase):
    setUp_fixture = _fixture.ParallelResearchTests.setUp

    def setUp(self):
        self.setUp_fixture()
        self.request = json.loads(self.request_path.read_text())
        self.request['tasks'] = self.request['tasks'][:1]
        self.request_path.write_bytes(runtime.canonical_bytes(self.request))
        self.fake.write_text(PROFILE_CLI)
        self.captures = self.root/'profile-captures'
        self.config_path = self.root/'runtime.json'
        self.profile_env = patch.dict(os.environ, {
            'MOCK_PROFILE_CAPTURES': str(self.captures), 'MOCK_PROFILE_RETRY': '',
            'MOCK_PROFILE_CONFIG': str(self.config_path), 'CLAUDE_CODE_SUBAGENT_MODEL': '',
            'MOCK_PARALLEL_BARRIER': '0', 'MOCK_PARALLEL_SLEEP': '0',
        })
        self.profile_env.start()
        self.addCleanup(self.profile_env.stop)

    @property
    def run_root(self):
        return self.methods/'output/runs/investment'/self.day/('a'*32)

    def custom_config(self, generators=('codex', 'claude')):
        profiles = []
        for producer in generators:
            profile = runtime.default_profile(producer)
            profile.update(profile_id=producer+'-requested', revision=2)
            profile['models']['main'].update(model='requested-'+producer, effort='high')
            if producer == 'claude':
                profile['models']['subagent']['model'] = 'requested-subagent'
            profiles.append(profile)
        return runtime.validate_config(dict(schema_version=runtime.CONFIG_SCHEMA, profiles=profiles,
                                            active={p['producer']: p['profile_id'] for p in profiles}))

    def run_tick(self, **options):
        options.setdefault('clis', {'codex': str(self.fake), 'claude': str(self.fake)})
        with patch.object(scheduler, 'datetime', wraps=datetime) as clock:
            clock.now.return_value = self.now
            return scheduler.tick(self.exchange, self.methods, execute=True, timeout=10, **options)

    def captured(self):
        return [json.loads(path.read_text()) for path in self.captures.glob('*.json')]

    def assert_no_reservation_or_launch(self):
        queue = self.methods/'output/research_queue'
        self.assertFalse((queue/'state.json').exists())
        self.assertFalse((queue/'initialized.json').exists())
        self.assertFalse(list(self.run_root.glob('execution/*/*/launched.json')))
        self.assertEqual(self.captured(), [])

    def test_tick_freezes_explicit_profiles_and_preserves_seal_production_identity(self):
        config = self.custom_config()
        self.config_path.write_bytes(runtime.canonical_bytes(config))
        request_raw = self.request_path.read_bytes()
        result = self.run_tick(runtime_config=self.config_path)
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['used'], 1)
        self.assertEqual(self.request_path.read_bytes(), request_raw)
        self.assertEqual((self.run_root/'request.json').read_bytes(), request_raw)
        plan = json.loads((self.run_root/'framework-snapshot/execution-plan.json').read_text())
        captured = {item['generator']: item for item in self.captured()}
        for producer in ('codex', 'claude'):
            profile = plan['profiles'][producer]
            self.assertEqual(profile['models']['main']['model'], 'requested-'+producer)
            args = captured[producer]['argv']
            self.assertEqual(args[args.index('--model')+1], 'requested-'+producer)
            process = json.loads((self.run_root/'execution/SH-600066'/producer/'process.json').read_text())
            self.assertEqual(process['execution_profile'], profile)
        self.assertEqual(captured['claude']['subagent_model'], 'requested-subagent')
        seal = json.loads(next((self.methods/'output/research_queue/sealed').glob('*.json')).read_text())
        self.assertEqual(set(seal), {'schema_version', 'task_id', 'batch_id', 'event_key', 'request',
                                     'request_sha256', 'budget_date', 'results'})
        self.assertEqual(seal['schema_version'], 'research-sealed/v1')
        self.assertEqual([item['generator'] for item in seal['results']], ['codex', 'claude'])
        self.assertEqual([item['actual_model'] for item in seal['results']], ['observed-codex', 'observed-claude'])

    def test_frozen_batch_resumes_when_current_config_file_is_invalid(self):
        config = self.custom_config()
        runner.prepare_request(self.request_path, self.methods, runtime_config=config)
        frozen_raw = (self.run_root/'framework-snapshot/execution-plan.json').read_bytes()
        records, rejected = scheduler.scan_requests(self.exchange, self.now)
        self.assertEqual(rejected, [])
        state = scheduler.new_state()
        scheduler.merge_candidates(state, records, self.now)
        scheduler.reserve(state, self.now)[0]['status'] = 'interrupted'
        scheduler.atomic_json(self.methods/'output/research_queue/state.json', state)
        self.config_path.write_text('not JSON anymore')
        with patch.object(runtime, 'load_config', side_effect=AssertionError('frozen resume must not read live config')):
            result = self.run_tick(runtime_config=self.config_path)
        self.assertEqual(result['failures'], [])
        self.assertEqual((self.run_root/'framework-snapshot/execution-plan.json').read_bytes(), frozen_raw)
        for capture in self.captured():
            self.assertEqual(capture['argv'][capture['argv'].index('--model')+1], 'requested-'+capture['generator'])

    def test_legacy_prepared_batch_inherits_defaults_despite_invalid_current_config(self):
        runner.prepare_request(self.request_path, self.methods)
        snapshot_path = self.run_root/'framework-snapshot/manifest.json'
        snapshot = json.loads(snapshot_path.read_text())
        del snapshot['execution_plan']
        snapshot_path.chmod(0o644)
        snapshot_path.write_bytes(runtime.canonical_bytes(snapshot))
        (self.run_root/'framework-snapshot/execution-plan.json').unlink()
        self.config_path.write_text('invalid current configuration')
        with patch.object(runtime, 'load_config', side_effect=AssertionError('legacy must inherit defaults')):
            result = self.run_tick(runtime_config=self.config_path)
        self.assertEqual(result['failures'], [])
        self.assertFalse((self.run_root/'framework-snapshot/execution-plan.json').exists())
        for capture in self.captured():
            self.assertNotIn('--model', capture['argv'])
            self.assertNotIn('--effort', capture['argv'])

    def test_requested_model_capability_failure_happens_before_reservation(self):
        self.fake.write_text(_fixture.FAKE_CLI)
        with patch.object(scheduler, 'reserve', wraps=scheduler.reserve) as reserve:
            with self.assertRaisesRegex(ValueError, '--model'):
                self.run_tick(runtime_config=self.custom_config())
        reserve.assert_not_called()
        self.assert_no_reservation_or_launch()

    def test_invalid_new_configuration_is_rejected_before_reservation(self):
        config = self.custom_config()
        config['profiles'][0]['token'] = 'PRIVATE-SECRET-VALUE'
        with patch.object(scheduler, 'reserve', wraps=scheduler.reserve) as reserve:
            with self.assertRaises(ValueError) as caught:
                self.run_tick(runtime_config=config)
        self.assertNotIn('PRIVATE', str(caught.exception))
        reserve.assert_not_called()
        self.assert_no_reservation_or_launch()

    def test_frozen_plan_tampering_cannot_fall_back_to_current_configuration(self):
        runner.prepare_request(self.request_path, self.methods, runtime_config=self.custom_config())
        path = self.run_root/'framework-snapshot/execution-plan.json'
        path.chmod(0o644)
        path.write_bytes(path.read_bytes()+b'\n')
        with patch.object(scheduler, 'reserve', wraps=scheduler.reserve) as reserve, \
             patch.object(runtime, 'load_config', side_effect=AssertionError('no fallback allowed')):
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                self.run_tick(runtime_config=self.root/'missing-config.json')
        reserve.assert_not_called()
        self.assert_no_reservation_or_launch()

    def test_missing_snapshot_manifest_cannot_downgrade_to_legacy_preflight(self):
        runner.prepare_request(self.request_path, self.methods, runtime_config=self.custom_config())
        (self.run_root/'framework-snapshot/manifest.json').unlink()
        with patch.object(scheduler, 'reserve', wraps=scheduler.reserve) as reserve, \
             patch.object(runtime, 'load_config', side_effect=AssertionError('no fallback allowed')):
            with self.assertRaises((ValueError, OSError)):
                self.run_tick(runtime_config=self.root/'missing-config.json')
        reserve.assert_not_called()
        self.assert_no_reservation_or_launch()

    def test_single_claude_request_requires_only_its_selected_profile_and_executable(self):
        self.request['generators'] = ['claude']
        self.request_path.write_bytes(runtime.canonical_bytes(self.request))
        with patch.object(scheduler, 'check_codex_cli', side_effect=AssertionError('codex not selected')):
            result = self.run_tick(runtime_config=self.custom_config(('claude',)), clis={'claude': str(self.fake)})
        self.assertEqual(result['failures'], [])
        plan = json.loads((self.run_root/'framework-snapshot/execution-plan.json').read_text())
        self.assertEqual(set(plan['profiles']), {'claude'})
        self.assertEqual([item['generator'] for item in self.captured()], ['claude'])

    def test_retry_keeps_frozen_profile_when_live_config_changes_after_first_launch(self):
        self.request['generators'] = ['claude']
        self.request_path.write_bytes(runtime.canonical_bytes(self.request))
        self.config_path.write_bytes(runtime.canonical_bytes(self.custom_config(('claude',))))
        with patch.dict(os.environ, {'MOCK_PROFILE_RETRY': 'claude'}), \
             patch.object(runtime, 'load_config', wraps=runtime.load_config) as load:
            result = self.run_tick(runtime_config=self.config_path, clis={'claude': str(self.fake)})
        self.assertEqual(result['failures'], [])
        self.assertEqual(load.call_count, 1)
        self.assertEqual(len(self.captured()), 2)
        for capture in self.captured():
            self.assertEqual(capture['argv'][capture['argv'].index('--model')+1], 'requested-claude')
            self.assertEqual(capture['subagent_model'], 'requested-subagent')
        self.assertEqual(self.config_path.read_text(), 'invalid current configuration during retry')
        retry = self.run_root/'execution/SH-600066/claude/retry-1/process.json'
        self.assertEqual(json.loads(retry.read_text())['execution_profile']['profile_id'], 'claude-requested')

    def test_profile_preflight_uses_scheduler_codex_callback_and_all_selected_profiles(self):
        config = self.custom_config()
        called = []
        original = scheduler.preflight_profile
        def preflight(cli, profile, root, *, codex_check=None):
            called.append(deepcopy(profile))
            self.assertIs(codex_check, scheduler.check_codex_cli)
            return original(cli, profile, root, codex_check=codex_check)
        with patch.object(scheduler, 'preflight_profile', side_effect=preflight), \
             patch.object(scheduler, 'check_codex_cli', wraps=scheduler.check_codex_cli) as check:
            result = self.run_tick(runtime_config=config)
        self.assertEqual(result['failures'], [])
        self.assertEqual({profile['profile_id'] for profile in called}, {'codex-requested', 'claude-requested'})
        self.assertEqual(check.call_count, 1)

    def test_empty_tick_and_plan_do_not_load_runtime_configuration(self):
        missing = self.root/'missing-config.json'
        with patch.object(runtime, 'load_config', side_effect=AssertionError('no runtime work')):
            plan = scheduler.tick(self.exchange, self.methods, runtime_config=missing)
            self.assertEqual(len(plan['selected']), 1)
            result = scheduler.tick(self.root/'empty-exchange', self.methods, execute=True,
                                    runtime_config=missing, clis={})
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['used'], 0)

    def test_prepare_entry_only_passes_new_keyword_when_explicit(self):
        records, _ = scheduler.scan_requests(self.exchange, self.now)
        entry = records[0]
        with patch.object(scheduler, 'prepare_request', return_value=self.run_root) as prepare:
            scheduler.prepare_entry(entry, self.methods)
            prepare.assert_called_once_with(Path(entry['request']), self.methods)
        config = self.custom_config()
        with patch.object(scheduler, 'prepare_request', return_value=self.run_root) as prepare:
            scheduler.prepare_entry(entry, self.methods, runtime_config=config)
            prepare.assert_called_once_with(Path(entry['request']), self.methods, runtime_config=config)

    def test_cli_forwards_explicit_config_without_changing_service(self):
        with patch.object(scheduler, 'tick', return_value={'mode': 'plan'}) as tick, \
             patch('builtins.print'):
            self.assertEqual(scheduler.main(['plan', '--runtime-config', str(self.config_path)]), 0)
        self.assertEqual(tick.call_args.kwargs['runtime_config'], self.config_path)
        self.assertFalse(tick.call_args.kwargs['execute'])

    def test_cli_defers_default_executable_resolution_and_only_forwards_explicit_overrides(self):
        with patch.object(scheduler, 'default_cli', side_effect=AssertionError('resolve the frozen profile later')), \
             patch.object(scheduler, 'tick', return_value={'mode': 'plan'}) as tick, \
             patch('builtins.print'):
            self.assertEqual(scheduler.main(['plan']), 0)
            self.assertEqual(tick.call_args.kwargs['clis'], {})
            self.assertEqual(scheduler.main(['plan', '--claude-cli', '/explicit/claude']), 0)
            self.assertEqual(tick.call_args.kwargs['clis'], {'claude': '/explicit/claude'})

    def test_mixed_frozen_and_new_harnesses_resolve_executables_per_profile(self):
        class AlternateClaude(harness.ClaudeCodeCLIAdapter):
            harness_id = 'scheduler-alternate-claude'
            executable = 'scheduler-alternate-cli'

        self.request['generators'] = ['claude']
        self.request_path.write_bytes(runtime.canonical_bytes(self.request))
        runner.prepare_request(self.request_path, self.methods, runtime_config=self.custom_config(('claude',)))
        old_plan_path = self.run_root/'framework-snapshot/execution-plan.json'
        frozen_raw = old_plan_path.read_bytes()
        second = deepcopy(self.request)
        second['batch_id'] = 'b'*32
        second['tasks'] = [deepcopy(self.tasks[1])]
        request_path = self.exchange/'requests'/second['batch_id']/'request.json'
        second_pack = request_path.parent/second['tasks'][0]['data_pack']['path']
        second_pack.parent.mkdir(parents=True)
        source_pack = self.request_path.parent/second['tasks'][0]['data_pack']['path']
        second_pack.write_bytes(source_pack.read_bytes())
        request_path.write_bytes(runtime.canonical_bytes(second))
        bin_dir = self.root/'profile-bin'
        bin_dir.mkdir()
        for executable, observed in (('claude', 'observed-old-harness'),
                                     ('scheduler-alternate-cli', 'observed-new-harness')):
            path = bin_dir/executable
            path.write_text(PROFILE_CLI.replace("'model':'observed-claude'", "'model':"+repr(observed)))
            path.chmod(0o700)
        new_config = self.custom_config(('claude',))
        new_profile = new_config['profiles'][0]
        new_profile.update(profile_id='claude-new-harness', harness=AlternateClaude.harness_id)
        new_profile['models']['main']['model'] = 'new-harness-model'
        new_config['active']['claude'] = new_profile['profile_id']
        checked = []
        original_preflight = scheduler.preflight_profile
        def preflight(cli, profile, root, *, codex_check=None):
            checked.append((profile['harness'], Path(cli).name))
            return original_preflight(cli, profile, root, codex_check=codex_check)
        with patch.dict(harness._ADAPTERS, {AlternateClaude.harness_id: AlternateClaude()}), \
             patch.dict(os.environ, {'PATH': str(bin_dir)+os.pathsep+os.environ.get('PATH', '')}), \
             patch.object(scheduler, 'preflight_profile', side_effect=preflight):
            result = self.run_tick(runtime_config=new_config, clis={})
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['used'], 2)
        self.assertEqual(set(checked), {('claude-code-cli', 'claude'),
                                       (AlternateClaude.harness_id, AlternateClaude.executable)})
        captures = {capture['argv'][capture['argv'].index('--model')+1]: capture for capture in self.captured()}
        self.assertEqual(Path(captures['requested-claude']['executable']).name, 'claude')
        self.assertEqual(Path(captures['new-harness-model']['executable']).name, AlternateClaude.executable)
        self.assertEqual(old_plan_path.read_bytes(), frozen_raw)
        new_plan = json.loads((self.methods/'output/runs/investment'/self.day/second['batch_id'] /
                               'framework-snapshot/execution-plan.json').read_text())
        self.assertEqual(new_plan['profiles']['claude']['harness'], AlternateClaude.harness_id)
        actual_models = {seal['results'][0]['actual_model'] for seal in (
            json.loads(path.read_text()) for path in (self.methods/'output/research_queue/sealed').glob('*.json'))}
        self.assertEqual(actual_models, {'observed-old-harness', 'observed-new-harness'})


if __name__ == '__main__':
    unittest.main()
