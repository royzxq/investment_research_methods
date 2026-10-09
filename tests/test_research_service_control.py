import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import research_service_control as control
from scripts.research_scheduler import queue_lock


ROOT = Path(__file__).resolve().parents[1]


class ResearchServiceControlTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / 'methods with spaces'
        self.project.mkdir()
        self.queue = self.project / 'output/research_queue'
        self.queue.mkdir(parents=True)
        self.state = self.queue / 'state.json'
        self.state.write_bytes(b'{"existing": "preserve"}\n')
        self.plist = self.root / 'Library/LaunchAgents' / f'{control.LABEL}.plist'
        self.plist.parent.mkdir(parents=True)
        self.write_plist()
        self.calls = []
        self.loaded = True
        self.pid = None
        self.fail = None
        self.addCleanup(patch.stopall)
        patch.object(control, 'ROOT', self.project).start()
        patch.object(Path, 'home', return_value=self.root).start()
        patch.object(control.subprocess, 'run', side_effect=self.launchctl).start()

    def write_plist(self, **fields):
        data = dict(Label=control.LABEL, StartCalendarInterval={'Hour': 5, 'Minute': 0},
                    WorkingDirectory=str(self.project),
                    ProgramArguments=['/bin/zsh', str(self.project / 'deploy/launchd/run_research.sh'), sys.executable])
        data.update(fields)
        self.plist.write_bytes(plistlib.dumps(data))

    def launchctl(self, args, **kwargs):
        self.calls.append(args)
        action = args[1]
        if action == self.fail:
            if kwargs.get('check'):
                raise subprocess.CalledProcessError(5, args, stderr='simulated failure')
            return subprocess.CompletedProcess(args, 5, '', 'simulated failure')
        if action == 'print':
            if not self.loaded:
                return subprocess.CompletedProcess(args, 113, '', 'Could not find service')
            output = 'state = not running\n' if self.pid is None else f'state = running\npid = {self.pid}\n'
            return subprocess.CompletedProcess(args, 0, output, '')
        return subprocess.CompletedProcess(args, 0, '', '')

    def test_start_reloads_idle_schedule_without_running_research_or_changing_state(self):
        self.assertIn('05:00', control.manage('start'))
        self.assertEqual([call[1] for call in self.calls], ['print', 'bootout', 'enable', 'bootstrap'])
        self.assertEqual(self.calls[-1][-1], str(self.plist))
        self.assertEqual(self.state.read_bytes(), b'{"existing": "preserve"}\n')

    def test_start_loads_unloaded_service_and_stop_is_idempotent(self):
        self.loaded = False
        control.manage('start')
        self.assertEqual([call[1] for call in self.calls], ['print', 'enable', 'bootstrap'])
        self.calls.clear()
        control.manage('stop')
        self.assertEqual([call[1] for call in self.calls], ['print'])
        self.assertTrue(self.plist.exists())
        self.assertTrue(self.state.exists())

    def test_stop_unloads_idle_service_without_removing_plist_or_state(self):
        control.manage('stop')
        self.assertEqual([call[1] for call in self.calls], ['print', 'bootout'])
        self.assertTrue(self.plist.exists())
        self.assertEqual(self.state.read_bytes(), b'{"existing": "preserve"}\n')

    def test_active_service_and_held_queue_lock_block_both_actions(self):
        self.pid = 123
        for action in ('start', 'stop'):
            self.calls.clear()
            with self.assertRaisesRegex(RuntimeError, '运行'):
                control.manage(action)
            self.assertEqual([call[1] for call in self.calls], ['print'])
        self.pid = None
        with queue_lock(self.queue):
            for action in ('start', 'stop'):
                self.calls.clear()
                with self.assertRaisesRegex(RuntimeError, '运行'):
                    control.manage(action)
                self.assertEqual(self.calls, [])

    def test_missing_or_unsafe_plist_never_unloads_existing_service(self):
        self.plist.unlink()
        with self.assertRaisesRegex(ValueError, '安装'):
            control.manage('start')
        for fields in ({'Label': 'wrong'}, {'RunAtLoad': True}, {'KeepAlive': True},
                       {'WorkingDirectory': '/another/checkout'}, {'ProgramArguments': ['/another/launcher']}):
            self.write_plist(**fields)
            with self.assertRaises(ValueError):
                control.manage('start')
            if 'WorkingDirectory' in fields or 'ProgramArguments' in fields or 'Label' in fields:
                with self.assertRaises(ValueError):
                    control.manage('stop')
        self.assertEqual(self.calls, [])

    def test_launchctl_errors_are_not_reported_as_success(self):
        for action in ('print', 'bootout', 'bootstrap'):
            self.fail = action
            self.calls.clear()
            with self.assertRaises((RuntimeError, subprocess.CalledProcessError)):
                control.manage('start')
            self.assertEqual(self.calls[-1][1], action)

    def test_root_scripts_work_from_another_directory_with_fake_launchctl(self):
        # Exercise the user entry points with real subprocesses, no host service calls.
        patch.stopall()
        shutil.copytree(ROOT / 'scripts', self.project / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('start.sh', 'stop.sh'):
            shutil.copy2(ROOT / name, self.project / name)
        commands = self.root / 'bin'
        commands.mkdir()
        log = self.root / 'launchctl.jsonl'
        (commands / 'python3').write_text(f'#!{sys.executable}\n'
            'import os,runpy,sys\nfrom pathlib import Path\nfrom unittest.mock import patch\n'
            'sys.argv=sys.argv[1:]\nsys.path.insert(0,str(Path(sys.argv[0]).parent))\n'
            "with patch.object(Path,'home',return_value=Path(os.environ['METHODS_TEST_HOME'])):\n"
            "    runpy.run_path(sys.argv[0],run_name='__main__')\n")
        (commands / 'launchctl').write_text(f'#!{sys.executable}\n'
            'import json,os,sys\n'
            "with open(os.environ['METHODS_TEST_LOG'],'a') as out: out.write(json.dumps(sys.argv[1:])+'\\n')\n"
            "if sys.argv[1]=='print': print('state = not running')\n")
        for path in commands.iterdir():
            path.chmod(0o755)
        env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ['PATH'],
                   METHODS_TEST_HOME=str(self.root), METHODS_TEST_LOG=str(log))
        for name in ('start.sh', 'stop.sh'):
            result = subprocess.run([str(self.project / name)], cwd=self.root, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual([call[0] for call in calls], ['print', 'bootout', 'enable', 'bootstrap', 'print', 'bootout'])
        self.assertEqual(self.state.read_bytes(), b'{"existing": "preserve"}\n')


if __name__ == '__main__':
    unittest.main()
