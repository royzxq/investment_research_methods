"""CLI adapter contracts verified locally without provider API calls."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_harness as harness
from scripts.research_exchange import _strict_json


def profile(producer, *, model=None, effort=None, subagent=None):
    return dict(profile_id=producer + '-default', revision=1,
                producer=producer, harness=harness.default_harness(producer),
                models=dict(main=dict(model=model, effort=effort),
                            subagent=dict(model=subagent)))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_new(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)


class ResearchHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'execution'
        self.folder.mkdir()
        self.schema_text = '{"type": "object", "description": "保留原始文本"}\n'
        (self.folder / 'receipt-schema.json').write_text(self.schema_text)
        self.cli = self.root / 'local-cli'
        self.cli.write_text('#!/bin/sh\nexit 0\n')
        self.cli.chmod(0o700)
        self.servers = {
            'first': {'command': '/local/one', 'args': ['--config', '一']},
            'second': {'command': '/local/two', 'args': []},
        }
        self.codex = harness.get_adapter('codex-cli')
        self.claude = harness.get_adapter('claude-code-cli')

    def context(self, producer, *, instruction='frozen delivery instruction', servers=None):
        return harness.LaunchContext(self.folder, self.root, producer,
                                     self.servers if servers is None else servers,
                                     instruction)

    def events(self, values):
        raw = b'\n'.join(value if isinstance(value, bytes) else json.dumps(value).encode()
                         for value in values)
        (self.folder / 'events.jsonl').write_bytes(raw + b'\n')

    def test_default_codex_argv_preserves_original_order_and_mcp_encoding(self):
        actual = self.codex.command(str(self.cli), self.context('codex'), profile('codex'))
        expected = [str(self.cli),
                    '-c', 'mcp_servers.second.command="/local/two"',
                    '-c', 'mcp_servers.second.args=[]',
                    '-c', 'mcp_servers.first.command="/local/one"',
                    '-c', 'mcp_servers.first.args=' + json.dumps(['--config', '一']),
                    '--no-daemon', 'exec', '--approve-for-me', '-c', 'web_search="live"',
                    '-c', 'mcp_servers.jev.enabled=false',
                    '--ephemeral', '--json', '--color', 'never', '--output-schema',
                    str(self.folder / 'receipt-schema.json'), '-o', str(self.folder / 'cli-receipt.json'),
                    '-C', str(self.root.resolve()), '-']
        self.assertEqual(actual, expected)
        self.assertIsNone(self.codex.instruction_from_command(actual))

    def test_default_claude_argv_preserves_original_schema_and_options(self):
        actual = self.claude.command(str(self.cli), self.context('claude'), profile('claude'))
        expected = [str(self.cli), '-p', '--permission-mode', 'auto', '--permission-prompts', 'none',
                    '--append-system-prompt', 'frozen delivery instruction',
                    '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
                    '--strict-mcp-config', '--mcp-config', json.dumps({'mcpServers': self.servers}),
                    '--json-schema', self.schema_text]
        self.assertEqual(actual, expected)
        self.assertEqual(self.claude.instruction_from_command(actual), 'frozen delivery instruction')

    def test_codex_explicit_model_and_effort_are_separate_argv_values(self):
        chosen = profile('codex', model='requested model', effort='high')
        actual = self.codex.command(str(self.cli), self.context('codex', servers={}), chosen)
        self.assertEqual(actual[:7], [str(self.cli), '--no-daemon', 'exec', '--model',
                                     'requested model', '-c', 'model_reasoning_effort="high"'])
        self.assertEqual(actual[7:], self.codex.command(str(self.cli), self.context('codex', servers={}),
                                                      profile('codex'))[3:])

    def test_claude_explicit_model_and_effort_are_separate_argv_values(self):
        actual = self.claude.command(str(self.cli), self.context('claude'),
                                    profile('claude', model='claude-chosen', effort='high'))
        self.assertEqual(actual[:6], [str(self.cli), '-p', '--model', 'claude-chosen', '--effort', 'high'])
        self.assertEqual(actual[6:], self.claude.command(str(self.cli), self.context('claude'),
                                                       profile('claude'))[2:])

    def test_null_model_settings_inherit_environment_without_mutation(self):
        env = {'HOME': '/local/user', 'CLAUDE_CODE_SUBAGENT_MODEL': 'inherited', 'PATH': '/bin'}
        for adapter in (self.codex, self.claude):
            with self.subTest(adapter=adapter.harness_id):
                result = adapter.environment(env, profile(adapter.producer))
                self.assertEqual(result, env)
                self.assertIsNot(result, env)
        self.assertEqual(env['CLAUDE_CODE_SUBAGENT_MODEL'], 'inherited')

    def test_claude_subagent_model_overrides_only_a_copied_environment(self):
        env = {'PATH': '/bin', 'CLAUDE_CODE_SUBAGENT_MODEL': 'inherited'}
        result = self.claude.environment(env, profile('claude', subagent='subagent-chosen'))
        self.assertEqual(result, {'PATH': '/bin', 'CLAUDE_CODE_SUBAGENT_MODEL': 'subagent-chosen'})
        self.assertEqual(env['CLAUDE_CODE_SUBAGENT_MODEL'], 'inherited')

    def test_codex_subagent_override_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'does not support a subagent model override'):
            self.codex.validate_profile(profile('codex', subagent='unsupported'))

    def test_wrong_profile_harness_and_producer_are_rejected(self):
        for key, value in (('producer', 'claude'), ('harness', 'claude-code-cli')):
            chosen = profile('codex')
            chosen[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'does not match adapter'):
                self.codex.validate_profile(chosen)

    def test_wrong_launch_context_producer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'context producer does not match adapter'):
            self.codex.command(str(self.cli), self.context('claude'), profile('codex'))

    def test_unknown_roles_and_model_fields_are_rejected(self):
        samples = []
        chosen = profile('claude')
        chosen['models']['reviewer'] = {'model': None}
        samples.append(chosen)
        chosen = profile('claude')
        chosen['models']['subagent']['effort'] = None
        samples.append(chosen)
        chosen = profile('claude')
        del chosen['models']['main']['effort']
        samples.append(chosen)
        for chosen in samples:
            with self.subTest(models=chosen['models']), self.assertRaises(ValueError):
                self.claude.validate_profile(chosen)

    def test_override_values_require_nonempty_text(self):
        for role, field in (('main', 'model'), ('main', 'effort'), ('subagent', 'model')):
            for value in ('', '  ', 1, False, [], {}):
                chosen = profile('claude')
                chosen['models'][role][field] = value
                with self.subTest(role=role, field=field, value=value), self.assertRaises(ValueError):
                    self.claude.validate_profile(chosen)

    def test_profile_and_environment_are_never_mutated(self):
        chosen = profile('claude', model='main', effort='high', subagent='worker')
        before = deepcopy(chosen)
        self.claude.command(str(self.cli), self.context('claude'), chosen)
        self.claude.environment({}, chosen)
        self.assertEqual(chosen, before)

    def test_claude_requires_delivery_instruction(self):
        for instruction in (None, ''):
            with self.subTest(instruction=instruction), self.assertRaisesRegex(ValueError, 'delivery instruction'):
                self.claude.command(str(self.cli), self.context('claude', instruction=instruction), profile('claude'))
        with self.assertRaisesRegex(ValueError, 'missing delivery instruction'):
            self.claude.instruction_from_command([str(self.cli), '-p'])

    def test_default_claude_preflight_only_checks_executable(self):
        with patch.object(harness.subprocess, 'run') as run:
            self.claude.preflight(str(self.cli), self.root, profile('claude'))
        run.assert_not_called()

    def test_preflight_rejects_missing_and_nonexecutable_files(self):
        for adapter in (self.codex, self.claude):
            for cli in (None, self.root, self.root / 'missing'):
                with self.subTest(adapter=adapter.harness_id, cli=cli), self.assertRaisesRegex(ValueError, 'executable unavailable'):
                    adapter.preflight(cli, self.root, profile(adapter.producer))
            self.cli.chmod(0o600)
            with self.subTest(adapter=adapter.harness_id), self.assertRaisesRegex(ValueError, 'executable unavailable'):
                adapter.preflight(str(self.cli), self.root, profile(adapter.producer))
            self.cli.chmod(0o700)

    def test_default_codex_preflight_invokes_compatibility_callback_once(self):
        check = Mock()
        with patch.object(harness.subprocess, 'run') as run:
            self.codex.preflight(str(self.cli), self.root, profile('codex'), codex_check=check)
        check.assert_called_once_with(str(self.cli), self.root)
        run.assert_not_called()

    def test_codex_default_capability_check_matches_original_options(self):
        outputs = ['  --no-daemon\n',
                   '  --approve-for-me\n  --ephemeral\n  --json\n  --color\n  --output-schema\n'
                   '  -o, --output-last-message\n  -C, --cd\n  -c, --config\n']
        with patch.object(harness.subprocess, 'run', side_effect=[subprocess.CompletedProcess([], 0, out, '')
                                                               for out in outputs]) as run:
            self.codex.preflight(str(self.cli), self.root, profile('codex'))
        self.assertEqual([call.args[0] for call in run.call_args_list],
                         [[str(self.cli), '--help'], [str(self.cli), 'exec', '--help']])

    def test_explicit_main_overrides_verify_declared_cli_options(self):
        for adapter, args, options in ((self.codex, ['exec', '--help'], '--model\n  --config'),
                                       (self.claude, ['--help'], '--model\n  --effort')):
            with self.subTest(adapter=adapter.harness_id):
                result = subprocess.CompletedProcess([], 0, '  ' + options + '\n', '')
                with patch.object(harness.subprocess, 'run', return_value=result) as run:
                    adapter.preflight(str(self.cli), self.root,
                                      profile(adapter.producer, model='chosen', effort='high'),
                                      codex_check=Mock())
                self.assertEqual(run.call_args.args[0], [str(self.cli), *args])

    def test_incidental_help_mentions_cannot_satisfy_requested_model_option(self):
        result = subprocess.CompletedProcess([], 0, 'Use --model to choose a model.\n  --effort\n', '')
        with patch.object(harness.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'lacks --model'):
                self.claude.preflight(str(self.cli), self.root, profile('claude', model='chosen'))

    def test_explicit_effort_requires_supported_config_or_effort_option(self):
        for adapter in (self.codex, self.claude):
            result = subprocess.CompletedProcess([], 0, '  --model\n', '')
            with self.subTest(adapter=adapter.harness_id), patch.object(harness.subprocess, 'run', return_value=result):
                with self.assertRaisesRegex(ValueError, 'lacks --config|lacks --effort'):
                    adapter.preflight(str(self.cli), self.root, profile(adapter.producer, effort='high'),
                                      codex_check=Mock())

    def test_capability_checks_reject_help_exit_failure_and_timeout(self):
        for effect in (subprocess.CompletedProcess([], 2, '', ''),
                       subprocess.TimeoutExpired('local-cli', 10), OSError('not available')):
            kwargs = {'side_effect': effect} if isinstance(effect, Exception) else {'return_value': effect}
            with self.subTest(effect=type(effect).__name__), patch.object(harness.subprocess, 'run', **kwargs):
                with self.assertRaisesRegex(ValueError, 'capability check failed'):
                    self.claude.preflight(str(self.cli), self.root, profile('claude', model='chosen'))

    def test_codex_receipt_reads_original_file_without_rewriting_it(self):
        receipt = {'status': 'completed', 'generator': 'codex'}
        path = self.folder / 'cli-receipt.json'
        path.write_bytes(encode(receipt))
        original = path.read_bytes()
        writer = Mock()
        self.assertEqual(self.codex.receipt(self.folder, _strict_json, writer, encode), receipt)
        writer.assert_not_called()
        self.assertEqual(path.read_bytes(), original)

    def test_claude_successful_final_receipt_is_saved(self):
        receipt = {'status': 'completed', 'generator': 'claude'}
        self.events([b'not-json', ['ignored'], {'type': 'result', 'subtype': 'error', 'is_error': True},
                     {'type': 'result', 'subtype': 'success', 'is_error': False, 'structured_output': receipt}])
        self.assertEqual(self.claude.receipt(self.folder, _strict_json, write_new, encode), receipt)
        self.assertEqual((self.folder / 'cli-receipt.json').read_bytes(), encode(receipt))

    def test_claude_error_result_rejected_even_with_zero_process_exit(self):
        result = subprocess.run([sys.executable, '-c',
                                 'import json; print(json.dumps({"type":"result",'
                                 '"subtype":"error_during_execution","is_error":True}))'],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        (self.folder / 'events.jsonl').write_bytes(result.stdout)
        with self.assertRaisesRegex(ValueError, 'no successful result'):
            self.claude.receipt(self.folder, _strict_json, write_new, encode)
        self.assertFalse((self.folder / 'cli-receipt.json').exists())

    def test_claude_last_result_controls_success(self):
        self.events([{'type': 'result', 'subtype': 'success', 'is_error': False, 'structured_output': {}},
                     {'type': 'result', 'subtype': 'error_during_execution', 'is_error': True}])
        with self.assertRaisesRegex(ValueError, 'no successful result'):
            self.claude.receipt(self.folder, _strict_json, write_new, encode)

    def test_claude_success_requires_explicit_false_and_a_structured_object(self):
        for final, message in (({'type': 'result', 'subtype': 'success', 'structured_output': {}}, 'no successful result'),
                               ({'type': 'result', 'subtype': 'success', 'is_error': False, 'structured_output': []},
                                'no structured research receipt')):
            self.events([final])
            with self.subTest(final=final), self.assertRaisesRegex(ValueError, message):
                self.claude.receipt(self.folder, _strict_json, write_new, encode)

    def test_codex_observed_model_uses_first_runtime_turn_event(self):
        self.events([b'\xff', b'bad-json', [], {'type': 'turn.started', 'model': '  '},
                     {'type': 'system', 'subtype': 'init', 'model': 'other-provider'},
                     {'type': 'turn.started', 'requested_model': 'requested'},
                     {'type': 'turn.started', 'model': 'runtime-model'},
                     {'type': 'turn.started', 'model': 'later-model'}])
        self.assertEqual(self.codex.observed_model(self.folder, _strict_json), 'runtime-model')

    def test_claude_observed_model_only_uses_runtime_system_init(self):
        self.events([{'type': 'turn.started', 'model': 'other-provider'},
                     {'type': 'system', 'subtype': 'other', 'model': 'not-init'},
                     {'type': 'system', 'subtype': 'init', 'model': 'actual-claude'}])
        self.assertEqual(self.claude.observed_model(self.folder, _strict_json), 'actual-claude')

    def test_requested_model_is_never_reported_as_observed(self):
        for adapter in (self.codex, self.claude):
            chosen = profile(adapter.producer, model='requested-only')
            adapter.command(str(self.cli), self.context(adapter.producer), chosen)
            self.assertIsNone(adapter.observed_model(self.folder, _strict_json))
        self.events([{'type': 'result', 'model': 'requested-only'},
                     {'type': 'turn.started', 'requested_model': 'requested-only'}])
        self.assertIsNone(self.codex.observed_model(self.folder, _strict_json))
        self.assertIsNone(self.claude.observed_model(self.folder, _strict_json))

    def test_registry_fails_closed_for_unknown_harness_or_producer(self):
        for name in ('dsh', 'coze', '', None, {}):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'unknown research harness'):
                harness.get_adapter(name)
        for producer in ('unregistered', '', None, {}):
            with self.subTest(producer=producer), self.assertRaisesRegex(ValueError, 'unknown research producer'):
                harness.default_harness(producer)
        self.assertEqual(harness.default_harness('codex'), 'codex-cli')
        self.assertEqual(harness.default_harness('claude'), 'claude-code-cli')

    def test_only_trusted_adapter_instances_can_be_registered_without_conflicts(self):
        class LocalAdapter(harness.CodexCLIAdapter):
            harness_id = 'local-test-cli'

        adapter = LocalAdapter()
        with patch.dict(harness._ADAPTERS):
            harness.register_adapter(adapter)
            self.assertIs(harness.get_adapter('local-test-cli'), adapter)
            with self.assertRaisesRegex(ValueError, 'already registered'):
                harness.register_adapter(adapter)
        with self.assertRaisesRegex(ValueError, 'harness_id'):
            harness.register_adapter({'harness_id': 'json-command', 'command': 'external-command'})

    def test_adapter_metadata_is_read_only(self):
        metadata = harness.adapter_metadata()
        self.assertEqual(set(metadata), {'codex-cli', 'claude-code-cli', 'dsh-cli'})
        self.assertEqual(dict(metadata['codex-cli']),
                         dict(harness_id='codex-cli', producer='codex', executable='codex'))
        with self.assertRaises(TypeError):
            metadata['new-cli'] = {}
        with self.assertRaises(TypeError):
            metadata['codex-cli']['producer'] = 'claude'
        with self.assertRaises(TypeError):
            self.codex.metadata['producer'] = 'claude'


if __name__ == '__main__':
    unittest.main()
