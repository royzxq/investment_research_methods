"""Methods-owned durable daily research queue. Explicit run; plan is read-only.

The daily budget counts listings, shared by both CLI generators. Sealed per-stock
receipts are the only input to the AI repository's preview/writeback consumer.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import importlib.util
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
    from .research_runner import (ROOT, read_request, run_batch, manifest, group_alive,
                                  check_codex_cli, observed_model, cancellation_scope, prepare_request)
    from .research_exchange import _strict_json, load_results, _timestamp
except ImportError:
    from research_runner import (ROOT, read_request, run_batch, manifest, group_alive,
                                 check_codex_cli, observed_model, cancellation_scope, prepare_request)
    from research_exchange import _strict_json, load_results, _timestamp

DAILY_LIMIT = 4
ZONE = ZoneInfo('Asia/Shanghai')


def journal(path, event, **fields):
    if path is None:
        return
    source=ROOT.parent/'ai_investment/src/infrastructure/research_loop_log.py'
    spec=importlib.util.spec_from_file_location('_shared_research_journal',source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.record(path,repository='investment_research_methods',stage='research',event=event,**fields)


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
    return dict(schema_version='research-queue/v1', entries={}, days={}, completed_events={})


def load_state(path):
    if not path.exists():
        if (path.parent/'initialized.json').exists() or any((path.parent/'sealed').glob('*.json')):
            raise ValueError('queue ledger missing after initialization; restore it before running')
        return new_state()
    state = _strict_json(path.read_bytes(), 'queue')
    if (set(state) != set(new_state()) or state['schema_version'] != 'research-queue/v1'
            or any(not isinstance(state[k], dict) for k in ('entries', 'days', 'completed_events'))):
        raise ValueError('invalid queue ledger; refuse resetting daily budget')
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
            continue  # Retry requires a fresh immutable input, not a reused single-use run.
        first = previous['first_seen'] if previous and previous['status'] != 'completed' else now.isoformat()
        state['entries'][key] = dict(record, first_seen=first, status='pending')


def reserve(state, now, *, held=frozenset()):
    today = now.astimezone(ZONE).date().isoformat()
    used = state['days'].setdefault(today, {})
    remaining = max(0, DAILY_LIMIT - len(used))
    candidates = [e for e in state['entries'].values() if e['status']=='pending'
                  and e['valuation_date']==today and e['task_id'] not in used
                  and (e['task_id'], e['event_key']) not in held]
    candidates.sort(key=lambda e: (e['priority'], e['first_seen'], e['task_id']))
    chosen = candidates[:remaining]
    for entry in chosen:
        entry.update(status='reserved', budget_date=today)
        used[entry['task_id']] = entry['event_key']
    return chosen


def run_entry(entry, methods, state_root, clis, timeout, cancelled, event_log=None, run_id=None):
    request_path = Path(entry['request'])
    request, raw, _ = read_request(request_path)
    if hashlib.sha256(raw).hexdigest() != entry['request_sha256']:
        raise ValueError('admitted request changed')
    # Prepare once before recording any provider failures; an incomplete run
    # directory must never prevent the second provider from receiving its pack.
    run = prepare_request(request_path, methods)
    results, succeeded = [], False
    for generator in request['generators']:
        folder = run / 'execution' / entry['task_id'] / generator
        saved = folder / 'entry.json'
        if (folder / 'launched.json').exists() and not saved.exists():
            process_path = folder / 'process.json'
            process = _strict_json(process_path.read_bytes(), 'process') if process_path.exists() else {}
            if process.get('pid') and group_alive(process['pid']):
                raise RuntimeError('interrupted research process group still exists; no duplicate launch')
            # Ambiguous claims never launch again. Preserve their failure evidence.
            stamp = datetime.now(ZONE).isoformat()
            failure = dict(task_id=entry['task_id'], generator=generator, status='failed',
                           reason='interrupted after durable claim; original attempt retained',
                           started_at=process.get('started_at', stamp), completed_at=stamp,
                           report=None, price_map=None)
            atomic_json(saved, failure)
        if not saved.exists():
            if cancelled.is_set():
                raise RuntimeError('scheduler cancelled; unlaunched provider remains pending')
            try:
                journal(event_log,'provider_dispatch',run_id=run_id,batch_id=entry['batch_id'],
                        task_id=entry['task_id'],generator=generator,details={'execution':str(folder)})
                launched = any((run/'execution'/entry['task_id']/g/'launched.json').exists()
                               for g in request['generators'])
                run_batch(request_path, methods, generator=generator, cli=clis[generator],
                          timeout=timeout, task_ids=[entry['task_id']], cancelled=cancelled,
                          launch_date=None if launched else entry['budget_date'])
            except (ValueError, OSError) as exc:
                if not saved.exists():
                    stamp = datetime.now(ZONE).isoformat()
                    atomic_json(saved, dict(task_id=entry['task_id'], generator=generator,
                                            status='failed', reason=str(exc), started_at=stamp,
                                            completed_at=stamp, report=None, price_map=None))
        result = _strict_json(saved.read_bytes(), 'entry')
        journal(event_log,'provider_finished',run_id=run_id,batch_id=entry['batch_id'],
                task_id=entry['task_id'],generator=generator,status=result['status'],
                details=dict(reason=result['reason'],actual_model=observed_model(folder,generator),
                             report=result.get('report'),price_map=result.get('price_map'),execution=str(folder)))
        succeeded = succeeded or result['status']=='completed'
        result_manifest = folder / 'queue-result.json'
        if not result_manifest.exists():
            atomic_json(result_manifest, manifest(request, raw, [result]))
        load_results(result_manifest, request_path, methods)
        results.append(dict(generator=generator, manifest=str(result_manifest.relative_to(methods)),
                            manifest_sha256=hashlib.sha256(result_manifest.read_bytes()).hexdigest(),
                            actual_model=observed_model(folder, generator)))
    seal = dict(schema_version='research-sealed/v1', task_id=entry['task_id'],
                batch_id=entry['batch_id'], event_key=entry['event_key'],
                request=entry['request'], request_sha256=entry['request_sha256'],
                budget_date=entry['budget_date'], results=results)
    path = state_root / 'sealed' / f"{entry['batch_id']}-{entry['task_id']}.json"
    if path.exists():
        if _strict_json(path.read_bytes(), 'seal') != seal:
            raise ValueError('sealed receipt already exists with different contents')
    else:
        atomic_json(path, seal)
    entry.update(status='completed' if succeeded else 'failed', sealed=str(path))
    journal(event_log,'stock_sealed',run_id=run_id,batch_id=entry['batch_id'],task_id=entry['task_id'],
            status=entry['status'],details={'seal':str(path)})


def tick(exchange, methods=ROOT, state_root=None, *, execute=False, clis=None, timeout=3600,
         once_daily=False,event_log=None):
    methods = Path(methods).resolve()
    state_root = Path(state_root or methods / 'output/research_queue')
    now = datetime.now(ZONE)
    if not execute:
        records, rejected = scan_requests(exchange, now)
        held = load_manual_holds(state_root)
        state = load_state(state_root / 'state.json')
        merge_candidates(state, records, now)
        selected = reserve(state, now, held=held)
        manual_held = sorted(e['task_id'] for e in state['entries'].values()
                             if (e['task_id'], e['event_key']) in held)
        return dict(selected=selected, rejected=rejected, mode='plan', manual_held=manual_held)
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
        if once_daily:
            atomic_json(check_path,dict(checked_on=now.date().isoformat(),checked_at=now.isoformat()))
        records, rejected = scan_requests(exchange, now)
        merge_candidates(state, records, now)
        eligible = [e for e in state['entries'].values() if (e['task_id'], e['event_key']) not in held]
        manual_held = sorted(e['task_id'] for e in state['entries'].values()
                             if (e['task_id'], e['event_key']) in held)
        journal(event_log,'queue_checked',run_id=run_id,
                details=dict(candidates=len(eligible),manual_held=manual_held,rejected=rejected))
        active = any(e['status'] in {'reserved','running','interrupted'} for e in eligible)
        available = any(e['status']=='pending' and e['valuation_date']==now.date().isoformat()
                        and e['task_id'] not in state['days'].get(now.date().isoformat(), {})
                        for e in eligible)
        if not active and (not available or len(state['days'].get(now.date().isoformat(), {})) >= DAILY_LIMIT):
            atomic_json(state_path, state)
            pending = [e for e in eligible if e['status'] in {'pending','failed'}]
            atomic_json(state_root/'refresh-needed.json', pending)
            journal(event_log,'no_research',run_id=run_id,details=dict(deferred=len(pending)))
            return dict(mode='run', used=len(state['days'].get(now.date().isoformat(), {})),
                        deferred=len(pending), rejected=rejected, failures=[], manual_held=manual_held)
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
        failures = []
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
                run_entry(entry, methods, state_root, clis, timeout, cancelled,event_log,run_id)
                if entry['status']=='completed':
                    state['completed_events'][entry['event_key']] = entry['sealed']
                else:
                    failures.append(dict(task_id=entry['task_id'], reason='all providers failed'))
            except (ValueError, OSError, RuntimeError) as exc:
                entry.update(status='interrupted', error=str(exc))
                failures.append(dict(task_id=entry['task_id'], reason=str(exc)))
                journal(event_log,'stock_failed',run_id=run_id,task_id=entry['task_id'],details={'reason':str(exc)})
            atomic_json(state_path, state)
        pending = [e for e in eligible if e['status'] in {'pending','failed'}]
        atomic_json(state_root / 'refresh-needed.json', pending)
        journal(event_log,'finished',run_id=run_id,details=dict(deferred=len(pending),failures=failures))
        return dict(mode='run', used=len(state['days'].get(now.date().isoformat(), {})),
                    deferred=len(pending), rejected=rejected, failures=failures, manual_held=manual_held)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('plan', 'run'))
    parser.add_argument('--exchange', type=Path, default=ROOT.parent / 'ai_investment/investment_rawdata/data_packs/research_exchange')
    parser.add_argument('--state-root', type=Path)
    parser.add_argument('--codex-cli', default=shutil.which('codex'))
    parser.add_argument('--claude-cli', default=shutil.which('claude'))
    parser.add_argument('--timeout-seconds', type=float, default=3600)
    parser.add_argument('--scheduled',action='store_true',help='Consume the daily check even when no input exists; no later admission today')
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error('timeout must be positive')
    try:
        result = tick(args.exchange, state_root=args.state_root, execute=args.mode=='run',
                      clis={'codex': args.codex_cli, 'claude': args.claude_cli}, timeout=args.timeout_seconds,
                      once_daily=args.scheduled,
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
