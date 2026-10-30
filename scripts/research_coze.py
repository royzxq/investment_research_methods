"""Methods-owned Coze email adapter. Transport stays in the Gmail skill.

Scan current sealed pairs; attach only verified email research as an immutable
supplement. A pending/held Coze opinion never changes the original pair seal.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

try:
    from .research_exchange import (_artifact, _contained_path, _strict_json, _timestamp,
                                    _report_sections, load_request, load_results, business_seat, seal_schema)
    from .research_paths import company_path
    from .stock_price_map import (fields, require, number, p1_quotes,
                                  validate_monitoring, validate_p2, string, iso_date)
except ImportError:
    from research_exchange import (_artifact, _contained_path, _strict_json, _timestamp,
                                   _report_sections, load_request, load_results, business_seat, seal_schema)
    from research_paths import company_path
    from stock_price_map import (fields, require, number, p1_quotes,
                                 validate_monitoring, validate_p2, string, iso_date)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'stock-research-coze/v2'
LEGACY_SCHEMA = 'stock-research-coze/v1'
SUPPORTED_SCHEMAS = {LEGACY_SCHEMA, SCHEMA}
SEAL_SCHEMA = 'research-sealed-coze/v1'
BASE_KEYS = {'schema_version', 'task_id', 'batch_id', 'event_key', 'request',
             'request_sha256', 'budget_date', 'results'}
DEFAULT_MAIL_ROOT = ROOT.parent/'ai_investment/investment_rawdata/coze_email'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return _strict_json(Path(path).read_bytes(), str(path))


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as sink:
            sink.write(raw); sink.flush(); os.fsync(sink.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def immutable(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == raw, 'immutable Coze artifact already exists with different bytes')
        return
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as sink:
            sink.write(raw); sink.flush(); os.fsync(sink.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()


@contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root/'adapter.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def divergent(a, b):
    if any(not isinstance(v, (int, float)) or isinstance(v, bool)
           or not math.isfinite(v) or v <= 0 for v in (a, b)):
        return False
    low, high = sorted(Decimal(str(v)) for v in (a, b))
    return high > low * Decimal('1.10')


def load_base(path, methods, exchange):
    methods, exchange = Path(methods).resolve(), Path(exchange).resolve()
    path = Path(path).resolve(strict=True)
    require(path.is_relative_to(methods/'output/research_queue/sealed'), 'base seal outside research queue')
    seal = read(path)
    if seal.get('schema_version') == 'research-sealed-recovery/v1':
        # Only the recovery validator may authorize the private single-seat
        # seal. Each report remains bound to its own request and batch.
        try:
            from .research_recovery import load_supplement as load_recovery
        except ImportError:
            from research_recovery import load_supplement as load_recovery
        base_path, recovery_path, verified = load_recovery(path, methods, exchange)
        base = _load_original_base(base_path, methods, exchange)
        recovered = _load_original_base(recovery_path, methods, exchange)
        generators = verified['recovered_generators']
        require(set(generators) <= set(recovered['documents']), 'recovery opinions incomplete')
        require(not set(base['documents']) & set(generators), 'recovery replaced a completed opinion')
        return dict(base, seal=verified, path=path, base_sha256=sha(path.read_bytes()),
                    round_path=base_path, documents=dict(base['documents'], **{
                        g:recovered['documents'][g] for g in generators}),
                    entries=dict(base['entries'], **{g:recovered['entries'][g] for g in generators}))
    return _load_original_base(path, methods, exchange)


def _load_original_base(path, methods, exchange):
    """Read an original-format seal after the caller verifies its location."""
    seal = read(path)
    fields(seal, BASE_KEYS, 'base seal')
    require(seal['schema_version'] in {'research-sealed/v1', 'research-sealed/v2'}, 'expected original two-model seal')
    request_path = Path(seal['request']).resolve(strict=True)
    require(request_path.is_relative_to(exchange), 'request outside exchange')
    require(sha(request_path.read_bytes()) == seal['request_sha256'], 'request hash mismatch')
    request = load_request(request_path)
    require(seal['schema_version'] == seal_schema(request), 'base seal/request version mismatch')
    require(request['batch_id'] == seal['batch_id'], 'batch mismatch')
    task = next((t for t in request['tasks'] if t['task_id'] == seal['task_id']), None)
    require(task is not None, 'task not in request')
    require(task['data_pack_meta'].get('research_trigger', {}).get('event_key') == seal['event_key'],
            'trigger mismatch')
    require(sorted(item['generator'] for item in seal['results']) == sorted(request['generators']),
            'provider set mismatch')
    documents, provider_entries = {}, {}
    for item in seal['results']:
        fields(item, {'generator', 'manifest', 'manifest_sha256', 'actual_model'}, 'provider')
        manifest = _contained_path(methods, item['manifest'], 'manifest')
        require(sha(manifest.read_bytes()) == item['manifest_sha256'], 'manifest hash mismatch')
        entries = [e for e in load_results(manifest, request_path, methods)['results']
                   if e['task_id'] == task['task_id'] and e['generator'] == item['generator']]
        require(len(entries) == 1, 'provider entry missing or duplicated')
        entry = entries[0]
        provider_entries[item['generator']] = entry
        if entry['status'] == 'completed':
            _, report = _artifact(entry['report'], methods, 'report')
            zero = _report_sections(report)[0]
            require(request['batch_id'] in zero and task['data_pack']['sha256'] in zero,
                    'report input binding missing')
            _, price = _artifact(entry['price_map'], methods, 'price map')
            documents[item['generator']] = _strict_json(price, 'price map')
    return dict(seal=seal, request=request, task=task, documents=documents, path=path,
                entries=provider_entries, base_sha256=sha(path.read_bytes()), request_path=request_path,
                round_path=path)


def pair_generators(documents):
    """Original two business seats, retaining each actual generating harness."""
    if len(documents) != 2:
        return None
    try:
        seats = {business_seat(generator): generator for generator in documents}
    except ValueError:
        return None
    if set(seats) != {'gemini', 'claude'}:
        return None
    return [seats['gemini'], seats['claude']]


def eligible(context):
    task, docs = context['task'], context['documents']
    generators = pair_generators(docs)
    if not re.fullmatch(r'(?:SH|SZ)-\d{6}', task['task_id']) or generators is None:
        return False
    prices = [(docs[g]['price_map'].get('p1') or {}).get('base') for g in generators]
    return divergent(*prices)


def failed_request(request):
    # The shared transport helper can overwrite status on a later record call;
    # failure history and retry prohibition remain the durable terminal receipt.
    return (request['status'] == 'failed' or request.get('retry_allowed') is False
            or any(item.get('to') == 'failed' for item in request.get('history', [])))


def reply_in_time(request, received_at):
    started = _timestamp(request.get('sent_at') or request['sending_at'], 'Coze send time')
    return started <= _timestamp(received_at, 'reply received_at') <= started + timedelta(minutes=15)


def scan(methods, exchange, mail_root, not_before):
    """Use the newest round's verified effective pair; no extra daily slot."""
    methods, mail_root = Path(methods).resolve(), Path(mail_root).resolve()
    cutoff = _timestamp(not_before, 'activation cutoff')
    root = methods/'output/research_queue/coze'
    with locked(root):
        candidates, errors = {}, []
        for path in sorted((methods/'output/research_queue/sealed').glob('*.json')):
            try:
                # Coze supplements never trigger another Coze request. A
                # validated seat recovery supplies the original missing seat.
                if read(path).get('schema_version') not in {
                        'research-sealed/v1', 'research-sealed/v2', 'research-sealed-recovery/v1'}:
                    continue
                context = load_base(path, methods, exchange)
                stamp = _timestamp(context['request']['created_at'], 'created_at')
                task_id = context['task']['task_id']
                order = (stamp, context['round_path'].name,
                         context['seal']['schema_version'] == 'research-sealed-recovery/v1')
                previous = candidates.get(task_id)
                if previous is None or order > previous[0]:
                    candidates[task_id] = (order, context)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append(dict(seal=str(path), reason=str(exc)))
        queue = read(methods/'output/research_queue/state.json')['entries'] if (methods/'output/research_queue/state.json').exists() else {}
        result = []
        for task_id, (order, context) in sorted(candidates.items()):
            stamp = order[0]
            if stamp < cutoff or not eligible(context):
                continue
            if task_id in queue and _timestamp(queue[task_id]['created_at'], 'queued created_at') > stamp:
                continue
            key = context['seal']['batch_id']+'-'+task_id
            folder = root/key
            path = folder/'intent.json'
            task = context['task']
            pack, _ = _artifact(task['data_pack'], context['request_path'].parent, 'pack')
            identity = dict(schema_version='coze-intent/v1', base_seal=str(context['path']),
                base_sha256=context['base_sha256'], batch_id=context['seal']['batch_id'],
                task_id=task_id, code=task['code'], name=task['name'],
                valuation_date=context['request']['valuation_date'], pack=str(pack),
                pack_sha256=task['data_pack']['sha256'], mail_root=str(mail_root),
                p1={g: context['documents'][g]['price_map']['p1']['base']
                    for g in pair_generators(context['documents'])})
            if path.exists():
                intent = read(path)
                if not all(intent.get(k) == v for k, v in identity.items()):
                    errors.append(dict(seal=str(context['path']), intent=str(path),
                                       reason='Coze intent input changed; existing intent preserved'))
                    continue
            else:
                intent = dict(identity, status='ready', request_id=None, reason=None)
                atomic(path, intent)
            result.append(dict(intent=str(path), **intent))
        return dict(intents=result, errors=errors)


