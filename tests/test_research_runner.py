"""Input delivery and CLI/manifest failures exercised without research APIs."""
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_runner import prepare_request, run_batch, stock_lock, publish_pair, group_alive
import scripts.research_runner as runner
from scripts import investment_maintenance as maintenance


FAKE_CLI = r'''#!/usr/bin/env python3
import hashlib,json,os,re,sys,time,subprocess,signal
from pathlib import Path
args=sys.argv[1:]
if '--help' in args:
 if os.environ.get('MOCK_CODEX_HELP')=='error': sys.exit(2)
 if os.environ.get('MOCK_CODEX_HELP')=='legacy':
  print('  -a, --ask-for-approval <POLICY>\n  --json\n  --ephemeral')
 elif 'exec' in args:
  print('  --approve-for-me\n  --ephemeral\n  --json\n  --color <COLOR>\n  --output-schema <FILE>\n  -o, --output-last-message <FILE>\n  -C, --cd <DIR>\n  -c, --config <key=value>')
 else:
  print('  --no-daemon')
 sys.exit(0)
payload=sys.stdin.buffer.read()
Path(os.environ['MOCK_INPUT']).write_bytes(payload)
mode=os.environ.get('MOCK_MODE','success')
if mode=='timeout':
 time.sleep(10)
if mode=='descendant':
 child=subprocess.Popen([sys.executable,'-c',"import os,signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,signal.SIG_IGN);Path(os.environ['MOCK_DESCENDANT_PID']).write_text(str(os.getpid()));time.sleep(60)"])
 time.sleep(60)
if mode=='nonzero':
 sys.exit(3)
if mode=='partial_failure' and b'600900.SH' in payload:
 sys.exit(3)
if mode=='api_error':
 print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'result':'offline failure'}))
 sys.exit(0)
args=sys.argv[1:]
schema=json.loads(args[args.index('--json-schema')+1]) if '--json-schema' in args else json.loads(Path(args[args.index('--output-schema')+1]).read_text())
get=lambda key:schema['properties'][key]['enum'][0]
code=get('code'); generator=get('generator'); day=get('valuation_date'); batch=get('batch_id'); sha=get('input_pack_sha256')
ticker,market=code.split('.')
report=get('report_path');price=get('price_map_path')
staged=Path(re.search(r'^本次交付暂存根：(.*)$',payload.decode(),re.M)[1])
report_file=staged/report
if mode=='exact_delivery_paths':
 delivery=args[args.index('--append-system-prompt')+1] if '--append-system-prompt' in args else payload.decode()
 report_match=re.search(r'^本次暂存报告绝对路径：(.*)$',delivery,re.M)
 price_match=re.search(r'^本次暂存价格JSON绝对路径：(.*)$',delivery,re.M)
 report_file=Path(report_match[1]) if report_match else staged/Path(report).name
 price_file=Path(price_match[1]) if price_match else staged/Path(price).name
report_file.parent.mkdir(parents=True,exist_ok=True)
frames=';'.join(json.loads(re.search(r'^框架指纹：(.*)。$',payload.decode(),re.M)[1]).values())
if mode=='framework_changes': Path('framework/investment_framework.md').write_text('changed during CLI run')
if mode=='snapshot_changes':
 snapshot=Path(re.search(r'^本批方法快照目录：(.*)$',payload.decode(),re.M)[1])/'investment_framework.md'
 snapshot.chmod(0o644);snapshot.write_text('changed snapshot during CLI run')
if mode=='runtime_input_changes': Path(os.environ['MOCK_TAMPER_PROMPT']).write_text('mutated executed prompt')
if mode=='delivery_changes': Path(os.environ['MOCK_TAMPER_DELIVERY']).write_text('mutated delivery instruction')
body='\n\n'.join(f'## {n}. section\n\n'+(f'batch={batch}; input={sha}; frames={frames}; price=25.30' if n==0 and mode!='unbound_report' else 'offline evidence') for n in range(9))
if mode=='hidden_binding': body=body.replace(f'batch={batch}; input={sha}; frames={frames}; price=25.30',f'<!-- batch={batch}; input={sha}; frames={frames} -->\noffline evidence')
report_file.write_text(body)
doc={'meta':{'schema_version':'stock-research/v2','code':code,'name':{'600066.SH':'宇通客车','600900.SH':'长江电力'}[code],'valuation_date':day,'currency':'CNY','generator':generator,'report_path':report},
'price_map':{'mode':'tracking','reason':'offline fixture','v50':{'low':20,'base':25,'high':30},'p1':{'low':10,'base':12,'high':15},'p2':{'status':'cancelled','price':None,'reason':'cancelled'},'t1':{'price_condition':'V50','events':['review']},'t2':{'price_condition':'unavailable','events':['failure']}},
'monitoring':[{'variable':'income','current':None,'as_of':None,'trigger':'falls','action':'review','source':'offline','next_check':'next report'}]}
receipt_price=price
if mode=='exact_delivery_paths': price=price_file
(staged/price).write_text(json.dumps(doc))
price=receipt_price
receipt={'batch_id':batch,'task_id':get('task_id'),'code':code,'generator':generator,'valuation_date':day,'input_pack_sha256':sha,'status':'completed','reason':None,'summary':'offline research completed','report_path':report,'price_map_path':price}
if mode=='completed_reason':receipt['reason']='wrong place for summary'
if mode=='wrong_input': receipt['input_pack_sha256']='0'*64
if mode=='wrong_provider': receipt['generator']='codex'
if '-o' in args:
 Path(args[args.index('-o')+1]).write_text(json.dumps(receipt))
 print(json.dumps({'type':'turn.completed'}))
else:
 print(json.dumps({'type':'result','subtype':'success','is_error':False,'structured_output':receipt}))
'''


class ResearchRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.methods = self.root / 'methods'
        self.methods.mkdir()
        for name in ('investment_framework.md', 'investment_framework_compact.md'):
            path = self.methods / 'framework' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('offline framework')
        self.exchange = self.root / 'exchange'
        self.pack = self.exchange / 'packs/SH-600066.md'
        self.pack.parent.mkdir(parents=True)
        self.raw_pack = '# 600066.SH 量价与基本面数据包\n- 最新收盘: 25.30 (20261006)\n- 最新成交量(手): 12,345 | 成交额(千元): 67,890\n\n末尾原始资料不可截断\n'
        self.pack.write_text(self.raw_pack)
        self.request_path = self.exchange / 'request.json'
        self.request = {'schema_version':'stock-research-request/v1','batch_id':'a'*32,
                        'created_at':'2026-10-06T08:00:00+08:00','valuation_date':'2026-10-06',
                        'generators':['codex','claude'],'tasks':[{
                            'task_id':'SH-600066','code':'600066.SH','name':'宇通客车','sources':['candidate_review'],
                            'data_pack':{'path':'packs/SH-600066.md','sha256':self.sha(self.pack)},
                            'data_pack_meta':{'candidate_review_response':{'needs_reanalysis':True},'missing_required':['financial.unit']}}]}
        self.write_request()
        self.fake = self.root / 'fake-claude'
        self.fake.write_text(FAKE_CLI)
        self.fake.chmod(0o700)
        self.capture = self.root / 'received-stdin.txt'
        self.env = patch.dict(os.environ, {'MOCK_INPUT':str(self.capture),'MOCK_MODE':'success'})
        self.env.start()
        self.addCleanup(self.env.stop)

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_request(self):
        self.request_path.write_text(json.dumps(self.request,ensure_ascii=False))

    def execute(self, **kw):
        return run_batch(self.request_path, self.methods, generator='claude', cli=str(self.fake), timeout=10, **kw)

    def test_new_delivery_rejects_stale_v50_reference_before_publication(self):
        self.fake.write_text(FAKE_CLI.replace("'price_condition':'V50'",
                                             "'price_condition':'V50上沿31元'"))
        entry = json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('V50.high', entry['reason'])
        self.assertEqual(list((self.methods/'research').rglob('*.json')), [])

    def test_midnight_reservation_is_checked_before_durable_launch(self):
        with patch('scripts.research_runner.stamp', return_value='2026-10-08T00:00:01+08:00'):
            with self.assertRaisesRegex(ValueError, 'reservation expired'):
                self.execute(launch_date='2026-10-07')
        self.assertFalse(self.capture.exists())
        self.assertEqual(list(self.methods.rglob('launched.json')), [])

    def test_prepare_embeds_exact_full_pack_for_both_providers(self):
        run = prepare_request(self.request_path, self.methods)
        self.assertEqual((run/'request.json').read_bytes(),self.request_path.read_bytes())
        self.assertEqual((run/'packs/SH-600066.md').read_bytes(),self.pack.read_bytes())
        for generator in ('codex','claude'):
            folder=run/f'execution/SH-600066/{generator}'
            payload=(folder/'prompt.txt').read_text()
            self.assertIn(self.raw_pack,payload)
            self.assertIn('missing_required',payload)
            self.assertIn('needs_reanalysis',payload)
            record=json.loads((folder/'input.json').read_text())
            self.assertEqual(record['prompt_sha256'],self.sha(folder/'prompt.txt'))
            self.assertEqual(record['input_pack_sha256'],self.sha(self.pack))
            self.assertIn(str(run/'framework-snapshot'),payload)
            self.assertIn('主代理及所有子代理',payload)
            for name, digest in record['framework_sha256'].items():
                self.assertEqual((run/'framework-snapshot'/name).read_bytes(),
                                 (self.methods/'framework'/name).read_bytes())
                self.assertEqual(self.sha(run/'framework-snapshot'/name),digest)

    def test_missing_pack_refused_without_launch(self):
        self.pack.unlink()
        with self.assertRaises((ValueError,OSError)): self.execute()
        self.assertFalse(self.capture.exists())

    def test_corrupt_pack_refused_without_launch(self):
        self.pack.write_text(self.raw_pack+'mutation')
        with self.assertRaises(ValueError): self.execute()
        self.assertFalse(self.capture.exists())

    def test_wrong_security_pack_refused_even_with_matching_hash(self):
        self.pack.write_text(self.raw_pack.replace('600066.SH','600900.SH'))
        self.request['tasks'][0]['data_pack']['sha256']=self.sha(self.pack)
        self.write_request()
        with self.assertRaisesRegex(ValueError,'security'): self.execute()
        self.assertFalse(self.capture.exists())

    def test_whitespace_pack_refused(self):
        self.pack.write_text('  \n')
        self.request['tasks'][0]['data_pack']['sha256']=self.sha(self.pack)
        self.write_request()
        with self.assertRaises(ValueError): self.execute()

    def test_prompt_truncation_after_prepare_refused(self):
        run=prepare_request(self.request_path,self.methods)
        (run/'execution/SH-600066/claude/prompt.txt').write_text('research this stock')
        with self.assertRaisesRegex(ValueError,'prompt'): self.execute()
        self.assertFalse(self.capture.exists())

    def test_local_pack_mutation_after_prepare_refused(self):
        run=prepare_request(self.request_path,self.methods)
        (run/'packs/SH-600066.md').write_text('changed')
        with self.assertRaises(ValueError): self.execute()
        self.assertFalse(self.capture.exists())

    def test_input_record_tampering_refused(self):
        run=prepare_request(self.request_path,self.methods)
        (run/'execution/SH-600066/claude/input.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'input record'): self.execute()

    def test_request_changed_after_prepare_refused(self):
        prepare_request(self.request_path,self.methods)
        self.request['tasks'][0]['name']='different company'; self.write_request()
        with self.assertRaisesRegex(ValueError,'request'): self.execute()
        self.assertFalse(self.capture.exists())

    def test_live_framework_change_resumes_snapshot_and_isolates_completed_research(self):
        run=prepare_request(self.request_path,self.methods)
        (self.methods/'framework/investment_framework.md').write_text('new version')
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2.md',entry['report']['path'])
        self.assertEqual((run/'framework-snapshot/investment_framework.md').read_text(),'offline framework')
        targets=json.loads((run/'execution/SH-600066/claude/targets.json').read_text())
        self.assertFalse((self.methods/targets['report_path']).exists())
        self.assertIn('needs_review',(self.methods/entry['report']['path']).read_text())

    def test_snapshot_changed_after_prepare_is_refused(self):
        run=prepare_request(self.request_path,self.methods)
        path=run/'framework-snapshot/investment_framework.md'
        path.chmod(0o644);path.write_text('tampered frozen input')
        with self.assertRaisesRegex(ValueError,'snapshot.*mismatch'):self.execute()
        self.assertFalse(self.capture.exists())

    def test_snapshot_changed_during_run_is_refused_before_publication(self):
        os.environ['MOCK_MODE']='snapshot_changes'
        result=self.execute();entry=json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('snapshot',entry['reason'])
        self.assertEqual(list((self.methods/'research').rglob('*.json')),[])
        state=json.loads((result.parent/'execution/SH-600066/claude/process.json').read_text())
        self.assertFalse(state['retryable'])

    def test_explicit_delivery_paths_publish_claude_pair(self):
        os.environ['MOCK_MODE'] = 'exact_delivery_paths'
        result = self.execute()
        entry = json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        self.assertTrue((self.methods / entry['report']['path']).is_file())
        self.assertTrue((self.methods / entry['price_map']['path']).is_file())

    def test_retry_delivery_paths_use_retry_staging_and_preserve_first_attempt(self):
        os.environ['MOCK_MODE'] = 'nonzero'
        result = self.execute()
        first = result.parent / 'execution/SH-600066/claude/entry.json'
        original = first.read_bytes()
        os.environ['MOCK_MODE'] = 'exact_delivery_paths'
        request, raw, _ = runner.read_request(self.request_path)
        retry = runner.run_provider(result.parent, request, raw, request['tasks'][0], 'claude',
                                    str(self.fake), self.methods, 10, threading.Event(), attempt=2)
        self.assertEqual(retry['status'], 'completed', retry['reason'])
        self.assertEqual(first.read_bytes(), original)
        staged = result.parent / 'staged/SH-600066/claude/retry-1'
        self.assertEqual((staged / retry['report']['path']).read_bytes(),
                         (self.methods / retry['report']['path']).read_bytes())

    def test_delivery_appendix_is_recorded_without_rewriting_frozen_input(self):
        run = prepare_request(self.request_path, self.methods)
        folder = run / 'execution/SH-600066/claude'
        originals = {name: (folder / name).read_bytes() for name in ('prompt.txt', 'input.json')}
        os.environ['MOCK_MODE'] = 'exact_delivery_paths'
        entry = json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        appendix = (folder / 'delivery-prompt.txt').read_bytes()
        process = json.loads((folder / 'process.json').read_text())
        self.assertEqual(process['delivery_prompt_sha256'], hashlib.sha256(appendix).hexdigest())
        for name, original in originals.items():
            self.assertEqual((folder / name).read_bytes(), original)

    def test_changed_delivery_appendix_is_rejected_before_publication(self):
        run = prepare_request(self.request_path, self.methods)
        os.environ.update(MOCK_MODE='delivery_changes',
                          MOCK_TAMPER_DELIVERY=str(run / 'execution/SH-600066/claude/delivery-prompt.txt'))
        entry = json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('delivery instruction changed', entry['reason'])
        self.assertFalse(list((self.methods / 'research').rglob('*.json')))

    def make_legacy_prepared(self):
        run=prepare_request(self.request_path,self.methods)
        request, raw, packs=runner.read_request(self.request_path)
        frameworks=runner.framework_hashes(self.methods)
        originals={}
        for generator in request['generators']:
            folder=run/'execution/SH-600066'/generator
            targets=json.loads((folder/'targets.json').read_text())
            prompt=runner.make_prompt(request,request['tasks'][0],generator,packs['SH-600066'],
                                      self.methods,frameworks,targets,snapshot=False)
            (folder/'prompt.txt').write_bytes(prompt)
            (folder/'input.json').write_bytes(runner.encode(runner.input_record(
                request,raw,request['tasks'][0],generator,prompt,frameworks,targets)))
            originals[generator]={name:(folder/name).read_bytes() for name in ('prompt.txt','input.json')}
        import shutil
        shutil.rmtree(run/'framework-snapshot')
        return run,originals

    def test_legacy_prepared_migrates_only_exact_bytes_and_preserves_history(self):
        run,originals=self.make_legacy_prepared()
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('framework-snapshot',self.capture.read_text())
        manifest=json.loads((run/'framework-snapshot/manifest.json').read_text())
        self.assertEqual(manifest['origin'],'legacy_exact_hash_migration')
        for generator,files in originals.items():
            for name,body in files.items():
                self.assertEqual((run/'execution/SH-600066'/generator/name).read_bytes(),body)
        state=json.loads((run/'execution/SH-600066/claude/process.json').read_text())
        self.assertIn('legacy-inputs',state['framework_input_record'])

    def test_legacy_prepared_unknown_bytes_require_new_batch_without_fabrication(self):
        run,originals=self.make_legacy_prepared()
        (self.methods/'framework/investment_framework.md').write_text('new version')
        with self.assertRaisesRegex(ValueError,'original batch preserved, rebuild a new batch'):
            self.execute()
        self.assertFalse((run/'framework-snapshot').exists())
        self.assertFalse(self.capture.exists())
        self.assertEqual((run/'execution/SH-600066/claude/prompt.txt').read_bytes(),originals['claude']['prompt.txt'])

    def test_completed_legacy_archive_remains_readable_without_live_framework(self):
        result=self.execute()
        run,_=self.make_legacy_prepared()
        (self.methods/'framework/investment_framework.md').write_text('new incompatible method')
        accepted=runner.load_results(result,run/'request.json',self.methods)
        self.assertEqual(accepted['results'][0]['status'],'completed')
        with self.assertRaisesRegex(ValueError,'already launched'):self.execute()
        self.assertFalse((run/'framework-snapshot').exists())

    def install_state_block(self, value):
        state={'schema':'investment-state/v1','as_of':'2026-10-06','evidence_cutoff':'2026-10-06',
               'source_report':None,'observations':[{'id':'turnover','value':value,'unit':'trillion',
               'observed_at':'2026-10-06','source':'offline fixture','status':'verified'}]}
        text='method remains fixed\n<!-- investment-state:start -->\n```json\n'+json.dumps(state)+'\n```\n<!-- investment-state:end -->\n'
        (self.methods/'framework/investment_framework.md').write_text(text)

    def test_state_observation_change_keeps_method_compatibility_without_restarting(self):
        self.install_state_block(1.5)
        run=prepare_request(self.request_path,self.methods)
        self.install_state_block(1.8)
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertNotIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['classification'],'state_only')
        self.assertFalse(checked['needs_review'])
        self.assertNotEqual(checked['snapshot_sha256'],checked['current_sha256'])

    def test_same_method_version_label_cannot_mask_threshold_change(self):
        path=self.methods/'framework/investment_framework.md'
        path.write_text('<!-- investment-method-version: same -->\nthreshold=1.6')
        prepare_request(self.request_path,self.methods)
        path.write_text('<!-- investment-method-version: same -->\nthreshold=2.0')
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2',entry['report']['path'])

    def test_malformed_state_block_cannot_grant_compatibility(self):
        self.install_state_block(1.5)
        run=prepare_request(self.request_path,self.methods)
        path=self.methods/'framework/investment_framework.md'
        path.write_text(path.read_text().replace('"unit": "trillion"','"threshold": 2.0'))
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertIn('Invalid state-only compatibility input',checked['reason'])

    def make_handoff(self, day='2026-10-05', status='adopted', revision=None,
                     supersedes=None, withdrawn_sources=None, compatibility=None):
        root=self.methods.resolve()
        reports={}
        for key,kind in (('market_research','market-research'),('change_decision','change-decision')):
            path=maintenance.weekly_path(root,day,kind,revision)
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(f'dated offline state evidence {day} {revision} {kind}')
            reports[key]=maintenance.file_ref(root,path,as_of=day)
        changes=[{'kind':'state_refresh','summary':'refresh observed state without changing methods'}]
        path=maintenance.weekly_path(root,day,'handoff',revision)
        record={'schema':maintenance.SCHEMA,'id':path.stem,'as_of':day,'revision':revision,
                'status':status,'adoption_basis':'explicit fixture adoption' if status=='adopted' else None,
                'method_status':'adopted','methods':maintenance.freeze_methods(root,day,revision),
                'reports':reports,'changes':changes,'classification':maintenance.classify_changes(changes),
                'supersedes':supersedes or [],'withdrawn_sources':withdrawn_sources or [],'evidence':[],
                'compatibility':compatibility or [],
                'rule_evaluations':[],'reviews':[]}
        return maintenance.write_handoff(root,record),reports

    def test_adopted_state_is_frozen_independently_of_framework_pr(self):
        handoff,reports=self.make_handoff()
        run=prepare_request(self.request_path,self.methods)
        snapshot=json.loads((run/'framework-snapshot/manifest.json').read_text())
        self.assertIsNotNone(snapshot['maintenance'])
        frozen=run/'framework-snapshot'/snapshot['maintenance']['handoff']['path']
        self.assertEqual(frozen.read_bytes(),handoff.read_bytes())
        for ref in reports.values():
            (self.methods/ref['path']).write_text('changed after preparation')
        handoff.write_text('changed after preparation')
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('已采纳维护接续',self.capture.read_text())
        self.assertIn(snapshot['maintenance']['handoff']['sha256'],self.capture.read_text())

    def test_future_handoff_is_not_used_before_valuation_cutoff(self):
        self.make_handoff('2026-10-07')
        run=prepare_request(self.request_path,self.methods)
        self.assertIsNone(json.loads((run/'framework-snapshot/manifest.json').read_text())['maintenance'])

    def test_proposed_handoff_is_not_silently_adopted(self):
        self.make_handoff(status='proposed')
        run=prepare_request(self.request_path,self.methods)
        self.assertIsNone(json.loads((run/'framework-snapshot/manifest.json').read_text())['maintenance'])

    def test_frozen_maintenance_source_tamper_is_detected(self):
        self.make_handoff()
        run=prepare_request(self.request_path,self.methods)
        snapshot=json.loads((run/'framework-snapshot/manifest.json').read_text())
        ref=snapshot['maintenance']['sources'][0]
        path=run/'framework-snapshot'/ref['path'];path.chmod(0o644);path.write_text('changed frozen source')
        with self.assertRaisesRegex(ValueError,'snapshot maintenance.*mismatch'):self.execute()
        self.assertFalse(self.capture.exists())

    def test_explicit_same_day_correction_is_checked_before_publication(self):
        old,reports=self.make_handoff()
        run=prepare_request(self.request_path,self.methods)
        self.make_handoff(revision=2,supersedes=[old.stem],withdrawn_sources=[reports['market_research']])
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['snapshot_sha256'],checked['current_sha256'])
        self.assertEqual(checked['maintenance_lifecycle']['status'],'withdrawn')
        self.assertTrue(checked['needs_review'])

    def test_unrelated_new_state_does_not_invalidate_frozen_adoption(self):
        self.make_handoff()
        run=prepare_request(self.request_path,self.methods)
        self.make_handoff('2026-10-06')
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertNotIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['maintenance_lifecycle']['status'],'active')

    def compatibility_review(self, old_methods, day="2026-10-06"):
        path=self.methods/'research/compatibility-review.md'
        path.parent.mkdir(exist_ok=True);path.write_text('Explicit adopted semantic compatibility review')
        return [{'status':'adopted','reason':'review confirms identical decision meaning for the method pair',
                 'methods':old_methods,'review':maintenance.file_ref(self.methods,path,as_of=day)}]

    def handoff_with_dated_decision_evidence(self):
        handoff,_=self.make_handoff()
        record=json.loads(handoff.read_text())
        trigger=self.methods/'research/trigger-evidence.md'
        trigger.write_text('Observed trigger evidence at 2026-10-04')
        record['rule_evaluations']=[{
            'rule_id':'R-test','as_of':'2026-10-04','rule_status':'adopted',
            'result':'triggered','affected_objects':['SH-600066'],
            'evidence':[maintenance.file_ref(self.methods,trigger,as_of='2026-10-04')]}]
        record['compatibility']=self.compatibility_review(record['methods'],day='2026-10-05')
        maintenance.validate_handoff(record,self.methods)
        handoff.write_text(json.dumps(record,ensure_ascii=False))
        return handoff,record

    def test_prepare_rejects_missing_or_future_decision_evidence_dates(self):
        for role in ('trigger','compatibility'):
            for date_kind in ('missing','future'):
                with self.subTest(role=role,date_kind=date_kind):
                    fixture=ResearchRunnerTests('runTest');fixture.setUp()
                    self.addCleanup(fixture.doCleanups)
                    handoff,record=fixture.handoff_with_dated_decision_evidence()
                    ref=(record['rule_evaluations'][0]['evidence'][0] if role=='trigger'
                         else record['compatibility'][0]['review'])
                    if date_kind=='missing':
                        ref.pop('as_of')
                    else:
                        # Trigger evidence is within the handoff date but beyond
                        # its own evaluation cutoff; compatibility exceeds both.
                        ref['as_of']='2026-10-05' if role=='trigger' else '2026-10-06'
                    handoff.write_text(json.dumps(record,ensure_ascii=False))
                    with self.assertRaisesRegex(ValueError,'(?i)date|as_of|future|cutoff'):
                        prepare_request(fixture.request_path,fixture.methods)
                    run=fixture.methods/'output/runs/investment/2026-10-06'/fixture.request['batch_id']
                    self.assertFalse((run/'request.json').exists())
                    self.assertFalse(fixture.capture.exists())

    def test_dated_trigger_and_compatibility_evidence_are_frozen(self):
        _,record=self.handoff_with_dated_decision_evidence()
        run=prepare_request(self.request_path,self.methods)
        snapshot=json.loads((run/'framework-snapshot/manifest.json').read_text())
        frozen=run/'framework-snapshot'/snapshot['maintenance']['handoff']['path']
        frozen_record=json.loads(frozen.read_text())
        self.assertEqual(frozen_record['rule_evaluations'][0]['evidence'][0]['as_of'],'2026-10-04')
        self.assertEqual(frozen_record['compatibility'][0]['review']['as_of'],'2026-10-05')
        for ref in (record['rule_evaluations'][0]['evidence'][0],record['compatibility'][0]['review']):
            self.assertEqual((run/'framework-snapshot/maintenance'/ref['path']).read_bytes(),
                             (self.methods/ref['path']).read_bytes())

    def test_upgraded_verification_rejects_old_snapshot_with_undated_or_future_evidence(self):
        for date_kind in ('missing','future'):
            with self.subTest(date_kind=date_kind):
                fixture=ResearchRunnerTests('runTest');fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                handoff,record=fixture.handoff_with_dated_decision_evidence()
                evidence=record['rule_evaluations'][0]['evidence'][0]
                if date_kind=='missing':
                    evidence.pop('as_of')
                else:
                    evidence['as_of']='2026-10-05'  # Later than the trigger's 10/04 cutoff.
                handoff.write_text(json.dumps(record,ensure_ascii=False))
                # Model an already-prepared batch from before the date fix;
                # byte hashes alone were accepted by that validator.
                with patch.object(maintenance,'validate_handoff',side_effect=lambda doc,root:doc), \
                     patch.object(runner,'validate_handoff',side_effect=lambda doc,root:doc):
                    run=prepare_request(fixture.request_path,fixture.methods)
                snapshot=run/'framework-snapshot/manifest.json'
                original=snapshot.read_bytes()
                import shutil
                shutil.rmtree(fixture.methods/'research')
                with self.assertRaisesRegex(ValueError,'(?i)date|as_of|future|cutoff'):
                    runner.verify_prepared(run,fixture.request_path.read_bytes(),fixture.methods)
                self.assertEqual(snapshot.read_bytes(),original)
                self.assertFalse(fixture.capture.exists())

    def test_valid_snapshot_verification_does_not_require_live_maintenance_sources(self):
        self.handoff_with_dated_decision_evidence()
        run=prepare_request(self.request_path,self.methods)
        import shutil
        shutil.rmtree(self.methods/'research')
        request,_,_,verified=runner.verify_prepared(run,self.request_path.read_bytes(),self.methods)
        self.assertEqual(request['batch_id'],self.request['batch_id'])
        self.assertIsNotNone(verified[('SH-600066','claude')]['maintenance'])

    def test_frozen_completed_pair_validates_with_dated_availability_and_no_live_files(self):
        completed=json.loads(self.execute().read_text())['results'][0]
        handoff,_=self.make_handoff('2026-10-06')
        record=json.loads(handoff.read_text())
        trigger=self.methods/'research/completed-trigger.md'
        trigger.write_text('Completed fixture trigger observed on 2026-10-06')
        record['rule_evaluations']=[{
            'rule_id':'R-completed','as_of':'2026-10-06','rule_status':'adopted',
            'result':'triggered','affected_objects':['SH-600066'],
            'evidence':[maintenance.file_ref(self.methods,trigger,as_of='2026-10-06')]}]
        record['reviews']=[{
            'company':'SH-600066','trigger_id':'R-completed','status':'completed',
            'evidence_cutoff':'2026-10-06','methods':record['methods'],
            'completion':{key:maintenance.file_ref(self.methods,completed[key]['path'],as_of='2026-10-06')
                          for key in ('report','price_map')}}]
        maintenance.validate_handoff(record,self.methods)
        handoff.write_text(json.dumps(record,ensure_ascii=False))
        self.request['batch_id']='b'*32;self.write_request()
        run=prepare_request(self.request_path,self.methods)
        import shutil
        shutil.rmtree(self.methods/'research')
        _,_,_,verified=runner.verify_prepared(run,self.request_path.read_bytes(),self.methods)
        ref=verified[('SH-600066','claude')]['maintenance']['handoff']
        frozen=json.loads((run/'framework-snapshot'/ref['path']).read_text())
        self.assertEqual(frozen['reviews'][0]['completion']['report']['as_of'],'2026-10-06')
        self.assertEqual(frozen['reviews'][0]['completion']['price_map']['as_of'],'2026-10-06')

    def test_adopted_review_of_both_method_pairs_can_confirm_compatibility(self):
        old_methods=maintenance.freeze_methods(self.methods,'2026-10-04')
        run=prepare_request(self.request_path,self.methods)
        (self.methods/'framework/investment_framework.md').write_text('reviewed editorial method change')
        self.make_handoff('2026-10-06',compatibility=self.compatibility_review(old_methods))
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertNotIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['classification'],'reviewed_compatible')
        self.assertFalse(checked['needs_review'])

    def test_future_or_proposed_compatibility_review_does_not_grant_release(self):
        for day,status in [('2026-10-07','adopted'),('2026-10-06','proposed')]:
            with self.subTest(day=day,status=status):
                # Each subcase has its own fixture to avoid already-launched state.
                fixture=ResearchRunnerTests('runTest');fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                old_methods=maintenance.freeze_methods(fixture.methods,'2026-10-04')
                prepare_request(fixture.request_path,fixture.methods)
                (fixture.methods/'framework/investment_framework.md').write_text('unverified current method')
                fixture.make_handoff(day,status,compatibility=fixture.compatibility_review(old_methods))
                entry=json.loads(fixture.execute().read_text())['results'][0]
                self.assertEqual(entry['status'],'completed')
                self.assertIn('-r2',entry['report']['path'])

    def test_withdrawal_has_priority_over_adopted_method_compatibility(self):
        old,reports=self.make_handoff()
        old_record=json.loads(old.read_text())
        run=prepare_request(self.request_path,self.methods)
        (self.methods/'framework/investment_framework.md').write_text('reviewed compatible new method')
        self.make_handoff('2026-10-06',compatibility=self.compatibility_review(old_record['methods']),
                          withdrawn_sources=[reports['market_research']])
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2',entry['report']['path'])
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['classification'],'needs_review')
        self.assertEqual(checked['maintenance_lifecycle']['status'],'withdrawn')

    def test_unplanned_provider_refused(self):
        self.request['generators']=['codex']; self.write_request()
        with self.assertRaisesRegex(ValueError,'planned'): self.execute()

    def test_actual_cli_receives_complete_stdin_and_valid_artifacts(self):
        manifest=self.execute()
        entry=json.loads(manifest.read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        received=self.capture.read_text()
        self.assertIn(self.raw_pack,received)
        folder=manifest.parent/'execution/SH-600066/claude'
        self.assertEqual(self.capture.read_bytes(),(folder/'prompt.txt').read_bytes())
        record=json.loads((folder/'process.json').read_text())
        self.assertGreater(record['pid'],0)
        self.assertEqual(record['exit_code'],0)
        self.assertEqual(record['status'],'completed')

    def test_retry_prompt_tampering_is_refused_before_publication(self):
        os.environ['MOCK_MODE']='nonzero'
        result=self.execute()
        retry_folder=result.parent/'execution/SH-600066/claude/retry-1'
        os.environ.update(MOCK_MODE='runtime_input_changes',MOCK_TAMPER_PROMPT=str(retry_folder/'prompt.txt'))
        request,raw,_=runner.read_request(self.request_path)
        entry=runner.run_provider(result.parent,request,raw,request['tasks'][0],'claude',
                                  str(self.fake),self.methods,10,threading.Event(),attempt=2)
        self.assertEqual(entry['status'],'failed')
        self.assertIn('executed prompt changed',entry['reason'])
        self.assertEqual(list((self.methods/'research').rglob('*.json')),[])

    def test_started_at_is_recorded_after_popen_not_before_preflight(self):
        clock={'value':'2026-10-06T08:00:00+08:00'}
        real_popen=runner.subprocess.Popen
        def launch(*args,**kwargs):
            # The preflight and stock lock can consume an arbitrary duration.
            clock['value']='2026-10-06T09:00:00+08:00'
            return real_popen(*args,**kwargs)
        with patch.object(runner,'stamp',side_effect=lambda:clock['value']), \
             patch.object(runner.subprocess,'Popen',side_effect=launch):
            manifest=self.execute()
        folder=manifest.parent/'execution/SH-600066/claude'
        process=json.loads((folder/'process.json').read_text())
        entry=json.loads((folder/'entry.json').read_text())
        self.assertEqual(process['started_at'],'2026-10-06T09:00:00+08:00')
        self.assertEqual(process['launched_at'],process['started_at'])
        self.assertEqual(entry['started_at'],process['started_at'])

    def test_same_batch_task_not_launched_twice(self):
        self.execute()
        before=self.capture.read_bytes()
        with self.assertRaisesRegex(ValueError,'already'): self.execute()
        self.assertEqual(self.capture.read_bytes(),before)

    def test_codex_cli_receives_same_pack_and_independent_result(self):
        manifest=run_batch(self.request_path,self.methods,generator='codex',cli=str(self.fake),timeout=10)
        entry=json.loads(manifest.read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertEqual(entry['generator'],'codex')
        self.assertIn(self.raw_pack,self.capture.read_text())
        claude=self.execute()
        self.assertTrue(manifest.exists())
        self.assertNotEqual(manifest,claude)

    def test_legacy_codex_rejected_without_consuming_batch_and_can_retry(self):
        with patch.dict(os.environ, {'MOCK_CODEX_HELP':'legacy'}):
            with self.assertRaisesRegex(ValueError, 'Incompatible Codex CLI.*--no-daemon'):
                run_batch(self.request_path,self.methods,generator='codex',cli=str(self.fake))
        self.assertFalse(self.capture.exists())
        run=prepare_request(self.request_path,self.methods)
        self.assertFalse(list(run.glob('execution/*/codex/launched.json')))
        self.assertFalse(list(run.glob('execution/*/codex/process.json')))
        self.assertFalse((run/'results-codex.json').exists())
        result=run_batch(self.request_path,self.methods,generator='codex',cli=str(self.fake))
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'],'completed')

    def test_codex_help_failure_rejected_before_launch(self):
        with patch.dict(os.environ, {'MOCK_CODEX_HELP':'error'}):
            with self.assertRaisesRegex(ValueError, 'capability check failed'):
                run_batch(self.request_path,self.methods,generator='codex',cli=str(self.fake))
        self.assertFalse(self.capture.exists())

    def test_codex_missing_auto_review_never_falls_back_to_bypass(self):
        replies=[subprocess.CompletedProcess([],0,'  --no-daemon\n',''),
                 subprocess.CompletedProcess([],0,'  -a, --ask-for-approval <POLICY>\n','')]
        with patch.object(runner.subprocess,'run',side_effect=replies):
            with self.assertRaisesRegex(ValueError, '--approve-for-me'):
                runner.check_codex_cli(str(self.fake),self.methods)

    def test_codex_help_timeout_is_clear_rejection(self):
        with patch.object(runner.subprocess,'run',side_effect=subprocess.TimeoutExpired('codex',10)):
            with self.assertRaisesRegex(ValueError, 'capability check failed'):
                runner.check_codex_cli(str(self.fake),self.methods)

    def test_binding_hidden_in_comment_rejected(self):
        os.environ['MOCK_MODE']='hidden_binding'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('section 0',entry['reason'])

    def test_cross_batch_stock_lock_prevents_launch(self):
        prepare_request(self.request_path,self.methods)
        with stock_lock(self.methods,'SH-600066','claude'):
            manifest=self.execute()
        entry=json.loads(manifest.read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('locked',entry['reason'])
        self.assertFalse(self.capture.exists())

    def test_provider_error_even_when_exit_zero_is_failed(self):
        os.environ['MOCK_MODE']='api_error'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIsNone(entry['report'])

    def test_nonzero_exit_is_failed(self):
        os.environ['MOCK_MODE']='nonzero'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('exit',entry['reason'])

    def test_wrong_input_receipt_rejected(self):
        os.environ['MOCK_MODE']='wrong_input'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('input_pack_sha256',entry['reason'])

    def test_wrong_provider_receipt_rejected(self):
        os.environ['MOCK_MODE']='wrong_provider'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')

    def test_completed_receipt_cannot_use_reason_as_summary(self):
        os.environ['MOCK_MODE']='completed_reason'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('reason must be null',entry['reason'])

    def test_permission_error_is_not_proof_of_dead_group(self):
        with patch('scripts.research_runner.os.killpg',side_effect=PermissionError):
            self.assertTrue(group_alive(123456))

    def test_report_without_batch_fingerprint_rejected(self):
        os.environ['MOCK_MODE']='unbound_report'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('report',entry['reason'])

    def test_timeout_produces_failure_and_releases_stock_lock(self):
        os.environ['MOCK_MODE']='timeout'
        manifest=run_batch(self.request_path,self.methods,generator='claude',cli=str(self.fake),timeout=0.1)
        entry=json.loads(manifest.read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('timeout',entry['reason'])
        with stock_lock(self.methods,'SH-600066','claude'): pass

    def test_one_task_failure_does_not_drop_other_task_result(self):
        pack=self.exchange/'packs/SH-600900.md'
        pack.write_text(self.raw_pack.replace('600066.SH','600900.SH'))
        self.request['tasks'].append({'task_id':'SH-600900','code':'600900.SH','name':'长江电力',
            'sources':['candidate_review'],'data_pack':{'path':'packs/SH-600900.md','sha256':self.sha(pack)},'data_pack_meta':{}})
        self.write_request()
        os.environ['MOCK_MODE']='partial_failure'
        entries=json.loads(self.execute(workers=2).read_text())['results']
        self.assertEqual([e['status'] for e in entries],['completed','failed'])
        self.assertIsNotNone(entries[0]['report'])
        self.assertIsNone(entries[1]['report'])

    def test_incomplete_preparation_is_not_repaired_or_launched(self):
        run=self.methods/'output/runs/investment/2026-10-06'/self.request['batch_id']
        run.mkdir(parents=True)
        with self.assertRaises(OSError): self.execute()
        self.assertFalse((run/'request.json').exists())
        self.assertFalse(self.capture.exists())

    def test_real_cli_rejects_missing_request_before_writing(self):
        proc=subprocess.run([sys.executable,str(ROOT/'scripts/research_runner.py'),'prepare','--request',str(self.root/'missing.json')],cwd=self.methods,capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertIn('rejected',proc.stderr)

    def test_next_batch_uses_revision_and_preserves_previous_artifacts(self):
        first=self.execute()
        entry=json.loads(first.read_text())['results'][0]
        old={field:(self.methods/entry[field]['path']).read_bytes() for field in ('report','price_map')}
        self.request['batch_id']='b'*32;self.write_request()
        second=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(second['status'],'completed')
        self.assertIn('-r2.md',second['report']['path'])
        for field in ('report','price_map'):
            self.assertEqual((self.methods/entry[field]['path']).read_bytes(),old[field])

    def test_target_occupied_after_prepare_refuses_launch(self):
        run=prepare_request(self.request_path,self.methods)
        targets=json.loads((run/'execution/SH-600066/claude/targets.json').read_text())
        target=self.methods/targets['report_path'];target.parent.mkdir(parents=True);target.write_text('other owner')
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertFalse(self.capture.exists())
        self.assertEqual(target.read_text(),'other owner')

    def test_publish_collision_does_not_overwrite_or_leave_partial_pair(self):
        staged=self.root/'staged';staged.mkdir()
        entry={}
        for field in ('report','price_map'):
            relative=f'research/{field}.txt'; source=staged/relative;source.parent.mkdir(exist_ok=True);source.write_text('new')
            entry[field]={'path':relative,'sha256':self.sha(source)}
        old=self.methods/entry['price_map']['path'];old.parent.mkdir();old.write_text('old')
        with self.assertRaises(FileExistsError):publish_pair(entry,staged,self.methods)
        self.assertEqual(old.read_text(),'old')
        self.assertFalse((self.methods/entry['report']['path']).exists())

    def test_published_artifact_does_not_share_inode_with_staging(self):
        result=self.execute();entry=json.loads(result.read_text())['results'][0]
        staged=result.parent/'staged/SH-600066/claude'/entry['report']['path']
        published=self.methods/entry['report']['path'];original=published.read_bytes()
        staged.write_text('later temporary change')
        self.assertEqual(published.read_bytes(),original)

    def test_framework_changes_do_not_replace_frozen_input_fingerprint(self):
        os.environ['MOCK_MODE']='framework_changes'
        result=self.execute();entry=json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        state=json.loads((result.parent/'execution/SH-600066/claude/process.json').read_text())
        self.assertTrue(state['framework_changed_during_run'])
        self.assertTrue(state['needs_review'])
        self.assertEqual(state['framework_compatibility'],'needs_review')
        self.assertIn('-r2.md',entry['report']['path'])
        record=json.loads((result.parent/'execution/SH-600066/claude/input.json').read_text())
        report=(self.methods/entry['report']['path']).read_text()
        for digest in record['framework_sha256'].values():self.assertIn(digest,report)
        self.assertEqual(self.capture.read_bytes(),(result.parent/'execution/SH-600066/claude/prompt.txt').read_bytes())

    def test_compatibility_is_recorded_before_any_publication(self):
        original=runner.publish_pair
        def publish_after_review(entry,staged,root):
            run=next((self.methods/'output/runs/investment/2026-10-06').iterdir())
            path=run/'execution/SH-600066/claude/framework-compatibility.json'
            self.assertTrue(path.is_file())
            self.assertEqual(json.loads(path.read_text())['classification'],'needs_review')
            self.assertIn('-r2.md',entry['report']['path'])
            return original(entry,staged,root)
        os.environ['MOCK_MODE']='framework_changes'
        with patch.object(runner,'publish_pair',side_effect=publish_after_review):
            self.assertEqual(json.loads(self.execute().read_text())['results'][0]['status'],'completed')

    def test_buy_candidate_with_null_reason_is_preserved_as_unadopted_revision(self):
        self.fake.write_text(FAKE_CLI.replace("'mode':'tracking','reason':'offline fixture'",
                                            "'mode':'buy_candidate','reason':None").replace(
            "'status':'cancelled','price':None,'reason':'cancelled'",
            "'status':'active','price':9,'reason':None"))
        os.environ['MOCK_MODE']='framework_changes'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        self.assertIn('-r2',entry['price_map']['path'])
        document=json.loads((self.methods/entry['price_map']['path']).read_text())
        self.assertIn('needs_review',document['price_map']['reason'])
        self.assertIn('不代表当前买入资格',document['price_map']['reason'])
        self.assertIn('needs_review',(self.methods/entry['report']['path']).read_text())
        self.assertEqual(document['price_map']['mode'],'frozen')
        self.assertEqual(document['price_map']['p2']['status'],'suspended')
        self.assertEqual(document['price_map']['p2']['price'],9)
        self.assertEqual(document['price_map']['p1']['base'],12)
        run=self.methods/'output/runs/investment/2026-10-06'/self.request['batch_id']
        checked=json.loads((run/'execution/SH-600066/claude/framework-compatibility.json').read_text())
        self.assertEqual(checked['original_price_state']['mode'],'buy_candidate')
        self.assertEqual(checked['original_price_state']['p2']['status'],'active')
        original=run/'staged/SH-600066/claude'/checked['original_targets']['price_map']
        original_price=json.loads(original.read_text())['price_map']
        self.assertEqual(original_price['mode'],'buy_candidate')
        self.assertEqual(original_price['p2']['status'],'active')

    def test_observation_active_p2_is_suspended_in_needs_review_revision(self):
        self.fake.write_text(FAKE_CLI.replace("'mode':'tracking'","'mode':'observation'").replace(
            "'status':'cancelled','price':None,'reason':'cancelled'",
            "'status':'active','price':9,'reason':None"))
        os.environ['MOCK_MODE']='framework_changes'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        price=json.loads((self.methods/entry['price_map']['path']).read_text())['price_map']
        self.assertEqual(price['mode'],'frozen')
        self.assertEqual(price['p2']['status'],'suspended')
        self.assertEqual(price['p2']['price'],9)

    def test_unavailable_p2_stays_without_price_in_needs_review_revision(self):
        self.fake.write_text(FAKE_CLI.replace("'status':'cancelled','price':None,'reason':'cancelled'",
                                            "'status':'unavailable','price':None,'reason':'missing input'"))
        os.environ['MOCK_MODE']='framework_changes'
        entry=json.loads(self.execute().read_text())['results'][0]
        self.assertEqual(entry['status'],'completed')
        price=json.loads((self.methods/entry['price_map']['path']).read_text())['price_map']
        self.assertEqual(price['mode'],'frozen')
        self.assertEqual(price['p2']['status'],'cancelled')
        self.assertIsNone(price['p2']['price'])
        self.assertIn('missing input',price['p2']['reason'])

    def test_timeout_kills_descendant_that_ignores_sigterm(self):
        pid_file=self.root/'descendant.pid'
        os.environ.update(MOCK_MODE='descendant',MOCK_DESCENDANT_PID=str(pid_file))
        result=run_batch(self.request_path,self.methods,generator='claude',cli=str(self.fake),timeout=5)
        self.assertEqual(json.loads(result.read_text())['results'][0]['status'],'failed')
        self.assertTrue(pid_file.exists())
        proc=subprocess.run(['ps','-o','stat=','-p',pid_file.read_text()],capture_output=True,text=True)
        self.assertTrue(not proc.stdout.strip() or proc.stdout.strip().startswith('Z'))

    def test_sigterm_to_runner_cleans_children_and_records_failure(self):
        pid_file=self.root/'descendant.pid'
        os.environ.update(MOCK_MODE='descendant',MOCK_DESCENDANT_PID=str(pid_file))
        wrapper=self.root/'wrapper.py'
        wrapper.write_text(f"import sys;sys.path.insert(0,{str(ROOT)!r});from scripts.research_runner import run_batch;run_batch({str(self.request_path)!r},{str(self.methods)!r},generator='claude',cli={str(self.fake)!r},timeout=60)")
        proc=subprocess.Popen([sys.executable,str(wrapper)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda:proc.kill() if proc.poll() is None else None)
        deadline=time.monotonic()+5
        while not pid_file.exists() and time.monotonic()<deadline:time.sleep(0.05)
        self.assertTrue(pid_file.exists())
        proc.send_signal(signal.SIGTERM);proc.communicate(timeout=8)
        result=self.methods/'output/runs/investment/2026-10-06'/self.request['batch_id']/'results-claude.json'
        entry=json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        self.assertIn('cancelled',entry['reason'])
        child=subprocess.run(['ps','-o','stat=','-p',pid_file.read_text()],capture_output=True,text=True)
        self.assertTrue(not child.stdout.strip() or child.stdout.strip().startswith('Z'))

    def test_state_write_error_after_popen_still_reaps_child(self):
        original=runner.save;calls=0
        def fail_once(path,value):
            nonlocal calls
            if path.name=='process.json':
                calls+=1
                if calls==2:raise OSError('simulated state write failure')
            return original(path,value)
        with patch.object(runner,'save',fail_once):result=self.execute()
        entry=json.loads(result.read_text())['results'][0]
        self.assertEqual(entry['status'],'failed')
        state=json.loads((result.parent/'execution/SH-600066/claude/process.json').read_text())
        self.assertIsNotNone(state['pid'])
        with self.assertRaises(ProcessLookupError):os.kill(state['pid'],0)

    def test_bad_second_staged_hash_does_not_publish_first_artifact(self):
        staged=self.root/'staged';staged.mkdir();entry={}
        for field in ('report','price_map'):
            path=staged/f'{field}.txt';path.write_text('original')
            entry[field]={'path':path.name,'sha256':self.sha(path)}
        (staged/'price_map.txt').write_text('changed after acceptance')
        with self.assertRaises(ValueError):publish_pair(entry,staged,self.methods)
        self.assertFalse((self.methods/'report.txt').exists())

    def test_closed_stdout_pipe_does_not_interrupt_archival(self):
        wrapper=self.root/'wrapper.py'
        wrapper.write_text(f"import sys;sys.path.insert(0,{str(ROOT)!r});from scripts.research_runner import run_batch;run_batch({str(self.request_path)!r},{str(self.methods)!r},generator='claude',cli={str(self.fake)!r},timeout=10)")
        proc=subprocess.Popen([sys.executable,str(wrapper)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda:proc.kill() if proc.poll() is None else None)
        self.assertIn('research_started',proc.stdout.readline())
        proc.stdout.close()
        self.assertEqual(proc.wait(timeout=10),0)
        proc.stderr.close()
        path=self.methods/'output/runs/investment/2026-10-06'/self.request['batch_id']/'results-claude.json'
        self.assertEqual(json.loads(path.read_text())['results'][0]['status'],'completed')


if __name__=='__main__': unittest.main()
