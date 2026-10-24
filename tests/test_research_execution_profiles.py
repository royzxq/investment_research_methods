"""Profile routing and immutable execution exercised with local fake CLIs only."""
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import test_research_runner as fixtures
from scripts import research_runner as runner, research_runtime as runtime, research_harness as harness


class ExecutionProfileIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ResearchRunnerTests('runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.args_path = self.f.root / 'arguments.json'
        self.child_path = self.f.root / 'child-model.txt'
        self.env = patch.dict(os.environ, {'MOCK_ARGS': str(self.args_path), 'MOCK_CHILD_MODEL': str(self.child_path)})
        self.env.start()
        self.addCleanup(self.env.stop)
        code = fixtures.FAKE_CLI.replace("payload=sys.stdin.buffer.read()", """Path(os.environ['MOCK_ARGS']).write_text(json.dumps(args))
Path(os.environ['MOCK_CHILD_MODEL']).write_text(os.environ.get('CLAUDE_CODE_SUBAGENT_MODEL',''))
payload=sys.stdin.buffer.read()""")
        code = code.replace("print('  --no-daemon')", "print('  --no-daemon\\n  --model <MODEL>\\n  --effort <EFFORT>')")
        code = code.replace("print('  --approve-for-me", "print('  --model <MODEL>\\n  --approve-for-me")
        self.f.fake.write_text(code)

    def config(self, model='requested-model', child='requested-child', effort='high'):
        config = runtime.load_config()
        profile = next(p for p in config['profiles'] if p['producer'] == 'claude')
        profile['profile_id'] = 'claude-configured'
        profile['revision'] = 2
        profile['models']['main'].update(model=model, effort=effort)
        profile['models']['subagent']['model'] = child
        config['active']['claude'] = profile['profile_id']
        return config

    def prepare(self, config=None):
        return runner.prepare_request(self.f.request_path, self.f.methods, runtime_config=config)

    def execute(self, config=None, **kw):
        return runner.run_batch(self.f.request_path, self.f.methods, generator='claude',
                                cli=str(self.f.fake), timeout=10, runtime_config=config, **kw)

    def context(self, run):
        request, raw, _ = runner.read_request(run / 'request.json')
        folder = run / 'execution' / request['tasks'][0]['task_id'] / 'claude'
        return request, raw, folder

    def change_plan(self, run):
        path = run / 'framework-snapshot' / runtime.PLAN_FILENAME
        plan = json.loads(path.read_text())
        plan['profiles']['claude']['revision'] += 1
        plan['profiles']['claude']['models']['subagent']['model'] = 'tampered-model'
        path.chmod(0o644)
        path.write_bytes(runtime.canonical_bytes(plan))
        manifest = run / 'framework-snapshot/manifest.json'
        snapshot = json.loads(manifest.read_text())
        snapshot['execution_plan']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.chmod(0o644)
        manifest.write_bytes(runner.encode(snapshot))

    def test_new_plan_binds_request_without_changing_input_contract(self):
        run = self.prepare(self.config())
        request, raw, folder = self.context(run)
        self.assertEqual(raw, self.f.request_path.read_bytes())
        self.assertEqual((run / 'packs/SH-600066.md').read_bytes(), self.f.pack.read_bytes())
        frameworks, snapshot = runner.snapshot_hashes(run)
        plan = runtime.load_plan(run, request, raw, snapshot)
        self.assertEqual(plan['request_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(plan['profiles']['claude']['models']['main']['model'], 'requested-model')
        record = json.loads((folder / 'input.json').read_text())
        targets = json.loads((folder / 'targets.json').read_text())
        self.assertEqual(record, runner.input_record(request, raw, request['tasks'][0], 'claude',
                                                    (folder / 'prompt.txt').read_bytes(), frameworks, targets))
        self.assertNotIn('execution_profile', record)
        self.assertNotIn(b'requested-model', (folder / 'prompt.txt').read_bytes())

    def test_explicit_model_options_and_child_environment_reach_cli(self):
        result = self.execute(self.config())
        entry = json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        args = json.loads(self.args_path.read_text())
        self.assertEqual(args[args.index('--model') + 1], 'requested-model')
        self.assertEqual(args[args.index('--effort') + 1], 'high')
        self.assertEqual(self.child_path.read_text(), 'requested-child')
        _, _, folder = self.context(result.parent)
        process = json.loads((folder / 'process.json').read_text())
        self.assertEqual(process['execution_profile']['profile_id'], 'claude-configured')
        self.assertIsNone(process['actual_model'])
        self.assertEqual(set(entry), runner.ENTRY_KEYS if hasattr(runner, 'ENTRY_KEYS') else
                         {'task_id','generator','status','reason','started_at','completed_at','report','price_map'})

    def test_observed_model_remains_runtime_evidence(self):
        self.f.fake.write_text(self.f.fake.read_text().replace("print(json.dumps({'type':'result','subtype':'success'", "print(json.dumps({'type':'system','subtype':'init','model':'actual-model'}))\n print(json.dumps({'type':'result','subtype':'success'"))
        result = self.execute(self.config())
        _, _, folder = self.context(result.parent)
        process = json.loads((folder / 'process.json').read_text())
        self.assertEqual(process['actual_model'], 'actual-model')
        self.assertEqual(process['execution_profile']['models']['main']['model'], 'requested-model')

    def test_prepared_batch_ignores_changed_or_unreadable_current_config(self):
        config_path = self.f.root / 'runtime.json'
        config_path.write_bytes(runtime.canonical_bytes(self.config()))
        run = self.prepare(config_path)
        request, raw, folder = self.context(run)
        original = {name: (folder / name).read_bytes() for name in ('prompt.txt','input.json','targets.json')}
        config_path.write_text('invalid current JSON')
        result = self.execute(config_path)
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'], 'completed')
        args = json.loads(self.args_path.read_text())
        self.assertEqual(args[args.index('--model'):args.index('--model')+4], ['--model','requested-model','--effort','high'])
        self.assertEqual(original, {name: (folder / name).read_bytes() for name in original})
        self.assertEqual((run / 'request.json').read_bytes(), raw)

    def test_legacy_prepared_batch_stays_legacy_and_does_not_rewrite(self):
        run = self.prepare()
        _, _, folder = self.context(run)
        plan = run / 'framework-snapshot' / runtime.PLAN_FILENAME
        plan.unlink()
        manifest = run / 'framework-snapshot/manifest.json'
        snapshot = json.loads(manifest.read_text()); snapshot.pop('execution_plan')
        manifest.chmod(0o644); manifest.write_bytes(runner.encode(snapshot))
        originals = {p: p.read_bytes() for p in (manifest, folder/'prompt.txt', folder/'input.json', run/'request.json')}
        result = self.execute(self.f.root / 'does-not-exist.json')
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'], 'completed')
        self.assertFalse(plan.exists())
        self.assertEqual(originals, {p: p.read_bytes() for p in originals})
        args = json.loads(self.args_path.read_text())
        self.assertNotIn('--model', args)
        process = json.loads((folder / 'process.json').read_text())
        self.assertIsNone(process['execution_plan_sha256'])

    def test_missing_or_tampered_plan_rejected_before_claim(self):
        for mode in ('missing', 'changed'):
            with self.subTest(mode=mode):
                run = self.prepare()
                request, raw, folder = self.context(run)
                plan = run / 'framework-snapshot' / runtime.PLAN_FILENAME
                original = plan.read_bytes()
                if mode == 'missing': plan.unlink()
                else:
                    plan.chmod(0o644); plan.write_bytes(original + b' ')
                with self.assertRaises(ValueError):
                    runner.run_provider(run, request, raw, request['tasks'][0], 'claude',
                                        str(self.f.fake), self.f.methods, 10, threading.Event())
                self.assertFalse((folder / 'launched.json').exists())
                plan.write_bytes(original)

    def test_unknown_harness_or_missing_active_producer_rejected_before_prepare(self):
        for mode in ('unknown', 'missing'):
            config = self.config()
            if mode == 'unknown': config['profiles'][0]['harness'] = 'not-registered'
            else: config['active'].pop('codex')
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.prepare(config)
            self.assertFalse((self.f.methods / 'output/runs/investment').exists())

    def test_unsupported_cli_option_rejected_before_claim(self):
        self.f.fake.write_text(fixtures.FAKE_CLI)
        run = self.prepare(self.config())
        request, raw, folder = self.context(run)
        with self.assertRaisesRegex(ValueError, 'lacks'):
            runner.run_provider(run, request, raw, request['tasks'][0], 'claude',
                                str(self.f.fake), self.f.methods, 10, threading.Event())
        self.assertFalse((folder / 'launched.json').exists())
        self.assertFalse(self.f.capture.exists())

    def test_retry_keeps_first_profile_despite_current_config_changes(self):
        os.environ['MOCK_MODE'] = 'nonzero'
        result = self.execute(self.config())
        request, raw, folder = self.context(result.parent)
        os.environ['MOCK_MODE'] = 'success'
        self.prepare(self.config(model='new-model', child='new-child'))
        entry = runner.run_provider(result.parent, request, raw, request['tasks'][0], 'claude',
                                    str(self.f.fake), self.f.methods, 10, threading.Event(), attempt=2)
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        self.assertEqual(self.child_path.read_text(), 'requested-child')
        process = json.loads((folder/'retry-1/process.json').read_text())
        self.assertEqual(process['execution_profile'], json.loads((folder/'process.json').read_text())['execution_profile'])

    def test_retry_rejects_self_consistent_rewritten_plan_before_claim(self):
        os.environ['MOCK_MODE'] = 'nonzero'
        result = self.execute(self.config())
        request, raw, folder = self.context(result.parent)
        self.change_plan(result.parent)
        with self.assertRaisesRegex(ValueError, 'differs from the first attempt'):
            runner.run_provider(result.parent, request, raw, request['tasks'][0], 'claude',
                                str(self.f.fake), self.f.methods, 10, threading.Event(), attempt=2)
        self.assertFalse((folder/'retry-1/launched.json').exists())

    def test_preflight_to_launch_profile_drift_does_not_start_cli(self):
        run = self.prepare(self.config())
        request, raw, folder = self.context(run)
        original = runner.preflight_profile
        def mutate(*args, **kwargs):
            original(*args, **kwargs)
            self.change_plan(run)
        with patch.object(runner, 'preflight_profile', side_effect=mutate):
            entry = runner.run_provider(run, request, raw, request['tasks'][0], 'claude',
                                        str(self.f.fake), self.f.methods, 10, threading.Event())
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('changed before launch', entry['reason'])
        self.assertFalse(self.f.capture.exists())
        self.assertIsNone(json.loads((folder/'process.json').read_text())['pid'])

    def test_profile_drift_during_execution_blocks_publication(self):
        run = self.prepare(self.config())
        request, raw, folder = self.context(run)
        original = runner.provider_receipt
        def mutate(*args, **kwargs):
            receipt = original(*args, **kwargs)
            self.change_plan(run)
            return receipt
        with patch.object(runner, 'provider_receipt', side_effect=mutate):
            entry = runner.run_provider(run, request, raw, request['tasks'][0], 'claude',
                                        str(self.f.fake), self.f.methods, 10, threading.Event())
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('profile changed during research', entry['reason'])
        targets = json.loads((folder/'targets.json').read_text())
        self.assertTrue(all(not (self.f.methods/path).exists() for path in targets.values()))

    def test_registered_adapter_routes_without_runner_branch(self):
        class Alternative(harness.ClaudeCodeCLIAdapter):
            harness_id = 'test-alternative-claude'
            executable = 'alternative-claude'
        config = self.config()
        next(p for p in config['profiles'] if p['producer']=='claude')['harness'] = Alternative.harness_id
        with patch.dict(harness._ADAPTERS):
            harness.register_adapter(Alternative())
            with patch.object(runner.shutil, 'which', return_value=str(self.f.fake)) as lookup:
                result = runner.run_batch(self.f.request_path, self.f.methods, generator='claude', timeout=10, runtime_config=config)
            lookup.assert_any_call('alternative-claude')
            self.assertEqual(json.loads(result.read_text())['results'][0]['status'], 'completed')
            _, _, folder = self.context(result.parent)
            self.assertEqual(json.loads((folder/'process.json').read_text())['execution_profile']['harness'], Alternative.harness_id)


if __name__ == '__main__':
    unittest.main()
