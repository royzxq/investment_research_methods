"""Trial isolation contracts; fake CLIs only, no provider requests."""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_harness_trial as trial


class HarnessTrialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.arm = self.root / 'arm'
        self.workspace = self.arm / 'workspace'
        self.workspace.mkdir(parents=True)
        self.private_probe = self.root / 'private-home-fixture'
        self.private_probe.write_text('fixture only; never printed by the probe')
        home_probe = patch.object(trial, '_home_private_probe', return_value=self.private_probe)
        home_probe.start()
        self.addCleanup(home_probe.stop)
        installed = self.root / 'installed-pdf-libs'
        for name in ('pymupdf', 'fitz'):
            (installed / name).mkdir(parents=True)
            (installed / name / '__init__.py').write_text('VERSION="fixture"\n')
        pdf_source = patch.object(trial, 'PYTHON_LIBS_SOURCE', installed)
        pdf_source.start()
        self.addCleanup(pdf_source.stop)
        self.cli = self.root / 'fake-cli'
        self.sandbox = self.root / 'fake-sandbox'
        self.sandbox.write_text('#!' + sys.executable + '\nimport os,sys\nos.execv(sys.argv[3],sys.argv[3:])\n')
        self.sandbox.chmod(0o700)
        self.write_cli([{'type': 'result', 'subtype': 'success', 'is_error': False}])

    def write_cli(self, events, code=0, prefix=''):
        self.cli.write_text('#!' + sys.executable + '\n' +
            'import json,os,pathlib,sys,time,signal,subprocess\n' + prefix +
            'p=pathlib.Path.cwd()\n' +
            '(p/"stdin.bin").write_bytes(sys.stdin.buffer.read())\n' +
            '(p/"argv.json").write_text(json.dumps(sys.argv[1:]))\n' +
            '(p/"environment.json").write_text(json.dumps(dict(os.environ)))\n' +
            'for event in ' + repr(events) + ': print(json.dumps(event),flush=True)\n' +
            'sys.stderr.write("fake diagnostics\\n")\n' +
            'sys.exit(' + repr(code) + ')\n')
        self.cli.chmod(0o700)

    def run_fake(self, harness='cc', **kwargs):
        with patch.object(trial, 'SANDBOX_EXEC', str(self.sandbox)), \
                patch.object(trial, 'verify_isolation', return_value={'success': True}):
            return trial.run_trial(harness, self.workspace, self.arm, b'\xe4\xb8\xad\n\n',
                                   'http://127.0.0.1:54321/' + harness,
                                   claude_cli=self.cli, dsh_cli=self.cli, **kwargs)

    def test_cc_argv_and_stdin_are_exact_without_dangerous_bypass(self):
        result = self.run_fake()
        self.assertTrue(result['success'])
        self.assertFalse(result['consensus_eligible'])
        self.assertFalse(result['production'])
        self.assertEqual((self.workspace / 'stdin.bin').read_bytes(), b'\xe4\xb8\xad\n\n')
        args = json.loads((self.workspace / 'argv.json').read_text())
        self.assertNotIn('--bare', args)
        self.assertEqual(args[args.index('--setting-sources') + 1], 'project')
        self.assertEqual(args[args.index('--tools') + 1], 'default')
        self.assertEqual(args[args.index('--model') + 1], 'deepseek-flash[1m]')
        self.assertEqual(args[args.index('--effort') + 1], 'high')
        self.assertEqual(args[args.index('--permission-mode') + 1], 'auto')
        self.assertEqual(args[args.index('--permission-prompts') + 1], 'none')
        self.assertEqual(json.loads(args[args.index('--mcp-config') + 1]), {'mcpServers': {}})
        self.assertNotIn('--dangerously-skip-permissions', args)
        self.assertEqual((self.arm / 'stderr.log').read_text(), 'fake diagnostics\n')
        self.assertEqual((self.arm / 'events.jsonl').stat().st_mode & 0o777, 0o600)

    def test_dsh_argv_and_all_frozen_settings(self):
        self.write_cli([{'type': 'status', 'phase': 'turn_end', 'reason': 'completed'},
                        {'type': 'final', 'text': 'done'}])
        result = self.run_fake('dsh')
        self.assertTrue(result['success'])
        args = json.loads((self.workspace / 'argv.json').read_text())
        self.assertEqual(args, ['--profile', 'headless', '--patch',
                               str(self.arm / 'dsh-isolation.patch.yml'), '--json', '-'])
        rows = {row['id']: row['config'] for row in json.loads((self.arm / 'dsh-isolation.patch.yml').read_text())}
        self.assertEqual(rows['llm-deepseek']['maxTokens'], 16384)
        self.assertEqual(rows['llm-deepseek']['baseURL'], 'http://127.0.0.1:54321/dsh')
        self.assertEqual(rows['web-search-deepseek']['baseURL'], 'http://127.0.0.1:54321/dsh/v1')
        self.assertEqual(rows['web-search-deepseek']['model'], 'deepseek-flash')
        self.assertEqual(rows['web-search-deepseek']['maxTokens'], 4096)
        self.assertEqual(rows['session-persistence-jsonl']['compression'], 'none')
        self.assertEqual(rows['session-persistence-jsonl']['root'], str(self.arm / 'dsh-sessions'))
        self.assertEqual(rows['subagent']['maxActiveSubagents'], 2)
        self.assertEqual(rows['tool-subagent']['provider'], 'spawn')
        self.assertEqual(rows['tool-subagent']['toolName'], 'subagent')
        self.assertEqual(rows['tool-subagent']['agentOptions']['reasoningEffort'], 'high')
        self.assertEqual(rows['approval']['policy'], 'never')
        self.assertEqual(rows['permission'], {'presets': {
            'trial': {'sandbox': 'danger-full-access', 'approval': 'never'}}, 'defaultPreset': 'trial'})
        self.assertEqual(rows['sandbox-policy']['mode'], 'danger-full-access')
        self.assertEqual(result['outer_sandbox'], 'seatbelt')
        self.assertEqual(result['dsh_inner_sandbox'], 'disabled-outer-seatbelt-enforced')

    def test_environment_drops_secrets_and_global_overrides(self):
        inherited = {'PATH': '/bin', 'LANG': 'C.UTF-8', 'DEEPSEEK_API_KEY': 'REAL_SECRET',
                     'ANTHROPIC_API_KEY': 'REAL_SECRET', 'ANTHROPIC_AUTH_TOKEN': 'REAL_SECRET',
                     'TUSHARE_TOKEN': 'REAL_SECRET', 'FEISHU_APP_SECRET': 'REAL_SECRET',
                     'HTTP_PROXY': 'http://secret-proxy', 'NODE_OPTIONS': '--require evil',
                     'DSH_TOOLS_MODE': 'ptc', 'HOME': '/unsafe', 'CLAUDE_CONFIG_DIR': '/unsafe'}
        env = trial.trial_environment(self.arm, 'http://127.0.0.1:12345/cc',
                                      harness='cc', inherited=inherited)
        self.assertNotIn('REAL_SECRET', json.dumps(env))
        for name in ('TUSHARE_TOKEN', 'FEISHU_APP_SECRET', 'ANTHROPIC_AUTH_TOKEN', 'HTTP_PROXY',
                     'NODE_OPTIONS', 'DSH_TOOLS_MODE'):
            self.assertNotIn(name, env)
        self.assertEqual(env['HOME'], str(self.arm / 'home'))
        self.assertEqual(env['CLAUDE_CODE_SUBAGENT_MODEL'], 'deepseek-flash')
        self.assertEqual(env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'], '16384')
        self.assertEqual(env['DEEPSEEK_API_KEY'], trial.DUMMY_KEY)
        self.assertEqual(env['ANTHROPIC_API_KEY'], trial.DUMMY_KEY)
        self.assertEqual(env['NARB_DISABLE_NATIVE_CACHE'], '1')
        self.assertEqual(env['CLAUDE_CODE_TMPDIR'], str(self.arm / 'tmp'))
        self.assertTrue(str(Path(env['CLAUDE_CODE_TMPDIR'])).startswith(str(self.arm)))
        for family in ('HAIKU', 'SONNET', 'OPUS', 'FABLE'):
            self.assertEqual(env['ANTHROPIC_DEFAULT_' + family + '_MODEL'], 'deepseek-flash')
        self.assertIn('/usr/local/bin', env['PATH'].split(os.pathsep))
        self.assertEqual(env['PYTHONPATH'], str(self.arm / 'python-libs'))
        self.assertEqual(env['PYTHONDONTWRITEBYTECODE'], '1')
        self.assertEqual(env['PATH'].split(os.pathsep)[0], str(self.arm / 'runtime-bin'))
        self.assertEqual(env['API_TIMEOUT_MS'], '120000')
        self.assertEqual(env['TMPPREFIX'], str(self.arm / 'tmp' / 'zsh'))

    def test_model_process_receives_isolated_environment(self):
        with patch.dict(os.environ, {'TUSHARE_TOKEN': 'SHOULD_NEVER_APPEAR',
                                      'DEEPSEEK_API_KEY': 'SHOULD_NEVER_APPEAR'}):
            self.run_fake()
        observed = json.loads((self.workspace / 'environment.json').read_text())
        self.assertNotIn('SHOULD_NEVER_APPEAR', json.dumps(observed))
        for name, folder in [('HOME', 'home'), ('TMPDIR', 'tmp'), ('DSH_HOME', 'dsh-home'),
                             ('DSH_AGENTS_HOME', 'agents-home'), ('CLAUDE_CONFIG_DIR', 'claude-config')]:
            self.assertEqual(observed[name], str(self.arm / folder))

    def test_proxy_is_loopback_exact_endpoint_only(self):
        samples = ['https://api.deepseek.com/anthropic', 'http://localhost:1234/dsh',
                   'http://127.0.0.1/dsh', 'http://user:pass@127.0.0.1:1234/dsh',
                   'http://127.0.0.1:1234/dsh?secret=x', 'http://127.0.0.1:1234/../cc',
                   'http://127.0.0.1:99999/dsh', 'http://127.0.0.1:1234/dsh#secret']
        for value in samples:
            with self.subTest(value=value), self.assertRaises(ValueError):
                trial.sandbox_profile(self.arm, value)

    def test_sandbox_policy_denies_writes_protected_reads_and_offline_network(self):
        policy = trial.sandbox_profile(self.arm, 'http://127.0.0.1:45678/dsh', online=False)
        self.assertIn('(deny file-write*)', policy)
        self.assertIn('(deny file-write* (subpath ' + json.dumps(str(self.arm / 'python-libs')), policy)
        for ancestor in self.arm.parents:
            self.assertIn('(literal ' + json.dumps(str(ancestor)) + ')', policy)
        self.assertNotIn('(subpath ' + json.dumps(str(self.root)) + '))\n', policy.split('(allow file-read-data ')[-1])
        self.assertIn('(allow file-read-data (subpath ' + json.dumps(str(self.arm)) + ')', policy)
        self.assertIn('(subpath ' + json.dumps(str(ROOT)) + ')', policy)
        self.assertIn('(deny file-read-data (subpath "/Users/xinquanzhou")', policy)
        self.assertNotIn('(deny file-read*', policy)
        self.assertNotIn('(subpath "/Users/xinquanzhou/.local")', policy)
        self.assertNotIn('(subpath "/Users/xinquanzhou/.nvm")', policy)
        self.assertIn('(deny network-outbound)', policy)
        self.assertIn('(remote ip "localhost:45678")', policy)
        self.assertNotIn('(remote ip "127.0.0.1:', policy)
        self.assertNotIn('(deny network-outbound)', trial.sandbox_profile(
            self.arm, 'http://127.0.0.1:45678/dsh', online=True))

    def test_policy_paths_are_data_with_quotes_and_newlines(self):
        folder = self.root / 'arm"\n(custom)'
        folder.mkdir()
        policy = trial.sandbox_profile(folder, 'http://127.0.0.1:1234/dsh')
        self.assertIn(json.dumps(str(folder)), policy)
        self.assertNotIn('arm"\n(custom)', policy)

    def test_isolation_failure_records_failure_and_never_launches_cli(self):
        with patch.object(trial, 'verify_isolation', return_value={'success': False}), \
                patch.object(trial.subprocess, 'Popen') as launch:
            result = trial.run_trial('cc', self.workspace, self.arm, 'test',
                                     'http://127.0.0.1:1234/cc', claude_cli=self.cli)
        launch.assert_not_called()
        self.assertEqual(result['error'], 'isolation_preflight_failed')
        self.assertFalse(json.loads((self.arm / 'process.json').read_text())['success'])

    def test_preflight_requires_every_negative_check_and_not_enoent(self):
        expected = {'inside_write': True, 'outside_write_denied': True,
                    'project_read_denied': True, 'other_arm_read_denied': True,
                    'private_home_read_denied': True, 'runtime_library_write_denied': True,
                    'runtime_executable_write_denied': True}
        def runner(args, **kwargs):
            self.assertNotIn('REAL_SECRET', json.dumps(kwargs))
            self.assertTrue(Path(args[-5]).exists())  # existing other-arm canary
            self.assertTrue(Path(args[-4]).is_file())  # metadata-only home probe
            return subprocess.CompletedProcess(args, 0, json.dumps(expected).encode(), b'')
        result = trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc', runner=runner)
        self.assertTrue(result['success'])
        expected['project_read_denied'] = False
        self.assertFalse(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc', runner=runner)['success'])
        expected['project_read_denied'] = True
        expected['private_home_read_denied'] = False
        self.assertFalse(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc', runner=runner)['success'])
        self.assertFalse(list(self.root.glob('.sandbox-*')))

    def test_preflight_refuses_if_no_existing_private_home_probe_is_available(self):
        with patch.object(trial, '_home_private_probe', return_value=None), \
                patch.object(trial.subprocess, 'run') as runner:
            result = trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc')
        runner.assert_not_called()
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'no_existing_private_home_probe')

    def test_offline_preflight_requires_proxy_and_other_port_denial(self):
        facts = {'inside_write': True, 'outside_write_denied': True, 'project_read_denied': True,
                 'other_arm_read_denied': True, 'private_home_read_denied': True,
                 'proxy_connect': True, 'other_network_denied': True,
                 'runtime_library_write_denied': True, 'runtime_executable_write_denied': True}
        def runner(args, **kwargs):
            self.assertGreater(int(args[-1]), 0)
            return subprocess.CompletedProcess(args, 0, json.dumps(facts), '')
        with patch.object(trial.socket, 'socket') as socket_factory:
            socket_factory.return_value.getsockname.return_value = ('127.0.0.1', 56789)
            self.assertTrue(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc',
                                                  online=False, runner=runner)['success'])
            facts['proxy_connect'] = False
            self.assertFalse(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc',
                                                   online=False, runner=runner)['success'])

    def test_preflight_unavailable_or_malformed_fails_closed(self):
        for result in (subprocess.CompletedProcess([], 1, b'', b'sandbox unavailable'),
                       subprocess.CompletedProcess([], 0, b'not JSON', b'')):
            with self.subTest(result=result):
                self.assertFalse(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc',
                    runner=lambda *args, **kwargs: result)['success'])
        def unavailable(*args, **kwargs):
            raise OSError('sandbox unavailable')
        self.assertFalse(trial.verify_isolation(self.arm, 'http://127.0.0.1:1234/cc',
                                                runner=unavailable)['success'])

    def test_success_requires_exit_zero_and_valid_terminal(self):
        cases = [('cc', [{'type': 'result', 'subtype': 'success', 'is_error': True}], 0),
                 ('cc', [{'type': 'result', 'subtype': 'success', 'is_error': False}], 1),
                 ('cc', [{'type': 'assistant'}], 0),
                 ('dsh', [{'type': 'final', 'text': 'done'}], 0),
                 ('dsh', [{'type': 'status', 'phase': 'turn_end', 'reason': 'error'},
                          {'type': 'final'}], 0),
                 ('dsh', [{'type': 'final'}, {'type': 'status', 'phase': 'turn_end',
                                             'reason': 'completed'}], 0),
                 ('dsh', [{'type': 'error'}, {'type': 'status', 'phase': 'turn_end',
                          'reason': 'completed'}, {'type': 'final'}], 0),
                 ('cc', [{'type': 'result', 'subtype': 'success', 'is_error': False},
                         {'type': 'assistant'}], 0)]
        for index, (harness, events, code) in enumerate(cases):
            with self.subTest(harness=harness, code=code):
                self.arm = self.root / ('arm-' + str(index))
                self.workspace = self.arm / 'workspace'
                self.workspace.mkdir(parents=True)
                self.write_cli(events, code)
                self.assertFalse(self.run_fake(harness)['success'])

    def test_truncated_events_are_recorded_separately(self):
        self.write_cli([{'type': 'text', 'truncated': True},
                        {'type': 'result', 'subtype': 'success', 'is_error': False}])
        result = self.run_fake()
        self.assertTrue(result['success'])
        self.assertEqual(result['truncated_events'], 1)

    def test_dsh_current_turn_end_reason_object_trace(self):
        # Projected shape actually emitted by DSH rc.2 in smoke-03; no model
        # thinking or report contents are copied into this regression fixture.
        events = self.arm / 'events.jsonl'
        trace = [
            {'type': 'session', 'sessionId': 'isolated-smoke-fixture'},
            {'type': 'status', 'phase': 'turn_start', 'turn': 1},
            {'type': 'status', 'phase': 'step_end', 'turn': 1, 'step': 1,
             'usage': {'inputTokens': 200, 'outputTokens': 20}},
            {'type': 'status', 'phase': 'turn_end', 'turn': 1, 'reason': {'kind': 'completed'}},
            {'type': 'final', 'text': 'fixture complete'},
        ]
        events.write_text(''.join(json.dumps(value) + '\n' for value in trace))
        result = trial.summarize_events(events, 'dsh')
        self.assertTrue(result['terminal_success'])
        self.assertEqual(result['last_turn_reason'], {'kind': 'completed'})
        for kind in ('failed', 'error', 'aborted', 'unknown', None):
            with self.subTest(kind=kind):
                trace[-2]['reason'] = {'kind': kind}
                events.write_text(''.join(json.dumps(value) + '\n' for value in trace))
                self.assertFalse(trial.summarize_events(events, 'dsh')['terminal_success'])
        for reason in ({}, {'completed': True}, None, 1):
            with self.subTest(reason=reason):
                trace[-2]['reason'] = reason
                events.write_text(''.join(json.dumps(value) + '\n' for value in trace))
                self.assertFalse(trial.summarize_events(events, 'dsh')['terminal_success'])

    def test_malformed_event_cannot_pass_success(self):
        self.write_cli([42, {'type': 'result', 'subtype': 'success', 'is_error': False}])
        result = self.run_fake()
        self.assertFalse(result['success'])
        self.assertEqual(result['invalid_event_lines'], 1)

    def test_dsh_new_or_mismatched_turn_cannot_reuse_completed_reason(self):
        start=lambda n:dict(type='status',phase='turn_start',turn=n)
        end=lambda n:dict(type='status',phase='turn_end',turn=n,reason={'kind':'completed'})
        final={'type':'final'}
        traces=[
            [start(1),end(1),start(2),final],
            [end(1),start(2),final],
            [start(1),end(1),final,start(2),final],
            [start(2),end(1),final],
            [start(1),end(1),end(1),final],
            [start(1),start(2),end(2),final],
        ]
        path=self.arm/'events.jsonl'
        for trace in traces:
            with self.subTest(trace=trace):
                path.write_text(''.join(json.dumps(e)+'\n' for e in trace))
                self.assertFalse(trial.summarize_events(path,'dsh')['terminal_success'])

    def test_dsh_genuine_recovery_and_legacy_terminal_remain_completed(self):
        traces=[[
            dict(type='status',phase='turn_start',turn=1),
            dict(type='status',phase='turn_end',turn=1,reason={'kind':'max-tokens'}),
            dict(type='status',phase='turn_start',turn=2),
            dict(type='status',phase='turn_end',turn=2,reason={'kind':'completed'}),
            dict(type='final')],
            [dict(type='status',phase='turn_end',reason='completed'),dict(type='final')]]
        path=self.arm/'events.jsonl'
        for trace in traces:
            with self.subTest(trace=trace):
                path.write_text(''.join(json.dumps(e)+'\n' for e in trace))
                result=trial.summarize_events(path,'dsh')
                self.assertTrue(result['terminal_success'])
                self.assertFalse(result['unended_turn']);self.assertTrue(result['turn_sequence_valid'])

    def test_exit_zero_cannot_hide_dsh_unended_second_turn(self):
        self.write_cli([
            dict(type='status',phase='turn_start',turn=1),
            dict(type='status',phase='turn_end',turn=1,reason={'kind':'completed'}),
            dict(type='status',phase='turn_start',turn=2),dict(type='final')])
        result=self.run_fake('dsh')
        self.assertEqual(result['exit_code'],0)
        self.assertTrue(result['unended_turn'])
        self.assertFalse(result['terminal_success']);self.assertFalse(result['success'])

    def test_runtime_pdf_dependencies_are_private_copies_with_frozen_hashes(self):
        result = self.run_fake()
        self.assertTrue(result['runtime_dependencies_intact'])
        manifest = json.loads((self.arm / 'runtime-deps.json').read_text())
        self.assertEqual(manifest['packages'], ['pymupdf', 'fitz'])
        self.assertEqual(set(manifest['files']), {'pymupdf/__init__.py', 'fitz/__init__.py'})
        self.assertEqual(set(manifest['executables']), {'python', 'python3', 'pdfinfo', 'pdftoppm', 'pdftotext'})
        target = self.arm / 'python-libs/pymupdf/__init__.py'
        self.assertFalse(target.is_symlink())
        target.chmod(0o600)
        target.write_text('changed')
        self.assertFalse(trial.runtime_libraries_intact(self.arm, manifest))

    def test_added_runtime_file_and_executable_cannot_pass_integrity(self):
        manifest = trial.freeze_python_libraries(self.arm)
        for folder in ('python-libs', 'runtime-bin'):
            with self.subTest(folder=folder):
                extra = self.arm / folder / 'unexpected-executable'
                extra.write_text('print("changed runtime")')
                extra.chmod(0o700)
                self.assertFalse(trial.runtime_libraries_intact(self.arm, manifest))
                extra.unlink()
                self.assertTrue(trial.runtime_libraries_intact(self.arm, manifest))

    def test_private_python_wrapper_disables_bytecode_even_with_isolated_flag(self):
        manifest = trial.freeze_python_libraries(self.arm)
        code = ('import sys,json;sys.path.insert(0,' + repr(str(self.arm / 'python-libs')) + ');'
                'import pymupdf;print(json.dumps({"dont_write_bytecode":sys.dont_write_bytecode}))')
        result = subprocess.run([str(self.arm / 'runtime-bin/python3'), '-I', '-c', code],
                                capture_output=True, check=True, text=True)
        self.assertEqual(json.loads(result.stdout), {'dont_write_bytecode': True})
        self.assertFalse(list((self.arm / 'python-libs').rglob('*.pyc')))
        self.assertTrue(trial.runtime_libraries_intact(self.arm, manifest))

    def test_pdf_bridge_rejects_unimplemented_options_without_creating_output(self):
        trial.freeze_python_libraries(self.arm)
        target = self.workspace / 'should-not-exist'
        result = subprocess.run([str(self.arm / 'runtime-bin/pdftoppm'), '-unimplemented',
                                  'does-not-exist.pdf', str(target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('unsupported compatibility option', result.stderr)
        self.assertFalse(target.exists())
        for tool, options in [('pdfinfo', ['-png']), ('pdftotext', ['-scale-to', '10']),
                              ('pdftoppm', ['-png', '-jpeg'])]:
            with self.subTest(tool=tool, options=options):
                rejected = subprocess.run([str(self.arm / 'runtime-bin' / tool), *options,
                                           'does-not-exist.pdf'], capture_output=True, text=True)
                self.assertEqual(rejected.returncode, 2)
                self.assertNotIn('no such file', rejected.stderr)

    def test_shared_output_and_timeout_settings_reach_both_harnesses(self):
        cc = self.run_fake(max_output_tokens=32768, stream_idle_timeout=180)
        env = json.loads((self.workspace / 'environment.json').read_text())
        self.assertEqual(env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'], '32768')
        self.assertEqual(env['API_TIMEOUT_MS'], '180000')
        self.assertTrue(cc['main_child_output_limit_shared'])
        run = self.root / 'second-arm'
        workspace = run / 'workspace'
        workspace.mkdir(parents=True)
        rows = {row['id']: row['config'] for row in json.loads(
            trial._dsh_patch(workspace, run, 'http://127.0.0.1:1234/dsh', 32768, 180))}
        self.assertEqual(rows['llm-deepseek']['maxTokens'], 32768)
        self.assertEqual(rows['tool-subagent']['agentOptions']['maxTokens'], 32768)
        self.assertEqual(rows['llm-deepseek']['streamIdleTimeoutMs'], 180000)

    def test_dependency_symlinks_are_rejected_without_following_them(self):
        (trial.PYTHON_LIBS_SOURCE / 'pymupdf' / 'external').symlink_to(self.private_probe)
        with self.assertRaisesRegex(ValueError, 'contains a symlink'):
            trial.freeze_python_libraries(self.arm)

    def test_runtime_dependency_root_symlink_is_not_traversed(self):
        outside = self.root / 'outside-libs'
        outside.mkdir()
        (self.arm / 'python-libs').symlink_to(outside, target_is_directory=True)
        self.assertFalse(trial.runtime_libraries_intact(self.arm, {'files': {}}))

    def test_process_record_never_follows_cli_created_symlink(self):
        target = self.root / 'outside-record.json'
        target.write_text('keep original')
        record = self.arm / 'process.json'
        record.symlink_to(target)
        trial._write_json(record, {'success': False})
        self.assertEqual(target.read_text(), 'keep original')
        self.assertFalse(record.is_symlink())
        self.assertEqual(json.loads(record.read_text()), {'success': False})

    def test_event_parser_does_not_follow_model_created_symlink(self):
        target = self.root / 'outside-events.jsonl'
        target.write_text('{"type":"result","subtype":"success","is_error":false}\n')
        events = self.arm / 'events.jsonl'
        events.symlink_to(target)
        with self.assertRaises(OSError):
            trial.summarize_events(events, 'cc')

    def test_event_parser_refuses_named_pipe_without_waiting(self):
        events = self.arm / 'events.jsonl'
        os.mkfifo(events)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            trial.summarize_events(events, 'cc')

    def test_unusable_event_path_returns_failure_without_losing_process_record(self):
        with patch.object(trial, 'summarize_events', side_effect=ValueError('not a regular file')):
            result = self.run_fake()
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'ValueError')
        self.assertEqual(json.loads((self.arm / 'process.json').read_text())['error'], 'ValueError')

    def test_timeout_stops_leader_and_records_result(self):
        # The leader may receive TERM during Python startup, before installing
        # its handler. The group escalation contract is pinned separately.
        self.write_cli([], prefix='signal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(30)\n')
        result = self.run_fake(timeout=0.05)
        self.assertTrue(result['timed_out'])
        self.assertFalse(result['success'])
        self.assertIn(result['exit_code'], (-signal.SIGTERM, -signal.SIGKILL))
        self.assertTrue((self.arm / 'process.json').exists())

    def test_cancel_event_stops_group_and_live_pid_is_visible(self):
        self.write_cli([], prefix='time.sleep(30)\n')
        cancelled = threading.Event()
        observed = {}
        def run():
            try:
                observed['result'] = self.run_fake(cancelled=cancelled, timeout=30)
            except BaseException as exc:
                observed['error'] = exc
        with patch.object(trial, '_kill_group', wraps=trial._kill_group) as cleanup:
            thread = threading.Thread(target=run)
            thread.start()
            try:
                deadline = time.monotonic() + 10
                live = {}
                while time.monotonic() < deadline:
                    record = self.arm / 'process.json'
                    if record.exists():
                        live = json.loads(record.read_text())
                        if live.get('pid'):
                            break
                    time.sleep(0.02)
                self.assertGreater(live.get('pid', 0), 0)
                self.assertIsNone(live['exit_code'])
                self.assertTrue(live['isolation']['success'])
                cancelled.set()
            finally:
                cancelled.set()
                thread.join(timeout=8)
            self.assertFalse(thread.is_alive())
            self.assertNotIn('error', observed)
            result = observed['result']
            self.assertTrue(result['cancelled'])
            self.assertFalse(result['timed_out'])
            self.assertFalse(result['success'])
            self.assertEqual(cleanup.call_args.args[0].pid, live['pid'])

    def test_preexisting_cancel_event_refuses_model_launch(self):
        cancelled = threading.Event()
        cancelled.set()
        with patch.object(trial.subprocess, 'Popen') as launch:
            result = self.run_fake(cancelled=cancelled)
        launch.assert_not_called()
        self.assertTrue(result['cancelled'])
        self.assertFalse(result['success'])

    def test_communicate_poll_sends_prompt_only_once(self):
        self.write_cli([{'type': 'result', 'subtype': 'success', 'is_error': False}],
                       prefix='time.sleep(.4)\n')
        observed = []
        original = subprocess.Popen.communicate
        def communicate(process, *args, **kwargs):
            observed.append((kwargs.get('input'), kwargs.get('timeout')))
            return original(process, *args, **kwargs)
        with patch.object(trial.subprocess.Popen, 'communicate', communicate):
            result = self.run_fake(timeout=10)
        self.assertTrue(result['success'])
        self.assertGreater(len(observed), 1)
        self.assertEqual(observed[0][0], b'\xe4\xb8\xad\n\n')
        self.assertTrue(all(value is None for value, timeout in observed[1:]))
        self.assertTrue(all(timeout <= .25 for value, timeout in observed))
        self.assertEqual((self.workspace / 'stdin.bin').read_bytes(), b'\xe4\xb8\xad\n\n')

    def test_cleanup_signals_group_and_reaps(self):
        class Process:
            pid = 345678
            calls = 0
            def wait(self, timeout):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired('fake', timeout)
                return -signal.SIGKILL
        process = Process()
        with patch.object(trial.os, 'killpg') as kill:
            trial._kill_group(process, grace=0.01)
        self.assertEqual([call.args for call in kill.call_args_list],
                         [(345678, signal.SIGTERM), (345678, signal.SIGKILL)])
        self.assertEqual(process.calls, 2)

    def test_existing_outputs_and_workspace_outside_arm_are_rejected(self):
        (self.arm / 'events.jsonl').write_text('existing research')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.run_fake()
        self.assertEqual((self.arm / 'events.jsonl').read_text(), 'existing research')
        with self.assertRaisesRegex(ValueError, 'inside'):
            trial.run_trial('cc', self.root, self.arm, 'prompt', 'http://127.0.0.1:1234/cc')

    def test_project_settings_hooks_and_plugins_are_rejected_before_launch(self):
        for name in ('.claude/settings.json', '.claude/settings.local.json',
                     '.claude/hooks', '.claude/plugins'):
            with self.subTest(name=name):
                forbidden = self.workspace / name
                forbidden.parent.mkdir(exist_ok=True)
                forbidden.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'exclude project settings'):
                    self.run_fake()
                forbidden.unlink()

    def test_symlink_workspace_rejected_but_cli_symlink_allowed(self):
        alias = self.arm / 'alias'
        alias.symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            trial.run_trial('cc', alias, self.arm, 'prompt', 'http://127.0.0.1:1234/cc')
        link = self.root / 'cli-alias'
        link.symlink_to(self.cli)
        self.cli = link
        self.assertTrue(self.run_fake()['success'])

    def test_invalid_harness_prompt_and_bounds_rejected(self):
        samples = [dict(harness='codex'), dict(prompt='  '), dict(prompt={}), dict(timeout=0),
                   dict(timeout=float('inf')), dict(timeout=True), dict(max_output_tokens=False)]
        samples.append(dict(online='false'))
        samples.append(dict(cancelled=True))
        samples.extend(dict(stream_idle_timeout=value) for value in (0, False, float('nan'), float('inf')))
        for extra in samples:
            args = dict(harness='cc', workspace=self.workspace, run_dir=self.arm, prompt='prompt',
                        proxy_url='http://127.0.0.1:1234/cc', claude_cli=self.cli)
            args.update(extra)
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                trial.run_trial(**args)


if __name__ == '__main__':
    unittest.main()
