"""Methods-owned durable daily research queue. Explicit run; plan is read-only.

The daily budget counts listings, shared by both CLI generators. Sealed per-stock
receipts are the only input to the AI repository's preview/writeback consumer.
"""
from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
from datetime import datetime, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from zoneinfo import ZoneInfo
from uuid import uuid4

try:
    from .research_runner import (ROOT, read_request, run_provider, manifest, group_alive,
                                  check_codex_cli, observed_model, cancellation_scope, prepare_request, execution_folder, retryable_failure)
    from .research_exchange import _strict_json, load_results, _timestamp, ENTRY_KEYS
    from .research_loop_log import record
except ImportError:
    from research_runner import (ROOT, read_request, run_provider, manifest, group_alive,
                                 check_codex_cli, observed_model, cancellation_scope, prepare_request, execution_folder, retryable_failure)
    from research_exchange import _strict_json, load_results, _timestamp, ENTRY_KEYS
    from research_loop_log import record

DAILY_LIMIT = 4
MAX_CONCURRENCY = 3
RESEARCH_INTERVAL = timedelta(days=7)
LISTING = r'(?:SH|SZ)-\d{6}|HK-\d{5}'
ZONE = ZoneInfo('Asia/Shanghai')


def journal(path, event, **fields):
    if path is None:
        return
    record(path, repository='investment_research_methods', stage='research', event=event, **fields)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.queue-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def queue_lock(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root / 'queue.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def new_state():
    return dict(schema_version='research-queue/v1', entries={}, days={}, completed_events={}, last_started={})


def load_state(path):
    if not path.exists():
        if (path.parent/'initialized.json').exists() or any((path.parent/'sealed').glob('*.json')):
            raise ValueError('queue ledger missing after initialization; restore it before running')
        return new_state()
    state = _strict_json(path.read_bytes(), 'queue')
    if (not isinstance(state, dict) or set(state) not in (set(new_state()), set(new_state())-{'last_started'})
            or state['schema_version'] != 'research-queue/v1'
            or any(not isinstance(state[k], dict) for k in ('entries', 'days', 'completed_events'))):
        raise ValueError('invalid queue ledger; refuse resetting daily budget')
    history = state.setdefault('last_started', {})
    if not isinstance(history, dict):
        raise ValueError('invalid research start history')
    for task, started in history.items():
        if (not re.fullmatch(LISTING, task) or not isinstance(started, dict)
                or set(started) != {'started_at', 'batch_id', 'request_sha256'}
                or not isinstance(started['batch_id'], str)
                or not re.fullmatch(r'[0-9a-f]{32}', started['batch_id'])
                or not isinstance(started['request_sha256'], str)
                or not re.fullmatch(r'[0-9a-f]{64}', started['request_sha256'])):
            raise ValueError('invalid research start history')
        _timestamp(started['started_at'], 'research started_at')
    for day, used in state['days'].items():
        datetime.strptime(day, '%Y-%m-%d')
        if not isinstance(used, dict) or len(used) > DAILY_LIMIT:
            raise ValueError('invalid daily budget ledger')
    for key, entry in state['entries'].items():
        if (not isinstance(entry, dict) or entry.get('task_id') != key
                or entry.get('status') not in {'pending','reserved','running','interrupted','completed','failed'}):
            raise ValueError('invalid queue entry')
        if entry['status'] in {'reserved','running','interrupted'} and key not in state['days'].get(entry.get('budget_date'), {}):
            raise ValueError('active entry missing durable daily reservation')
    return state


def sync_started(state, methods):
    """Rebuild missing starts from immutable runner evidence, never from reservations.

    New launched_at timestamps follow Popen; legacy preflight timestamps use
    completion instead. A PID proves launch; missing evidence remains conservative.
    Both providers in a batch share its earliest start, including resumed runs.
    """
    rounds, uncertain = {}, {}
    for request_path in sorted((methods/'output/runs/investment').glob('*/*/request.json')):
        if not re.fullmatch(r'[0-9a-f]{32}', request_path.parent.name):
            continue  # The retired runner used a different layout and no current contract.
        claims = sorted([*request_path.parent.glob('execution/*/*/launched.json'),
                         *request_path.parent.glob('execution/*/*/retry-1/launched.json')])
        if not claims:
            continue
        request, raw, _ = read_request(request_path)
        if (request['batch_id'] != request_path.parent.name
                or request['valuation_date'] != request_path.parent.parent.name):
            raise ValueError('research history request path mismatch')
        digest = hashlib.sha256(raw).hexdigest()
        tasks = {task['task_id'] for task in request['tasks']}
        for claim_path in claims:
            folder = claim_path.parent
            endpoint = folder.parent if folder.name == 'retry-1' else folder
            task, generator = endpoint.parent.name, endpoint.name
            claim = _strict_json(claim_path.read_bytes(), 'research claim')
            if (task not in tasks or generator not in request['generators']
                    or not isinstance(claim, dict) or set(claim) != {'claimed_at', 'request_sha256'}
                    or claim['request_sha256'] != digest):
                raise ValueError('invalid research history claim')
            claimed = _timestamp(claim['claimed_at'], 'research claimed_at')
            if claimed < _timestamp(request['created_at'], 'request created_at'):
                raise ValueError('research claim precedes request')
            started, proven = datetime.now(ZONE), False
            process_path = folder/'process.json'
            if process_path.exists():
                process = _strict_json(process_path.read_bytes(), 'research process')
                if (not isinstance(process, dict) or process.get('task_id') != task
                        or process.get('generator') != generator
                        or process.get('status') not in {'starting','running','completed','failed'}):
                    raise ValueError('invalid research history process')
                started = _timestamp(process.get('started_at'), 'research process started_at')
                if started < claimed:
                    raise ValueError('research process precedes claim')
                pid = process.get('pid')
                if pid is None and process['status'] == 'failed':
                    continue  # Runner positively recorded a failure before Popen.
                if pid is not None and (type(pid) is not int or pid <= 0):
                    raise ValueError('invalid research process pid')
                if process['status'] in {'running','completed'} and pid is None:
                    raise ValueError('launched research process missing pid')
                proven = pid is not None
                if process.get('launched_at') is not None:
                    launched = _timestamp(process['launched_at'], 'research launched_at')
                    if not proven or launched != started:
                        raise ValueError('invalid actual research launch timestamp')
                elif process.get('completed_at') is not None:
                    completed = _timestamp(process['completed_at'], 'research process completed_at')
                    if completed < started:
                        raise ValueError('invalid research process chronology')
                    started = completed  # Legacy started_at preceded Popen; delay safely.
                else:
                    started = datetime.now(ZONE)  # Unfinished legacy evidence has no safe exact start.
            elif (folder/'entry.json').exists():
                result = _strict_json((folder/'entry.json').read_bytes(), 'research entry')
                if (not isinstance(result, dict) or set(result) != ENTRY_KEYS
                        or result['task_id'] != task or result['generator'] != generator
                        or result['status'] not in {'completed','failed'}):
                    raise ValueError('invalid research history entry')
                started = _timestamp(result['started_at'], 'research entry started_at')
                completed = _timestamp(result['completed_at'], 'research entry completed_at')
                if not claimed <= started <= completed:
                    raise ValueError('invalid research entry chronology')
                started, proven = completed, result['status'] == 'completed'
            identity = (task, request['batch_id'], digest)
            evidence = rounds if proven else uncertain
            evidence[identity] = min(evidence.get(identity, started), started)
    for identity, started in uncertain.items():
        rounds.setdefault(identity, started)
    for (task, batch, digest), started in rounds.items():
        previous = state['last_started'].get(task)
        if previous:
            old = _timestamp(previous['started_at'], 'research started_at')
            if (previous['batch_id'], previous['request_sha256']) != (batch, digest) and old >= started:
                continue
        state['last_started'][task] = dict(started_at=started.astimezone(ZONE).isoformat(),
                                           batch_id=batch, request_sha256=digest)
    return rounds


def cooldown_until(state, entry, now):
    previous = state['last_started'].get(entry['task_id'])
    if previous:
        eligible = _timestamp(previous['started_at'], 'research started_at') + RESEARCH_INTERVAL
        if now < eligible:
            return eligible.astimezone(ZONE).isoformat()
    return None


def release_reservation(state, entry):
    state['days'].get(entry.get('budget_date'), {}).pop(entry['task_id'], None)
    entry.pop('budget_date', None)
    entry['status'] = 'pending'


def apply_cooldown(state, methods, now, held):
    started_rounds = sync_started(state, methods)
    skipped = []
    for entry in state['entries'].values():
        identity = (entry['task_id'], entry['batch_id'], entry['request_sha256'])
        active = entry['status'] in {'reserved','running','interrupted'}
        if (entry['task_id'], entry['event_key']) in held:
            if active:
                # Retire a stopped automatic round before merging fresh evidence.
                # Keep its files, charged quota and launch history; a live or
                # uncertain process still blocks replacement and new admission.
                execution = methods/'output/runs/investment'/entry['valuation_date']/entry['batch_id']/'execution'/entry['task_id']
                for claim in [*execution.glob('*/launched.json'), *execution.glob('*/retry-1/launched.json')]:
                    require_stopped_process(claim.parent)
                if identity in started_rounds:
                    entry.update(status='failed', error='manual handoff; original automatic round retained')
                else:
                    release_reservation(state, entry)
            continue
        if active and identity in started_rounds:
            continue  # Completing the original pair is not a fresh round.
        next_eligible = cooldown_until(state, entry, now)
        if active and (next_eligible or entry['budget_date'] != now.astimezone(ZONE).date().isoformat()):
            release_reservation(state, entry)
        if (next_eligible and entry['status'] == 'pending'
                and (entry['task_id'], entry['event_key']) not in held):
            skipped.append(dict(task_id=entry['task_id'], batch_id=entry['batch_id'],
                                event_key=entry['event_key'], next_eligible_at=next_eligible))
    return sorted(skipped, key=lambda item: item['task_id'])


def load_manual_holds(root):
    """User-declared handoffs suppress an event, without claiming completion."""
    path = Path(root)/'manual_holds.json'
    if not path.exists():
        return set()
    document = _strict_json(path.read_bytes(), 'manual holds')
    if (not isinstance(document, dict) or set(document) != {'schema_version', 'tasks'}
            or document['schema_version'] != 'research-manual-holds/v1'
            or not isinstance(document['tasks'], dict)):
        raise ValueError('invalid manual holds document')
    held = set()
    for task, entry in document['tasks'].items():
        if (not re.fullmatch(r'(?:SH|SZ)-\d{6}|HK-\d{5}', task)
                or not isinstance(entry, dict) or set(entry) != {'event_key', 'reason', 'created_at'}
                or not isinstance(entry['event_key'], str)
                or not re.fullmatch(r'[0-9a-f]{64}', entry['event_key'])
                or not isinstance(entry['reason'], str) or not entry['reason'].strip()):
            raise ValueError('invalid manual hold entry')
        _timestamp(entry['created_at'], 'manual hold created_at')
        held.add((task, entry['event_key']))
    return held


def scan_requests(exchange, now):
    records, rejected = [], []
    for path in sorted(Path(exchange).glob('requests/*/request.json')):
        try:
            batch_records = []
            request, raw, _ = read_request(path)
            if _timestamp(request['created_at'], 'created_at') > now:
                raise ValueError('future request')
            for task in request['tasks']:
                trigger = task['data_pack_meta'].get('research_trigger')
                if trigger is None:  # Historical/manual requests are not automatic admissions.
                    continue
                if (not isinstance(trigger, dict) or set(trigger) != {'schema_version', 'priority', 'event_key', 'evidence'}
                        or trigger['schema_version'] != 'research-trigger/v1'
                        or type(trigger['priority']) is not int or not 1 <= trigger['priority'] <= 4
                        or not isinstance(trigger['evidence'], dict)):
                    raise ValueError('invalid research scheduling evidence')
                code, market = task['code'].split('.')
                identity = dict(market='HK' if market=='HK' else 'A', code=code,
                                sources=sorted(task['sources']), evidence=trigger['evidence'])
                event_key = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False,
                                                      allow_nan=False).encode()).hexdigest()
                if trigger['event_key'] != event_key:
                    raise ValueError('trigger evidence hash mismatch')
                batch_records.append(dict(task_id=task['task_id'], event_key=event_key,
                                    priority=trigger['priority'], request=str(path.resolve()),
                                    request_sha256=hashlib.sha256(raw).hexdigest(),
                                    batch_id=request['batch_id'], valuation_date=request['valuation_date'],
                                    created_at=request['created_at']))
            records.extend(batch_records)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            rejected.append(dict(path=str(path), reason=str(exc)))
    return records, rejected


