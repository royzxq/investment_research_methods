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
    return dict(schema_version=SCHEMA, status=process.get('status'), attempt=process.get('attempt'),
                wall_seconds=_duration(process.get('started_at'), process.get('completed_at')),
                profile_id=profile.get('profile_id'), profile_revision=profile.get('revision'),
                execution_plan_sha256=process.get('execution_plan_sha256'),
                sessions=sessions, sources=sources, issues=sorted(set(issues)),
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
