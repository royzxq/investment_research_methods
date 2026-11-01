"""Durable, at-most-once local Coze CLI transport. Never publishes prices.

Only submit() can send, with two explicit gates. History/artifact operations are
read-only remotely. No login, token handling, SMTP or production writer lives here.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
BUDGET = timedelta(minutes=15)
LEDGER_SCHEMA = 'coze-cli-ledger/v1'
RECEIPT_SCHEMA = 'coze-cli-receipt/v1'
RID = re.compile(r'coze-cli-[0-9a-f]{32}')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc)


def timestamp(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(dt.tzinfo is not None, 'timezone required')
    return dt


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    def invalid(value):
        raise ValueError('nonfinite JSON: '+value)
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=invalid)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def mkdirs(path):
    path = Path(path)
    if path.exists():
        return
    mkdirs(path.parent)
    path.mkdir(mode=0o700, exist_ok=True)
    fsync_directory(path.parent)


def atomic(path, value):
    path = Path(path)
    mkdirs(path.parent)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
        fsync_directory(path.parent)
    finally:
        Path(tmp).unlink(missing_ok=True)


def immutable(path, raw):
    path = Path(path)
    mkdirs(path.parent)
    if path.exists():
        require(path.read_bytes() == raw, 'immutable CLI evidence changed')
        return
    # Publish only after a complete write, including on crash.
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.link(tmp, path)
        fsync_directory(path.parent)
    finally:
        Path(tmp).unlink(missing_ok=True)


def contained(root, value):
    path = Path(value).resolve(strict=True)
    require(path.is_relative_to(Path(root).resolve()), 'CLI evidence outside request scope')
    return path


def load_config(path=None, *, methods=ROOT):
    methods = Path(methods).resolve()
    cfg = read(path or methods/'config/coze_cli.json')
    require(cfg.get('schema_version') == 'coze-cli-config/v1', 'unsupported CLI config')
    require(type(cfg.get('enabled')) is bool, 'enabled must be boolean')
    for key in ('session_id', 'claw_id', 'user_id'):
        require(isinstance(cfg.get(key), str) and cfg[key].isdigit(), 'missing pinned '+key)
    require(Path(cfg['executable']).is_absolute(), 'CLI executable must be absolute')
    require(isinstance(cfg.get('attachment_hosts'), list) and cfg['attachment_hosts'], 'artifact hosts required')
    cfg['state_dir'] = str((methods/cfg['state_dir']).resolve())
    return cfg


def terminal(request):
    return (request['status'] == 'failed' or request.get('retry_allowed') is False
            or any(h.get('to') == 'failed' for h in request.get('history', [])))


def started(request):
    return timestamp(request.get('sent_at') or request['sending_at'])


def timely(request, created_at):
    return started(request) <= timestamp(created_at) <= started(request)+BUDGET


def message_time(message):
    value = message.get('create_time')
    require(isinstance(value, (str, int)) and not isinstance(value, bool)
            and str(value).isdigit(), 'missing server message time')
    return datetime.fromtimestamp(int(value)/1000, timezone.utc).isoformat()


def reply_data(message):
    value = message.get('content')
    require(isinstance(value, str), 'missing raw CLI content')
    try:
        content = json.loads(value)
        reply = content['message_data']['reply']
    except (ValueError, KeyError, TypeError):
        return {}, {}
    require(isinstance(content, dict) and isinstance(reply, dict), 'invalid CLI reply envelope')
    return content, reply


def verify_message(request, message):
    content, reply = reply_data(message)
    require(message.get('source') == 2, 'not an agent reply')
    require((message.get('sender') or {}).get('claw_id') == request['claw_id'], 'wrong reply claw')
    require(content.get('id') == message.get('id') and bool(message.get('id')), 'reply ID mismatch')
    require(content.get('session_id') == request['session_id'], 'wrong reply session')
    require(reply.get('reply_to_message_id') == request['message_id'], 'wrong request reference')
    require(timely(request, message_time(message)), 'reply outside 15-minute receipt window')
    require('files' in message and (message['files'] is None or isinstance(message['files'], list)), 'full attachment inventory required')
    require(isinstance(reply.get('content'), str), 'missing reply text')
    return content, reply


def verify_request_message(request, message):
    require(message.get('id') == request['message_id'], 'request message ID mismatch')
    require(message.get('source') == 1 and
            (message.get('sender') or {}).get('user_id') == request['user_id'], 'wrong request author')
    require(isinstance(message.get('content'), str) and
            digest(message['content'].encode()) == request['query_sha256'], 'submitted query hash mismatch')
    require(timestamp(message_time(message)) >= timestamp(request['sending_at']), 'request predates send attempt')


def safe_query(query):
    # The official CLI also interprets @ immediately after CJK/punctuation as
    # local file/agent mentions. Preserve the pack and hold rather than upload.
    require('@' not in query, 'CLI file/agent mention in pack requires review; @ is forbidden')


def embedded_media(text):
    return re.search(r'!\[|<\s*(?:img|svg|object|embed|iframe|audio|video|picture|canvas)\b|data:(?:image|audio|video)/', text, re.I) is not None


def serialized(method):
    @wraps(method)
    def wrapped(self, rid, *args, **kwargs):
        folder = self.folder(rid)
        mkdirs(folder)
        with (folder/'operation.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return method(self, rid, *args, **kwargs)
    return wrapped


class Client:
    def __init__(self, config, *, run=subprocess.run, clock=now, downloader=None):
        self.config, self.run, self.clock = dict(config), run, clock
        self.root = Path(config['state_dir']).resolve()
        self.downloader = downloader or self.download

    @contextmanager
    def ledger(self):
        mkdirs(self.root)
        with (self.root/'.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            path = self.root/'requests.json'
            db = read(path) if path.exists() else dict(schema_version=LEDGER_SCHEMA, requests={})
            require(db.get('schema_version') == LEDGER_SCHEMA, 'unsupported CLI ledger')
            yield db
            atomic(path, db)

    def folder(self, rid):
        require(isinstance(rid, str) and RID.fullmatch(rid), 'invalid CLI request ID')
        return self.root/rid

    def pinned(self, request):
        for key in ('session_id', 'claw_id', 'user_id'):
            require(request[key] == self.config[key], 'CLI target changed: '+key)

    def get(self, rid):
        self.folder(rid)
        with self.ledger() as db:
            request = dict(db['requests'][rid])
        self.pinned(request)
        return request

    def call(self, args, *, payload=None, receipt=None):
        result = self.run([self.config['executable'], *args, '--format', 'json'],
                          input=payload, capture_output=True, text=True, timeout=45,
                          env={**os.environ, 'COZE_CLI_NO_UPDATE_NOTIFIER':'1',
                               'COZE_CLI_NO_SKILL_NOTIFIER':'1'})
        if receipt:
            # Only submit receipts are retained whole; history is filtered before
            # persisting, so unrelated private session messages are not copied.
            immutable(receipt, encoded(dict(exit_code=result.returncode,
                                            stdout=result.stdout, stderr=result.stderr)))
        require(result.returncode == 0, 'Coze CLI command failed (exit '+str(result.returncode)+')')
        value = json.loads(result.stdout)
        require(isinstance(value, dict), 'CLI JSON object required')
        return value

    def prepare(self, intent, *, public_input_reviewed=False):
        require(public_input_reviewed is True, 'read complete pack and confirm public input before prepare')
        require(intent.get('transport') == 'cli', 'CLI intent required; never convert legacy requests')
        require(intent['status'] not in {'failed', 'completed'} and intent.get('retry_allowed') is not False,
                'terminal intent cannot prepare')
        for key in ('session_id', 'claw_id', 'user_id'):
            require(intent[key] == self.config[key], 'intent target mismatch')
        raw = Path(intent['pack']).read_bytes()
        require(digest(raw) == intent['pack_sha256'], 'frozen pack changed')
        text = raw.decode('utf-8')
        code, market = intent['code'].split('.')
        require(market in {'SH', 'SZ'} and re.fullmatch(r'\d{6}', code), 'only SH/SZ supported')
        require(re.search(r'^#\s+'+re.escape(intent['code'])+r'\s+量价与基本面数据包', text, re.M), 'pack identity mismatch')
        date_match = re.search(r'^- 估值时点:\s*(\d{8}|\d{4}-\d{2}-\d{2})', text, re.M)
        require(date_match and date_match[1].replace('-', '') == intent['valuation_date'].replace('-', ''), 'pack date mismatch')
        require('最新收盘:' in text, 'pack missing latest close')
        with self.ledger() as db:
            same = [r for r in db['requests'].values() if r['intent_key'] == intent['base_sha256']+':'+intent['task_id']]
            if same:
                require(len(same) == 1, 'ambiguous existing CLI request')
                request = same[0]
                self.pinned(request)
                require(request['pack_sha256'] == intent['pack_sha256'], 'existing input changed')
                return request
            rid = 'coze-cli-'+uuid.uuid4().hex
            query = (f'【请求ID：{rid}】\n'
                     '请使用投研估值分析技能进行股票调研，并且给出明确的价格地图\n'
                     f'仅调研 {intent["name"]} {intent["code"]}，估值日 {intent["valuation_date"]}。'
                     '请在当前聊天交付完整研究原文和可下载报告附件，明确人民币 P1.base 与单一 T1 及原句依据。'
                     '监控项提供 variable/current/as_of/trigger/action/source/next_check；缺证据保持缺口，不编造。\n'
                     '仅使用公开公司资料和本次完整冻结包。禁止发送邮件、调用邮件分身、'
                     '交易、生产写回、创建定时任务、修改长期记忆或框架。'
                     '不要复用历史报价或把其他证券历史结论混入本轮报告。\n'
                     +text+'\n------').strip()
            safe_query(query)
            folder = self.folder(rid)
            immutable(folder/'pack.md', raw)
            immutable(folder/'query.txt', query.encode())
            request = dict(request_id=rid, intent_key=intent['base_sha256']+':'+intent['task_id'],
                           base_sha256=intent['base_sha256'], task_id=intent['task_id'],
                           code=intent['code'], name=intent['name'], valuation_date=intent['valuation_date'],
                           pack_sha256=intent['pack_sha256'], query_sha256=digest(query.encode()),
                           session_id=intent['session_id'], claw_id=intent['claw_id'], user_id=intent['user_id'],
                           status='prepared', prepared_at=self.clock().isoformat(), attempts=0,
                           message_id=None, replies=[], history=[], public_input_reviewed=True)
            db['requests'][rid] = request
            return request

    def preflight(self, request):
        auth = self.call(['auth', 'status'])
        require(auth.get('logged_in') is True and
                (auth.get('user') or {}).get('user_id') == request['user_id'], 'wrong/unavailable CLI account')
        page = self.call(['agent', 'message', 'list', '--project-id', request['session_id'], '--size', '10'])
        require(page.get('code') == 0, 'session identity check failed')
        require(any(m.get('source') == 2 and (m.get('sender') or {}).get('claw_id') == request['claw_id']
                    and reply_data(m)[0].get('session_id') == request['session_id']
                    for m in page.get('data', {}).get('messages', [])), 'pinned agent not verified in session')

    def submit(self, rid, *, allow_submit=False):
        require(self.config['enabled'] is True and allow_submit is True, 'submission disabled; explicit enable and allow-submit required')
        request = self.get(rid)
        require(request['status'] == 'prepared' and request['attempts'] == 0, 'already claimed; reconcile, never resend')
        self.preflight(request)
        query = (self.folder(rid)/'query.txt').read_text(encoding='utf-8')
        require(digest(query.encode()) == request['query_sha256'], 'prepared query changed')
        safe_query(query)
        with self.ledger() as db:
            current = db['requests'][rid]
            require(current['status'] == 'prepared' and current['attempts'] == 0, 'send claimed concurrently')
            current.update(status='sending', attempts=1, sending_at=self.clock().isoformat())
        try:
            receipt = self.call(['session', 'message', '--session-id', request['session_id']],
                                payload=query, receipt=self.folder(rid)/'submit-receipt.json')
            require(receipt.get('session_id') == request['session_id'] and
                    isinstance(receipt.get('message_id'), str) and receipt['message_id'] and
                    receipt.get('status') == 'accepted', 'invalid submit receipt')
            with self.ledger() as db:
                current = db['requests'][rid]
                require(not terminal(current), 'request failed while submitting')
                current.update(status='pending', message_id=receipt['message_id'],
                               receipt_observed_at=self.clock().isoformat())
        except Exception:
            with self.ledger() as db:
                current = db['requests'][rid]
                if not terminal(current):
                    current.update(status='send_unknown', reason='submission response uncertain; reconcile history, do not resend')
        return self.get(rid)

    def history(self, request):
        cursor, seen, messages = None, set(), []
        boundary = timestamp(request.get('sent_at') or request.get('sending_at') or request['prepared_at'])-timedelta(seconds=60)
        last_time, by_id = None, {}
        for _ in range(100):
            args = ['agent','message','list','--project-id',request['session_id'],'--size','10']
            if cursor:
                args += ['--cursor', str(cursor)]
            page = self.call(args)
            require(page.get('code') == 0, 'history search failed; do not expire')
            data = page.get('data')
            require(isinstance(data, dict) and isinstance(data.get('messages'), list), 'incomplete history response')
            require('next_cursor' in data and (data['next_cursor'] is None or isinstance(data['next_cursor'], str)),
                    'missing/invalid history cursor; do not expire')
            items = data['messages']
            for item in items:
                created = timestamp(message_time(item))
                require(last_time is None or created <= last_time, 'history is not descending; do not expire')
                last_time = created
                mid = item.get('id')
                require(isinstance(mid, str) and mid, 'history message ID missing')
                require(mid not in by_id or by_id[mid] == item, 'history changed during pagination; do not expire')
                if mid not in by_id:
                    by_id[mid] = item
                    messages.append(item)
            # The API defaults to descending order. Verify that ordering above
            # and cover the whole send window, without scanning unrelated years.
            if items and all(timestamp(message_time(m)) < boundary for m in items):
                return messages
            cursor = data.get('next_cursor')
            if not cursor:
                return messages
            require(cursor not in seen, 'history cursor loop; do not expire')
            seen.add(cursor)
        raise ValueError('history pagination limit; do not expire')

    def download(self, url, target):
        hosts = set(self.config['attachment_hosts'])
        def check(value):
            u = urllib.parse.urlsplit(value)
            require(u.scheme == 'https' and u.hostname in hosts and not u.username and not u.password
                    and u.port in (None, 443), 'untrusted attachment URL')
        check(url)
        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                check(newurl)
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        opener = urllib.request.build_opener(Redirect())
        with opener.open(url, timeout=45) as source:
            raw = source.read(25*1024*1024+1)
            declared = source.headers.get('Content-Length')
            if declared is not None:
                require(declared.isdigit() and int(declared) == len(raw), 'truncated or invalid attachment length')
        require(0 < len(raw) <= 25*1024*1024, 'empty or oversized attachment')
        immutable(target, raw)

    @serialized
    def collect(self, rid):
        request = self.get(rid)
        require(not terminal(request), 'terminal request; do not resume or resend')
        if request['status'] == 'complete':
            self.capture(rid)
            return request
        require(request['status'] != 'prepared', 'request not submitted')
        checked_at = self.clock()
        messages = self.history(request)  # A failed/partial search cannot trigger expiry.
        if not request.get('message_id'):
            matches = [m for m in messages if m.get('source') == 1 and
                       (m.get('sender') or {}).get('user_id') == request['user_id'] and
                       isinstance(m.get('content'), str) and digest(m['content'].encode()) == request['query_sha256']
                       and timestamp(message_time(m)) >= timestamp(request['sending_at'])]
            by_id = {m['id']:m for m in matches}
            if len(by_id) != 1:
                return self._after_check(rid, [], reason='send receipt missing or ambiguous', checked_at=checked_at)
            request['message_id'] = next(iter(by_id))
        original = next((m for m in messages if m.get('id') == request['message_id']), None)
        require(original is not None, 'original request not found; do not expire')
        verify_request_message(request, original)
        request['sent_at'] = message_time(original)
        original_path = self.folder(rid)/'request-message.json'
        if original_path.exists():
            frozen = read(original_path)
            verify_request_message(request, frozen)
            require(message_time(frozen) == message_time(original), 'request server time changed')
        else:
            immutable(original_path, encoded(original))
        snapshots = []
        for m in messages:
            content, reply = reply_data(m)
            if reply.get('reply_to_message_id') != request['message_id']:
                continue
            # Keep late evidence separate; it cannot become a publication candidate.
            if not timely(request, message_time(m)):
                immutable(self.folder(rid)/'late'/digest(encoded(m)), encoded(m))
                continue
            _, reply = verify_message(request, m)
            folder = self.folder(rid)/'replies'/digest(encoded(m))
            immutable(folder/'message.json', encoded(m))
            immutable(folder/'body.txt', reply['content'].encode())
            inventory_path = folder/'attachments.json'
            previous = read(inventory_path) if inventory_path.exists() else []
            evidence = []
            for index, item in enumerate(m['files'] or []):
                require(isinstance(item, dict), 'invalid attachment inventory')
                key = str(index)
                prior = previous[index] if index < len(previous) else {}
                entry = dict(prior, key=key, filename=item.get('file_name'), status='blocked')
                try:
                    require(isinstance(item.get('file_url'), str) and item['file_url'], 'attachment URL unavailable')
                    raw_path = folder/f'attachment-{index:03d}.bin'
                    if not raw_path.exists():
                        self.downloader(item['file_url'], raw_path)
                    raw = raw_path.read_bytes()
                    require(raw and len(raw) <= 25*1024*1024, 'empty or oversized attachment')
                    if index < len(previous) and previous[index].get('raw_sha256'):
                        require(digest(raw) == previous[index]['raw_sha256'], 'attachment original changed')
                    entry.update(raw_file=str(raw_path), raw_sha256=digest(raw))
                    if prior.get('manually_verified'):
                        extracted = contained(folder, prior['text_file']).read_bytes()
                        require(digest(extracted) == prior['text_sha256'] and extracted.strip(), 'manual extraction changed')
                        entry.update(status='read')
                        evidence.append(entry)
                        continue
                    suffix = Path(item.get('file_name') or '').suffix.lower()
                    require(suffix in {'.md','.txt','.json','.csv','.tsv'}, 'binary/image attachment requires verified full-text extraction')
                    text = raw.decode('utf-8')
                    require(text.strip() and '\x00' not in text, 'attachment text empty or binary')
                    require(not embedded_media(text), 'embedded image/media requires verified full reading')
                    immutable(folder/f'attachment-{index:03d}.txt', text.encode())
                    entry.update(status='read', text_file=str(folder/f'attachment-{index:03d}.txt'), text_sha256=digest(text.encode()))
                except (ValueError, OSError, UnicodeError) as exc:
                    entry['reason'] = type(exc).__name__+': '+str(exc).split('?')[0][:200]
                evidence.append(entry)
            atomic(inventory_path, evidence)
            snapshots.append(dict(id=m['id'], folder=str(folder), created_at=message_time(m),
                                  observed_at=self.clock().isoformat(), stream_final=reply.get('stream') is False,
                                  message_sha256=digest(encoded(m))))
        with self.ledger() as db:
            current = db['requests'][rid]
            require(not terminal(current), 'request failed during collection')
            if current['status'] == 'complete':
                return current
            current.update(message_id=request['message_id'], sent_at=request['sent_at'])
        return self._after_check(rid, snapshots, checked_at=checked_at)

    def _after_check(self, rid, snapshots, reason=None, checked_at=None):
        with self.ledger() as db:
            request = db['requests'][rid]
            require(not terminal(request), 'terminal request')
            for reply in snapshots:
                require(not any(r['request_id'] != rid and any(x['id'] == reply['id'] for x in r['replies'])
                                for r in db['requests'].values()), 'reply already belongs to another request')
            old = {(r['id'], r['message_sha256']):r for r in request['replies']}
            old.update({(r['id'],r['message_sha256']):r for r in snapshots})
            request['replies'] = list(old.values())
            request['last_successful_check_at'] = self.clock().isoformat()
            request['history_started_at'] = (checked_at or self.clock()).isoformat()
            if request['status'] != 'complete':
                if not request['replies'] and (checked_at or self.clock()) >= started(request)+BUDGET:
                    request['history'].append(dict(at=self.clock().isoformat(), to='failed'))
                    request.update(status='failed', retry_allowed=False, reason='no correlated reply within 15 minutes')
                elif request['replies']:
                    request.update(status='partial', reason=reason)
                elif reason:
                    request['reason'] = reason
            return request

    @serialized
    def record_extraction(self, rid, reply_id, key, text_file, raw_sha256, *, verified_fulltext=False):
        require(verified_fulltext is True, 'full text/image reading must be explicitly verified')
        request = self.get(rid)
        require(not terminal(request) and request['status'] != 'complete', 'terminal/complete request')
        candidates = [r for r in request['replies'] if r['id'] == reply_id]
        require(candidates, 'unknown reply')
        selected = candidates[-1]
        folder = contained(self.folder(rid), selected['folder'])
        evidence = read(folder/'attachments.json')
        item = next(a for a in evidence if a['key'] == key)
        raw = contained(folder, item['raw_file']).read_bytes()
        require(digest(raw) == raw_sha256 == item['raw_sha256'], 'attachment original changed')
        text = Path(text_file).read_text(encoding='utf-8')
        require(text.strip(), 'full extracted text empty')
        target = folder/('verified-'+key+'.txt')
        immutable(target, text.encode())
        item.update(status='read', text_file=str(target), text_sha256=digest(text.encode()), manually_verified=True)
        atomic(folder/'attachments.json', evidence)

    def fail(self, rid, reason):
        require(isinstance(reason, str) and reason.strip(), 'failure reason required')
        with self.ledger() as db:
            request = db['requests'][rid]
            require(request['status'] != 'complete', 'published selection cannot be failed')
            if not terminal(request):
                request['history'].append(dict(at=self.clock().isoformat(), to='failed'))
                request.update(status='failed', retry_allowed=False, reason=reason)
            return request

    @serialized
    def complete(self, rid, reply_id, *, verified_identity=False, validator=None):
        require(verified_identity is True, 'read full report and verify security/currency/date first')
        with self.ledger() as db:
            request = db['requests'][rid]
            require(not terminal(request), 'failed request cannot complete')
            if request['status'] == 'complete':
                require(request['selected_reply_id'] == reply_id, 'completed reply cannot change')
                return request
            rows = [r for r in request['replies'] if r['id'] == reply_id]
            require(rows and rows[-1]['stream_final'], 'reply still streaming or missing')
            selected = rows[-1]
            folder = contained(self.folder(rid), selected['folder'])
            message = read(folder/'message.json')
            verify_message(request, message)
            require(digest(encoded(message)) == selected['message_sha256'], 'reply snapshot changed')
            evidence = read(folder/'attachments.json')
            require(len(evidence) == len(message['files'] or []) and
                    [a['key'] for a in evidence] == [str(i) for i in range(len(message['files'] or []))], 'attachment inventory incomplete')
            body = contained(folder, folder/'body.txt').read_text(encoding='utf-8')
            require(body == reply_data(message)[1]['content'], 'reply body changed')
            parts = [body]
            for item in evidence:
                require(item['status'] == 'read', 'unread attachment')
                raw = contained(folder, item['raw_file']).read_bytes()
                text = contained(folder, item['text_file']).read_bytes()
                require(digest(raw) == item['raw_sha256'] and digest(text) == item['text_sha256']
                        and text.strip(), 'attachment evidence changed')
                parts.append(text.decode('utf-8'))
            result = '\n\n'.join(parts)
            code = request['code'].split('.')[0]
            day = request['valuation_date']
            y, mo, d = day.split('-')
            require(code in result and any(value in result for value in
                    (day,day.replace('-',''),f'{y}年{int(mo)}月{int(d)}日')), 'result identity/date missing')
            require('人民币' in result or 'CNY' in result or '元/股' in result, 'result currency missing')
            result_path = folder/'result.md'
            if validator is not None:
                validator(result)
            immutable(result_path, result.encode())
            request.update(status='complete', selected_reply_id=reply_id, selected_folder=str(folder),
                           result_file=str(result_path), result_sha256=digest(result.encode()), verified_identity=True)
            return request

    def capture(self, rid):
        request = self.get(rid)
        require(request['status'] == 'complete' and not terminal(request), 'CLI research incomplete/failed')
        folder = contained(self.folder(rid), request['selected_folder'])
        message = read(folder/'message.json')
        verify_message(request, message)
        selected = next(r for r in request['replies'] if r['id'] == request['selected_reply_id'] and r['folder'] == str(folder))
        require(digest(encoded(message)) == selected['message_sha256'], 'selected message changed')
        original = read(self.folder(rid)/'request-message.json')
        verify_request_message(request, original)
        text = contained(folder, request['result_file']).read_bytes()
        require(digest(text) == request['result_sha256'], 'complete result changed')
        attachments = []
        evidence = read(folder/'attachments.json')
        require(len(evidence) == len(message['files'] or []), 'incomplete attachment evidence')
        for i, item in enumerate(evidence):
            require(item['key'] == str(i) and item['status'] == 'read', 'attachment inventory changed')
            raw = contained(folder, item['raw_file']).read_bytes()
            extracted = contained(folder, item['text_file']).read_bytes()
            require(digest(raw) == item['raw_sha256'] and digest(extracted) == item['text_sha256']
                    and extracted.strip(), 'attachment evidence changed')
            attachments.append(dict(key=item['key'], filename=item['filename'], raw=raw.hex(),
                                    text=extracted.decode(), status='read'))
        require(text.decode() == '\n\n'.join([reply_data(message)[1]['content']]+[a['text'] for a in attachments]), 'result does not preserve full body and attachments')
        return dict(request=request, message=message, request_message=original,
                    text=text.decode(), raw_path=request['result_file'], attachments=attachments,
                    submission_receipt=((self.folder(rid)/'submit-receipt.json').read_bytes().hex()
                        if (self.folder(rid)/'submit-receipt.json').exists() else None),
                    transport='cli')