def merge_candidates(state, records, now):
    for record in sorted(records, key=lambda r: (r['created_at'], r['batch_id'])):
        key = record['task_id']
        if record['event_key'] in state['completed_events']:
            continue
        previous = state['entries'].get(key)
        if previous and previous['status'] in {'reserved', 'running', 'interrupted'}:
            continue
        if previous and previous['created_at'] > record['created_at']:
            continue
        if previous and previous['status'] == 'failed' and previous['request_sha256'] == record['request_sha256']:
            continue  # Exhausted rounds need fresh input after cooldown; do not reopen a seal.
        first = previous['first_seen'] if previous and previous['status'] != 'completed' else now.isoformat()
        state['entries'][key] = dict(record, first_seen=first, status='pending')


def reserve(state, now, *, held=frozenset()):
    today = now.astimezone(ZONE).date().isoformat()
    used = state['days'].setdefault(today, {})
    remaining = max(0, DAILY_LIMIT - len(used))
    candidates = [e for e in state['entries'].values() if e['status']=='pending'
                  and e['valuation_date']==today and e['task_id'] not in used
                  and (e['task_id'], e['event_key']) not in held
                  and cooldown_until(state, e, now) is None]
    candidates.sort(key=lambda e: (e['priority'], e['first_seen'], e['task_id']))
    chosen = candidates[:remaining]
    for entry in chosen:
        entry.update(status='reserved', budget_date=today)
        used[entry['task_id']] = entry['event_key']
    return chosen