def validate_coze_p2(value):
    validate_p2(value, exported=True)
    if value['status'] in {'active', 'suspended'}:
        number(value['price'], 'Coze P2 price required for active/suspended', positive=True)
    else:
        require(value['price'] is None, 'cancelled/unavailable Coze P2 must have null price')


def validate_extraction(value, text, *, schema=SCHEMA):
    require(schema in SUPPORTED_SCHEMAS, 'unsupported Coze extraction schema')
    legacy = schema == LEGACY_SCHEMA
    fields(value, {'p1', 't1', 'monitoring', 'evidence'} | ({'p2'} if legacy else set()), 'Coze extraction')
    p1 = p1_quotes(value['p1'])
    require('base' in p1, 'Coze requires explicit P1.base')
    t1 = number(value['t1'], 'Coze requires explicit T1', positive=True)
    fields(value['evidence'], {'p1', 't1'}, 'price evidence', optional={'p2'} if legacy else set())
    for key, price in (('p1', p1['base']), ('t1', t1)):
        quote = string(value['evidence'][key], key+' quote')
        require(quote in text, 'price quote not in complete Coze result')
        require(re.search(key, quote, re.I) is not None, 'quote does not identify '+key)
        numbers = [Decimal(n.replace(',', '')) for n in re.findall(r'(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?', quote)]
        require(price in numbers, 'price absent from quoted source')
        if key == 't1':
            require(set(numbers) == {price}, 'ambiguous T1 quote; do not infer a range endpoint')
        elif re.search(r'\d\s*(?:-|–|—|~|～|至|到)\s*\d', quote):
            require(re.search(r'基准|base|单价', quote, re.I), 'P1 interval has no explicit base quote')
        require(re.search(r'元|CNY|人民币', quote, re.I), 'price quote missing CNY unit')
    for price in p1.values():
        require(price in [Decimal(n.replace(',', '')) for n in re.findall(r'(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?', value['evidence']['p1'])], 'P1 interval absent from quote')
        require(price % Decimal('.01') == 0, 'P1 exceeds CNY precision')
    require(t1 % Decimal('.01') == 0, 'T1 exceeds CNY precision')
    if legacy and value['p2'] is not None:
        validate_coze_p2(value['p2'])
        if value['p2']['price'] is not None:
            price = number(value['p2']['price'], 'p2', positive=True)
            quote = string(value['evidence'].get('p2'), 'p2 quote')
            require(quote in text and re.search('P2', quote, re.I), 'P2 quote missing')
            require(price < p1['base'] and price % Decimal('.01') == 0, 'invalid P2')
            require(price in [Decimal(n.replace(',', '')) for n in re.findall(r'(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?', quote)], 'P2 absent from quote')
    require(isinstance(value['monitoring'], list), 'monitoring must be a list')


