"""Bounded local evidence tools for the native research runner.

The service never ranks candidates or calls a model. Explicit context names are
a consumer contract, not authentication of the host's actual caller. Receipts
record delivery only; coverage and verbatim quotes do not establish truth.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import difflib
import fcntl
import hashlib
import importlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import uuid

try:
    from . import research_evidence as evidence, research_reader as reader
except ImportError:
    import research_evidence as evidence
    import research_reader as reader

SCHEMA = 'research-local/v1'
TOOLS = ('research_locate', 'research_read', 'research_check', 'research_finish')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def strict_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('non-finite JSON number: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_new(path, raw):
    """Publish complete bytes once; never overwrite an audit or original draft."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.local-new-')
    try:
        with os.fdopen(fd, 'wb') as sink:
            sink.write(raw)
            sink.flush()
            os.fsync(sink.fileno())
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def save_json(path, value):
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.local-state-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as sink:
            sink.write(dumps(value) + '\n')
            sink.flush()
            os.fsync(sink.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def tool_result(value):
    # Exactly one text item: no duplicate full body in structuredContent.
    return {'content': [{'type': 'text', 'text': dumps(value)}]}


class LocalResearchService:
    """Frozen configuration plus a shared immutable-source registry.

    ``call(name, arguments)`` is the runner/CLI API. ``mcp_id`` is reserved for
    the stdio adapter so its complete JSON-RPC response also fits max_bytes.
    Every read/check/finish requires an explicit arguments.context. Each
    context has its own ledger; only config.context may request completion.
    """
    def __init__(self, config):
        require(isinstance(config, dict), 'configuration must be an object')
        self.config = deepcopy(config)
        self.root = Path(config['root']).resolve(strict=True)
        require(self.root.is_dir(), 'root must be a directory')
        self.execution = reader.contained(self.root, config['execution_dir'])
        output = reader.contained(self.root, 'output')
        require(self.execution.is_relative_to(output) and self.execution != output,
                'execution_dir must be inside root/output/')
        self.context = self._context(config.get('context'))
        roots = config.get('allowed_source_roots')
        require(isinstance(roots, list) and roots, 'allowed_source_roots must be a nonempty array')
        self.source_roots = [reader.contained(self.root, name) for name in roots]
        self.max_bytes = config.get('max_bytes', 9000)
        require(type(self.max_bytes) is int and 1024 <= self.max_bytes <= 128000,
                'max_bytes must be 1024..128000')
        require(config.get('completion_handler', 'research_runner') == 'research_runner',
                'unsupported completion handler')
        self.directory = self.execution / 'evidence'
        self.directory.mkdir(parents=True, exist_ok=True)
        self._owned(self.directory)
        self.config.update(root=str(self.root), execution_dir=str(self.execution),
                           allowed_source_roots=[str(p) for p in self.source_roots],
                           context=self.context, max_bytes=self.max_bytes,
                           completion_handler='research_runner')
        self.config_sha256 = digest(dumps(self.config).encode('utf-8'))
        with self._registry() as state:
            if config.get('plan_path'):
                path = self._input(config['plan_path'])
                if str(path) not in state['plans']:
                    self._register_plan(state, path)
                else:
                    self._load_plan(state, path)

    @staticmethod
    def _context(value):
        require(isinstance(value, str) and value.strip() and len(value) <= 200,
                'explicit context must identify this consumer and current context epoch (1..200 characters)')
        return value

    def _owned(self, path):
        target = Path(path).resolve()
        require(target.is_relative_to(self.execution) and target.is_relative_to(self.root / 'output'),
                'service output escapes execution_dir or root/output/')
        return target

    def _input(self, name):
        require(isinstance(name, str) and name, 'path must be a nonempty string')
        return reader.contained(self.root, name)

    def _source(self, name):
        path = self._input(name)
        require(any(path.is_relative_to(root) for root in self.source_roots),
                'source is outside allowed_source_roots')
        return path

    @contextmanager
    def _lock(self, name):
        path = self._owned(self.directory / name)
        require(not (self.directory / name).is_symlink(), 'service lock must not be a symlink')
        with path.open('a', encoding='utf-8') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    @contextmanager
    def _registry(self):
        with self._lock('registry.lock'):
            path = self._owned(self.directory / 'registry.json')
            state = strict_json(path.read_bytes()) if path.exists() else {
                'schema': SCHEMA, 'config_sha256': self.config_sha256,
                'sources': {}, 'plans': {}, 'active_plan': None, 'checks': {}}
            require(state.get('schema') == SCHEMA and state.get('config_sha256') == self.config_sha256,
                    'service configuration changed or registry is invalid; create a new execution')
            require(all(isinstance(state.get(k), dict) for k in ('sources', 'plans', 'checks')),
                    'invalid service registry')
            yield state
            save_json(path, state)

    def _document(self, state, name, expected=None, register=False):
        path = self._source(name)
        pinned = state['sources'].get(str(path))
        require(register or pinned is not None, 'source is not registered; locate it first')
        require(expected is None or pinned is None or expected == pinned, 'source hash differs from registered version')
        doc = reader.Document(self.root, str(path), pinned or expected)
        require(expected is None or expected == doc.sha256, 'source changed; offsets are invalid')
        if register:
            state['sources'][str(path)] = doc.sha256
        return doc

    def _load_plan(self, state, name):
        path = self._input(str(name))
        require(str(path) in state['plans'], 'plan is not registered; locate the plan first')
        require(digest(path.read_bytes()) == state['plans'][str(path)],
                'registered plan changed; register an extended plan at a new path')
        plan = evidence.Plan(self.root, path)
        for doc in plan.docs.values():
            self._document(state, str(doc.path), doc.sha256)
        return plan

    def _register_plan(self, state, path):
        require(path.is_relative_to(self.root / 'output'), 'plan must be inside root/output/')
        if str(path) in state['plans']:
            return self._load_plan(state, path)
        # Validate authorization before Plan reads any source, not after reading.
        raw = path.read_bytes()
        data = strict_json(raw)
        require(isinstance(data, dict) and isinstance(data.get('units'), list), 'invalid plan units')
        for unit in data['units']:
            require(isinstance(unit, dict), 'plan unit must be an object')
            self._source(unit['path'])
        plan = evidence.Plan(self.root, path)
        if state['active_plan']:
            old = self._load_plan(state, state['active_plan'])
            for id_, unit in old.units.items():
                require(id_ in plan.units, 'extended plan removed an existing source unit')
                new = plan.units[id_]
                require(new['path'] == unit['path'] and new['sha256'] == unit['sha256']
                        and new['start'] <= unit['start'] and new['end'] >= unit['end'],
                        'extended plan replaced or narrowed an existing source unit')
                require({link['id'] for link in unit['requires']}.issubset(
                            {link['id'] for link in new['requires']}),
                        'extended plan removed contextual dependencies')
            for topic, ids in old.topics.items():
                require(topic in plan.topics and set(ids).issubset(plan.topics[topic]),
                        'extended plan removed topic obligations')
            require(set(old.data['gaps']).issubset(plan.data['gaps']),
                    'extended plan removed known gaps; keep explicit gaps for final review')
        for doc in plan.docs.values():
            self._document(state, str(doc.path), doc.sha256, register=True)
        state['plans'][str(path)] = plan.sha256
        state['active_plan'] = str(path)
        return plan

    def _plan(self, state, arguments):
        path = arguments.get('plan_path') or state['active_plan']
        require(path, 'no active evidence plan; locate a plan first')
        plan = self._load_plan(state, path)
        require(str(plan.path) == state['active_plan'], 'use the current extended plan, not an older plan')
        return plan

    def ledger_path(self, context):
        context = self._context(context)
        return self._owned(self.directory / ('reads-' + digest(context.encode('utf-8')) + '.json'))

    @contextmanager
    def _ledger(self, context):
        with reader.ledger_file(self.root, str(self.ledger_path(context))) as state:
            yield state

    def _ack(self, registry, ledger, context, receipt):
        if receipt is None:
            return
        require(isinstance(receipt, str) and receipt, 'ack must be one explicit received receipt')
        bundles = ledger.setdefault('bundles', {})
        require(isinstance(bundles, dict), 'invalid receipt bundle ledger')
        if receipt in bundles:
            ranges = bundles[receipt]
            require(isinstance(ranges, list) and ranges and self._bundle_receipt(context, ranges) == receipt,
                    'invalid or corrupted bundle receipt')
            entries = []
            for item in ranges:
                require(isinstance(item, dict), 'invalid bundle range')
                doc = self._document(registry, item['path'], item['sha256'])
                a, b = item['start'], item['end']
                require(type(a) is int and type(b) is int and 0 <= a < b <= len(doc.text),
                        'invalid bundle received range')
                entries.append((reader.entry_for(ledger, context, doc), [a, b]))
            # Validation of every member precedes the first acknowledgement.
            for entry, span in entries:
                entry['acknowledged'] = reader.merge_ranges(entry['acknowledged'] + [span])
            del bundles[receipt]
            return
        matches = [(path, entry) for path, entry in ledger['contexts'].get(context, {}).items()
                   if receipt in entry.get('pending', {})]
        require(len(matches) == 1, 'receipt not pending for this source hash and explicit context')
        path, entry = matches[0]
        doc = self._document(registry, path, entry.get('sha256'))
        checked = reader.entry_for(ledger, context, doc)
        reader.acknowledge(checked, receipt)

    @staticmethod
    def _bundle_receipt(context, ranges):
        identity = [[r['path'], r['sha256'], r['start'], r['end']] for r in ranges]
        return digest(dumps(['bundle/v1', context, identity]).encode('utf-8'))

    def stage_delivery(self, context, ranges):
        """Runner-only: stage an inline packet receipt without acknowledging it.

        The caller must actually include the complete declared original ranges
        in its prompt. Only a later consumer's explicit ack records receipt.
        This is not exposed as a model-callable tool.
        """
        context = self._context(context)
        require(isinstance(ranges, list) and ranges, 'inline delivery needs nonempty ranges')
        with self._registry() as registry:
            canonical = []
            for item in ranges:
                doc = self._document(registry, item['path'], item['sha256'], register=True)
                a, b = item['start'], item['end']
                require(type(a) is int and type(b) is int and 0 <= a < b <= len(doc.text),
                        'invalid inline delivery range')
                canonical.append(dict(path=str(doc.path), sha256=doc.sha256, start=a, end=b))
            receipt = self._bundle_receipt(context, canonical)
            with self._ledger(context) as ledger:
                bundles = ledger.setdefault('bundles', {})
                require(isinstance(bundles, dict), 'invalid receipt bundle ledger')
                bundles[receipt] = canonical
            result = dict(context=context, receipt=receipt, ranges=canonical,
                          status='staged_unacknowledged', evidence_status='unverified')
        self._event('stage_delivery', {'context': context, 'ranges': ranges}, result=result)
        return result

    def evidence_state(self, context):
        """Fresh source-bound delivery state for runner gates; never semantic truth."""
        context = self._context(context)
        with self._registry() as registry:
            with self._ledger(context) as ledger:
                documents = {path: self._document(registry, path, sha)
                             for path, sha in registry['sources'].items()}
                sources = {path: dict(sha256=doc.sha256,
                    acknowledged=deepcopy(reader.entry_for(ledger, context, doc)['acknowledged']))
                    for path, doc in documents.items()}
                result = dict(context=context, sources=sources, evidence_status='unverified',
                              research_complete=False, check=deepcopy(registry['checks'].get(context)))
                if registry['active_plan']:
                    plan = self._plan(registry, {})
                    received = plan.received(plan.entries(ledger, context))
                    result.update(plan_sha256=plan.sha256, received_units=received,
                                  topics=plan.topics, gaps=plan.data['gaps'],
                                  unassigned_units=[u for u, topics in plan.membership.items() if not topics])
        self._event('evidence_state', {'context': context}, result=result)
        return result

    def _artifact(self, label, value=None, raw=None, suffix='.json'):
        path = self._owned(self.directory / (label + '-' + uuid.uuid4().hex + suffix))
        write_new(path, raw if raw is not None else (dumps(value) + '\n').encode('utf-8'))
        return str(path)

    def _budget(self, arguments):
        budget = arguments.get('max_bytes', self.max_bytes)
        require(type(budget) is int and 1024 <= budget <= self.max_bytes,
                'max_bytes may only lower the frozen budget, with a minimum of 1024')
        return budget

    @staticmethod
    def _wire(value, mcp_id):
        if mcp_id is not _CLI:
            value = {'jsonrpc': '2.0', 'id': mcp_id, 'result': tool_result(value)}
        return len(dumps(value).encode('utf-8')) + 1

    def _page(self, meta, items, arguments, budget, mcp_id):
        offset, limit = arguments.get('offset', 0), arguments.get('limit', 20)
        require(type(offset) is int and type(limit) is int, 'offset and limit must be integers')
        value = dict(meta, **reader.page_items(items, offset, limit))
        while self._wire(value, mcp_id) > budget and value['items']:
            value['items'].pop()
            value['next_offset'] = offset + len(value['items'])
        require(self._wire(value, mcp_id) <= budget
                and (value['items'] or offset >= value['total']),
                'one locator entry exceeds max_bytes; lower metadata or raise the frozen budget')
        return value

    def _locate(self, state, arguments, budget, mcp_id):
        require(not arguments.get('ack'), 'locate cannot acknowledge original text')
        require(bool(arguments.get('path')) != bool(arguments.get('plan_path')),
                'locate requires exactly one path or plan_path')
        if arguments.get('plan_path'):
            plan = self._register_plan(state, self._input(arguments['plan_path']))
            require(str(plan.path) == state['active_plan'], 'cannot reactivate an older plan')
            outline = plan.outline()
            audit_path = self._artifact('plan-outline', outline)
            items = [dict(id=id_, path=unit['path'], sha256=unit['sha256'],
                          start=unit['start'], end=unit['end'], requires=unit['requires'],
                          topics=plan.membership[id_]) for id_, unit in plan.units.items()]
            meta = dict(status='located_plan', plan_path=str(plan.path), plan_sha256=plan.sha256,
                        audit_path=audit_path, unique_characters=outline['unique_characters'],
                        units=len(plan.units), topics=len(plan.topics),
                        gaps_count=len(outline['gaps']), unassigned_count=len(outline['unassigned_units']),
                        locator_only=True, evidence_status='unverified', research_complete=False)
        else:
            doc = self._document(state, arguments['path'], arguments.get('sha256'), register=True)
            mode = arguments.get('mode', 'index')
            require(mode in ('index', 'find'), 'locate mode must be index or find')
            items = doc.outline() if mode == 'index' else doc.locate(
                arguments.get('pattern'), arguments.get('regex', False))
            meta = dict(doc.meta(), status='located_source', locator_only=True)
        return self._page(meta, items, arguments, budget, mcp_id), None

    def _packet(self, doc, start, end, entry, context, arguments, budget, mcp_id, extra=None):
        end = len(doc.text) if end is None else end
        require(type(start) is int and type(end) is int and 0 <= start <= end <= len(doc.text),
                'invalid character range; locate again')
        count = arguments.get('max_chars', 12000)
        require(type(count) is int and 1 <= count <= 40000, 'max_chars must be 1..40000')
        force = arguments.get('force', False)
        require(type(force) is bool, 'force must be boolean')
        known = [] if force else entry['acknowledged']
        missing = reader.uncovered(start, end, known)
        if not missing:
            return dict(doc.meta(), status='empty' if start == end else 'already_acknowledged',
                        requested=[start, end], content='', context=context, next_start=None, **(extra or {}))
        a, remaining_end = missing[0]
        def payload(stop):
            receipt = digest(dumps([context, str(doc.path), doc.sha256, a, stop]).encode('utf-8'))
            remaining = reader.uncovered(start, end, known + [[a, stop]])
            return dict(doc.meta(), status='returned_unacknowledged', requested=[start, end],
                        returned=doc.location(a, stop), content=doc.text[a:stop], context=context,
                        receipt=receipt, next_start=remaining[0][0] if remaining else None,
                        requested_text_returned=not remaining,
                        starts_mid_line=a > 0 and doc.text[a - 1] not in '\n\f',
                        ends_mid_line=stop < len(doc.text) and doc.text[stop - 1] not in '\n\f',
                        **(extra or {}))
        low, high, fit = a + 1, min(a + count, remaining_end), None
        while low <= high:
            middle = (low + high) // 2
            if self._wire(payload(middle), mcp_id) <= budget:
                fit, low = middle, middle + 1
            else:
                high = middle - 1
        require(fit is not None, 'metadata plus one original character exceeds max_bytes')
        if fit < remaining_end and doc.text[fit - 1] != '\n':
            newline = doc.text.rfind('\n', a, fit)
            if newline >= a:
                fit = newline + 1
        value = payload(fit)
        entry['pending'][value['receipt']] = [a, fit]
        return value

    def _read(self, registry, arguments, budget, mcp_id):
        context = self._context(arguments.get('context'))
        with self._ledger(context) as ledger:
            self._ack(registry, ledger, context, arguments.get('ack'))
            if arguments.get('path'):
                doc = self._document(registry, arguments['path'], arguments.get('sha256'))
                require(not arguments.get('plan_path'), 'choose source path or plan_path')
                require(not (arguments.get('lines') and arguments.get('pages')), 'choose lines or pages')
                require(not ((arguments.get('lines') or arguments.get('pages'))
                            and ('start' in arguments or 'end' in arguments)),
                        'choose character offsets or lines/pages')
                selected = SimpleNamespace(lines=arguments.get('lines'), pages=arguments.get('pages'),
                                           start=arguments.get('start', 0), end=arguments.get('end'))
                a, b = reader.selected_range(doc, selected)
                value = self._packet(doc, a, b, reader.entry_for(ledger, context, doc),
                                     context, arguments, budget, mcp_id)
            else:
                require(not any(k in arguments for k in ('start', 'end', 'lines', 'pages', 'force', 'sha256')),
                        'plan reads use their complete declared ranges; locate extensions instead')
                plan = self._plan(registry, arguments)
                entries = plan.entries(ledger, context)
                pending = [(path, a, b) for path, ranges in plan.ranges.items() for start, end in ranges
                           for a, b in reader.uncovered(start, end, entries[path]['acknowledged'])]
                if pending:
                    value = self._bundle(plan, pending, ledger, context, arguments, budget, mcp_id)
                else:
                    value = dict(status='all_received_in_this_context', context=context,
                                 plan_sha256=plan.sha256, units=len(plan.units),
                                 evidence_status='unverified', research_complete=False)
            require(self._wire(value, mcp_id) <= budget, 'serialized response exceeds max_bytes')
        return value, None

    def _bundle(self, plan, pending, ledger, context, arguments, budget, mcp_id):
        """Fit nonadjacent ranges/files in one envelope with one atomic receipt."""
        max_chars = arguments.get('max_chars', 12000)
        require(type(max_chars) is int and 1 <= max_chars <= 40000, 'max_chars must be 1..40000')
        def block(path, a, b):
            doc = plan.docs[path]
            return dict(path=path, sha256=doc.sha256, returned=doc.location(a, b),
                        content=doc.text[a:b], starts_mid_line=a > 0 and doc.text[a - 1] not in '\n\f',
                        ends_mid_line=b < len(doc.text) and doc.text[b - 1] not in '\n\f')
        def payload(blocks):
            ranges = [dict(path=item['path'], sha256=item['sha256'],
                           start=item['returned']['start'], end=item['returned']['end']) for item in blocks]
            returned = {}
            for item in ranges:
                returned.setdefault(item['path'], []).append([item['start'], item['end']])
            left = [(path, x, y) for path, a, b in pending
                    for x, y in reader.uncovered(a, b, returned.get(path, []))]
            return dict(status='returned_unacknowledged', context=context, plan_sha256=plan.sha256,
                        blocks=blocks, receipt=self._bundle_receipt(context, ranges),
                        requested_text_returned=not left, remaining_ranges=len(left),
                        next_range=dict(path=left[0][0], start=left[0][1], end=left[0][2]) if left else None,
                        evidence_status='unverified', research_complete=False)
        blocks, count = [], 0
        for path, a, b in pending:
            low, high, fit = a + 1, min(b, a + max_chars - count), None
            while low <= high:
                middle = (low + high) // 2
                if self._wire(payload(blocks + [block(path, a, middle)]), mcp_id) <= budget:
                    fit, low = middle, middle + 1
                else:
                    high = middle - 1
            if fit is None:
                require(blocks, 'bundle metadata plus one original character exceeds max_bytes')
                break
            doc = plan.docs[path]
            if fit < b and doc.text[fit - 1] != '\n':
                newline = doc.text.rfind('\n', a, fit)
                if newline >= a:
                    fit = newline + 1
            blocks.append(block(path, a, fit))
            count += fit - a
            if fit < b or count >= max_chars:
                break
        value = payload(blocks)
        ranges = [dict(path=item['path'], sha256=item['sha256'], start=item['returned']['start'],
                       end=item['returned']['end']) for item in blocks]
        bundles = ledger.setdefault('bundles', {})
        require(isinstance(bundles, dict), 'invalid receipt bundle ledger')
        bundles[value['receipt']] = ranges
        return value

    def _check(self, registry, arguments, budget, mcp_id):
        context = self._context(arguments.get('context'))
        with self._ledger(context) as ledger:
            self._ack(registry, ledger, context, arguments.get('ack'))
            if not arguments.get('review_path'):
                require(not arguments.get('repair_whitespace'), 'review_path is required for quote repair')
                value = dict(status='acknowledged' if arguments.get('ack') else 'delivery_checked',
                             context=context, evidence_status='unverified', research_complete=False)
                if registry['active_plan']:
                    plan = self._plan(registry, arguments)
                    received = plan.received(plan.entries(ledger, context))
                    value.update(plan_sha256=plan.sha256, received_units=sum(received.values()),
                                 pending_units=sum(not n for n in received.values()))
                detail = None
            else:
                plan = self._plan(registry, arguments)
                path = self._input(arguments['review_path'])
                require(path.is_relative_to(self.root / 'output'), 'review_path must be inside root/output/')
                raw = path.read_bytes()
                review = strict_json(raw)
                require(isinstance(review, dict), 'review must be a JSON object')
                detail = plan.check(ledger, context, review)
                repair = arguments.get('repair_whitespace', True)
                require(type(repair) is bool, 'repair_whitespace must be boolean')
                repairs = []
                revised = deepcopy(review)
                if repair:
                    for issue in detail['quote_audit']['issues']:
                        suggestion = issue.get('suggestion')
                        if suggestion and suggestion['kind'] == 'unique_whitespace_only':
                            quote = revised['claims'][issue['claim_index']]['quotes'][issue['quote_index']]
                            original = suggestion['original_text']
                            require(''.join(quote['text'].split()) == ''.join(original.split()),
                                    'quote repair attempted a non-whitespace change')
                            repairs.append(dict(claim_index=issue['claim_index'], quote_index=issue['quote_index'],
                                                unit_id=issue['unit_id'], before=quote['text'], after=original,
                                                start=suggestion['start'], end=suggestion['end']))
                            quote['text'] = original
                repaired_path = None
                if repairs:
                    original_path = self._artifact('review-original', raw=raw)
                    revised_raw = (json.dumps(revised, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
                    repaired_path = self._artifact('review-repaired', raw=revised_raw)
                    diff = ''.join(difflib.unified_diff(raw.decode('utf-8').splitlines(keepends=True),
                                                       revised_raw.decode('utf-8').splitlines(keepends=True),
                                                       fromfile=str(path), tofile=repaired_path))
                    diff_path = self._artifact('review-diff', raw=diff.encode('utf-8'), suffix='.diff')
                    detail = plan.check(ledger, context, revised)
                    detail['whitespace_repairs'] = repairs
                    detail['original_review_path'] = original_path
                    detail['repaired_review_path'] = repaired_path
                    detail['diff_path'] = diff_path
                detail.update(review_path=str(path), review_sha256=digest(raw), context=context)
                audit_path = self._artifact('check-audit', detail)
                pending = sum(len(row['pending_delivery']) for row in detail['topics'].values())
                missing = sum(len(row['missing_from_review']) for row in detail['topics'].values())
                value = dict(status='coverage_checked', context=context, plan_sha256=plan.sha256,
                             coverage_complete=detail['coverage_complete'], evidence_status='unverified',
                             research_complete=False, pending_topic_units=pending,
                             missing_topic_units=missing, gaps_count=len(detail['gaps']),
                             unassigned_count=len(detail['unassigned_units']),
                             quote_issues=len(detail['quote_audit']['issues']),
                             repaired_quotes=len(repairs), audit_path=audit_path,
                             interpretation='Declared coverage and verbatim text only; semantic verification remains required.')
                if repaired_path:
                    value['repaired_review_path'] = repaired_path
                registry['checks'][context] = dict(value, review_path=repaired_path or str(path),
                    review_sha256=digest(Path(repaired_path).read_bytes()) if repaired_path else digest(raw))
            require(self._wire(value, mcp_id) <= budget, 'check summary exceeds max_bytes')
        return value, detail

    def _finish(self, registry, arguments, budget, mcp_id):
        context = self._context(arguments.get('context'))
        require(context == self.context, 'finish is only authorized for the configured main context')
        # The callback owns all business validation, snapshot compatibility and
        # completion publication. A final explicit ack/review can share this call.
        detail = None
        if arguments.get('ack') or arguments.get('review_path'):
            _, detail = self._check(registry, arguments, budget, mcp_id)
        if registry['active_plan']:
            plan = self._plan(registry, arguments)
            checked = registry['checks'].get(context)
            require(checked and checked.get('plan_sha256') == plan.sha256
                    and not any(checked.get(key, 1) for key in
                                ('pending_topic_units', 'missing_topic_units', 'quote_issues', 'unassigned_count')),
                    'check complete declared plan delivery and review coverage before finish')
            require(digest(self._input(checked['review_path']).read_bytes()) == checked['review_sha256'],
                    'checked review changed; check it again before finish')
        module = importlib.import_module('.research_runner', __package__) if __package__ else importlib.import_module('research_runner')
        handler = getattr(module, 'finish_native', None)
        require(callable(handler), 'research_runner.finish_native is unavailable')
        result = handler(deepcopy(self.config), deepcopy(arguments))
        require(isinstance(result, dict), 'completion handler must return a JSON object')
        if self._wire(result, mcp_id) > budget:
            full_path = self._artifact('finish-result', result)
            result = dict(status=result.get('status', 'completion_returned'), result_path=full_path)
        require(self._wire(result, mcp_id) <= budget, 'completion summary exceeds max_bytes')
        return result, detail

    def _event(self, name, arguments, result=None, error=None, detail=None):
        event = dict(schema=SCHEMA, timestamp=datetime.now(timezone.utc).isoformat(),
                     event_id=uuid.uuid4().hex, tool=name, arguments=arguments,
                     result=result, error=error)
        if detail is not None:
            event['detail'] = detail
        with self._lock('events.lock'):
            path = self._owned(self.directory / 'tool-events.jsonl')
            with path.open('a', encoding='utf-8') as sink:
                sink.write(dumps(event) + '\n')
                sink.flush()
                os.fsync(sink.fileno())

    def call(self, name, arguments, *, mcp_id=None, _mcp=False):
        wire_id = mcp_id if _mcp else _CLI
        try:
            require(name in TOOLS, 'unknown research tool: ' + str(name))
            require(isinstance(arguments, dict), 'tool arguments must be an object')
            budget = self._budget(arguments)
            with self._registry() as state:
                method = getattr(self, '_' + name.removeprefix('research_'))
                result, detail = method(state, arguments, budget, wire_id)
                require(self._wire(result, wire_id) <= budget, 'serialized response exceeds max_bytes')
            self._event(name, arguments, result=result, detail=detail)
            return result
        except Exception as error:
            self._event(name, arguments, error={'type': type(error).__name__, 'message': str(error)})
            raise


_CLI = object()


def tool_definitions():
    def definition(name, description, properties, required=(), extra=False):
        return dict(name=name, description=description,
                    inputSchema=dict(type='object', properties=properties,
                                     required=list(required), additionalProperties=extra))
    text = {'type': 'string'}
    integer = {'type': 'integer'}
    boolean = {'type': 'boolean'}
    shared = dict(context=text, ack=text, max_bytes=integer, plan_path=text)
    return [
        definition('research_locate', 'Locate/register every candidate without full text or semantic ranking. Use path OR plan_path. Pagination preserves total and next_offset; previews never count as received evidence.',
                   dict(path=text, plan_path=text, sha256=text, mode={'enum': ['index', 'find']},
                        pattern=text, regex=boolean, offset=integer, limit=integer, max_bytes=integer)),
        definition('research_read', 'Return one bounded original-text packet. Explicit context/epoch is required for each consumer; actual host caller is not authenticated. Ack only the one previous packet fully received in that same context. Without ack, text is replayed; plan sources and dependencies are merged without dropping units.',
                   dict(shared, path=text, sha256=text, start=integer, end=integer,
                        lines=text, pages=text, max_chars=integer, force=boolean), ('context',)),
        definition('research_check', 'Combine final explicit receipt acknowledgement and optional review JSON audit. Unique whitespace-only quote mismatches can be repaired into new files preserving original/diff. IDs, delivery, and verbatim quotes do not establish semantic verification or research completion.',
                   dict(shared, review_path=text, repair_whitespace=boolean), ('context',)),
        definition('research_finish', 'Request runner business validation and completion from the configured main context only. Optional final ack/review shares this call. The runner owns snapshot and stock-artifact checks; use its completion argument contract.',
                   dict(shared, review_path=text, repair_whitespace=boolean), ('context',), extra=True),
    ]


def serve(service, source=None, sink=None):
    """JSONL stdio MCP: initialize, tools/list, tools/call and notifications."""
    source, sink = source or sys.stdin, sink or sys.stdout
    initialized = False
    for line in source:
        id_ = None
        try:
            try:
                request = strict_json(line)
            except (ValueError, TypeError) as error:
                raise _RPCError(-32700, 'Parse error: ' + str(error)) from error
            if not isinstance(request, dict) or request.get('jsonrpc') != '2.0' or not isinstance(request.get('method'), str):
                raise _RPCError(-32600, 'Invalid Request')
            id_ = request.get('id')
            require(id_ is None or type(id_) in (str, int, float), 'invalid JSON-RPC id')
            require(not isinstance(id_, str) or len(id_) <= 200, 'JSON-RPC id is too long')
            method = request['method']
            params = request.get('params', {})
            if not isinstance(params, dict):
                raise _RPCError(-32602, 'Invalid params')
            if 'id' not in request:
                service._event(method, params, result={'status': 'notification_received'})
                continue
            if method == 'initialize':
                initialized = True
                result = dict(protocolVersion=params.get('protocolVersion', '2024-11-05'),
                              capabilities={'tools': {'listChanged': False}},
                              serverInfo={'name': 'research-local', 'version': '1.0.0'})
                service._event(method, params, result=result)
            elif not initialized:
                raise _RPCError(-32002, 'Server not initialized')
            elif method == 'tools/list':
                result = {'tools': tool_definitions()}
                service._event(method, params, result=result)
            elif method == 'tools/call':
                if not isinstance(params.get('name'), str) or not isinstance(params.get('arguments', {}), dict):
                    raise _RPCError(-32602, 'Invalid tool call params')
                try:
                    value = service.call(params['name'], params.get('arguments', {}), mcp_id=id_, _mcp=True)
                    result = tool_result(value)
                except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
                    result = tool_result({'status': 'not_verified', 'error': str(error)[:500]})
                    result['isError'] = True
            elif method == 'ping':
                result = {}
                service._event(method, params, result=result)
            else:
                raise _RPCError(-32601, 'Method not found')
            response = {'jsonrpc': '2.0', 'id': id_, 'result': result}
        except _RPCError as error:
            service._event('protocol_error', {'request': line.rstrip('\n')}, error={'code': error.code, 'message': str(error)})
            response = {'jsonrpc': '2.0', 'id': id_, 'error': {'code': error.code, 'message': str(error)[:500]}}
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            service._event('protocol_error', {'request': line.rstrip('\n')}, error={'code': -32600, 'message': str(error)})
            response = {'jsonrpc': '2.0', 'id': id_, 'error': {'code': -32600, 'message': str(error)[:500]}}
        sink.write(dumps(response) + '\n')
        sink.flush()


class _RPCError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('call', 'serve'))
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--tool', choices=TOOLS)
    parser.add_argument('--args', default='{}', help='JSON object; use --args-file for literal multiline data')
    parser.add_argument('--args-file', type=Path)
    arguments = parser.parse_args(argv)
    try:
        service = LocalResearchService(strict_json(arguments.config.read_bytes()))
        if arguments.command == 'serve':
            require(not arguments.tool and not arguments.args_file and arguments.args == '{}',
                    'serve receives tool arguments through stdio')
            serve(service)
        else:
            require(arguments.tool, 'call requires --tool')
            require(not arguments.args_file or arguments.args == '{}', 'choose --args or --args-file')
            args = strict_json(arguments.args_file.read_bytes() if arguments.args_file else arguments.args)
            result = service.call(arguments.tool, args)
            print(dumps(result))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(dumps({'status': 'not_verified', 'error': str(error)[:500]}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