def prepare_entry(entry, methods):
    request_path = Path(entry['request'])
    request, raw, _ = read_request(request_path)
    if hashlib.sha256(raw).hexdigest() != entry['request_sha256']:
        raise ValueError('admitted request changed')
    # Prepare once before recording any provider failures; an incomplete run
    # directory must never prevent the second provider from receiving its pack.
    run = prepare_request(request_path, methods)
    return request, raw, run


def require_stopped_process(folder):
    """A durable claim without launch/stop evidence may hide an orphaned CLI."""
    path = folder / 'process.json'
    process = _strict_json(path.read_bytes(), 'process') if path.exists() else {}
    if not isinstance(process, dict):
        raise ValueError('invalid research process record')
    pid = process.get('pid')
    if ((folder / 'launched.json').exists()
            and ('pid' not in process or pid is None and process.get('status') != 'failed')):
        raise RuntimeError(f'previous research launch uncertain; inspect attempt before recovery: {folder}')
    if pid is not None:
        if type(pid) is not int or pid <= 0:
            raise ValueError('invalid research process pid')
        if group_alive(pid):
            raise RuntimeError('research process group still exists; preserve result and concurrency slot')
    return process


def run_provider_entry(entry, generator, request, raw, run, methods, clis, timeout,
                       cancelled, event_log=None, run_id=None):
    task = next(task for task in request['tasks'] if task['task_id']==entry['task_id'])
    # Retrying stays in the same worker slot. The coordinator receives only the
    # terminal outcome, so a first failure cannot prematurely seal a stock.
    for attempt in (1, 2):
        folder = execution_folder(run, task, generator, attempt)
        saved = folder / 'entry.json'
        if (folder / 'launched.json').exists() and not saved.exists():
            process = require_stopped_process(folder)
            stamp = datetime.now(ZONE).isoformat()
            atomic_json(saved, dict(task_id=entry['task_id'], generator=generator, status='failed',
                                   reason='interrupted after durable claim; original attempt retained',
                                   started_at=process.get('started_at', stamp), completed_at=stamp,
                                   report=None, price_map=None))
        if not saved.exists():
            if cancelled.is_set():
                raise RuntimeError('scheduler cancelled; unlaunched provider remains pending')
            try:
                journal(event_log,'provider_dispatch',run_id=run_id,batch_id=entry['batch_id'],
                        task_id=entry['task_id'],generator=generator,
                        details={'execution':str(folder),'attempt':attempt})
                run_provider(run, request, raw, task, generator, clis[generator], methods,
                             timeout, cancelled, launch_date=entry['budget_date'], attempt=attempt)
            except (ValueError, OSError) as exc:
                if not saved.exists():
                    if cancelled.is_set():
                        raise RuntimeError('scheduler cancelled; unlaunched provider remains pending') from exc
                    process_path = folder/'process.json'
                    process = _strict_json(process_path.read_bytes(), 'process') if process_path.exists() else {}
                    if process.get('pid') and group_alive(process['pid']):
                        raise RuntimeError('research process group still exists; preserve active attempt') from exc
                    stamp = datetime.now(ZONE).isoformat()
                    atomic_json(saved, dict(task_id=entry['task_id'], generator=generator,
                                            status='failed', reason=str(exc), started_at=stamp,
                                            completed_at=stamp, report=None, price_map=None))
        result = _strict_json(saved.read_bytes(), 'entry')
        require_stopped_process(folder)
        model = observed_model(folder, generator)
        retry = attempt == 1 and result['status'] == 'failed' and retryable_failure(folder)
        journal(event_log,'provider_finished',run_id=run_id,batch_id=entry['batch_id'],
                task_id=entry['task_id'],generator=generator,status=result['status'],
                details=dict(reason=result['reason'],actual_model=model,attempt=attempt,
                             retryable=retry,report=result.get('report'),
                             price_map=result.get('price_map'),execution=str(folder)))
        result_manifest = folder / 'queue-result.json'
        if not result_manifest.exists():
            atomic_json(result_manifest, manifest(request, raw, [result]))
        load_results(result_manifest, Path(entry['request']), methods)
        if retry:
            if cancelled.is_set():
                raise RuntimeError('scheduler cancelled; retry remains pending without a final seal')
            journal(event_log,'provider_retry_scheduled',run_id=run_id,batch_id=entry['batch_id'],
                    task_id=entry['task_id'],generator=generator,
                    details=dict(reason=result['reason'],attempt=2,max_attempts=2,execution=str(folder/'retry-1')))
            continue
        return result['status'], dict(generator=generator, manifest=str(result_manifest.relative_to(methods)),
                                     manifest_sha256=hashlib.sha256(result_manifest.read_bytes()).hexdigest(),
                                     actual_model=model)


