import json
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from zoneinfo import ZoneInfo
import unittest

from scripts.research_scheduler import new_state, apply_admission, pending_admissions, merge_candidates

NOW = datetime(2026, 11, 3, 5, tzinfo=ZoneInfo('Asia/Shanghai'))


class AdmissionTests(unittest.TestCase):
    def setup_queue(self, root, *, sources=None, priority=3, status='pending'):
        task = 'SH-600001'
        path = root / 'requests/batch/request.json'; path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'tasks': [dict(task_id=task, sources=sources or ['candidate_review'])]}))
        e = dict(task_id=task, status=status, request=str(path), event_key='a'*64, batch_id='b'*32,
                 request_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), valuation_date='2026-11-03', created_at='2026-11-03T04:30:00+08:00',
                 priority=priority, first_seen='2026-10-30T05:00:00+08:00')
        state=new_state();state['entries'][task]=e
        row=dict(task_id=task, original_sources=['candidate_review'], effective_sources=[],
                 original_event_key='a'*64, decisions=[dict(source='candidate_review', disposition='waiting',
                    reason='等待披露', valid_until='2026-11-10', reopen_when='下一公告', review_sha256='d'*64)])
        doc=dict(schema_version='research-admission/v1', date='2026-11-03',
                 observed_at='2026-11-03T04:34:00+08:00',
                 created_at='2026-11-03T04:35:00+08:00', listings=[row], warnings=[])
        p=root/'admission/latest.json';p.parent.mkdir();p.write_text(json.dumps(doc))
        return state,e,doc,p

    def test_wait_survives_rescan_without_completing_or_resetting_age(self):
        with TemporaryDirectory() as d:
            root=Path(d);s,e,doc,p=self.setup_queue(root)
            first=e['first_seen']; record=dict(e);record.pop('status');record.pop('first_seen')
            apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[])
            merge_candidates(s,[record],NOW)
            apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[])
            self.assertEqual(s['entries'][e['task_id']]['first_seen'],first)
            self.assertFalse(s['completed_events']);self.assertFalse(s['days'])
            self.assertEqual(s['entries'][e['task_id']]['status'],'pending')

    def test_priority_one_active_and_newer_requests_are_protected(self):
        for mode in ('stale','active','newer','other_source','between_observation_and_publish'):
            with self.subTest(mode=mode), TemporaryDirectory() as d:
                root=Path(d);s,e,doc,p=self.setup_queue(root)
                if mode=='stale':e['priority']=1
                if mode=='active':e['status']='running'
                if mode=='newer':e['created_at']='2026-11-03T04:36:00+08:00'
                if mode=='between_observation_and_publish':e['created_at']='2026-11-03T04:34:30+08:00'
                if mode=='other_source':
                    Path(e['request']).write_text(json.dumps({'tasks':[dict(task_id=e['task_id'],sources=['earnings_disclosure'])]}))
                apply_admission(s,root,NOW)
                self.assertNotIn('admission',e)

    def test_expired_missing_corrupt_snapshots_do_not_suppress(self):
        for mode in ('expired','missing','corrupt','future'):
            with self.subTest(mode=mode), TemporaryDirectory() as d:
                root=Path(d);s,e,doc,p=self.setup_queue(root)
                if mode=='expired':doc['date']='2026-11-02'
                if mode=='future':doc['created_at']='2026-11-03T06:00:00+08:00'
                p.write_text(json.dumps(doc))
                if mode=='corrupt':p.write_text('{bad')
                if mode=='missing':p.unlink()
                apply_admission(s,root,NOW)
                self.assertEqual(pending_admissions(s,NOW),[e])

    def test_partial_source_filter_requires_a_fresh_pack_with_effective_sources(self):
        with TemporaryDirectory() as d:
            root=Path(d);s,e,doc,p=self.setup_queue(root, sources=['candidate_review','earnings_disclosure'])
            doc['listings'][0]['original_sources'].append('earnings_disclosure')
            doc['listings'][0]['effective_sources']=['earnings_disclosure']
            p.write_text(json.dumps(doc));apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[])
            self.assertTrue(e['admission']['requires_fresh_input'])
            e['created_at']='2026-11-03T04:36:00+08:00'
            Path(e['request']).write_text(json.dumps({'tasks':[dict(task_id=e['task_id'],sources=['earnings_disclosure'])]}))
            e['request_sha256']=hashlib.sha256(Path(e['request']).read_bytes()).hexdigest()
            apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[e])

    def test_historical_disposition_needs_proof_for_each_source(self):
        with TemporaryDirectory() as d:
            root=Path(d);s,e,doc,p=self.setup_queue(root,sources=['candidate_review','sell_agent'])
            row=doc['listings'][0];row['original_sources'].append('sell_agent')
            row['original_event_key']='e'*64
            old=dict(event_key=e['event_key'],request_sha256=e['request_sha256'])
            row['decisions'][0]['supersedes']=[old]
            row['decisions'].append(dict(row['decisions'][0],source='sell_agent',supersedes=[]))
            p.write_text(json.dumps(doc));apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[e])
            row['decisions'][1]['supersedes']=[old]
            p.write_text(json.dumps(doc));apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[])

    def test_handled_event_new_facts_get_new_waiting_time(self):
        with TemporaryDirectory() as d:
            root=Path(d);s,e,doc,p=self.setup_queue(root)
            doc['listings'][0]['decisions'][0]['disposition']='handled'
            p.write_text(json.dumps(doc));apply_admission(s,root,NOW)
            record={k:v for k,v in e.items() if k not in {'status','first_seen','admission'}}
            old=dict(record)
            record.update(event_key='f'*64,created_at=NOW.isoformat())
            merge_candidates(s,[old,record],NOW)
            self.assertEqual(s['entries'][e['task_id']]['first_seen'],NOW.isoformat())

    def test_disposition_expires_on_expiry_day(self):
        with TemporaryDirectory() as d:
            root=Path(d);s,e,doc,p=self.setup_queue(root)
            doc['listings'][0]['decisions'][0]['valid_until']='2026-11-03'
            p.write_text(json.dumps(doc));apply_admission(s,root,NOW)
            self.assertEqual(pending_admissions(s,NOW),[e])