def validate_document(doc):
    fields(doc, {'meta', 'price_map', 'monitoring', 'extraction'}, 'Coze document')
    meta = doc['meta']
    fields(meta, {'schema_version', 'generator', 'code', 'name', 'valuation_date', 'currency', 'report_path'}, 'meta')
    require(meta['schema_version'] in SUPPORTED_SCHEMAS and meta['generator'] == 'coze', 'Coze schema/generator mismatch')
    require(re.fullmatch(r'\d{6}\.(SH|SZ)', meta['code']) and meta['currency'] == 'CNY', 'Coze only supports SH/SZ CNY')
    iso_date(meta['valuation_date'], 'Coze valuation_date')
    for key in ('name', 'report_path'):
        string(meta[key], key)
    # Coze promises prices, not the local nine-section valuation methodology.
    pm = doc['price_map']
    legacy = meta['schema_version'] == LEGACY_SCHEMA
    fields(pm, {'p1', 't1', 'v50', 'mode', 'reason'} | ({'p2'} if legacy else set()), 'price_map')
    require(pm['mode'] == 'observation', 'Coze supplemental opinion must remain observation')
    require(pm['v50'] is None, 'do not manufacture local V50')
    p1 = p1_quotes(pm['p1'])
    require('base' in p1, 'Coze missing P1.base')
    if legacy:
        validate_coze_p2(pm['p2'])
    fields(pm['t1'], {'price_condition'} | ({'events'} if legacy else set()), 't1')
    match = re.fullmatch(r'股价≥(\d+(?:\.\d+)?)元/股', pm['t1']['price_condition'])
    require(match is not None and number(float(match[1]), 'T1', positive=True) > 0, 'Coze missing explicit T1')
    if legacy:
        require(pm['t1']['events'] == [], 'Coze adapter does not invent events')
    if doc['monitoring']:
        validate_monitoring(doc['monitoring'], meta['valuation_date'])
    fields(doc['extraction'], {'p1', 't1', 'monitoring', 'evidence'} | ({'p2'} if legacy else set()), 'extraction')
    require(pm['p1'] == doc['extraction']['p1'] and float(match[1]) == doc['extraction']['t1']
            and doc['monitoring'] == doc['extraction']['monitoring'], 'Coze extraction/document mismatch')
    if legacy:
        expected_p2 = doc['extraction']['p2'] or dict(status='unavailable', price=None, reason='Coze未提供P2')
        require(pm['p2'] == expected_p2, 'Coze P2 extraction mismatch')