def seal_entry(entry, state_root, request, results, event_log=None, run_id=None):
    succeeded = any(results[g][0]=='completed' for g in request['generators'])
    seal = dict(schema_version='research-sealed/v1', task_id=entry['task_id'],
                batch_id=entry['batch_id'], event_key=entry['event_key'],
                request=entry['request'], request_sha256=entry['request_sha256'],
                budget_date=entry['budget_date'], results=[results[g][1] for g in request['generators']])
    path = state_root / 'sealed' / f"{entry['batch_id']}-{entry['task_id']}.json"
    if path.exists():
        if _strict_json(path.read_bytes(), 'seal') != seal:
            raise ValueError('sealed receipt already exists with different contents')
    else:
        atomic_json(path, seal)
    entry.update(status='completed' if succeeded else 'failed', sealed=str(path))
    journal(event_log,'stock_sealed',run_id=run_id,batch_id=entry['batch_id'],task_id=entry['task_id'],
            status=entry['status'],details={'seal':str(path)})


def reject_live_previous_attempts(state, methods):
    """An orphaned old CLI must not sit outside the new concurrency budget."""
    for entry in state['entries'].values():
        if entry['status'] not in {'reserved','running','interrupted'}:
            continue
        execution = methods/'output/runs/investment'/entry['valuation_date']/entry['batch_id']/'execution'/entry['task_id']
        for claim in [*execution.glob('*/launched.json'), *execution.glob('*/retry-1/launched.json')]:
            require_stopped_process(claim.parent)


