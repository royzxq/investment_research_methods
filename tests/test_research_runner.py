"""Input delivery and CLI/manifest failures exercised without research APIs."""
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_runner import prepare_request, run_batch, stock_lock, publish_pair, group_alive
import scripts.research_runner as runner


FAKE_CLI = r'''#!/usr/bin/env python3
import hashlib,json,os,re,sys,time,subprocess,signal
from pathlib import Path
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
report_file=staged/report; report_file.parent.mkdir(parents=True,exist_ok=True)
frames=';'.join(json.loads(re.search(r'^框架指纹：(.*)。$',payload.decode(),re.M)[1]).values())
if mode=='framework_changes': Path('framework/investment_framework.md').write_text('changed during CLI run')
body='\n\n'.join(f'## {n}. section\n\n'+(f'batch={batch}; input={sha}; frames={frames}; price=25.30' if n==0 and mode!='unbound_report' else 'offline evidence') for n in range(9))
if mode=='hidden_binding': body=body.replace(f'batch={batch}; input={sha}; frames={frames}; price=25.30',f'<!-- batch={batch}; input={sha}; frames={frames} -->\noffline evidence')
report_file.write_text(body)
doc={'meta':{'schema_version':'stock-research/v2','code':code,'name':{'600066.SH':'宇通客车','600900.SH':'长江电力'}[code],'valuation_date':day,'currency':'CNY','generator':generator,'report_path':report},
'price_map':{'mode':'tracking','reason':'offline fixture','v50':{'low':20,'base':25,'high':30},'p1':{'low':10,'base':12,'high':15},'p2':{'status':'cancelled','price':None,'reason':'cancelled'},'t1':{'price_condition':'V50','events':['review']},'t2':{'price_condition':'unavailable','events':['failure']}},
'monitoring':[{'variable':'income','current':None,'as_of':None,'trigger':'falls','action':'review','source':'offline','next_check':'next report'}]}
(staged/price).write_text(json.dumps(doc))
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

    def test_framework_changed_after_prepare_refused(self):
        prepare_request(self.request_path,self.methods)
        (self.methods/'framework/investment_framework.md').write_text('new version')
        with self.assertRaises(ValueError): self.execute()

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
        record=json.loads((result.parent/'execution/SH-600066/claude/input.json').read_text())
        report=(self.methods/entry['report']['path']).read_text()
        for digest in record['framework_sha256'].values():self.assertIn(digest,report)
        self.assertEqual(self.capture.read_bytes(),(result.parent/'execution/SH-600066/claude/prompt.txt').read_bytes())

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