def email_result(intent):
    root = Path(intent['mail_root']).resolve(strict=True)
    request = read(root/'requests.json')['requests'][intent['request_id']]
    require(not failed_request(request), 'failed Coze request is terminal; no late result')
    require(request['status'] == 'complete', 'Coze email research incomplete; keep held')
    for key, expected in (('stock_code', intent['code'].split('.')[0]), ('market', 'CN'),
                          ('as_of', intent['valuation_date']), ('pack_sha256', intent['pack_sha256'])):
        require(request[key] == expected, 'Coze email '+key+' mismatch')
    require(sha((root/intent['request_id']/'pack.md').read_bytes()) == intent['pack_sha256'], 'email frozen pack changed')
    path = Path(request['result_file']).resolve(strict=True)
    require(path.is_relative_to(root/intent['request_id']), 'email result outside request folder')
    reply = next((r for r in request['replies'] if Path(r['folder']).resolve() == path.parent and r['outcome'] == 'complete'), None)
    require(reply is not None, 'complete reply receipt missing')
    message, attachments = read(path.parent/'message.json'), read(path.parent/'attachments.json')
    require(message['id'] == reply['id'], 'reply ID mismatch')
    require(reply_in_time(request, message['received_at']),
            'Coze reply arrived after the 15-minute deadline; no late publication')
    # Reuse the email skill's correlation and attachment guards, not snippets.
    import importlib.util
    # Helper location is fixed by the installed skill, never supplied by mail.
    spec = importlib.util.spec_from_file_location('_coze_email_helper', Path.home()/'.codex/skills/coze-stock-research-email/scripts/requests.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    require(helper.match(read(root/'requests.json'), message)['request_id'] == intent['request_id'], 'email association mismatch')
    inventory = message['attachments']
    require(len(attachments) == len(inventory) == len({a['key'] for a in attachments}) == len({a['key'] for a in inventory}) and {a['key'] for a in attachments} == {a['key'] for a in inventory}, 'attachment inventory mismatch')
    for attachment in attachments:
        extracted = Path(attachment['extracted_text_file']).resolve(strict=True)
        require(attachment['status'] == 'read' and extracted.is_relative_to(path.parent)
                and extracted.read_text().strip(), 'attachment incomplete or outside reply folder')
    return path, path.read_text(encoding='utf-8'), request


def capture_email(intent, extraction_path):
    """Take one consistent read under the transport helper's existing lock."""
    root = Path(intent['mail_root']).resolve(strict=True)
    with (root/'.lock').open('rb') as stream:
        fcntl.flock(stream, fcntl.LOCK_SH | fcntl.LOCK_NB)
        raw_path, text, request = email_result(intent)
        message = read(raw_path.parent/'message.json')
        associations = read(root/'requests.json').get('manual_associations', {})
        return dict(base_sha256=intent['base_sha256'], raw_path=str(raw_path), text=text,
            request=request, message=message, extraction=read(extraction_path),
            manual_associations={message['id']: associations[message['id']]} if message['id'] in associations else {},
            attachments=[dict(key=a['key'], filename=a['filename'], status=a['status'],
                text=Path(a['extracted_text_file']).read_text(encoding='utf-8'))
                for a in read(raw_path.parent/'attachments.json')])


def bind(intent_path, request_id):
    intent_path = Path(intent_path).resolve(strict=True)
    with locked(intent_path.parent.parent):
        intent = read(intent_path)
        require(intent['status'] != 'failed' and intent.get('retry_allowed') is not False,
                'failed Coze intent is terminal; no retry')
        require(intent['request_id'] in (None, request_id), 'intent already bound to another request')
        request = read(Path(intent['mail_root'])/'requests.json')['requests'][request_id]
        require(not failed_request(request) and request['status'] != 'superseded',
                'failed Coze request is terminal; no retry')
        require(request['stock_code'] == intent['code'].split('.')[0] and request['market'] == 'CN'
                and request['pack_sha256'] == intent['pack_sha256'] and request['as_of'] == intent['valuation_date'], 'request input mismatch')
        # A completed matching request may be reused; no duplicate email.
        if intent['request_id'] == request_id:
            return intent
        intent.update(request_id=request_id, status='pending', reason=None)
        atomic(intent_path, intent)
        return intent


def hold(intent_path, reason):
    intent_path = Path(intent_path).resolve(strict=True)
    with locked(intent_path.parent.parent):
        intent = read(intent_path)
        require(intent['status'] not in {'completed', 'failed'} and intent.get('retry_allowed') is not False,
                'cannot reopen terminal Coze opinion')
        intent.update(status='held', reason=string(reason, 'hold reason'))
        atomic(intent_path, intent)
        return intent


def expire(methods, mail_root, now=None):
    """Close unanswered sends after 15 minutes; never resend or accept late results.

    Call only after a successful, fully paginated inbox/thread check has recorded
    all newly matched replies. Unmatched mail does not prove request ownership.
    """
    methods, mail_root = Path(methods).resolve(), Path(mail_root).resolve()
    checked = now or datetime.now(timezone.utc)
    require(checked.tzinfo is not None, 'timeout clock must include timezone')
    root = methods/'output/research_queue/coze'
    failed = []
    with locked(root), (mail_root/'.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        ledger_path = mail_root/'requests.json'
        db = read(ledger_path)
        require(db.get('version') == 1, 'unsupported email ledger version')
        intents = [(path, read(path)) for path in root.glob('*/intent.json')]
        for request_id, request in db['requests'].items():
            bound = [(path, intent) for path, intent in intents if intent.get('request_id') == request_id]
            monitor_path = mail_root/request_id/'monitor.json'
            monitor = read(monitor_path) if monitor_path.exists() else dict(request_id=request_id, notified=[])
            if not bound and monitor.get('automation_id') != 'coze':
                continue
            if request['status'] == 'superseded' or any(i['status'] == 'completed' for _, i in bound):
                continue
            terminal = failed_request(request)
            if request['status'] in {'pending', 'partial', 'sending', 'send_unknown', 'complete'} and not terminal:
                sent = request.get('sent_at') or request.get('sending_at')
                if not sent:
                    continue
                started = _timestamp(sent, 'Coze send time')
                deadline = started + timedelta(minutes=15)
                timely = any(started <= _timestamp(r['received_at'], 'reply received_at') <= deadline
                             for r in request.get('replies', []))
                if checked < deadline or timely:
                    continue
                request.setdefault('history', []).append(dict(at=checked.isoformat(),
                    **{'from': request['status'], 'to': 'failed'}))
                request.update(status='failed', failure_kind='reply_timeout', retry_allowed=False,
                    failed_at=checked.isoformat(), reply_deadline=deadline.isoformat(),
                    failure_reason='发送后15分钟内未收到可确认归属的Coze回复；失败终止，不重试')
                atomic(ledger_path, db)
            if not failed_request(request):
                continue
            if request['status'] != 'failed':
                request.setdefault('history', []).append(dict(at=checked.isoformat(),
                    **{'from': request['status'], 'to': 'failed'}))
                request.update(status='failed', retry_allowed=False)
                atomic(ledger_path, db)
            # Also recover a crash after the ledger update but before intent/monitor.
            for path, intent in bound:
                intent.update(status='failed', retry_allowed=False,
                    reason=request.get('failure_reason', 'Coze请求失败；不重试'))
                atomic(path, intent)
            monitor.update(status='failed', last_check_status=request.get('failure_kind', 'research_failed'),
                retry_allowed=False, last_checked_at=checked.isoformat())
            atomic(monitor_path, monitor)
            failed.append(dict(request_id=request_id, reason=request.get('failure_reason', 'Coze请求失败'),
                               notification_needed='terminal_failed:'+request_id not in monitor.get('notified', [])))
    return dict(failed=failed)


def freeze_email(intent, selected, methods, report_path):
    """Archive the accepted reply, including duplicate-name attachment texts.

    Later messages may update the transport ledger's result_file. They must not
    change the bytes or interpretation of a previously published opinion.
    """
    folder = (methods/report_path).parent/'evidence/coze'/intent['request_id']
    result_path = folder/'result.md'
    text = selected['text']
    immutable(result_path, text.encode())
    pack_path = folder/'pack.md'
    immutable(pack_path, Path(intent['pack']).read_bytes())
    attachments = []
    for index, item in enumerate(selected['attachments']):
        raw = item['text'].encode('utf-8')
        target = folder/f'attachment-{index:03d}.txt'
        immutable(target, raw)
        attachments.append(dict(key=item['key'], filename=item['filename'], status=item['status'],
            file=dict(path=str(target.relative_to(methods)), sha256=sha(raw))))
    archive = dict(request=selected['request'], message=selected['message'], attachments=attachments,
        manual_associations=selected['manual_associations'],
        pack=dict(path=str(pack_path.relative_to(methods)), sha256=sha(pack_path.read_bytes())),
        result=dict(path=str(result_path.relative_to(methods)), sha256=sha(text.encode())))
    receipt_path = folder/'mail-receipt.json'
    immutable(receipt_path, encoded(archive))
    return archive['result'], dict(path=str(receipt_path.relative_to(methods)), sha256=sha(receipt_path.read_bytes()))


def archived_email(third, intent, methods):
    receipt_path, raw = _artifact(third['mail_receipt'], methods, 'Coze mail receipt')
    archive = _strict_json(raw, 'mail receipt')
    fields(archive, {'request', 'message', 'attachments', 'pack', 'result', 'manual_associations'}, 'mail archive')
    require(archive['result'] == third['email_result'], 'archived result descriptor changed')
    result_path, text = _artifact(archive['result'], methods, 'archived email result')
    _, pack = _artifact(archive['pack'], methods, 'archived email pack')
    require(sha(pack) == intent['pack_sha256'], 'archived input pack mismatch')
    request, message = archive['request'], archive['message']
    require(request['request_id'] == intent['request_id'] and request['status'] == 'complete', 'archived request mismatch')
    require(not failed_request(request) and reply_in_time(request, message['received_at']),
            'archived Coze reply is failed or outside the 15-minute deadline')
    for key, expected in (('stock_code', intent['code'].split('.')[0]), ('market', 'CN'),
                          ('as_of', intent['valuation_date']), ('pack_sha256', intent['pack_sha256'])):
        require(request[key] == expected, 'archived request '+key+' mismatch')
    import importlib.util
    spec = importlib.util.spec_from_file_location('_coze_email_helper', Path.home()/'.codex/skills/coze-stock-research-email/scripts/requests.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    require(helper.match(dict(requests={intent['request_id']: request}, manual_associations=archive['manual_associations']), message)['request_id'] == intent['request_id'], 'archived email association mismatch')
    inventory, evidence = message['attachments'], archive['attachments']
    require(len(evidence) == len(inventory) == len({a['key'] for a in evidence}) == len({a['key'] for a in inventory}) and {a['key'] for a in evidence} == {a['key'] for a in inventory}, 'archived attachment mismatch')
    for item in evidence:
        _, content = _artifact(item['file'], methods, 'archived attachment')
        require(item['status'] == 'read' and content.decode().strip(), 'archived attachment incomplete')
    require(result_path.parent == receipt_path.parent, 'Coze archive scope mismatch')
    return text.decode('utf-8')


def publish(intent_path, extraction_path, methods, exchange):
    intent_path, methods = Path(intent_path).resolve(strict=True), Path(methods).resolve()
    with locked(intent_path.parent.parent):
        intent = read(intent_path)
        if intent['status'] == 'completed':
            return intent
        require(intent['status'] != 'failed' and intent.get('retry_allowed') is not False,
                'failed Coze intent is terminal; late replies cannot publish')
        try:
            context = load_base(intent['base_seal'], methods, exchange)
            require(context['base_sha256'] == intent['base_sha256'] and eligible(context), 'Coze trigger changed')
            for key, expected in (('batch_id', context['seal']['batch_id']), ('task_id', context['task']['task_id']),
                    ('code', context['task']['code']), ('name', context['task']['name']),
                    ('valuation_date', context['request']['valuation_date']), ('pack_sha256', context['task']['data_pack']['sha256'])):
                require(intent[key] == expected, 'Coze intent '+key+' mismatch')
            selected_path = intent_path.parent/'selected-reply.json'
            selected = read(selected_path) if selected_path.exists() else None
            if selected is None:
                selected = capture_email(intent, extraction_path)
                selected['delivery_schema'] = SCHEMA
                raw_path, text, request = Path(selected['raw_path']), selected['text'], selected['request']
                extracted = selected['extraction']
            else:
                require(selected['base_sha256'] == intent['base_sha256']
                        and selected['request']['request_id'] == intent['request_id'], 'selected reply binding changed')
                raw_path, text, request = Path(selected['raw_path']), selected['text'], selected['request']
                extracted = selected['extraction']
            require(not failed_request(request) and reply_in_time(request, selected['message']['received_at']),
                    'selected Coze reply is failed or outside the 15-minute deadline')
            selected_schema = selected.get('delivery_schema', LEGACY_SCHEMA)
            validate_extraction(extracted, text, schema=selected_schema)
            code, market = context['task']['code'].split('.')
            # Persist chosen targets before publishing either half; retry reuses them.
            if 'targets' not in intent:
                revision = None
                while any(company_path(market, code, intent['valuation_date'], kind, methods,
                          revision=revision, generator='coze').exists() for kind in ('research', 'price-map')):
                    revision = (revision or 1)+1
                intent['targets'] = {kind: str(company_path(market, code, intent['valuation_date'], kind,
                                     methods, revision=revision, generator='coze').relative_to(methods))
                                     for kind in ('research', 'price-map')}
                atomic(intent_path, intent)
            targets = intent['targets']
            doc = dict(meta=dict(schema_version=selected_schema, generator='coze', code=intent['code'], name=intent['name'],
                valuation_date=intent['valuation_date'], currency='CNY', report_path=targets['research']),
                price_map=dict(mode='observation', reason='Coze独立补充报价；不代表新增执行许可', v50=None,
                    p1=extracted['p1'], t1=dict(price_condition=f"股价≥{extracted['t1']}元/股")),
                monitoring=extracted['monitoring'], extraction=extracted)
            if selected_schema == LEGACY_SCHEMA:
                doc['price_map']['p2'] = extracted['p2'] or dict(status='unavailable', price=None, reason='Coze未提供P2')
                doc['price_map']['t1']['events'] = []
            validate_document(doc)
            # Select only fully validated content, before any formal artifact.
            # Crash recovery reuses it even if later replies change the inbox ledger.
            immutable(selected_path, encoded(selected))
            email_descriptor, mail_receipt = freeze_email(intent, selected, methods, targets['research'])
            report = (f"# Coze 股票调研原文\n\n证券：{intent['name']} {intent['code']}；币种：CNY\n"
                f"估值日：{intent['valuation_date']}；批次：{intent['batch_id']}\n"
                f"数据包SHA256：{intent['pack_sha256']}\n请求ID：{intent['request_id']}\n"
                f"原文：{raw_path}\n\n---\n\n{text}").encode()
            price = encoded(doc)
            immutable(methods/targets['research'], report)
            immutable(methods/targets['price-map'], price)
            seal = dict({key: context['seal'][key] for key in BASE_KEYS}, schema_version=SEAL_SCHEMA,
                base_seal=dict(path=str(context['path'].relative_to(methods)), sha256=context['base_sha256']),
                coze=dict(intent=str(intent_path.relative_to(methods)), request_id=intent['request_id'],
                    email_result=email_descriptor, mail_receipt=mail_receipt,
                    report=dict(path=targets['research'], sha256=sha(report)),
                    price_map=dict(path=targets['price-map'], sha256=sha(price))))
            sealed = methods/'output/research_queue/sealed'/f"{intent['batch_id']}-{intent['task_id']}-coze.json"
            immutable(sealed, encoded(seal))
            intent.update(status='completed', reason=None, sealed=str(sealed))
            atomic(intent_path, intent)
            return intent
        except (ValueError, OSError, KeyError, TypeError) as exc:
            intent.update(status='held', reason=str(exc))
            atomic(intent_path, intent)
            raise


def load_supplement(path, methods, exchange):
    """Return an original seal path and verified third-model document."""
    methods = Path(methods).resolve()
    seal = read(path)
    fields(seal, BASE_KEYS | {'base_seal', 'coze'}, 'supplement seal')
    require(seal['schema_version'] == SEAL_SCHEMA, 'unsupported supplement seal')
    base_path, base_raw = _artifact(seal['base_seal'], methods, 'base seal')
    context = load_base(base_path, methods, exchange)
    require(eligible(context), 'supplement lacks eligible two-model P1 divergence')
    require(all(seal[k] == context['seal'][k] for k in BASE_KEYS-{'schema_version'}), 'supplement changed original pair')
    third = seal['coze']
    fields(third, {'intent', 'request_id', 'email_result', 'mail_receipt', 'report', 'price_map'}, 'third opinion')
    intent_path = _contained_path(methods, third['intent'], 'intent')
    require(intent_path.parent.parent == methods/'output/research_queue/coze', 'intent outside Coze queue')
    intent = read(intent_path)
    require(intent['base_sha256'] == sha(base_raw) and intent['request_id'] == third['request_id'], 'intent binding mismatch')
    text = archived_email(third, intent, methods)
    report_path, report = _artifact(third['report'], methods, 'Coze report')
    price_path, price = _artifact(third['price_map'], methods, 'Coze price map')
    doc = _strict_json(price, 'Coze price map')
    validate_document(doc); validate_extraction(doc['extraction'], text, schema=doc['meta']['schema_version'])
    for key, expected in (('code', context['task']['code']), ('name', context['task']['name']),
                          ('valuation_date', context['request']['valuation_date']), ('report_path', third['report']['path'])):
        require(doc['meta'][key] == expected, 'Coze '+key+' mismatch')
    require(report.decode().endswith(text), 'Coze original report not preserved')
    # Targets are allocated by the adapter; cannot point to another producer.
    require(third['report']['path'] == intent['targets']['research'] and third['price_map']['path'] == intent['targets']['price-map'], 'Coze artifact target mismatch')
    return base_path, doc, third


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--methods', type=Path, default=ROOT)
    parser.add_argument('--exchange', type=Path, default=ROOT.parent/'ai_investment/investment_rawdata/data_packs/research_exchange')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('scan'); p.add_argument('--mail-root', type=Path, default=DEFAULT_MAIL_ROOT)
    p.add_argument('--not-before', required=True)
    p = sub.add_parser('expire'); p.add_argument('--mail-root', type=Path, default=DEFAULT_MAIL_ROOT)
    p = sub.add_parser('bind'); p.add_argument('--intent', required=True); p.add_argument('--request-id', required=True)
    p = sub.add_parser('hold'); p.add_argument('--intent', required=True); p.add_argument('--reason', required=True)
    p = sub.add_parser('publish'); p.add_argument('--intent', required=True); p.add_argument('--extraction', required=True)
    args = parser.parse_args()
    if args.command == 'scan':
        result = scan(args.methods, args.exchange, args.mail_root, args.not_before)
    elif args.command == 'expire':
        result = expire(args.methods, args.mail_root)
    elif args.command == 'bind':
        result = bind(args.intent, args.request_id)
    elif args.command == 'hold':
        result = hold(args.intent, args.reason)
    else:
        result = publish(args.intent, args.extraction, args.methods, args.exchange)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
