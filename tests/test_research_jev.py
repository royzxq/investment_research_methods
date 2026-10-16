"""Conditional routing, original-candidate retention and immutable audit data."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import research_jev as jev


class FakeBackend:
    def __init__(self,responses=None):
        self.calls=[];self.closed=False;self.responses=list(responses or [])
    def triage(self,items,query):
        self.calls.append((items,query))
        if self.responses:
            value=self.responses.pop(0)
            if isinstance(value,Exception):raise value
            return value
        return {'results':[{'id':x['id'],'answers':{'relevant':{'noul':0.9 if i==0 else 0.2,'verdict':'yes' if i==0 else 'no'}}} for i,x in enumerate(items)],
                'model':'fixture','usage':{'input_tokens':100,'output_tokens':2}}
    def close(self):self.closed=True


class ResearchJevTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.folder=self.root/'output/run/claude'
        self.folder.mkdir(parents=True)
        self.fake=FakeBackend()

    def setup(self,mode='auto',backend=True):
        with patch.object(jev,'backend_command',return_value=['fake'] if backend else None):
            self.pins=jev.prepare(self.folder,self.root,task_id='SH-600276',day='2026-10-13',generator='claude',mode=mode)
        self.cfg=json.loads((self.folder/'jev/config.json').read_text())
        self.service=jev.Service(self.cfg,lambda *_:self.fake)

    def manifest(self,n=8,length=1600,purpose='announcements',**extras):
        rows=[]
        for i in range(n):
            p=Path(self.cfg['materials_dir'])/f'public-{i}.txt'
            p.write_text('原文不得回传主模型 '+('披露事项'*length)[:length])
            rows.append({'id':f'A{i}','path':str(p),'sha256':jev.sha(p.read_bytes()),'start':0,'end':len(p.read_text()),
                         'public_url':'https://example.test/disclosure','title':'public candidate'})
        p=self.folder/'jev/candidates.json'
        p.write_text(json.dumps({'schema_version':jev.MANIFEST_SCHEMA,'purpose':purpose,'query':'许可及现金义务','candidates':rows,**extras},ensure_ascii=False))
        return p

    def test_auto_triggers_and_no_candidate_removed(self):
        self.setup();p=self.manifest();r=self.service.route(p)
        self.assertEqual(r['status'],'ranked');self.assertEqual(len(self.fake.calls),1)
        self.assertEqual({x['id'] for x in r['items']},{f'A{i}' for i in range(8)})
        self.assertTrue(any(x['verdict']=='no' for x in r['items']))
        self.assertNotIn('原文不得回传主模型',jev.encode(r))
        self.assertIn('原文不得回传主模型',self.fake.calls[0][0][0]['text'])
        self.assertFalse(r['research_complete']);self.assertTrue(self.fake.closed)

    def test_small_candidate_count_skips_with_reason(self):
        self.setup();r=self.service.route(self.manifest(n=2,length=7000))
        self.assertEqual(r['reason'],'candidate_count_below_threshold');self.assertEqual(self.fake.calls,[])

    def test_small_text_skips_even_many_candidates(self):
        self.setup();r=self.service.route(self.manifest(n=8,length=20))
        self.assertEqual(r['reason'],'candidate_text_below_threshold')

    def test_annual_threshold(self):
        self.setup();r=self.service.route(self.manifest(n=6,length=2200,purpose='annual_sections'))
        self.assertEqual(r['status'],'ranked')

    def test_precise_location_skips(self):
        self.setup();r=self.service.route(self.manifest(selection_complete=True))
        self.assertEqual(r['reason'],'declared_precise_location');self.assertEqual(self.fake.calls,[])

    def test_off_disables_registration_and_backend(self):
        self.setup('off');r=self.service.route(self.manifest())
        self.assertEqual(r['reason'],'disabled');self.assertEqual(jev.registration(self.folder),{})
        self.assertEqual(self.fake.calls,[])

    def test_force_runs_small_precise_batch(self):
        self.setup('force');r=self.service.route(self.manifest(n=1,length=20,selection_complete=True))
        self.assertEqual(r['reason'],'explicit_force');self.assertEqual(len(self.fake.calls),1)

    def test_all_backend_errors_keep_original_order_and_unknown_cost(self):
        self.setup();self.fake.responses=[{'error':{'kind':'authentication','retryable':True,'message':'private-secret'}}]
        r=self.service.route(self.manifest())
        self.assertEqual(r['status'],'fallback');self.assertEqual(len(self.fake.calls),1)
        self.assertEqual([x['id'] for x in r['items']],[f'A{i}' for i in range(8)])
        self.assertNotIn('private-secret',(self.folder/'jev/calls.jsonl').read_text())
        saved=json.loads(Path(r['result_path']).read_text());self.assertIsNone(saved['cost'])

    def test_partial_retry_only_failed_item_once(self):
        self.setup('force')
        self.fake.responses=[{'results':[{'id':'A0','answers':{'relevant':{'noul':0.8,'verdict':'yes'}}},
            {'id':'A1','error':{'kind':'connection','retryable':True}}],'usage':{'input_tokens':10,'output_tokens':1},'model':'fixture'},
            {'results':[{'id':'A1','answers':{'relevant':{'noul':0.1,'verdict':'no'}}}],'usage':{'input_tokens':5,'output_tokens':1},'model':'fixture'}]
        r=self.service.route(self.manifest(n=2))
        self.assertEqual(r['status'],'ranked');self.assertEqual(len(self.fake.calls),2)
        self.assertEqual([x['id'] for x in self.fake.calls[1][0]],['A1'])

    def test_permanent_failed_item_does_not_retry(self):
        self.setup('force');self.fake.responses=[{'results':[{'id':'A0','error':{'kind':'invalid_request','retryable':False}}]}]
        r=self.service.route(self.manifest(n=1));self.assertEqual(r['status'],'fallback')
        self.assertEqual(len(self.fake.calls),1)

    def test_transient_top_error_retries_at_most_once(self):
        self.setup();self.fake.responses=[{'error':{'kind':'connection','retryable':True}}]*2
        r=self.service.route(self.manifest());self.assertEqual(len(self.fake.calls),2);self.assertEqual(r['status'],'fallback')

    def test_timeout_falls_back_and_failed_usage_unknown(self):
        self.setup();self.fake.responses=[TimeoutError()]
        r=self.service.route(self.manifest());saved=json.loads(Path(r['result_path']).read_text())
        self.assertEqual(saved['status'],'fallback');self.assertEqual(saved['usage'],[])
        self.assertIn('failed_requests_unknown',saved['usage_scope'])

    def test_cache_reuse_does_not_repeat_api_on_pagination_or_formatting(self):
        self.setup();p=self.manifest();r=self.service.route(p,limit=2)
        self.assertEqual(r['next_offset'],2)
        data=json.loads(p.read_text());p.write_text(json.dumps(data,indent=4,ensure_ascii=False))
        again=self.service.route(p,offset=2,limit=2)
        self.assertEqual(len(self.fake.calls),1);self.assertEqual(again['result_path'],r['result_path'])

    def test_source_mutation_refuses_cached_result(self):
        self.setup();p=self.manifest();self.service.route(p)
        row=json.loads(p.read_text())['candidates'][0];Path(row['path']).write_text('changed')
        with self.assertRaises(ValueError):self.service.route(p)
        self.assertEqual(len(self.fake.calls),1)

    def test_scope_and_source_url_checked_before_sending(self):
        self.setup();p=self.manifest();data=json.loads(p.read_text())
        outside=self.root/'output/private.txt';outside.write_text('do not disclose')
        data['candidates'][0]['path']=str(outside);p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):self.service.route(p)
        self.assertEqual(self.fake.calls,[])

    def test_source_symlink_escape_refused(self):
        self.setup();p=self.manifest();data=json.loads(p.read_text());src=Path(data['candidates'][0]['path'])
        src.unlink();other=self.root/'output/private.txt';other.write_text('private');src.symlink_to(other)
        with self.assertRaises(ValueError):self.service.route(p)

    def test_missing_backend_reports_reason_and_fallback(self):
        self.setup(backend=False);r=self.service.route(self.manifest())
        self.assertEqual(r['reason'],'backend_unavailable');self.assertTrue(r['fallback_required'])
        summary=jev.summarize(self.folder);self.assertIn('backend_unavailable',summary['decision_reasons'])

    def test_no_candidate_submission_is_not_claimed_not_needed(self):
        self.setup();summary=jev.summarize(self.folder)
        self.assertEqual(summary['status'],'not_requested');self.assertEqual(summary['reason'],'no_candidate_batch_submitted')

    def test_registered_config_uses_wrapper_not_unlogged_raw_tools(self):
        self.setup();server=jev.registration(self.folder)
        self.assertEqual(set(server),{'jev_research'})
        self.assertIn('research_jev.py',server['jev_research']['args'][0])

    def test_invalid_result_ids_preserve_all_candidates(self):
        self.setup();self.fake.responses=[{'results':[{'id':'other','answers':{'relevant':{'noul':1}}}]}]
        r=self.service.route(self.manifest());self.assertEqual(r['status'],'fallback');self.assertEqual(len(r['items']),8)

    def test_batch_limit_never_silently_truncates(self):
        self.setup();r=self.service.route(self.manifest(n=51,length=250))
        self.assertEqual(r['candidate_count'],51);self.assertTrue(r['fallback_required'])
        self.assertEqual(self.fake.calls,[]);self.assertIsNotNone(r['next_offset'])

    def test_response_budget_paginates_without_losing_entries(self):
        self.setup();self.cfg['max_response_bytes']=1800
        service=jev.Service(self.cfg,lambda *_:self.fake);p=self.manifest()
        r=service.route(p,limit=50)
        self.assertLessEqual(len(jev.encode(r).encode())+600,1800);self.assertIsNotNone(r['next_offset'])

    def test_summary_reports_route_and_partial_failures(self):
        self.setup();self.fake.responses=[{'error':{'kind':'authentication','retryable':False}}]
        self.service.route(self.manifest());s=jev.summarize(self.folder)
        self.assertEqual(s['status'],'invoked');self.assertEqual(s['fallback_batches'],1);self.assertEqual(s['usage_records'],[])

    def test_backend_start_failure_is_not_a_tool_submission(self):
        self.setup()
        def unavailable(*_):raise OSError('not executable')
        service=jev.Service(self.cfg,unavailable)
        result=service.route(self.manifest());summary=jev.summarize(self.folder)
        self.assertEqual(result['status'],'fallback')
        self.assertEqual(summary['status'],'fallback')
        self.assertEqual(summary['backend_tool_submissions'],0)
        self.assertEqual(summary['submitted_candidate_requests'],None)

    def test_summary_preview_does_not_freeze_final_journal(self):
        self.setup()
        self.assertEqual(jev.summarize(self.folder,persist=False)['status'],'not_requested')
        self.assertFalse((self.folder/'jev/summary.json').exists())
        self.service.route(self.manifest())
        self.assertEqual(jev.summarize(self.folder)['status'],'invoked')

    def test_invalid_submission_is_not_reported_as_never_requested(self):
        self.setup();p=self.manifest(purpose='valuation')
        with self.assertRaises(ValueError):self.service.route(p)
        summary=jev.summarize(self.folder)
        self.assertEqual(summary['status'],'fallback')
        self.assertEqual(summary['route_requests'],1)
        self.assertEqual(summary['failed_route_requests'],1)
        self.assertEqual(summary['backend_tool_submissions'],0)

    def test_paged_response_cost_is_recorded_without_repeat_backend(self):
        self.setup();p=self.manifest()
        first=self.service.route(p,limit=2)
        second=self.service.route(p,offset=first['next_offset'],limit=2)
        summary=jev.summarize(self.folder)
        self.assertEqual(summary['route_requests'],2)
        self.assertEqual(summary['backend_tool_submissions'],1)
        self.assertEqual(summary['submitted_candidate_requests'],8)
        self.assertEqual(summary['cache_returns'],1)
        self.assertEqual(summary['tool_response_bytes'],len(jev.encode(first).encode())+len(jev.encode(second).encode()))

    def test_manifest_unsupported_purpose_refused(self):
        self.setup();p=self.manifest(purpose='valuation')
        with self.assertRaises(ValueError):self.service.route(p)
        self.assertEqual(self.fake.calls,[])

    def test_empty_candidates_logged(self):
        self.setup();r=self.service.route(self.manifest(n=0))
        self.assertEqual(r['reason'],'no_candidates')

    def test_real_stdio_transport_sends_large_input_without_partial_write(self):
        path=self.root/'fake_mcp.py'
        path.write_text('''import json,sys
for line in sys.stdin:
 r=json.loads(line);m=r['method']
 if m.startswith('notifications/'):continue
 if m=='initialize':v={'protocolVersion':'2024-11-05','capabilities':{},'serverInfo':{'name':'fake','version':'1'}}
 elif m=='tools/list':v={'tools':[{'name':'jev_triage'}]}
 else:
  items=r['params']['arguments']['items']
  v={'structuredContent':{'received_characters':len(items[0]['text']),'results':[]}}
 print(json.dumps({'jsonrpc':'2.0','id':r['id'],'result':v}),flush=True)
''')
        client=jev.Backend([sys.executable,str(path)],timeout=2)
        try:
            result=client.triage([{'id':'large','text':'正文'*70000}],'query')
            self.assertEqual(result['received_characters'],140000)
        finally:client.close()
        self.assertIsNotNone(client.proc.returncode)

    def test_real_stdio_wrong_tool_cleans_up_child(self):
        path=self.root/'wrong_mcp.py'
        path.write_text('''import json,sys
for l in sys.stdin:
 r=json.loads(l)
 if r['method'].startswith('notifications/'):continue
 v={'tools':[]} if r['method']=='tools/list' else {}
 print(json.dumps({'jsonrpc':'2.0','id':r['id'],'result':v}),flush=True)
''')
        with self.assertRaisesRegex(ValueError,'not advertised'):
            jev.Backend([sys.executable,str(path)],timeout=1)
