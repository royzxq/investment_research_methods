"""Offline service configuration checks; never install or run a scheduler."""
import io
import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import install_research_service as installer
from scripts import research_runtime


class InstallResearchRuntimeConfigTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.executable = sys.executable

    def save_config(self, name='runtime config.json', value=None):
        path = self.root / name
        path.write_text(json.dumps(research_runtime.load_config() if value is None else value))
        return path

    def service(self, **kwargs):
        return installer.service(self.executable, self.executable, self.executable,
                                 root=self.root, **kwargs)

    def test_default_plist_matches_existing_bytes_and_never_loads_config(self):
        expected = dict(Label=installer.LABEL,
            ProgramArguments=['/bin/zsh', str(self.root/'deploy/launchd/run_research.sh'),
                              self.executable, self.executable, self.executable],
            WorkingDirectory=str(self.root),
            StartCalendarInterval=[{'Minute': minute} for minute in (0, 15, 30, 45)],
            EnvironmentVariables={'TZ': 'Asia/Shanghai'},
            ThrottleInterval=60, ExitTimeOut=45,
            StandardOutPath=str(self.root/'output/research_queue/service.log'),
            StandardErrorPath=str(self.root/'output/research_queue/service-error.log'))
        with patch.object(research_runtime, 'load_config', side_effect=AssertionError('unexpected config read')):
            self.assertEqual(plistlib.dumps(self.service()), plistlib.dumps(expected))
            self.assertEqual(plistlib.dumps(self.service(runtime_config=None)), plistlib.dumps(expected))

    def test_absolute_valid_config_with_spaces_is_one_extra_wrapper_argument(self):
        config = self.save_config()
        baseline = self.service()
        configured = self.service(runtime_config=config)
        self.assertEqual(configured['ProgramArguments'], baseline['ProgramArguments'] + [str(config)])
        baseline['ProgramArguments'].append(str(config))
        self.assertEqual(configured, baseline)

    def test_relative_config_is_rejected_before_reading(self):
        with patch.object(research_runtime, 'load_config', side_effect=AssertionError('relative path read')):
            for path in ('runtime.json', '../runtime.json', Path('runtime config.json')):
                with self.subTest(path=str(path)), self.assertRaisesRegex(ValueError, 'absolute'):
                    self.service(runtime_config=path)

    def test_dsh_path_has_its_own_literal_wrapper_slot_and_preserves_legacy_claude(self):
        baseline = self.service()
        configured = self.service(dsh=self.executable)
        self.assertEqual(configured['ProgramArguments'], baseline['ProgramArguments'] + ['', self.executable])
        config = self.save_config()
        configured = self.service(runtime_config=config, dsh=self.executable)
        self.assertEqual(configured['ProgramArguments'], baseline['ProgramArguments'] + [str(config), self.executable])
        with self.assertRaisesRegex(ValueError, 'absolute executable'):
            self.service(dsh='relative-dsh')

    def test_missing_directory_and_unreadable_config_are_rejected(self):
        for path in (self.root/'missing.json', self.root):
            with self.subTest(path=path.name), self.assertRaisesRegex(ValueError, 'cannot read'):
                self.service(runtime_config=path)
        config = self.save_config()
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('private path')):
            with self.assertRaisesRegex(ValueError, 'cannot read') as caught:
                self.service(runtime_config=config)
        self.assertNotIn('private path', str(caught.exception))

    def test_invalid_schema_and_secret_fields_are_rejected_without_echo(self):
        wrong_schema = research_runtime.load_config()
        wrong_schema['schema_version'] = 'unsupported/v1'
        extra_secret = research_runtime.load_config()
        extra_secret['api_key'] = 'PRIVATE-SECRET-VALUE'
        for value in ({}, wrong_schema, extra_secret):
            with self.subTest(value_type=type(value).__name__):
                config = self.save_config(value=value)
                with self.assertRaises(ValueError) as caught:
                    self.service(runtime_config=config)
                self.assertNotIn('PRIVATE-SECRET-VALUE', str(caught.exception))
        config.write_text('{invalid-json')
        with self.assertRaisesRegex(ValueError, 'invalid strict JSON'):
            self.service(runtime_config=config)

    def test_cli_preview_accepts_explicit_config_without_installing(self):
        config = self.save_config()
        output = io.BytesIO()
        arguments = ['install_research_service.py', '--python', self.executable,
                     '--codex-cli', self.executable, '--claude-cli', self.executable,
                     '--runtime-config', str(config)]
        with patch.object(sys, 'argv', arguments), \
                patch.object(sys, 'stdout', SimpleNamespace(buffer=output)), \
                patch.object(installer.subprocess, 'run', side_effect=AssertionError('must only preview')):
            installer.main()
        self.assertEqual(plistlib.loads(output.getvalue())['ProgramArguments'][-1], str(config))


