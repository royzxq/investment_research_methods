"""Restore a completed staged delivery without relaunching or rewriting history."""
import errno
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
import test_research_runner as fixture
import test_research_dsh as dsh_fixture
from scripts import research_runner as runner, research_recovery as recovery
from scripts import research_runtime as runtime, research_coze as coze


class PublicationRestoreTests(unittest.TestCase):
    def setUp(self):
        f=self.f=fixture.ResearchRunnerTests('runTest');f.setUp();self.addCleanup(f.doCleanups)
        for name in ('root','methods','exchange','pack','request_path','fake'):
            setattr(f,name,getattr(f,name).resolve())
        f.request.update(schema_version='stock-research-request/v2',generators=['codex','dsh'])
        f.request['tasks'][0]['data_pack_meta']['research_trigger']={'event_key':'original-event'}
        f.write_request()
        config=runtime.load_config();profile=runtime.default_profile('dsh')
        config['profiles'].append(profile);config['active']['dsh']=profile['profile_id']
        original=runner.write_new
        def collide(path,raw):
            if path.as_posix().endswith('/runner/research-validation.json'):
                agent=path.parent.parent/'research-validation.json'
                agent.write_text('{"agent_self_check":true}')
                raise FileExistsError(errno.EEXIST,'File exists',str(agent))
            original(path,raw)
        # Reproduce an already-frozen historical parallel batch: Codex publication
        # failed while the other seat independently completed before sequencing.
        snapshot_writer=runner.write_framework_snapshot
        def legacy_snapshot(*args,**kwargs):
            kwargs['evidence_workflow']=None
            return snapshot_writer(*args,**kwargs)
        with patch.object(runner,'write_new',side_effect=collide), \
                patch.object(runner,'write_framework_snapshot',side_effect=legacy_snapshot):
            result=runner.run_batch(f.request_path,f.methods,generator='codex',cli=str(f.fake),timeout=5,runtime_config=config)
        self.run=result.parent;self.folder=self.run/'execution/SH-600066/codex'
        self.assertEqual(recovery.read(result)['results'][0]['status'],'failed')
        dsh=f.root/'fake-dsh';dsh.write_text(dsh_fixture.build_fake_dsh_cli());dsh.chmod(0o700)
        with patch.dict(os.environ,{'DEEPSEEK_API_KEY':'offline-fixture'}):
            other=runner.run_batch(f.request_path,f.methods,generator='dsh',cli=str(dsh),timeout=5,runtime_config=config)
        self.assertEqual(recovery.read(other)['results'][0]['status'],'completed')
        native=self.folder/'queue-result.json';runner.write_new(native,result.read_bytes())
        self.base=f.methods/'output/research_queue/sealed'/('a'*32+'-SH-600066.json')
        seal=dict(schema_version='research-sealed/v2',task_id='SH-600066',batch_id='a'*32,
            event_key='original-event',request=str(f.request_path),request_sha256=f.sha(f.request_path),
            budget_date=f.request['valuation_date'],results=[dict(generator=g,
                manifest=p.relative_to(f.methods).as_posix(),manifest_sha256=f.sha(p),actual_model=None)
                for g,p in [('codex',native),('dsh',other)]])
        runner.write_new(self.base,runner.encode(seal))
        self.protected={p:p.read_bytes() for p in f.methods.rglob('*') if p.is_file()}

    def restore(self):
        return recovery.restore_publication(self.base,self.f.exchange,self.f.methods,
            authorization='Human requested restore of exact staged Codex bytes, without new research')

    def test_restore_preserves_history_existing_opinion_and_native_bytes_then_replays(self):
        with patch.object(runner,'run_provider',side_effect=AssertionError('no research launch')):
            wrapper=self.restore()
            self.assertEqual(self.restore(),wrapper)
        base,private,value=recovery.load_supplement(wrapper,self.f.methods,self.f.exchange)
        self.assertEqual(base,self.base)
        before=recovery.read(base);after=recovery.read(private)
        self.assertEqual(after['results'][1],before['results'][1])
        self.assertEqual(value['results'],before['results'])
        self.assertEqual(value['recovered_generators'],['codex'])
        context=coze.load_base(wrapper,self.f.methods,self.f.exchange)
        self.assertEqual(set(context['documents']),{'codex','dsh'})
        self.assertEqual({p:p.read_bytes() for p in self.protected},self.protected)
        candidate=recovery.read(self.folder/'candidate-result.json')['results'][0]
        for key in ('report','price_map'):
            self.assertEqual(recovery.sha(self.f.methods/candidate[key]['path']),candidate[key]['sha256'])
        all_bytes={p:p.read_bytes() for p in self.f.methods.rglob('*') if p.is_file()}
        self.restore()
        self.assertEqual({p:p.read_bytes() for p in all_bytes},all_bytes)
        # A sealed historical acceptance must survive later OS PID reuse.
        with patch.object(runner,'group_alive',return_value=True):
            self.assertEqual(self.restore(),wrapper)

    def test_staged_tamper_fails_before_publication(self):
        candidate=recovery.read(self.folder/'candidate-result.json')['results'][0]
        staged=runner.staging_root(self.f.methods,self.f.request,self.f.request['tasks'][0],'codex')
        report=staged/candidate['report']['path'];report.write_bytes(report.read_bytes()+b'\ntampered')
        with self.assertRaisesRegex(ValueError,'hash|sha256'):
            self.restore()
        self.assertFalse((self.f.methods/candidate['report']['path']).exists())

    def test_changed_native_runtime_or_occupied_target_is_rejected(self):
        runtime_path=self.folder/'jev-runtime-prompt.txt';original=runtime_path.read_bytes()
        runtime_path.write_bytes(original+b'changed')
        with self.assertRaisesRegex(ValueError,'execution inputs'):
            self.restore()
        runtime_path.write_bytes(original)
        candidate=recovery.read(self.folder/'candidate-result.json')['results'][0]
        target=self.f.methods/candidate['report']['path'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text('other existing report')
        with self.assertRaisesRegex(ValueError,'hash|sha256'):
            self.restore()
        self.assertEqual(target.read_text(),'other existing report')

    def test_live_or_nonzero_original_cannot_be_restored(self):
        with patch.object(runner,'group_alive',return_value=True),self.assertRaisesRegex(ValueError,'stopped'):
            self.restore()
        process=self.folder/'process.json';value=recovery.read(process);value['exit_code']=3
        process.write_bytes(runner.encode(value))
        with self.assertRaisesRegex(ValueError,'exit-zero'):
            self.restore()
