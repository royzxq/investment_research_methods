"""DSH production adapter boundaries, without billable model requests."""
import ast
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_harness as harness
from scripts import research_dsh as dsh
from scripts.research_exchange import _strict_json


# The existing shared artifact fixture remains the sole report/audit builder;
# this wrapper adds only the native DSH CLI protocol. The source can be supplied
# by consumer tests after applying their existing valuation substitutions.
FAKE_DSH_CLI = r'''#!/usr/bin/env python3
import io,json,os,sys
from contextlib import redirect_stdout
from pathlib import Path
args=sys.argv[1:]
if '--help' in args:
 print('  --profile <name>\n  --patch <file>\n  --json')
 sys.exit(0)
folder=Path(args[args.index('--patch')+1]).parent
rows=json.loads((folder/'dsh-runtime.patch.json').read_text())
delivery=next(row['config']['personaPrefix'] for row in rows if row.get('id')=='system-prompt')
sys.argv=[sys.argv[0],'-p','--json-schema',(folder/'receipt-schema.json').read_text(),'--append-system-prompt',delivery]
source=__LEGACY_SOURCE_REPR__
capture=io.StringIO()
with redirect_stdout(capture):
 exec(compile(source,'offline-shared-artifact-fixture','exec'),{'__name__':'__main__'})
result=json.loads(capture.getvalue().strip().splitlines()[-1])
success=result.get('subtype')=='success' and result.get('is_error') is False
session='session-offline-dsh'
events=[{'type':'session','sessionId':session,'cwd':str(Path.cwd())},
 {'type':'status','phase':'turn_start','turn':1},
 {'type':'status','phase':'turn_end','turn':1,'reason':{'kind':'completed' if success else 'error'}},
 {'type':'final','text':json.dumps(result.get('structured_output',{}))}]
for event in events: print(json.dumps(event))
persist=folder/'dsh-sessions'/'offline-namespace'/session/'session.v4.jsonl'
persist.parent.mkdir(parents=True,exist_ok=True)
persist.write_text(json.dumps({'type':'session','version':4,'id':session,'cwd':str(Path.cwd())})+'\n'+json.dumps({'type':'request/header','data':{'header':{'config':{'model':'offline-dsh-observed'}}}})+'\n')
sys.exit(0 if success else 1)
'''


def build_fake_dsh_cli(legacy_source=None):
    if legacy_source is None:
        tree = ast.parse((ROOT / 'tests/test_research_runner.py').read_text())
        node = next(node for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(name, ast.Name) and name.id == 'FAKE_CLI' for name in node.targets))
        value = node.value.func.value if isinstance(node.value, ast.Call) else node.value
        legacy_source = ast.literal_eval(value).replace('__RESEARCH_TEST_ROOT__', str(ROOT))
    return FAKE_DSH_CLI.replace('__LEGACY_SOURCE_REPR__', repr(legacy_source))


def profile():
    return dict(profile_id='dsh-production', revision=1, producer='dsh', harness='dsh-cli',
                models=dict(main=dict(model='deepseek-flash', effort='high'),
                            subagent=dict(model='deepseek-flash')))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False) + '\n').encode()


def write_new(path, raw):
    path.write_bytes(raw)


class ResearchDSHTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'execution'
        self.folder.mkdir()
        (self.folder / 'receipt-schema.json').write_text('{"type":"object"}')
        self.adapter = harness.get_adapter('dsh-cli')
        self.context = harness.LaunchContext(self.folder, self.root, 'dsh', {}, 'frozen delivery')
        self.adapter.command('/local/dsh', self.context, profile())
        self.receipt = {'status': 'completed', 'generator': 'dsh'}

    def events(self, rows):
        (self.folder / 'events.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))

    def success(self):
        return [dict(type='session', sessionId='session-test', cwd=str(self.root)),
                dict(type='status', phase='turn_start', turn=1),
                dict(type='status', phase='turn_end', turn=1, reason=dict(kind='completed')),
                dict(type='final', text=json.dumps(self.receipt))]

    def parse(self):
        return self.adapter.receipt(self.folder, _strict_json, write_new, encode)

    def test_registry_and_legacy_defaults(self):
        self.assertEqual(harness.default_harness('claude'), 'claude-code-cli')
        self.assertEqual(harness.default_harness('dsh'), 'dsh-cli')
        self.assertEqual(self.adapter.producer, 'dsh')

    def test_profile_keeps_model_flexibility_and_explicit_capabilities(self):
        value = profile()
        value['models']['main'].update(model='deepseek-pro', effort='max')
        value['models']['subagent']['model'] = 'deepseek-flash'
        self.adapter.validate_profile(value)
        for role, key, value in (('main', 'effort', 'medium'), ('main', 'model', None),
                                 ('subagent', 'model', None)):
            item = profile()
            item['models'][role][key] = value
            with self.subTest(role=role, key=key), self.assertRaises(ValueError):
                self.adapter.validate_profile(item)

    def test_launch_homes_and_official_routes_are_per_attempt(self):
        original = {'DEEPSEEK_API_KEY': 'unit-test-placeholder', 'DSH_HOME': '/shared/home',
                    'DEEPSEEK_BASE_URL': 'https://untrusted.invalid', 'DSH_PERMISSION_MODE': 'danger-full-access'}
        env = self.adapter.launch_environment(original, profile(), self.context)
        self.assertEqual(env['DEEPSEEK_BASE_URL'], dsh.BASE_URL)
        self.assertEqual(env['DEEPSEEK_SEARCH_BASE_URL'], dsh.SEARCH_URL)
        self.assertNotIn('DSH_PERMISSION_MODE', env)
        for name in ('HOME', 'DSH_HOME', 'DSH_AGENTS_HOME', 'XDG_CONFIG_HOME'):
            self.assertTrue(Path(env[name]).is_relative_to(self.folder.resolve()))
        self.assertEqual(original['DSH_HOME'], '/shared/home')
        self.assertEqual(env['DSH_TELEMETRY_DISABLED'], '1')

    def test_fallback_key_requires_exact_official_cc_provider(self):
        cc = self.root / '.claude'
        cc.mkdir()
        settings = cc / 'settings.json'
        value = {'env': {'ANTHROPIC_BASE_URL': dsh.BASE_URL, 'ANTHROPIC_AUTH_TOKEN': 'unit-fallback'}}
        settings.write_text(json.dumps(value))
        with patch.object(dsh.Path, 'home', return_value=self.root):
            self.assertEqual(dsh._key({}), 'unit-fallback')
            self.assertEqual(dsh._key({'DEEPSEEK_API_KEY': 'unit-direct'}), 'unit-direct')
            with self.assertRaises(ValueError):
                dsh._key({'ANTHROPIC_BASE_URL': 'https://different.invalid'})
            for url in ('https://api.deepseek.com/anthropic/', 'https://api.deepseek.com.evil/anthropic',
                        'https://api.anthropic.com', None):
                value['env']['ANTHROPIC_BASE_URL'] = url
                settings.write_text(json.dumps(value))
                with self.subTest(url=url), self.assertRaises(ValueError):
                    dsh._key({})

    def test_patch_has_native_mcp_sandbox_and_only_nonsecret_key_reference(self):
        folder = self.root / 'with-mcp'
        folder.mkdir()
        (folder / 'receipt-schema.json').write_text('{"type":"object"}')
        context = harness.LaunchContext(folder, self.root, 'dsh',
            {'jev_research': {'command': '/trusted/python', 'args': ['serve', '--config', '/public/path']}}, 'delivery')
        self.adapter.command('/local/dsh', context, profile())
        rows = json.loads((folder / 'dsh-runtime.patch.json').read_text())
        by_id = {row['id']: row for row in rows if 'id' in row}
        self.assertEqual(by_id['sandbox-policy']['config']['mode'], 'workspace-write')
        self.assertEqual(by_id['approval']['config']['policy'], 'never')
        self.assertEqual(by_id['llm-deepseek']['config']['maxTokens'], 32768)
        self.assertEqual(by_id['llm-deepseek']['config']['streamIdleTimeoutMs'], 180000)
        inserted = [entry for row in rows for entry in row.get('insert', [])]
        mcp = next(row for row in inserted if row['id'] == 'research-mcp-jev_research')
        self.assertEqual(mcp['name'], '@deepseek-ai/dsh-mcp-client')
        self.assertEqual(set(mcp['config']['env']), {'JEV_KEY_FILE'})
        self.assertTrue(mcp['config']['env']['JEV_KEY_FILE'].endswith('/.config/typesafe/key'))
        self.assertNotIn('unit-test-placeholder', (folder / 'dsh-runtime.patch.json').read_text())
        self.assertFalse(json.loads((folder / 'dsh-runtime.json').read_text())['auto_review'])

    def test_receipt_requires_ordered_completed_terminal(self):
        self.events(self.success())
        self.assertEqual(self.parse(), self.receipt)
        self.assertEqual(json.loads((self.folder / 'cli-receipt.json').read_text()), self.receipt)

    def test_failed_cancelled_missing_and_misordered_terminations_fail_closed(self):
        base = self.success()
        cases = [base[:-1], base[1:], [base[0], *base[2:]], [base[0], base[2], base[1], base[3]],
                 base + [dict(type='status', phase='step_start')],
                 [*base[:-1], dict(type='error', message='failure'), base[-1]],
                 [base[0], base[1], base[1], base[2], base[3]]]
        for reason in ('error', 'aborted', 'cancelled', 'max_tokens', 'max-tokens', 'max_steps'):
            rows = deepcopy(base)
            rows[-2]['reason']['kind'] = reason
            cases.append(rows)
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.events(rows)
                self.parse()

    def test_final_receipt_must_be_exact_strict_json_object(self):
        for final in ('```json\n{}\n```', 'done {}', '[1]', '{"status":1,"status":2}', '{"value":NaN}'):
            rows = self.success()
            rows[-1]['text'] = final
            self.events(rows)
            with self.subTest(final=final), self.assertRaises(ValueError):
                self.parse()

    def test_invalid_lines_or_truncated_terminal_cannot_be_ignored(self):
        self.events(self.success())
        with (self.folder / 'events.jsonl').open('a') as stream:
            stream.write('not-json\n')
        with self.assertRaises(ValueError):
            self.parse()
        for i in (1, 2, 3):
            rows = self.success()
            rows[i]['truncated'] = True
            self.events(rows)
            with self.subTest(index=i), self.assertRaises(ValueError):
                self.parse()

    def test_runtime_patch_changes_are_rejected(self):
        self.events(self.success())
        (self.folder / 'dsh-runtime.patch.json').write_text('[]')
        with self.assertRaisesRegex(ValueError, 'runtime changed'):
            self.parse()

    def test_observed_model_uses_only_matching_persisted_main_session(self):
        self.events(self.success())
        self.assertIsNone(self.adapter.observed_model(self.folder, _strict_json))
        root = self.folder / 'dsh-sessions' / 'workspace-namespace' / 'session-test'
        root.mkdir(parents=True)
        path = root / 'session.v4.jsonl'
        path.write_text(json.dumps({'type': 'session', 'id': 'session-test', 'cwd': str(self.root)}) + '\n'
                        + json.dumps({'type': 'request/header', 'data': {'header': {'config': {'model': 'observed-actual'}}}}) + '\n')
        self.assertEqual(self.adapter.observed_model(self.folder, _strict_json), 'observed-actual')
        path.unlink()
        path.symlink_to(self.folder / 'receipt-schema.json')
        self.assertIsNone(self.adapter.observed_model(self.folder, _strict_json))

    def test_capability_preflight_is_local_and_catches_missing_flags(self):
        cli = self.root / 'dsh'
        cli.write_text('#!/bin/sh\nexit 0\n')
        cli.chmod(0o700)
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'unit-placeholder'}):
            output = subprocess.CompletedProcess([], 0, '  --profile <p>\n  --patch <f>\n  --json\n', '')
            with patch.object(dsh.subprocess, 'run', return_value=output) as run:
                self.adapter.preflight(str(cli), self.root, profile())
                self.assertEqual(run.call_count, 2)
                self.assertEqual(run.call_args.kwargs['stdin'], subprocess.DEVNULL)
            with patch.object(dsh.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '  --json\n', '')):
                with self.assertRaises(ValueError):
                    self.adapter.preflight(str(cli), self.root, profile())

    def test_data_env_bridge_is_a_narrow_in_memory_forwarder(self):
        # Node executes only the fixed plugin against a fake service; no DSH or API.
        node = '/Users/xinquanzhou/.local/share/dsh-runtime/node_modules/node/bin/node'
        if not Path(node).is_file():
            self.skipTest('bundled Node unavailable')
        script = self.root / 'test-bridge.mjs'
        script.write_text('''import {apply} from './execution/dsh-data-environment.mjs';
const runtime={spawn(spec){return spec}};
const ctx={subprocess:runtime,on(){}};
apply(ctx);
const got=runtime.spawn({env:{PUBLIC_FLAG:'yes'}});
if(got.env.TUSHARE_TOKEN!=='fake-data-token'||got.env.PUBLIC_FLAG!=='yes'||got.env.DEEPSEEK_API_KEY!==undefined)process.exit(2);
''')
        env = dict(os.environ, TUSHARE_TOKEN='fake-data-token', DEEPSEEK_API_KEY='fake-model-key')
        result = subprocess.run([node, str(script)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pdf_python_preserves_virtual_environment_launcher(self):
        venv = self.root / 'venv/bin'
        venv.mkdir(parents=True)
        launcher = venv / 'python3'
        launcher.symlink_to(sys.executable)
        dsh._pdf_python.cache_clear()
        self.addCleanup(dsh._pdf_python.cache_clear)
        def probe(args, **kwargs):
            return subprocess.CompletedProcess(args, 0 if args[0] == str(launcher) else 1, b'', b'')
        with patch.object(dsh.sys, 'executable', str(launcher)), patch.object(dsh.subprocess, 'run', side_effect=probe):
            self.assertEqual(dsh._pdf_python(), str(launcher))


if __name__ == '__main__':
    unittest.main()