@unittest.skipUnless(shutil.which('zsh'), 'requires zsh to check the macOS wrapper')
class ResearchServiceWrapperTests(unittest.TestCase):
    def test_unset_shell_variable_does_not_skip_later_tool_credentials(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wrapper = root/'deploy/launchd/run_research.sh'
            wrapper.parent.mkdir(parents=True)
            capture = root/'environment.json'
            stub = root/'capture.py'
            stub.write_text('import json,os,sys\nfrom pathlib import Path\n'
                            'Path(sys.argv[1]).write_text(json.dumps({"tushare":bool(os.environ.get("TUSHARE_TOKEN"))}))\n')
            source = (installer.ROOT/'deploy/launchd/run_research.sh').read_text()
            wrapper.write_text(source.replace('exec /usr/bin/caffeinate -i -s "${scheduler_args[@]}"',
                'exec "$1" "'+str(stub)+'" "'+str(capture)+'"'))
            home = root/'home'; home.mkdir()
            (home/'.zshrc').write_text('export PYTHONPATH="$UNSET_RESEARCH_PATH:/offline"\n'
                                     'export TUSHARE_TOKEN=offline-test-placeholder\n')
            env = {'HOME':str(home), 'PATH':'/usr/bin:/bin:/usr/sbin:/sbin'}
            subprocess.run([shutil.which('zsh'), '-f', str(wrapper), sys.executable,
                            '/unused/codex', '/unused/claude'], env=env, check=True,
                           capture_output=True, text=True)
            self.assertEqual(json.loads(capture.read_text()), {'tushare': True})

    def test_optional_config_is_forwarded_as_literal_argument_to_stub_only(self):
        """Run a copied wrapper with bootstrap disabled and caffeinate stubbed."""
        source = (installer.ROOT/'deploy/launchd/run_research.sh').read_text()
        bootstrap = 'if [ -f "$HOME/.zshrc" ]; then'
        command = 'exec /usr/bin/caffeinate '
        self.assertEqual(source.count(bootstrap), 1)
        self.assertEqual(source.count(command), 1)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wrapper = root/'project with spaces/deploy/launchd/run_research.sh'
            wrapper.parent.mkdir(parents=True)
            capture = root/'captured argv.json'
            stub = root/'caffeinate stub'
            stub.write_text('#!' + sys.executable + '\n'
                'import json, os, pathlib, sys\n'
                'pathlib.Path(os.environ["RESEARCH_WRAPPER_STUB_OUTPUT"]).write_text(json.dumps(sys.argv[1:]))\n')
            stub.chmod(0o700)
            wrapper.write_text(source.replace(bootstrap, 'if false; then').replace(
                command, 'exec ' + shlex.quote(str(stub)) + ' '))
            env = dict(os.environ, RESEARCH_WRAPPER_STUB_OUTPUT=str(capture))
            paths = ['/python path', '/codex path', '/claude path']
            expected = ['-i', '-s', paths[0], 'scripts/research_scheduler.py', 'run',
                        '--scheduled', '--codex-cli', paths[1], '--claude-cli', paths[2]]
            malicious_name = str(root/'runtime config $(touch INJECTED).json')
            for optional in ([], [''], [malicious_name]):
                with self.subTest(optional=optional):
                    subprocess.run([shutil.which('zsh'), str(wrapper), *paths, *optional],
                                   env=env, check=True, capture_output=True, text=True)
                    extra = ['--runtime-config', malicious_name] if optional == [malicious_name] else []
                    self.assertEqual(json.loads(capture.read_text()), expected + extra)
                    self.assertFalse((wrapper.parents[2]/'INJECTED').exists())
            dsh_name = str(root/'dsh path $(touch INJECTED)')
            subprocess.run([shutil.which('zsh'), str(wrapper), *paths, malicious_name, dsh_name],
                           env=env, check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(capture.read_text()), expected +
                             ['--runtime-config', malicious_name, '--dsh-cli', dsh_name])
            self.assertFalse((wrapper.parents[2]/'INJECTED').exists())


if __name__ == '__main__':
    unittest.main()
