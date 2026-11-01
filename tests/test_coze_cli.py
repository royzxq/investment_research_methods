"""Offline protocol tests: the runner never calls a real CLI or network."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from scripts import coze_cli as cli


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.time = datetime(2026, 11, 1, tzinfo=timezone.utc)
        self.config = dict(enabled=True, executable='/never/real/coze', state_dir=str(self.root/'state'),
            session_id='123', claw_id='456', user_id='789', attachment_hosts=['static.coze.site'])
        self.calls, self.messages, self.send_timeout, self.pages = [], [], False, None
        self.client = cli.Client(self.config, run=self.run_cli, clock=lambda:self.time,
                                 downloader=lambda url,path:cli.immutable(path, self.attachment))
        pack = self.root/'pack.md'
        pack.write_text('# 600900.SH 量价与基本面数据包\n- 估值时点: 20261101\n- 最新收盘: 26 (20261030)\n')
        self.intent = dict(transport='cli', status='ready', base_sha256='a'*64, task_id='SH-600900',
            code='600900.SH', name='长江电力', valuation_date='2026-11-01', pack=str(pack),
            pack_sha256=cli.digest(pack.read_bytes()), session_id='123', claw_id='456', user_id='789')
        self.attachment = b'P1: 17.50 CNY; T1: 21.50 CNY'

    def run_cli(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if args[1:3] == ['auth','status']:
            value = dict(logged_in=True, user={'user_id':'789'})
        elif args[1:3] == ['session','message']:
            if self.send_timeout: raise TimeoutError('simulated lost receipt')
            value = dict(session_id='123', message_id='submitted', status='accepted')
        else:
            if not self.messages:
                value = dict(code=0, data=dict(messages=[self.reply('prior', target='prior')], next_cursor=None))
            elif self.pages:
                value = self.pages.pop(0)
            else:
                value = dict(code=0, data=dict(messages=self.messages, next_cursor=None))
        return SimpleNamespace(returncode=0, stdout=json.dumps(value), stderr='')

    def prepare(self):
        return self.client.prepare(self.intent, public_input_reviewed=True)['request_id']

    def send(self):
        rid = self.prepare()
        self.client.submit(rid, allow_submit=True)
        request = self.client.get(rid)
        self.original = dict(id='submitted', source=1, sender={'user_id':'789'}, files=[],
            create_time=str(int(self.time.timestamp()*1000)+1000),
            content=(self.client.folder(rid)/'query.txt').read_text())
        self.messages = [self.original]
        return rid

    def reply(self, mid='answer', *, target='submitted', seconds=60, files=None, stream=False):
        data = dict(id=mid, session_id='123', message_data={'reply':dict(
            content='长江电力 600900.SH 2026-11-01 人民币。P1: 17.50元/股；T1: 21.50元/股。',
            reply_to_message_id=target, stream=stream)})
        return dict(id=mid, source=2, sender={'claw_id':'456'}, content=json.dumps(data),
            create_time=str(int((self.time+timedelta(seconds=seconds)).timestamp()*1000)), files=files or [])

    def test_prepare_freezes_full_pack_and_reuses_one_identity(self):
        rid = self.prepare()
        self.assertEqual(self.prepare(), rid)
        self.assertIn(Path(self.intent['pack']).read_text(), (self.client.folder(rid)/'query.txt').read_text())
        self.assertEqual(self.calls, [])
        self.assertEqual(self.client.get(rid)['attempts'], 0)

    def test_prepare_review_and_pack_integrity_required(self):
        with self.assertRaises(ValueError): self.client.prepare(self.intent)
        Path(self.intent['pack']).write_text('changed')
        with self.assertRaises(ValueError): self.prepare()

    def test_double_gate_and_no_duplicate_submission(self):
        rid = self.prepare()
        with self.assertRaises(ValueError): self.client.submit(rid)
        self.client.config['enabled'] = False
        with self.assertRaises(ValueError): self.client.submit(rid, allow_submit=True)
        self.client.config['enabled'] = True
        self.client.submit(rid, allow_submit=True)
        with self.assertRaises(ValueError): self.client.submit(rid, allow_submit=True)
        sends = [x for x in self.calls if x[0][1:3] == ['session','message']]
        self.assertEqual(len(sends), 1)
        self.assertNotIn('--wait', sends[0][0])
        self.assertEqual(sends[0][1]['input'], (self.client.folder(rid)/'query.txt').read_text())

    def test_sending_directory_sync_failure_prevents_external_call(self):
        from unittest.mock import patch
        rid=self.prepare()
        sync=cli.fsync_directory
        def fail_claim(path):
            if cli.read(self.client.root/'requests.json')['requests'][rid]['status']=='sending':
                raise OSError('simulated directory sync failure')
            sync(path)
        with patch.object(cli,'fsync_directory',side_effect=fail_claim):
            with self.assertRaises(OSError):self.client.submit(rid,allow_submit=True)
        self.assertEqual([c for c in self.calls if c[0][1:3]==['session','message']],[])
        self.assertEqual(self.client.get(rid)['status'],'sending')
        with self.assertRaises(ValueError):self.client.submit(rid,allow_submit=True)

    def test_all_cli_mentions_rejected_including_cjk_and_punctuation(self):
        for text in (' @.env','来源:@.env','（@config/secret.json','中文@file.txt','`@file`','user@example.com'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):cli.safe_query(text)

    def test_atomic_and_immutable_sync_parent_after_publishing(self):
        from unittest.mock import patch
        target=self.root/'entry.json'
        observed=[]
        def sync(path):
            observed.append((path,target.exists()))
        with patch.object(cli,'fsync_directory',side_effect=sync):cli.atomic(target,{'status':'sending'})
        self.assertEqual(observed,[(self.root,True)])
        observed.clear();target=self.root/'proof.bin'
        with patch.object(cli,'fsync_directory',side_effect=sync):cli.immutable(target,b'proof')
        self.assertEqual(observed,[(self.root,True)])

    def test_preflight_identity_failure_does_not_claim(self):
        rid = self.prepare()
        self.client.config['user_id'] = '999'
        with self.assertRaises(ValueError): self.client.submit(rid, allow_submit=True)
        self.assertEqual(cli.read(self.client.root/'requests.json')['requests'][rid]['attempts'], 0)

    def test_unknown_send_reconciles_unique_actual_query_without_resend(self):
        self.send_timeout = True
        rid = self.send()
        self.assertEqual(self.client.get(rid)['status'], 'send_unknown')
        with self.assertRaises(ValueError): self.client.submit(rid, allow_submit=True)
        self.messages.insert(0, self.reply())
        result = self.client.collect(rid)
        self.assertEqual(result['message_id'], 'submitted')
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['attempts'], 1)

    def test_ambiguous_unknown_send_cannot_associate(self):
        self.send_timeout = True
        rid = self.send()
        self.messages.append(dict(self.original, id='second'))
        result = self.client.collect(rid)
        self.assertIsNone(result['message_id'])
        self.assertEqual(result['status'], 'send_unknown')

    def test_native_capture_requires_final_verified_reply(self):
        rid = self.send()
        self.messages.insert(0,self.reply(stream=True))
        self.client.collect(rid)
        with self.assertRaises(ValueError): self.client.complete(rid,'answer',verified_identity=True)
        self.messages[0] = self.reply()
        self.client.collect(rid)
        with self.assertRaises(ValueError): self.client.complete(rid,'answer')
        self.client.complete(rid,'answer',verified_identity=True)
        captured = self.client.capture(rid)
        self.assertEqual(captured['transport'],'cli')
        self.assertNotIn('received_at',captured['message'])
        self.assertEqual(self.client.collect(rid)['status'],'complete')

    def test_unrelated_reply_never_becomes_candidate(self):
        rid = self.send()
        self.messages.insert(0,self.reply(target='someone-else'))
        self.assertEqual(self.client.collect(rid)['replies'], [])

    def test_real_protocol_null_files_progress_does_not_block_final_report(self):
        rid=self.send();progress=self.reply(mid='progress');progress['files']=None
        self.messages=[self.reply(),progress,self.original]
        self.assertEqual(len(self.client.collect(rid)['replies']),2)
        self.client.complete(rid,'answer',verified_identity=True)

    def test_failed_validation_does_not_freeze_incomplete_selection(self):
        rid=self.send();self.messages.insert(0,self.reply());self.client.collect(rid)
        def reject(text):raise ValueError('missing price or monitoring')
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True,validator=reject)
        self.assertEqual(self.client.get(rid)['status'],'partial')

    def test_explicit_failure_is_terminal_even_with_timely_partial(self):
        rid=self.send();self.messages.insert(0,self.reply());self.client.collect(rid)
        self.client.fail(rid,'confirmed execution failure')
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)

    def test_operation_lock_prevents_poll_and_extraction_race(self):
        import fcntl
        rid=self.send()
        with (self.client.folder(rid)/'operation.lock').open('a') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):self.client.collect(rid)

    def test_repoll_does_not_redownload_or_rebaseline_modified_original(self):
        rid=self.send();self.messages.insert(0,self.reply(files=[dict(file_name='r.md',file_url='https://static.coze.site/r')]))
        result=self.client.collect(rid)
        self.client.downloader=lambda *args:self.fail('downloaded an existing original again')
        self.client.collect(rid)
        folder=Path(result['replies'][0]['folder']);(folder/'attachment-000.bin').write_bytes(b'tampered')
        self.client.collect(rid)
        self.client.collect(rid)
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)

    def test_declared_length_mismatch_rejects_truncated_download(self):
        from unittest.mock import patch, MagicMock
        source=MagicMock();source.read.return_value=b'short';source.headers={'Content-Length':'100'}
        source.__enter__.return_value=source
        opener=MagicMock();opener.open.return_value=source
        with patch.object(cli.urllib.request,'build_opener',return_value=opener):
            with self.assertRaisesRegex(ValueError,'truncated'):
                self.client.download('https://static.coze.site/r',self.root/'truncated')
        self.assertFalse((self.root/'truncated').exists())

    def test_binary_digest_survives_repeated_failed_polls(self):
        rid=self.send();self.messages.insert(0,self.reply(files=[dict(file_name='r.pdf',file_url='https://static.coze.site/r')]))
        result=self.client.collect(rid);folder=Path(result['replies'][0]['folder'])
        baseline=cli.read(folder/'attachments.json')[0]['raw_sha256']
        (folder/'attachment-000.bin').write_bytes(b'tampered')
        for _ in range(2):
            self.client.collect(rid)
            item=cli.read(folder/'attachments.json')[0]
            self.assertEqual(item['raw_sha256'],baseline)
            self.assertEqual(item['status'],'blocked')
        text=self.root/'fake.txt';text.write_text('fake replacement')
        with self.assertRaises(ValueError):
            self.client.record_extraction(rid,'answer','0',text,cli.digest(b'tampered'),verified_fulltext=True)

    def test_text_and_original_tamper_cannot_rebaseline_together(self):
        rid=self.send();self.messages.insert(0,self.reply(files=[dict(file_name='r.md',file_url='https://static.coze.site/r')]))
        result=self.client.collect(rid);folder=Path(result['replies'][0]['folder'])
        for name in ('attachment-000.bin','attachment-000.txt'):(folder/name).write_bytes(b'tampered')
        for _ in range(2):self.client.collect(rid)
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)

    def test_wrong_agent_and_session_rejected(self):
        for change in ('sender','session'):
            with self.subTest(change=change):
                rid=self.send(); reply=self.reply()
                if change=='sender': reply['sender']={'claw_id':'999'}
                else:
                    data=json.loads(reply['content']);data['session_id']='999';reply['content']=json.dumps(data)
                self.messages.insert(0,reply)
                with self.assertRaises(ValueError): self.client.collect(rid)
                self.client=cli.Client(dict(self.config,state_dir=str(self.root/change)),run=self.run_cli,clock=lambda:self.time)
                self.messages=[]

    def test_timeout_after_successful_history_is_terminal(self):
        rid=self.send();self.time+=timedelta(minutes=16)
        result=self.client.collect(rid)
        self.assertEqual(result['status'],'failed')
        self.assertFalse(result['retry_allowed'])
        self.messages.insert(0,self.reply())
        for action in (lambda:self.client.collect(rid),lambda:self.client.complete(rid,'answer',verified_identity=True)):
            with self.assertRaises(ValueError): action()

    def test_failed_or_partial_pagination_cannot_expire(self):
        rid=self.send();self.time+=timedelta(hours=1)
        self.pages=[dict(code=0,data=dict(messages=[self.reply(target='other')],next_cursor='next')),dict(code=401)]
        with self.assertRaises(ValueError): self.client.collect(rid)
        self.assertEqual(self.client.get(rid)['status'],'pending')

    def test_missing_cursor_loop_and_unsorted_pages_cannot_expire(self):
        rid=self.send();self.time+=timedelta(hours=1)
        scenarios=[
            [dict(code=0,data=dict(messages=[]))],
            [dict(code=0,data=dict(messages=[],next_cursor='same'))]*2,
            [dict(code=0,data=dict(messages=[self.original,self.reply()],next_cursor=None))],
        ]
        for pages in scenarios:
            self.pages=pages
            with self.assertRaises(ValueError):self.client.collect(rid)
            self.assertEqual(self.client.get(rid)['status'],'pending')

    def test_descending_pagination_covers_window_without_scanning_all_old_history(self):
        rid=self.send()
        old=dict(self.original,id='old',create_time=str(int((self.time-timedelta(minutes=2)).timestamp()*1000)))
        self.pages=[dict(code=0,data=dict(messages=[self.reply(),self.original],next_cursor='older')),
                    dict(code=0,data=dict(messages=[old],next_cursor='years-of-older-history'))]
        result=self.client.collect(rid)
        self.assertEqual(result['status'],'partial')
        self.assertEqual(self.pages,[])

    def test_scan_crossing_deadline_cannot_fail_reply_arriving_after_first_page(self):
        rid=self.send();start=self.time
        old=dict(self.original,id='old',create_time=str(int((start-timedelta(minutes=2)).timestamp()*1000)))
        self.pages=[dict(code=0,data=dict(messages=[self.original],next_cursor='older')),
                    dict(code=0,data=dict(messages=[old],next_cursor=None))]
        self.time=start+timedelta(seconds=900)  # server request is +1s, deadline +901s
        runner=self.client.run
        def cross_deadline(*args,**kwargs):
            response=runner(*args,**kwargs)
            self.time=start+timedelta(seconds=902)
            return response
        self.client.run=cross_deadline
        self.assertEqual(self.client.collect(rid)['status'],'pending')
        reply=self.reply();reply['create_time']=str(int((start+timedelta(seconds=900.5)).timestamp()*1000))
        self.messages=[reply,self.original]
        self.assertEqual(self.client.collect(rid)['status'],'partial')

    def test_deadline_uses_server_send_time_and_late_poll_retains_timely(self):
        rid=self.send();self.messages.insert(0,self.reply(seconds=901))
        self.time+=timedelta(hours=1)
        self.assertEqual(self.client.collect(rid)['status'],'partial')
        self.client.complete(rid,'answer',verified_identity=True)

    def test_late_reply_does_not_publish(self):
        rid=self.send();self.messages.insert(0,self.reply(seconds=902))
        self.time+=timedelta(hours=1)
        self.assertEqual(self.client.collect(rid)['status'],'failed')

    def test_duplicate_attachment_names_preserve_distinct_originals(self):
        rid=self.send()
        files=[dict(file_name='/Drive/report.md',file_url='https://static.coze.site/'+str(i)) for i in range(2)]
        self.messages.insert(0,self.reply(files=files))
        self.client.collect(rid);self.client.complete(rid,'answer',verified_identity=True)
        data=self.client.capture(rid)
        self.assertEqual([a['key'] for a in data['attachments']],['0','1'])
        self.assertEqual(len(data['attachments']),2)

    def test_binary_unread_and_manual_extraction_survive_poll(self):
        rid=self.send()
        self.messages.insert(0,self.reply(files=[dict(file_name='r.pdf',file_url='https://static.coze.site/r')]))
        self.client.collect(rid)
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)
        text=self.root/'extracted.txt';text.write_text('Full attachment text')
        self.client.record_extraction(rid,'answer','0',text,cli.digest(self.attachment),verified_fulltext=True)
        self.client.collect(rid)
        self.client.complete(rid,'answer',verified_identity=True)
        self.assertIn('Full attachment text',self.client.capture(rid)['text'])

    def test_embedded_media_requires_manual_full_reading(self):
        for media in ('![chart](https://example.com/chart.png)', '![chart][ref]\n[ref]: https://example.com/chart.png',
                      '<IMG src="chart.png">','<svg>chart</svg>','<object data="chart.pdf"></object>'):
            with self.subTest(media=media):
                self.assertTrue(cli.embedded_media(media))
        rid=self.send();self.attachment=b'![chart][ref]\n[ref]: https://example.com/chart.png'
        self.messages.insert(0,self.reply(files=[dict(file_name='r.md',file_url='https://static.coze.site/r')]))
        self.client.collect(rid)
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)

    def test_tampered_body_and_attachment_never_complete(self):
        rid=self.send();self.messages.insert(0,self.reply());result=self.client.collect(rid)
        folder=Path(result['replies'][0]['folder']);(folder/'body.txt').write_text('fake 600900.SH 2026-11-01 CNY')
        with self.assertRaises(ValueError):self.client.complete(rid,'answer',verified_identity=True)

    def test_tampered_complete_message_cannot_replay(self):
        rid=self.send();self.messages.insert(0,self.reply());self.client.collect(rid)
        result=self.client.complete(rid,'answer',verified_identity=True)
        path=Path(result['selected_folder'])/'message.json';data=cli.read(path);data['extra']='tampered';cli.atomic(path,data)
        with self.assertRaises(ValueError):self.client.capture(rid)

    def test_untrusted_url_rejected_before_network(self):
        for url in ('http://static.coze.site/r','https://evil.example/r','https://static.coze.site:999/r','https://user@static.coze.site/r'):
            with self.assertRaises(ValueError):self.client.download(url,self.root/'unused')


if __name__=='__main__': unittest.main()