def tick(exchange, methods=ROOT, state_root=None, *, execute=False, clis=None, timeout=3600,
         once_daily=False,event_log=None,max_concurrency=MAX_CONCURRENCY):
    if type(max_concurrency) is not int or not 1 <= max_concurrency <= MAX_CONCURRENCY:
        raise ValueError(f'max_concurrency must be an integer from 1 to {MAX_CONCURRENCY}')
    methods = Path(methods).resolve()
    state_root = Path(state_root or methods / 'output/research_queue')
    now = datetime.now(ZONE)
    if execute and once_daily and now.hour < 5:
        # Calendar wakeups are only a clock gate, not a research check. A host
        # timezone change or DST must never consume today's marker before 05:00.
        return dict(mode='run', status='not_due', failures=[], rejected=[])
    if not execute:
        records, rejected = scan_requests(exchange, now)
        held = load_manual_holds(state_root)
        state = load_state(state_root / 'state.json')
        apply_cooldown(state, methods, now, held)
        merge_candidates(state, records, now)
        cooldown_skipped = apply_cooldown(state, methods, now, held)
        selected = reserve(state, now, held=held)
        manual_held = sorted(e['task_id'] for e in state['entries'].values()
                             if (e['task_id'], e['event_key']) in held)
        return dict(selected=selected, rejected=rejected, mode='plan', manual_held=manual_held, cooldown_skipped=cooldown_skipped)
    with queue_lock(state_root), cancellation_scope() as cancelled:
        run_id='research-'+uuid4().hex
        check_path=state_root/'daily-check.json'
        if once_daily and check_path.exists():
            checked=_strict_json(check_path.read_bytes(),'daily research check')
            if (not isinstance(checked,dict) or set(checked)!={'checked_on','checked_at'}
                    or not isinstance(checked['checked_on'],str)
                    or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',checked['checked_on'])
                    or checked['checked_on']>now.date().isoformat()
                    or _timestamp(checked['checked_at'],'checked_at').astimezone(ZONE).date().isoformat()!=checked['checked_on']):
                raise ValueError('invalid daily research check; refuse a second admission')
            if checked['checked_on']==now.date().isoformat():
                journal(event_log,'already_checked',run_id=run_id)
                return dict(mode='run',status='already_checked',failures=[],rejected=[])
        journal(event_log,'check_started',run_id=run_id)
        held = load_manual_holds(state_root)
        state_path = state_root / 'state.json'
        state = load_state(state_path)
        reject_live_previous_attempts(state, methods)
        if once_daily:
            atomic_json(check_path,dict(checked_on=now.date().isoformat(),checked_at=now.isoformat()))
        records, rejected = scan_requests(exchange, now)
        apply_cooldown(state, methods, now, held)
        merge_candidates(state, records, now)
        cooldown_skipped = apply_cooldown(state, methods, now, held)
        for skipped in cooldown_skipped:
            journal(event_log,'cooldown_skipped',run_id=run_id,task_id=skipped['task_id'],
                    batch_id=skipped['batch_id'],details=skipped)
        eligible = [e for e in state['entries'].values() if (e['task_id'], e['event_key']) not in held]
        manual_held = sorted(e['task_id'] for e in state['entries'].values()
                             if (e['task_id'], e['event_key']) in held)
        journal(event_log,'queue_checked',run_id=run_id,
                details=dict(candidates=len(eligible),manual_held=manual_held,rejected=rejected))
        active = any(e['status'] in {'reserved','running','interrupted'} for e in eligible)
        available = any(e['status']=='pending' and e['valuation_date']==now.date().isoformat()
                        and e['task_id'] not in state['days'].get(now.date().isoformat(), {})
                        and cooldown_until(state, e, now) is None
                        for e in eligible)
        if not active and (not available or len(state['days'].get(now.date().isoformat(), {})) >= DAILY_LIMIT):
            atomic_json(state_path, state)
            pending = [e for e in eligible if e['status'] in {'pending','failed'}]
            atomic_json(state_root/'refresh-needed.json', pending)
            journal(event_log,'no_research',run_id=run_id,details=dict(deferred=len(pending)))
            return dict(mode='run', used=len(state['days'].get(now.date().isoformat(), {})),
                        deferred=len(pending), rejected=rejected, failures=[], manual_held=manual_held, cooldown_skipped=cooldown_skipped)
        clis = clis or {g: shutil.which(g) for g in ('codex', 'claude')}
        # Fail before reserving any daily slots on invalid executables.
        for generator in ('codex', 'claude'):
            if not clis.get(generator) or not os.access(clis[generator], os.X_OK):
                raise ValueError(f'{generator} executable unavailable; no quota reserved')
        check_codex_cli(clis['codex'], methods)
        reserve(state, now, held=held)
        atomic_json(state_path, state)
        journal(event_log,'quota_reserved',run_id=run_id,details=dict(
            used=len(state['days'][now.date().isoformat()]),
            selected=[dict(task_id=e['task_id'],priority=e['priority']) for e in eligible if e['status']=='reserved']))
        if not (state_root/'initialized.json').exists():
            atomic_json(state_root/'initialized.json', dict(created_at=now.isoformat()))
        failures, contexts, jobs, outcomes, errors = [], {}, deque(), {}, {}
        def persist_entry(entry, error=None):
            if error is not None:
                entry.update(status='interrupted', error=str(error))
                failures.append(dict(task_id=entry['task_id'], reason=str(error)))
                journal(event_log,'stock_failed',run_id=run_id,task_id=entry['task_id'],details={'reason':str(error)})
            elif entry['status']=='completed':
                entry.pop('error', None)
                state['completed_events'][entry['event_key']] = entry['sealed']
            elif entry['status']=='failed':
                failures.append(dict(task_id=entry['task_id'], reason='all providers failed'))
            started_rounds = sync_started(state, methods)
            identity = (entry['task_id'], entry['batch_id'], entry['request_sha256'])
            if identity not in started_rounds:
                state['days'].get(entry.get('budget_date'), {}).pop(entry['task_id'], None)
                if entry['status'] == 'interrupted':
                    entry['status'] = 'pending'
                    entry.pop('budget_date', None)
            atomic_json(state_path, state)

        for entry in sorted(eligible, key=lambda e: (e['priority'], e['first_seen'], e['task_id'])):
            if entry['status'] not in {'reserved', 'running', 'interrupted'}:
                continue
            if cancelled.is_set():
                break
            actual_today = datetime.now(ZONE).date().isoformat()
            run = methods/'output/runs/investment'/entry['valuation_date']/entry['batch_id']
            if entry['budget_date'] != actual_today and not any(
                    (run/'execution'/entry['task_id']/g/'launched.json').exists() for g in ('codex','claude')):
                state['days'][entry['budget_date']].pop(entry['task_id'], None)
                entry['status'] = 'pending'
                atomic_json(state_path, state)
                continue
            entry['status'] = 'running'
            atomic_json(state_path, state)
            try:
                request, raw, run = prepare_entry(entry, methods)
                contexts[entry['task_id']] = (entry, request)
                outcomes[entry['task_id']] = {}
                jobs.extend((entry, generator, request, raw, run) for generator in request['generators'])
            except (ValueError, OSError, RuntimeError) as exc:
                persist_entry(entry, exc)
        journal(event_log,'parallel_dispatch_started',run_id=run_id,
                details=dict(max_concurrency=max_concurrency, max_attempts=2, providers=len(jobs)))
        active = {}
        with ThreadPoolExecutor(max_workers=max_concurrency) as pool:
            try:
                while active or jobs and not cancelled.is_set():
                    while jobs and len(active)<max_concurrency and not cancelled.is_set():
                        entry, generator, request, raw, run = jobs.popleft()
                        future = pool.submit(run_provider_entry, entry, generator, request, raw, run,
                                             methods, clis, timeout, cancelled, event_log, run_id)
                        active[future] = (entry, generator)
                    if not active:
                        break
                    finished, _ = wait(active, timeout=.25, return_when=FIRST_COMPLETED)
                    for future in finished:
                        entry, generator = active.pop(future)
                        task_id = entry['task_id']
                        try:
                            outcomes[task_id][generator] = future.result()
                        except (ValueError, OSError, RuntimeError) as exc:
                            if isinstance(exc, RuntimeError):
                                # Cancellation or an old group still occupies a slot:
                                # stop admission rather than release it into new work.
                                cancelled.set()
                            errors[task_id] = str(exc)
                            outcomes[task_id][generator] = None
                        request = contexts[task_id][1]
                        if len(outcomes[task_id]) == len(request['generators']):
                            try:
                                if task_id in errors:
                                    raise RuntimeError(errors[task_id])
                                seal_entry(entry, state_root, request, outcomes[task_id], event_log, run_id)
                                persist_entry(entry)
                            except (ValueError, OSError, RuntimeError) as exc:
                                cancelled.set()  # Even a transient coordinator write failure stops admission.
                                persist_entry(entry, exc)
            except BaseException:
                cancelled.set()
                raise
        for task_id, (entry, request) in contexts.items():
            if len(outcomes[task_id]) < len(request['generators']):
                persist_entry(entry, errors.get(task_id, 'scheduler cancelled; unlaunched provider remains pending'))
        pending = [e for e in eligible if e['status'] in {'pending','failed'}]
        atomic_json(state_root / 'refresh-needed.json', pending)
        journal(event_log,'finished',run_id=run_id,details=dict(deferred=len(pending),failures=failures))
        return dict(mode='run', used=len(state['days'].get(now.date().isoformat(), {})),
                    deferred=len(pending), rejected=rejected, failures=failures, manual_held=manual_held, cooldown_skipped=cooldown_skipped)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('plan', 'run'))
    parser.add_argument('--exchange', type=Path, default=ROOT.parent / 'ai_investment/investment_rawdata/data_packs/research_exchange')
    parser.add_argument('--state-root', type=Path)
    parser.add_argument('--codex-cli', default=shutil.which('codex'))
    parser.add_argument('--claude-cli', default=shutil.which('claude'))
    parser.add_argument('--timeout-seconds', type=float, default=3600)
    parser.add_argument('--max-concurrency',type=int,choices=range(1,MAX_CONCURRENCY+1),default=MAX_CONCURRENCY,
                        help='Maximum live Codex/Claude research CLI processes combined (default: 3)')
    parser.add_argument('--scheduled',action='store_true',help='Consume the daily check even when no input exists; no later admission today')
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error('timeout must be positive')
    try:
        result = tick(args.exchange, state_root=args.state_root, execute=args.mode=='run',
                      clis={'codex': args.codex_cli, 'claude': args.claude_cli}, timeout=args.timeout_seconds,
                      once_daily=args.scheduled,
                      max_concurrency=args.max_concurrency,
                      event_log=ROOT.parent/'ai_investment/logs/research_loop/events.jsonl' if args.mode=='run' else None)
    except BlockingIOError:
        result = dict(mode=args.mode, status='already_running')
    except (ValueError,OSError,RuntimeError) as exc:
        journal(ROOT.parent/'ai_investment/logs/research_loop/events.jsonl','check_failed',details={'reason':str(exc)})
        result=dict(mode=args.mode,failures=[{'reason':str(exc)}],rejected=[])
    print(json.dumps(result, ensure_ascii=False))
    return 2 if result.get('failures') or result.get('rejected') else 0


if __name__ == '__main__':
    raise SystemExit(main())
