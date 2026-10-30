"""CLI registration and durable never-requested/disabled audit records."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import research_runner as runner
from scripts import research_jev as jev
spec=importlib.util.spec_from_file_location('jev_runner_fixture',Path(__file__).with_name('test_research_runner.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class JevRunnerTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ResearchRunnerTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)

    def test_claude_execution_registers_jev_and_preserves_original_prompt(self):
        run=runner.prepare_request(self.fx.request_path,self.fx.methods)
        folder=run/'execution/SH-600066/claude';original=(folder/'prompt.txt').read_bytes()
        capture={};original_popen=runner.subprocess.Popen
        def popen(args,**kw):capture['args']=args;return original_popen(args,**kw)
        with patch.object(runner.subprocess,'Popen',side_effect=popen):result=self.fx.execute()
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'],'completed')
        args=capture['args'];servers=json.loads(args[args.index('--mcp-config')+1])['mcpServers']
        self.assertEqual(set(servers),{'jev_research'})
        self.assertEqual((folder/'prompt.txt').read_bytes(),original)
        self.assertEqual(self.fx.capture.read_bytes(),(folder/'jev-runtime-prompt.txt').read_bytes())
        process=json.loads((folder/'process.json').read_text())
        self.assertEqual(process['jev']['status'],'not_requested')
        self.assertEqual(process['jev']['reason'],'no_candidate_batch_submitted')

    def test_off_does_not_register_even_if_backend_installed(self):
        result=self.fx.execute(jev_mode='off');folder=result.parent/'execution/SH-600066/claude'
        args=runner.command(str(self.fx.fake),'claude',folder,self.fx.methods)
        self.assertEqual(json.loads(args[args.index('--mcp-config')+1])['mcpServers'],{})
        self.assertEqual(json.loads((folder/'process.json').read_text())['jev']['status'],'disabled')

    def test_codex_registers_audited_wrapper_and_disables_raw_jev(self):
        run=runner.prepare_request(self.fx.request_path,self.fx.methods);folder=run/'execution/SH-600066/codex'
        jev.prepare(folder,self.fx.methods,task_id='SH-600066',day='2026-10-06',generator='codex')
        args=runner.command('codex','codex',folder,self.fx.methods)
        self.assertIn('mcp_servers.jev.enabled=false',args)
        self.assertTrue(any(x.startswith('mcp_servers.jev_research.command=') for x in args))

    def test_mode_validation_precedes_launch(self):
        with self.assertRaisesRegex(ValueError,'Jev mode'):
            self.fx.execute(jev_mode='invalid')
        self.assertFalse(self.fx.capture.exists())

    def test_failed_cli_still_has_not_requested_audit(self):
        import os
        os.environ['MOCK_MODE']='nonzero';result=self.fx.execute()
        folder=result.parent/'execution/SH-600066/claude'
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'],'failed')
        self.assertTrue((folder/'runner/jev-summary.json').exists())

    def test_journal_failure_is_nonfatal_telemetry(self):
        with patch.object(jev,'summarize',side_effect=RuntimeError('audit unavailable')):
            result=self.fx.execute()
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'],'completed')
        process=json.loads((result.parent/'execution/SH-600066/claude/process.json').read_text())
        self.assertEqual(process['jev_audit_error'],'RuntimeError')
