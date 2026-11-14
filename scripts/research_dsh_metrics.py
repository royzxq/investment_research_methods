"""Read-only DSH attempt accounting; never participates in research acceptance.

Session logs are the sole counter source (CLI events only identify the root).
No prompts, command strings, tool arguments/results or credentials are emitted.
Usage follows DSH's replacement/retry semantics, not a sum of stream chunks.
Missing usage and auxiliary search billing remain unknown, never zero dollars.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import statistics

try:
    from .research_dsh import MAX_EVENT_LINE
except ImportError:
    from research_dsh import MAX_EVENT_LINE

SCHEMA = 'research-dsh-metrics/v1'
TOKEN_FIELDS = ('inputTokens', 'outputTokens', 'cacheReadTokens', 'cacheWriteTokens', 'totalTokens')


def recovery_metrics(folder):
    """Summarize recovery evidence separately from provider usage and acceptance.

    No source URLs, requests, excerpts or reviewer prose leave the evidence store.
    Reading/use claims remain claims, and do not establish final report citations.
    """
    root = Path(folder) / 'evidence-recovery'
    if not root.exists() and not root.is_symlink():
        return None
    result = dict(schema_version='research-evidence-effects/v1', cases=0, attempts=0,
        categories={}, triggers={}, document_kinds={}, retrieval_statuses={}, deduplicated_requests=0,
        supplemental_tool_calls=0, document_download_attempts=0, recovery_wall_ms_sum=0,
        artifacts_checked_cases=0, reads_recorded=0, cases_read=0,
        use_assessments_recorded=0, cases_with_declared_use=0, cases_awaiting_assessment=0,
        final_citations_verified=None, facts_independently_verified=None, sources=[], issues=[])

    def checked(directory, record):
        name = record['file']
        if (not isinstance(name, str) or Path(name).name != name or directory.is_symlink()
                or directory.resolve() != directory):
            raise ValueError('unsafe recovery artifact')
        fd = os.open(directory / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError('not a regular recovery artifact')
            raw = stream.read(32 * 1024 * 1024 + 1)
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) > 32 * 1024 * 1024 or (record.get('sha256') and record['sha256'] != digest):
            raise ValueError('changed recovery artifact')
        return raw, digest

    if root.is_symlink() or not root.is_dir():
        result['issues'].append('unsafe_recovery_directory')
        return result
    root = root.resolve()
    for directory in sorted(root.iterdir()):
        if not re.fullmatch(r'[a-f0-9]{64}', directory.name):
            continue
        try:
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError('unsafe gap directory')
            events = sorted(directory.glob('event-*.json'))
            if not events or len(events) > 1000 or not re.fullmatch(r'event-\d{6}\.json', events[-1].name):
                raise ValueError('missing or invalid recovery event')
            raw, digest = checked(directory, {'file': events[-1].name})
            state = json.loads(raw)
            if (state['schema_version'] != 'research-evidence-recovery/v1' or state['gap_id'] != directory.name
                    or state['revision'] != int(events[-1].stem.split('-')[1])
                    or state['category'] not in ('document', 'pagination')
                    or state['retrieval_status'] not in ('detected', 'running', 'retrieved', 'partial', 'conflict', 'failed', 'cancelled', 'blocked')
                    or type(state['attempts']) is not int or not 0 <= state['attempts'] <= 3
                    or type(state['deduplicated_requests']) is not int or state['deduplicated_requests'] < 0
                    or not isinstance(state['reads'], list) or len(state['reads']) > 100
                    or not isinstance(state['reviews'], list) or len(state['reviews']) > 100):
                raise ValueError('invalid recovery record')
            # Validate every referenced source before calling the case traceable.
            for page in state['pages']:
                checked(directory, page['raw'])
            if state.get('document'):
                subdir = state['document_directory']
                if not isinstance(subdir, str) or not re.fullmatch(r'document-[1-3]', subdir):
                    raise ValueError('invalid document directory')
                docdir = directory / subdir
                manifest, _ = checked(docdir, state['document_manifest'])
                document = json.loads(manifest)
                if document != state['document']:
                    raise ValueError('changed document manifest')
                checked(docdir, document['raw'])
                for part in document['parts']:
                    checked(docdir, part)
            reads = {x['receipt_id'] for x in state['reads']}
            if any(x['receipt_id'] not in reads or x['disposition'] not in
                   ('used_for_scope', 'used_partial', 'unresolved', 'rejected', 'not_used') for x in state['reviews']):
                raise ValueError('unbound use assessment')
            counters = {key: state.get(key, 0) for key in
                        ('supplemental_tool_calls', 'document_download_attempts', 'recovery_wall_ms')}
            if any(type(value) is not int or value < 0 for value in counters.values()):
                raise ValueError('invalid recovery counters')
            triggers = state.get('triggers', [])
            if not isinstance(triggers, list) or any(x not in
                    ('pdf', 'web_truncated_or_empty', 'pagination_incomplete', 'explicit_document') for x in triggers):
                raise ValueError('invalid recovery triggers')
            kind = state.get('document', {}).get('kind')
            if kind is not None and kind not in ('pdf', 'html', 'text'):
                raise ValueError('invalid document kind')
            result['cases'] += 1
            result['attempts'] += state['attempts']
            result['deduplicated_requests'] += state['deduplicated_requests']
            for key, target in [('supplemental_tool_calls', 'supplemental_tool_calls'),
                                ('document_download_attempts', 'document_download_attempts'),
                                ('recovery_wall_ms', 'recovery_wall_ms_sum')]:
                result[target] += counters[key]
            for trigger in set(triggers):
                result['triggers'][trigger] = result['triggers'].get(trigger, 0) + 1
            if kind:
                result['document_kinds'][kind] = result['document_kinds'].get(kind, 0) + 1
            for field, value in [('categories', state['category']), ('retrieval_statuses', state['retrieval_status'])]:
                result[field][value] = result[field].get(value, 0) + 1
            result['artifacts_checked_cases'] += int(bool(state['pages'] or state.get('document')))
            result['reads_recorded'] += len(reads)
            result['cases_read'] += int(bool(reads))
            result['use_assessments_recorded'] += len(state['reviews'])
            # A later correction for the same read supersedes its earlier use claim.
            latest = {x['receipt_id']: x for x in state['reviews']}
            result['cases_with_declared_use'] += int(any(x['disposition'].startswith('used_') for x in latest.values()))
            result['cases_awaiting_assessment'] += int(not latest or any(x['disposition'] == 'unresolved' for x in latest.values()))
            result['sources'].append(dict(path=str(events[-1].relative_to(root.parent)), sha256=digest))
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            result['issues'].append('invalid_or_changed_recovery_case')
    result['issues'] = sorted(set(result['issues']))
    return result


def context_metrics(folder):
    """Recorded context activity and final citation audit, never semantic proof.

    Unlike the final runner audit this read-only summary does not reopen source
    documents. Reopened counts are explicit model reads; automatic pin/citation
    checks are kept separate. No excerpts, URLs or annotation prose are emitted.
    """
    root = Path(folder) / 'evidence-context'
    if not root.exists() and not root.is_symlink():
        return None
    result = dict(schema_version='research-evidence-context-effects/v1', sources=0, anchors=0,
        pins=0, stances={}, required_citations=0, citations_generated=0, events={},
        final_report_audit=None, sources_reverified=False, semantic_verification='not_performed', issues=[])

    def read(path):
        if path.is_symlink() or path.parent.resolve() != path.parent or not path.is_file():
            raise ValueError('unsafe context record')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError('not a regular context record')
            raw = stream.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError('oversized context record')
        return json.loads(raw)

    try:
        if root.is_symlink() or not root.is_dir():
            raise ValueError('unsafe context directory')
        root = root.resolve()
        pins = {}
        for category, prefix in [('sources', 's'), ('anchors', 'e'), ('pins', 'p'), ('citations', 'c')]:
            directory = root / category
            if directory.is_symlink():
                raise ValueError('unsafe context directory')
            files = sorted(directory.glob('*.json'))
            if len(files) > 1024:
                raise ValueError('too many context records')
            for path in files:
                record = read(path)
                raw = json.dumps(record['data'], ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
                if record['id'] != prefix + '-' + hashlib.sha256(raw).hexdigest() or path.name != record['id'] + '.json':
                    raise ValueError('changed context record')
                if category == 'pins':
                    data = record['data']
                    if type(data['revision']) is not int or data['revision'] < 1:
                        raise ValueError('invalid pin revision')
                    previous = pins.get(data['evidence_id'])
                    if previous is None or previous['revision'] < data['revision']:
                        pins[data['evidence_id']] = data
                else:
                    result[category if category != 'citations' else 'citations_generated'] += 1
        result['pins'] = len(pins)
        for pin in pins.values():
            if pin['stance'] not in ('support', 'counterevidence', 'unresolved', 'rejected'):
                raise ValueError('invalid stance')
            result['stances'][pin['stance']] = result['stances'].get(pin['stance'], 0) + 1
            result['required_citations'] += int(pin['required_citation'] and pin['stance'] != 'rejected')
        events = sorted((root / 'events').glob('*.json'))
        if len(events) > 8192:
            raise ValueError('too many context events')
        for path in events:
            event = read(path)
            kind = event['kind']
            if event['schema_version'] != 'research-evidence-context-event/v1' or kind not in (
                    'opened', 'reopened', 'pin_source_checked', 'citation_source_checked', 'audit_source_checked', 'indexing_failed'):
                raise ValueError('invalid context event')
            result['events'][kind] = result['events'].get(kind, 0) + 1
        audit_path = root.parent / 'runner/evidence-citations.json'
        if audit_path.exists() or audit_path.is_symlink():
            audit = read(audit_path)
            if (audit['schema_version'] != 'research-evidence-citations/v1'
                    or audit['status'] not in ('mechanical_pass', 'failed', 'not_exercised')
                    or not re.fullmatch(r'[a-f0-9]{64}', audit['report_sha256'])
                    or any(type(audit[k]) is not int or audit[k] < 0 for k in ('citation_markers', 'verified_evidence', 'required_evidence'))
                    or any(x['code'] not in ('unknown_citation', 'citation_text_or_locator_changed',
                        'citation_source_unavailable_or_changed', 'required_evidence_not_cited') for x in audit['issues'])):
                raise ValueError('invalid final citation audit')
            result['final_report_audit'] = {k: audit[k] for k in ('status', 'report_sha256', 'citation_markers', 'verified_evidence', 'required_evidence')}
            result['final_report_audit']['issue_codes'] = sorted({x['code'] for x in audit['issues']})
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        result['issues'].append('invalid_or_changed_context_store')
    return result


def _rows(path):
    digest = hashlib.sha256()
    rows, invalid = [], 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('metrics requires a regular log file')
        while True:
            raw = stream.readline(MAX_EVENT_LINE + 1)
            if not raw:
                break
            if len(raw) > MAX_EVENT_LINE:
                raise ValueError('metrics event exceeds supported bound')
            digest.update(raw)
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
                if not isinstance(row, dict):
                    raise ValueError()
                rows.append(row)
            except (ValueError, UnicodeError):
                invalid += 1
    return rows, digest.hexdigest(), invalid


def _number(value):
    return type(value) in (int, float) and value >= 0 and value < float('inf')


def _usage(data, kind):
    if kind == 'assistant/message' and isinstance(data.get('usage'), dict):
        return data['usage']
    stream = data.get('stream', [])
    if isinstance(stream, list):
        # Native v4 stores raw chunks inside timed records. Text/reasoning
        # runs may be packed, but usage is always a {type: chunk, chunk: ...}.
        for record in reversed(stream):
            if not isinstance(record, dict) or record.get('type') != 'chunk':
                continue
            chunk = record.get('chunk')
            if isinstance(chunk, dict) and chunk.get('type') == 'usage':
                return chunk['usage'] if isinstance(chunk.get('usage'), dict) else None
    return None


def _duration(start, end):
    try:
        value = (datetime.fromisoformat(end.replace('Z', '+00:00')) -
                 datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds()
        return round(value, 3) if value >= 0 else None
    except (TypeError, ValueError, AttributeError):
        return None


def session_metrics(rows):
    calls, results, jobs, usage = {}, {}, {}, {}
    retries = Counter()
    counts = Counter()
    duplicates = missing_usage = invalid_records = compaction_failures = 0
    seen = set()
    for row in rows:
        seq = row.get('seq')
        if type(seq) is int:
            if seq in seen:
                duplicates += 1
                continue
            seen.add(seq)
        kind, data = row.get('type'), row.get('data', {})
        if not isinstance(kind, str) or not isinstance(data, dict):
            invalid_records += 1
            continue
        counts[kind] += 1
        step = (data.get('turn'), data.get('step'))
        if kind in ('assistant/message', 'assistant/attempt', 'llm/retry-started') and not all(
                type(value) is int and value >= 0 for value in step):
            invalid_records += 1
            continue
        if kind == 'llm/retry-started':
            retries[step] += 1
        elif kind in ('assistant/message', 'assistant/attempt'):
            value = _usage(data, kind)
            if value is not None:
                usage[(*step, retries[step])] = value
            else:
                missing_usage += 1
        elif kind == 'tool/call':
            call_id, name = data.get('callId'), data.get('name')
            if isinstance(call_id, str) and isinstance(name, str):
                # Emit only bounded conventional tool identifiers, never arbitrary text.
                name = name if re.fullmatch(r'[\w./:-]{1,160}', name) else 'unrecognized-tool'
                calls[call_id] = (name, row.get('time'))
        elif kind == 'tool/result':
            message = data.get('message', {})
            if isinstance(message, dict) and isinstance(message.get('toolCallId'), str):
                results[message['toolCallId']] = (message.get('isError'), row.get('time'))
        elif kind == 'job/settled' and data.get('kind') == 'bash':
            job_id = data.get('jobId')
            if isinstance(job_id, str):
                match = re.fullmatch(r'exit code: (-?\d+)', str(data.get('detail', '')))
                jobs[job_id] = int(match[1]) if match else None
        elif kind == 'compaction/end' and data.get('error') is not None:
            compaction_failures += 1
    tools = {}
    for call_id, (name, start) in calls.items():
        item = tools.setdefault(name, dict(calls=0, results=0, errors=0, unknown_error_status=0,
                                          missing_results=0, duration_ms=0, timed_results=0))
        item['calls'] += 1
        if call_id not in results:
            item['missing_results'] += 1
            continue
        error, end = results[call_id]
        item['results'] += 1
        item['errors'] += error is True
        item['unknown_error_status'] += type(error) is not bool
        if _number(start) and _number(end) and end >= start:
            item['duration_ms'] += end - start
            item['timed_results'] += 1
    tokens = {}
    for field in TOKEN_FIELDS:
        known = [value[field] for value in usage.values() if _number(value.get(field))]
        tokens[field] = dict(known_sum=sum(known), known_samples=len(known),
                             missing_samples=len(usage) - len(known))
    return dict(tools=tools, usage_samples=len(usage), tokens=tokens,
                assistant_records_without_usage=missing_usage,
                assistant_records=counts['assistant/message'] + counts['assistant/attempt'],
                llm_retries=sum(retries.values()),
                auxiliary_search_requests=counts['web/deepseek-search-llm-request'],
                compactions=counts['compaction/end'] - compaction_failures,
                compaction_attempts=dict(started=counts['compaction/start'], failed=compaction_failures,
                    incomplete=max(0, counts['compaction/start'] - counts['compaction/end'])),
                bash_jobs=dict(settled=len(jobs), nonzero_exit=sum(v is not None and v != 0 for v in jobs.values()),
                               unknown_exit=sum(v is None for v in jobs.values())),
                duplicate_sequences=duplicates, invalid_records=invalid_records)


def summarize(folder, process=None):
    folder = Path(folder).resolve()
    if process is None:
        try:
            process = json.loads((folder / 'process.json').read_text())
        except (OSError, ValueError):
            process = {}
    root_id = None
    issues, sources, sessions = [], [], []
    try:
        rows, digest, invalid = _rows(folder / 'events.jsonl')
        sources.append(dict(path='events.jsonl', sha256=digest, invalid_lines=invalid, counter_source=False))
        roots = {r.get('sessionId') for r in rows if r.get('type') == 'session' and isinstance(r.get('sessionId'), str)}
        if len(roots) == 1:
            root_id = next(iter(roots))
    except (OSError, ValueError):
        issues.append('missing_or_unreadable_cli_events')
    persistence = folder / 'dsh-sessions'
    if persistence.is_symlink():
        issues.append('symlink_session_root_rejected')
        paths = []
    else:
        # Spawned agents use bare UUIDs; only the root has a session- prefix.
        paths = sorted(persistence.glob('*/*/session.v4.jsonl'))
    for path in paths:
        relative = path.relative_to(folder)
        if any(parent.is_symlink() for parent in (path, path.parent, path.parent.parent)):
            issues.append('symlink_session_file_rejected')
            continue
        try:
            rows, digest, invalid = _rows(path)
        except (OSError, ValueError):
            issues.append('unreadable_session_file')
            continue
        header = rows[0] if rows else {}
        if header.get('type') != 'session' or header.get('version') != 4 or header.get('id') != path.parent.name:
            issues.append('invalid_session_header')
            continue
        sources.append(dict(path=str(relative), sha256=digest, invalid_lines=invalid, counter_source=True))
        sessions.append(dict(session_id=path.parent.name,
                             role='main' if path.parent.name == root_id else 'child_or_unattributed',
                             **session_metrics(rows)))
    if not any(s['role'] == 'main' for s in sessions):
        issues.append('missing_main_session')
    if any(s['invalid_lines'] for s in sources):
        issues.append('malformed_log_lines')
    if any(s['duplicate_sequences'] for s in sessions):
        issues.append('duplicate_sequences')
    if any(s['invalid_records'] for s in sessions):
        issues.append('invalid_session_records')
    profile = process.get('execution_profile', {})
    try:
        recovery = recovery_metrics(folder)
    except (OSError, ValueError, TypeError):
        recovery = dict(schema_version='research-evidence-effects/v1', issues=['unreadable_recovery_store'])
    context = context_metrics(folder)
    return dict(schema_version=SCHEMA, status=process.get('status'), attempt=process.get('attempt'),
                wall_seconds=_duration(process.get('started_at'), process.get('completed_at')),
                profile_id=profile.get('profile_id'), profile_revision=profile.get('revision'),
                execution_plan_sha256=process.get('execution_plan_sha256'),
                sessions=sessions, sources=sources, issues=sorted(set(issues)),
                **({'evidence_recovery': recovery} if recovery is not None else {}),
                **({'evidence_context': context} if context is not None else {}),
                cost_usd=None, cost_complete=False,
                accounting_notes=['inputTokens is uncached input; cacheRead/cacheWrite are separate',
                                  'known_sum is a lower bound when usage fields or failed calls are absent',
                                  'auxiliary model/search/fetch billing is not fully reported in DSH logs',
                                  'tool duration sums can overlap; wall_seconds includes the attempt only'])


def aggregate(attempts):
    tools = defaultdict(Counter)
    tokens = {field: Counter() for field in TOKEN_FIELDS}
    for attempt in attempts:
        for session in attempt['sessions']:
            for field, value in session['tokens'].items():
                tokens[field].update(value)
            for name, data in session['tools'].items():
                tools[name].update(data)
    successful = [a['wall_seconds'] for a in attempts if a['status'] == 'completed' and a['wall_seconds'] is not None]
    return dict(attempts=len(attempts), statuses=dict(Counter(a['status'] or 'unknown' for a in attempts)),
                retries=sum(type(a['attempt']) is int and a['attempt'] > 1 for a in attempts),
                completed_median_seconds=statistics.median(successful) if successful else None,
                tools={k: dict(v) for k, v in sorted(tools.items())},
                tokens={k: dict(v) for k, v in tokens.items()},
                assistant_records_without_usage=sum(s['assistant_records_without_usage'] for a in attempts for s in a['sessions']),
                attempt_wall_seconds=sum(a['wall_seconds'] for a in attempts if a['wall_seconds'] is not None),
                auxiliary_search_requests=sum(s['auxiliary_search_requests'] for a in attempts for s in a['sessions']),
                bash_nonzero_exits=sum(s['bash_jobs']['nonzero_exit'] for a in attempts for s in a['sessions']),
                cost_usd=None, cost_complete=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-root', type=Path, default=Path('output/runs/investment'))
    parser.add_argument('--from-date', required=True)
    parser.add_argument('--through-date', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for date in (args.from_date, args.through_date):
        datetime.strptime(date, '%Y-%m-%d')
    attempts = []
    for day in sorted(args.runs_root.iterdir()):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day.name) or not args.from_date <= day.name <= args.through_date:
            continue
        # Explicit attempt layout excludes unrelated benchmark and nested artifact logs.
        paths = list(day.glob('*/execution/*/dsh/process.json')) + list(day.glob('*/execution/*/dsh/retry-1/process.json'))
        for path in sorted(set(paths)):
            value = summarize(path.parent)
            value['attempt_path'] = str(path.parent.resolve())
            attempts.append(value)
    document = dict(schema_version='research-dsh-metrics-batch/v1', summary=aggregate(attempts),
                    by_status={status: aggregate([a for a in attempts if a['status'] == status])
                               for status in ('completed', 'failed')}, attempts=attempts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(document['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
