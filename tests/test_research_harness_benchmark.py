"""Offline gates for the explicit experimental runner; never invoke models."""
from pathlib import Path
import json
import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tests'))
from scripts import research_harness_benchmark as bench
from scripts import research_acceptance
from test_research_experiment_contract import fixture as research_fixture, report_for


class ResearchHarnessBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def result(self,task,document):
        p=self.root/'workspace/outputs';p.mkdir(parents=True,exist_ok=True)
        names={'smoke':'smoke.json','probe':'probe-result.json','research':'result.json'}
        (p/names[task]).write_text(json.dumps(document))
        return p

    def test_missing_artifact_is_not_completed(self):
        result=bench.validate_artifacts(self.root,'research')
        self.assertFalse(result['file_exists']);self.assertIn('missing expected file',result['errors'])

    def test_smoke_must_match_actual_file(self):
        self.result('smoke',{'ok':True,'value':42})
        self.assertEqual(bench.validate_artifacts(self.root,'smoke')['errors'],[])
        self.result('smoke',{'ok':False,'value':42})
        self.assertIn('smoke content mismatch',bench.validate_artifacts(self.root,'smoke')['errors'])

    def test_invalid_duplicate_and_nonfinite_json_not_accepted(self):
        p=self.result('smoke',{})/'smoke.json'
        for raw in ('{"ok":true,"ok":true,"value":42}','{"ok":true,"value":NaN}','{"ok":true,"value":1e400}','[]'):
            p.write_text(raw)
            self.assertFalse(bench.validate_artifacts(self.root,'smoke')['strict_json'])

    def test_probe_keeps_null_and_weighted_margin(self):
        document=dict(schema_version='harness-tool-probe/v1',arithmetic=dict(revenue=300000000,profit=60000000,margin=.2,debt=None),
                      independent_check=dict(completed=True),recovery=dict(first_exit=42,second_exit=0,ok=True),web=dict(search_succeeded=True,fetch_succeeded=True))
        self.result('probe',document)
        result=bench.validate_artifacts(self.root,'probe')
        self.assertTrue(result['arithmetic_correct']);self.assertTrue(result['recovery_correct'])
        self.assertTrue(result['reported_fields_require_log_verification'])
        document['arithmetic']['debt']=0;self.result('probe',document)
        self.assertFalse(bench.validate_artifacts(self.root,'probe')['arithmetic_correct'])

    def test_invalid_probe_containers_return_errors(self):
        for field in ('arithmetic','independent_check','recovery','web'):
            document=dict(schema_version='harness-tool-probe/v1',arithmetic={},independent_check={},recovery={},web={})
            document[field]=None
            self.result('probe',document)
            self.assertTrue(bench.validate_artifacts(self.root,'probe')['errors'])

    def test_research_never_becomes_production_acceptance(self):
        document=dict(schema_version='harness-research-experiment/v1',code='300750.SZ',valuation_date='2026-10-21',currency='CNY',price_map={},research_controls={},monitoring=[],audit={})
        p=self.result('research',document)
        (p/'report.md').write_text('\n'.join(f'## {n}. section\nbody' for n in range(9)))
        result=bench.validate_artifacts(self.root,'research')
        self.assertTrue(result['nine_sections']);self.assertFalse(result['production_acceptance'])
        strict=bench.validate_artifacts(self.root,'research',delivery_contract=True)
        self.assertTrue(strict['strict_json']);self.assertEqual(strict['errors'],[])
        self.assertEqual(strict['delivery_contract']['status'],'failed')
        document['generator']='claude';self.result('research',document)
        self.assertIn('research exact fields',bench.validate_artifacts(self.root,'research')['errors'])

    def research_delivery(self, *, acceptance=False):
        document,review=research_fixture()
        report=report_for(document,review)
        if acceptance:
            claims=dict(schema_version=research_acceptance.SCHEMA,
                r14=dict(**review['r14'],inputs={key:dict(status='unknown',sources=[],derivation=None)
                    for key in research_acceptance.INPUTS},calculation=None),
                recovery=dict(operator='all_of',scopes=document['audit']['release_all_of']))
            report+='\n\n'+research_acceptance.render_block(claims,document['audit'],root=self.root/'workspace')
        return document,report

    def test_legacy_delivery_does_not_retroactively_require_new_acceptance(self):
        document,report=self.research_delivery()
        output=self.result('research',document);(output/'report.md').write_text(report)
        result=bench.validate_artifacts(self.root,'research',delivery_contract=True)
        self.assertEqual(result['delivery_contract']['status'],'passed')
        self.assertNotIn('acceptance',result['delivery_contract'])
        required=bench.validate_artifacts(self.root,'research',delivery_contract=True,require_acceptance=True)
        self.assertEqual(required['delivery_contract']['status'],'failed')
        self.assertIn('acceptance',str(required['delivery_contract']['errors']))

    def test_new_acceptance_runs_even_without_legacy_delivery_flag(self):
        document,report=self.research_delivery(acceptance=True)
        output=self.result('research',document);(output/'report.md').write_text(report)
        result=bench.validate_artifacts(self.root,'research',require_acceptance=True)
        self.assertEqual(result['delivery_contract']['status'],'passed')
        self.assertEqual(result['delivery_contract']['acceptance']['schema_version'],bench.ACCEPTANCE_CONTRACT)
        self.assertFalse(result['production_acceptance'])

    def test_root_cannot_be_formal_or_parent_directory(self):
        for path in (ROOT,ROOT/'research/investment/companies',bench.EXPERIMENTS,bench.FOLLOWUP_EXPERIMENTS,bench.EXPERIMENTS/'../outside'):
            with self.subTest(path=path),self.assertRaises(ValueError):bench.safe_experiment(path)

    def test_trial_requires_explicit_execution_flag_before_model_imports(self):
        with self.assertRaises(SystemExit):bench.main(['probe','--directory',str(bench.EXPERIMENTS/'unused')])
        self.assertFalse((bench.EXPERIMENTS/'unused').exists())

    def frozen_experiment(self,name='experiment'):
        target=self.root/name;(target/'frozen').mkdir(parents=True);(target/'prompts').mkdir()
        (target/'frozen/input.txt').write_text('frozen');(target/'prompts/research.txt').write_text('original prompt')
        (target/'prompts/smoke.txt').write_text('smoke')
        manifest=dict(schema_version=bench.SCHEMA,frozen=bench.inventory(target/'frozen'),prompts=bench.inventory(target/'prompts'))
        (target/'manifest.json').write_text(json.dumps(manifest))
        return target

    def test_followup_preserves_original_corpus_and_freezes_execution_tools(self):
        source=self.frozen_experiment('source');target=self.root/'new'
        original=bench.inventory(source)
        with patch.object(bench,'EXPERIMENTS',self.root):
            bench.prepare_from_frozen(target,source,execution_files=['scripts/research_harness_benchmark.py'],addendum='original method unchanged')
            manifest=bench.verify_experiment(target)
            self.assertEqual(manifest['frozen'],bench.inventory(source/'frozen'))
            self.assertEqual(original,bench.inventory(source))
            self.assertEqual(manifest['planned']['research_per_arm'],2)
            self.assertEqual(manifest['acceptance_contract'],bench.ACCEPTANCE_CONTRACT)
            self.assertEqual(manifest['execution_source_sha256']['research_acceptance.py'],
                             bench.digest(ROOT/'scripts/research_acceptance.py'))
            for name in bench.ACCEPTANCE_EXECUTION_FILES:
                self.assertEqual(bench.digest(target/'execution-tools'/Path(name).name),bench.digest(ROOT/name))
            prompt=(target/'prompts/research.txt').read_text()
            self.assertIn('execution-tools/acceptance-gates.md',prompt)
            self.assertIn('--require-acceptance --root .',prompt)
            with self.assertRaisesRegex(ValueError,'immutable'):
                bench.prepare_from_frozen(target,source,execution_files=[],addendum='x')
            (target/'execution-tools/delivery-addendum.md').write_text('changed')
            with self.assertRaisesRegex(ValueError,'tools changed'):bench.verify_experiment(target)

    def test_followup_rejects_unsafe_execution_file_before_creating(self):
        source=self.frozen_experiment('source')
        with patch.object(bench,'EXPERIMENTS',self.root):
            for filename in ('../secrets','/absolute'):
                with self.assertRaises(ValueError):
                    bench.prepare_from_frozen(self.root/'bad',source,execution_files=[filename],addendum='x')
                self.assertFalse((self.root/'bad').exists())

    def test_new_initial_prepare_uses_independent_shared_gate(self):
        repo=self.root/'synthetic-repo';source=repo/'source-run';materials=repo/'materials'
        (source/'packs').mkdir(parents=True);(source/'packs/SZ-300750.md').write_text('synthetic offline pack')
        (source/'framework-snapshot').mkdir()
        for name in ('investment_framework.md','investment_framework_compact.md'):
            (source/'framework-snapshot'/name).write_text('synthetic original '+name)
        materials.mkdir();(materials/'finance-announcement-source-ledger.json').write_text('[]')
        for name in bench.ACCEPTANCE_EXECUTION_FILES:
            target=repo/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        for name in bench.ACCEPTANCE_SOURCE_FILES:
            target=repo/'scripts'/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/'scripts'/name).read_bytes())
        for skill in ('stock-research','deep-research-auto'):
            target=repo/'.agents/skills'/skill;target.mkdir(parents=True,exist_ok=True)
            (target/'SKILL.md').write_text('synthetic method entry')
        target=self.root/'initial'
        with patch.object(bench,'EXPERIMENTS',self.root),patch.object(bench,'ROOT',repo),patch.object(bench,'SOURCE_RUN',source),patch.object(bench,'MATERIALS',materials):
            bench.prepare_experiment(target)
            manifest=bench.verify_experiment(target)
        self.assertEqual(manifest['acceptance_contract'],bench.ACCEPTANCE_CONTRACT)
        self.assertEqual(manifest['delivery_contract'],'harness-delivery-checks/v1')
        self.assertIn('research_acceptance.py',manifest['execution_tools'])
        self.assertIn('--require-acceptance --root .',(target/'prompts/research.txt').read_text())
        self.assertEqual((target/'prompts/smoke.txt').read_text(),bench.SMOKE_PROMPT)
        self.assertEqual((target/'prompts/probe.txt').read_text(),bench.PROBE_PROMPT)
        self.assertEqual((target/'frozen/framework/investment_framework.md').read_bytes(),
                         (source/'framework-snapshot/investment_framework.md').read_bytes())

    def test_new_manifest_cannot_omit_frozen_gate_dependencies_or_hashes(self):
        source=self.frozen_experiment('source');target=self.root/'new'
        with patch.object(bench,'EXPERIMENTS',self.root):
            bench.prepare_from_frozen(target,source,execution_files=[],addendum='x')
            original=json.loads((target/'manifest.json').read_text())
            for field in ('execution_tools','execution_source_sha256','delivery_contract'):
                broken=dict(original);broken.pop(field)
                (target/'manifest.json').write_text(json.dumps(broken))
                with self.subTest(field=field),self.assertRaisesRegex(ValueError,'complete frozen gate dependencies'):
                    bench.verify_experiment(target)
            for field,key in (('execution_tools','research_acceptance.py'),
                              ('execution_tools','acceptance-gates.md'),
                              ('execution_source_sha256','research_acceptance.py')):
                broken=json.loads(json.dumps(original));broken[field].pop(key)
                (target/'manifest.json').write_text(json.dumps(broken))
                with self.subTest(field=field,key=key),self.assertRaisesRegex(ValueError,'complete frozen gate dependencies'):
                    bench.verify_experiment(target)
            (target/'manifest.json').write_text(json.dumps(original))
            bench.verify_experiment(target)

    def test_legacy_manifest_selects_original_contract(self):
        source=self.frozen_experiment('source')
        manifest=json.loads((source/'manifest.json').read_text())
        manifest['delivery_contract']='harness-delivery-checks/v1'
        (source/'manifest.json').write_text(json.dumps(manifest))
        with patch.object(bench,'EXPERIMENTS',self.root):
            checked=bench.verify_experiment(source)
        self.assertFalse(bench.requires_acceptance(checked))
        self.assertNotIn('acceptance_contract',checked)

    def test_unknown_acceptance_contract_refused_before_credentials_or_output(self):
        for index,version in enumerate((None,False,'stock-research-acceptance/v99')):
            source=self.frozen_experiment('unknown-'+str(index))
            manifest=json.loads((source/'manifest.json').read_text());manifest['acceptance_contract']=version
            (source/'manifest.json').write_text(json.dumps(manifest))
            with patch.object(bench,'EXPERIMENTS',self.root),patch.object(Path,'home',side_effect=AssertionError('credential access')):
                with self.assertRaisesRegex(ValueError,'unknown frozen acceptance contract'):
                    bench.run_pair(source,'research')
            self.assertFalse((source/'runs').exists())

    def test_run_pair_selects_frozen_acceptance_and_records_only_new_dependency(self):
        settings=self.root/'.claude';settings.mkdir()
        (settings/'settings.json').write_text(json.dumps({'env':{'ANTHROPIC_AUTH_TOKEN':'synthetic-local-only','ANTHROPIC_BASE_URL':'https://api.deepseek.com/anthropic'}}))
        document,report=self.research_delivery()
        class FakeProxy:
            def __init__(self,*args,**kwargs):pass
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def url(self,arm):return 'http://127.0.0.1:1/'+arm
            def stop_arm(self,*args):pass
            def summary(self):return {'by_arm':{}}
        def fake_trial(arm,workspace,*args,**kwargs):
            (workspace/'outputs/result.json').write_text(json.dumps(document))
            (workspace/'outputs/report.md').write_text(report)
            return {'success':True}
        for version in (None,bench.ACCEPTANCE_CONTRACT):
            if version:
                source=self.frozen_experiment('new-run-source');target=self.root/'new-run'
                with patch.object(bench,'EXPERIMENTS',self.root):
                    bench.prepare_from_frozen(target,source,execution_files=[],addendum='offline shared gate')
            else:
                target=self.frozen_experiment('old-run')
            manifest=json.loads((target/'manifest.json').read_text())
            manifest.update(delivery_contract='harness-delivery-checks/v1',planned=dict(
                research_per_arm=2,max_output_tokens=32768,stream_idle_timeout_seconds=180,research_timeout_seconds=2400))
            if version:manifest['acceptance_contract']=version
            (target/'manifest.json').write_text(json.dumps(manifest))
            with patch.object(bench,'EXPERIMENTS',self.root),patch.object(Path,'home',return_value=self.root),patch.object(bench,'cli_identity',return_value={}),patch('scripts.research_experiment_proxy.ObservingProxy',FakeProxy),patch('scripts.research_harness_trial.run_trial',fake_trial),patch('builtins.print'):
                result=bench.run_pair(target,'research',timeout=2400,max_output_tokens=32768,stream_idle_timeout=180)
            expected='failed' if version else 'passed'
            for arm in ('cc','dsh'):
                self.assertEqual(result['outcomes'][arm]['artifacts']['delivery_contract']['status'],expected)
                self.assertEqual(result['outcomes'][arm]['experimental_delivery_contract_pass'],not bool(version))
            self.assertEqual('research_acceptance.py' in result['source_sha256'],bool(version))
            configuration=json.loads((target/'runs/research-01/configuration.json').read_text())
            self.assertEqual('research_acceptance.py' in configuration['source_sha256'],bool(version))

    def test_followup_rejects_unplanned_third_research_before_credentials(self):
        source=self.frozen_experiment('source');target=self.root/'new'
        with patch.object(bench,'EXPERIMENTS',self.root):
            bench.prepare_from_frozen(target,source,execution_files=[],addendum='x')
            with self.assertRaisesRegex(ValueError,'frozen follow-up plan'):
                bench.run_pair(target,'research',3,timeout=2400,max_output_tokens=32768,stream_idle_timeout=180)

    def test_failure_gate_cancels_only_affected_arm(self):
        target=self.frozen_experiment()
        settings=self.root/'.claude';settings.mkdir()
        (settings/'settings.json').write_text(json.dumps({'env':{'ANTHROPIC_AUTH_TOKEN':'synthetic-local-only','ANTHROPIC_BASE_URL':'https://api.deepseek.com/anthropic'}}))
        cc_stopped=threading.Event();dsh_cancelled=[];stops=[]
        class FakeProxy:
            def __init__(self,*args,**kwargs):pass
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def url(self,arm):return 'http://127.0.0.1:1/'+arm
            def stop_arm(self,arm,reason):stops.append((arm,reason))
            def summary(self):
                return {'subsequent_requests_blocked':False,'by_arm':{'cc':{'subsequent_requests_blocked':True,'block_reason':'UnknownUsageLimit'},'dsh':{'subsequent_requests_blocked':False}}}
        def fake_trial(arm,workspace,run,prompt,url,*,cancelled,**kwargs):
            if arm=='cc':
                self.assertTrue(cancelled.wait(3));cc_stopped.set()
            else:
                self.assertTrue(cc_stopped.wait(3));dsh_cancelled.append(cancelled.is_set())
            (workspace/'outputs/smoke.json').write_text('{"ok":true,"value":42}')
            return {'success':arm=='dsh','terminal_success':arm=='dsh','cancelled':cancelled.is_set()}
        with patch.object(bench,'EXPERIMENTS',self.root),patch.object(Path,'home',return_value=self.root),patch.object(bench,'cli_identity',return_value={}),patch('scripts.research_experiment_proxy.ObservingProxy',FakeProxy),patch('scripts.research_harness_trial.run_trial',fake_trial),patch('builtins.print'):
            result=bench.run_pair(target,'smoke')
        self.assertEqual(dsh_cancelled,[False])
        self.assertEqual(result['outcomes']['cc']['supervisor_cancellation_reason'],'UnknownUsageLimit')
        self.assertIsNone(result['outcomes']['dsh']['supervisor_cancellation_reason'])
        self.assertTrue(result['outcomes']['dsh']['process_success'])
        self.assertIn(('dsh','ArmFinished'),stops)

    def test_frozen_input_and_prompt_hashes_rechecked_before_credential(self):
        target=self.root/'experiment';(target/'frozen').mkdir(parents=True);(target/'prompts').mkdir()
        (target/'frozen/input.txt').write_text('frozen');(target/'prompts/probe.txt').write_text('prompt')
        manifest=dict(schema_version=bench.SCHEMA,frozen=bench.inventory(target/'frozen'),prompts=bench.inventory(target/'prompts'))
        (target/'manifest.json').write_text(json.dumps(manifest))
        with patch.object(bench,'EXPERIMENTS',self.root):
            bench.verify_experiment(target)
            (target/'frozen/input.txt').write_text('changed')
            with self.assertRaisesRegex(ValueError,'changed'):bench.verify_experiment(target)

    def test_artifact_symlinks_refused(self):
        actual=self.root/'actual';actual.write_text('private')
        link=self.root/'link';link.symlink_to(actual)
        with self.assertRaises(ValueError):bench.digest(link)

    def test_fifo_and_missing_input_fail_without_blocking(self):
        workspace=self.root/'workspace';workspace.mkdir()
        fifo=workspace/'fifo';os.mkfifo(fifo)
        with self.assertRaises(ValueError):bench.read_regular(fifo)
        self.assertEqual(bench.arm_input_status(workspace,{'fifo':'hash','absent':'hash'}),{'fifo':False,'absent':False})

    def test_output_parent_symlink_is_rejected(self):
        outside=self.root/'outside';outside.mkdir()
        (outside/'smoke.json').write_text('{"ok":true,"value":42}')
        workspace=self.root/'workspace';workspace.mkdir()
        (workspace/'outputs').symlink_to(outside,target_is_directory=True)
        result=bench.validate_artifacts(self.root,'smoke')
        self.assertFalse(result['strict_json']);self.assertTrue(result['errors'])


if __name__=='__main__':unittest.main()
