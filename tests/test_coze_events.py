"""Durable event boundaries; all clients are offline fakes."""
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
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
from scripts import coze_events as events, coze_cli as cli, research_scheduler as scheduler


class EventsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.time=datetime(2026,11,3,tzinfo=timezone.utc)
        self.cfg=dict(schema_version='coze-events-config/v1',enabled=True,dispatch_enabled=False,
                      not_before=self.time.isoformat(),recovery_interval_seconds=3600)
        cli.atomic(self.root/'config/coze_events.json',self.cfg)
        self.request=self.root/'request.json';cli.atomic(self.request,dict(created_at=self.time.isoformat()))
        self.seal=self.root/'output/research_queue/sealed/batch-SH-600900.json'
        cli.atomic(self.seal,dict(schema_version='research-sealed/v2',task_id='SH-600900',request=str(self.request),
                                 request_sha256=cli.digest(self.request.read_bytes())))

    def test_disabled_has_no_outbox_and_does_not_scan(self):
        self.cfg['enabled']=False;cli.atomic(self.root/'config/coze_events.json',self.cfg)
        self.assertIsNone(events.enqueue(self.seal,self.root))
        self.assertTrue(events.reconcile(self.root)['disabled'])
        self.assertFalse(events.outbox(self.root).exists())

    def test_activation_does_not_backfill_prior_requests(self):
        self.cfg['not_before']=(self.time+timedelta(seconds=1)).isoformat()
        cli.atomic(self.root/'config/coze_events.json',self.cfg)
        self.assertIsNone(events.enqueue(self.seal,self.root))
        self.assertFalse(events.outbox(self.root).exists())

    def test_activation_requires_explicit_cutoff(self):
        self.cfg['not_before']=None;cli.atomic(self.root/'config/coze_events.json',self.cfg)
        with self.assertRaises(ValueError):events.enqueue(self.seal,self.root)

    def test_repeated_seal_notification_is_idempotent(self):
        key=events.enqueue(self.seal,self.root)
        self.assertEqual(events.enqueue(self.seal,self.root),key)
        self.assertEqual(len(list((events.outbox(self.root)/'events').glob('*'))),1)

    def test_reconcile_repairs_seal_to_event_and_event_to_marker_crash_gaps(self):
        self.assertEqual(events.reconcile(self.root)['repaired'],1)
        root=events.outbox(self.root);marker=next((root/'pending').iterdir());marker.unlink()
        events.reconcile(self.root)
        self.assertTrue(marker.exists())
        cli.atomic(root/'jobs'/f'{marker.name}.json',dict(phase='awaiting_public_review'))
        marker.unlink();events.reconcile(self.root)
        self.assertFalse(marker.exists())
        cli.atomic(root/'jobs'/f'{marker.name}.json',dict(phase='ready'))
        events.reconcile(self.root);self.assertTrue(marker.exists())

    def test_supplement_does_not_recurse(self):
        data=cli.read(self.seal);data['schema_version']='research-sealed-coze/v2';cli.atomic(self.seal,data)
        self.assertIsNone(events.enqueue(self.seal,self.root))

    def test_recovery_seal_emits_the_same_kind_of_event(self):
        data=cli.read(self.seal);data['schema_version']='research-sealed-recovery/v1';cli.atomic(self.seal,data)
        self.assertIsNotNone(events.enqueue(self.seal,self.root))

    def test_hash_changed_request_is_rejected(self):
        cli.atomic(self.request,dict(created_at=self.time.isoformat(),changed=True))
        with self.assertRaises(ValueError):events.enqueue(self.seal,self.root)

    def test_bad_historical_seal_cannot_block_recovery_of_new_events(self):
        (self.seal.parent/'000-bad.json').write_text('{broken')
        result=events.reconcile(self.root)
        self.assertEqual(result['repaired'],1);self.assertEqual(len(result['errors']),1)

    def test_unsent_superseded_job_is_closed_without_dispatch(self):
        key=self.reviewed_job();self.cfg['dispatch_enabled']=True;cli.atomic(self.root/'config/coze_events.json',self.cfg)
        class Fake:
            def get(self,rid):return dict(request_id=rid,status='prepared')
            def submit(self,rid,*,allow_submit,claim_guard):
                with claim_guard():raise AssertionError('stale request sent')
        with patch.object(events.transport,'load_config',return_value={'enabled':True}),\
             patch.object(events.adapter,'current_cli_intent',side_effect=ValueError('CLI intent is not the latest eligible round')):
            self.assertEqual(events.step(key,self.root,self.root/'exchange',client_factory=lambda cfg:Fake())['phase'],'superseded')

    def test_event_hook_failure_cannot_fail_base_seal(self):
        entry=dict(task_id='SH-600900',batch_id='batch',event_key='e',request=str(self.request),
                   request_sha256=cli.digest(self.request.read_bytes()),budget_date='2026-11-03')
        self.seal.unlink()
        with patch.object(events,'enqueue',side_effect=OSError('outbox unavailable')):
            scheduler.seal_entry(entry,self.seal.parent.parent,dict(schema_version='stock-research-request/v2',generators=['codex','dsh']),
                                 {'codex':('completed',{}),'dsh':('completed',{})})
        self.assertTrue(self.seal.exists());self.assertEqual(entry['status'],'completed')

    def test_event_qualification_runs_after_seal_off_provider_path(self):
        key=events.enqueue(self.seal,self.root)
        with patch.object(events.adapter,'load_base',return_value={}),patch.object(events.adapter,'eligible',return_value=False):
            self.assertEqual(events.step(key,self.root,self.root/'exchange')['phase'],'ineligible')

    def reviewed_job(self,phase='ready'):
        key=events.enqueue(self.seal,self.root)
        intent=self.root/'intent.json';cli.atomic(intent,dict(request_id='rid',pack_sha256='pack',base_sha256=key,status='pending'))
        cli.atomic(events.outbox(self.root)/'jobs'/f'{key}.json',dict(key=key,phase=phase,
                   public_input_reviewed=True,intent=str(intent),pack_sha256='pack',research_event_at=self.time.isoformat()))
        return key

    def test_beijing_midnight_boundary_and_utc_equivalent(self):
        cutoff='2026-11-03T00:00:00+08:00'
        for stamp in ('2026-11-03T00:00:00+08:00','2026-11-02T16:00:00+00:00'):
            context=dict(request={'created_at':stamp},entries={'codex':{'completed_at':stamp},'dsh':{'completed_at':stamp}})
            self.assertEqual(events.research_event_time(context,cutoff),'2026-11-02T16:00:00+00:00')
        context=dict(request={'created_at':'2026-11-03T00:00:00+08:00'},
                     entries={'codex':{'completed_at':'2026-11-02T23:59:59+08:00'}})
        with self.assertRaisesRegex(ValueError,'completion predates'):
            events.research_event_time(context,cutoff)

    def test_old_batch_finishing_after_cutoff_is_still_excluded(self):
        context=dict(request={'created_at':'2026-11-02T23:59:59+08:00'},
                     entries={'dsh':{'completed_at':'2026-11-03T05:00:00+08:00'}})
        with self.assertRaisesRegex(ValueError,'batch predates'):
            events.research_event_time(context,'2026-11-03T00:00:00+08:00')

    def test_old_queued_job_cannot_resume_after_cutoff_moves_forward(self):
        key=self.reviewed_job('watching')
        self.cfg['not_before']=(self.time+timedelta(days=1)).isoformat()
        cli.atomic(self.root/'config/coze_events.json',self.cfg)
        with self.assertRaisesRegex(ValueError,'event not in active epoch'):
            events.step(key,self.root,self.root/'exchange')

    def test_old_recovery_resealed_now_is_not_repaired_into_new_epoch(self):
        import os
        self.cfg['not_before']=(self.time+timedelta(days=1)).isoformat()
        cli.atomic(self.root/'config/coze_events.json',self.cfg)
        data=cli.read(self.seal);data['schema_version']='research-sealed-recovery/v1';cli.atomic(self.seal,data)
        os.utime(self.seal,None)
        self.assertIsNone(events.enqueue(self.seal,self.root))
        self.assertEqual(events.reconcile(self.root)['repaired'],0)

    def test_approval_is_explicit_and_cannot_reopen_terminal(self):
        key=self.reviewed_job('awaiting_public_review')
        with self.assertRaises(ValueError):events.approve(key,self.root)
        self.assertEqual(events.approve(key,self.root,public_input_reviewed=True)['phase'],'ready')
        with self.assertRaises(ValueError):events.approve(key,self.root,public_input_reviewed=True)
        with self.assertRaises(ValueError):events.approve('../escape',self.root,public_input_reviewed=True)

    def test_dispatch_switches_block_all_client_calls(self):
        key=self.reviewed_job()
        with patch.object(events.transport,'load_config',return_value={'enabled':False}):
            def forbidden(cfg):self.fail('client created while disabled')
            self.assertEqual(events.step(key,self.root,self.root/'exchange',client_factory=forbidden)['phase'],'blocked_dispatch')

    def test_unknown_send_only_collects_and_never_submits_again(self):
        key=self.reviewed_job();self.cfg['dispatch_enabled']=True;cli.atomic(self.root/'config/coze_events.json',self.cfg)
        owner=self
        class Fake:
            def get(self,rid):return dict(request_id=rid,status='send_unknown',sending_at=owner.time.isoformat(),history=[])
            def submit(self,*a,**kw):owner.fail('unknown send resubmitted')
            def collect(self,rid):return dict(self.get(rid),status='partial')
        with patch.object(events.transport,'load_config',return_value={'enabled':True}),\
             patch.object(events.adapter,'current_cli_intent',side_effect=AssertionError('sent requests must still collect after supersession')):
            result=events.step(key,self.root,self.root/'exchange',client_factory=lambda cfg:Fake())
        self.assertEqual(result['phase'],'watching')

    def test_cross_deadline_pending_remains_watching_until_post_deadline_check(self):
        key=self.reviewed_job('watching');self.cfg['dispatch_enabled']=True;cli.atomic(self.root/'config/coze_events.json',self.cfg)
        owner=self
        class Fake:
            def get(self,rid):return dict(request_id=rid,status='pending',sending_at=owner.time.isoformat(),history=[])
            def collect(self,rid):return dict(self.get(rid),history_started_at=(owner.time+timedelta(seconds=899)).isoformat(),replies=[])
        with patch.object(events.transport,'load_config',return_value={'enabled':True}):
            self.assertEqual(events.step(key,self.root,self.root/'exchange',client_factory=lambda cfg:Fake())['phase'],'watching')

    def test_launchd_plan_is_event_primary_and_hourly_repair_only(self):
        worker,recovery=events.launchd_plan(self.root)
        self.assertIn('QueueDirectories',worker);self.assertNotIn('StartInterval',worker)
        self.assertEqual(recovery['StartInterval'],3600)
        self.assertFalse((self.root/'Library').exists())

    def test_launchd_plan_pins_only_required_nonsecret_runtime_environment(self):
        with patch.dict(os.environ, {'PATH':'/usr/bin:/bin', 'COZE_TEST_SECRET':'never-copy'}, clear=True):
            plans=events.launchd_plan(self.root)
        for plan in plans:
            saved=plistlib.loads(plistlib.dumps(plan))
            self.assertEqual(saved['EnvironmentVariables'], {
                'PATH':'/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'})
            self.assertTrue(Path(saved['ProgramArguments'][0]).is_absolute())
            self.assertEqual(saved['ProgramArguments'][0],sys.executable)
        with self.assertRaisesRegex(ValueError,'absolute'):
            events.launchd_plan(self.root,python='python3')

    def test_launchd_minimal_environment_runs_fake_node_cli_via_pinned_python(self):
        worker,_=events.launchd_plan(self.root)
        environment=worker['EnvironmentVariables']
        # Static environment validation above is mandatory even on CI hosts
        # without Node. On this deployment host, exercise the actual shebang
        # chain using a harmless local JS fixture, never the real Coze CLI.
        if shutil.which('node',path=environment['PATH']) is None:
            self.skipTest('Node is not installed in the planned runtime PATH')
        fake=self.root/'fake-coze'
        fake.write_text('#!/usr/bin/env node\nprocess.stdout.write("offline-launchd-ok");\n')
        fake.chmod(0o700)
        result=subprocess.run([worker['ProgramArguments'][0],'-I','-c',
            'import subprocess,sys; subprocess.run([sys.argv[1]],check=True)',str(fake)],
            env=environment,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'offline-launchd-ok')

    def test_busy_unsent_job_does_not_block_other_active_collection(self):
        root=events.outbox(self.root)
        first, second='a'*64, 'b'*64
        for key in (first,second):cli.immutable(root/'pending'/key,b'event\n')
        visited=[]
        def step(key,*args):
            visited.append(key)
            if key==first:raise BlockingIOError('scheduler owns queue.lock')
            return dict(phase='watching')
        with patch.object(events,'step',side_effect=step):
            events.drain(self.root,self.root/'exchange',once=True)
        self.assertEqual(visited,[first,second])
        self.assertTrue((root/'pending'/first).exists())
        self.assertTrue((root/'pending'/second).exists())

    def test_reconstructed_ready_job_retains_wakeup_until_submission_step(self):
        root=events.outbox(self.root);key='a'*64
        cli.immutable(root/'pending'/key,b'event\n')
        with patch.object(events,'step',return_value=dict(phase='ready')):
            events.drain(self.root,self.root/'exchange',once=True)
        self.assertTrue((root/'pending'/key).exists())


if __name__=='__main__':unittest.main()
