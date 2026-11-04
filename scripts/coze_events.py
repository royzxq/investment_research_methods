"""Sealed research -> durable event outbox -> isolated CLI worker.

No live dispatch without activation, transport enablement and per-pack review.
Only reconcile scans seals; the primary path is an O(1) post-seal notification.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import timezone
import fcntl
import json
from pathlib import Path
import plistlib
import sys
import time

try:
    from . import research_coze as adapter, coze_cli as transport
except ImportError:
    import research_coze as adapter
    import coze_cli as transport

ROOT = Path(__file__).resolve().parents[1]
# The installed Coze executable uses /usr/bin/env node. launchd's default
# system-only PATH cannot find Homebrew Node; never copy interactive exports
# (which may contain credentials) into a generated service definition.
LAUNCHD_PATH = '/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'


def settings(methods):
    path = Path(methods)/'config/coze_events.json'
    if not path.exists():
        return dict(enabled=False, dispatch_enabled=False, not_before=None)
    cfg = transport.read(path)
    transport.require(cfg.get('schema_version') == 'coze-events-config/v1', 'unsupported event config')
    transport.require(type(cfg.get('enabled')) is bool and type(cfg.get('dispatch_enabled')) is bool,
                      'explicit event switches required')
    if cfg['enabled']:
        transport.require(cfg.get('not_before') is not None, 'activation cutoff required; never inherit historical eligibility')
        transport.timestamp(cfg['not_before'])
    transport.require(type(cfg.get('recovery_interval_seconds')) is int and cfg['recovery_interval_seconds'] >= 3600,
                      'recovery interval must be at least hourly')
    return cfg


def outbox(methods):
    return Path(methods)/'output/research_queue/coze-events'


def valid_key(key):
    transport.require(len(key) == 64 and all(c in '0123456789abcdef' for c in key), 'invalid event key')


def research_event_time(context, cutoff):
    """Use hash-verified research receipts, never file mtime or restart time.

    Legacy seals have no independent publication clock. Latest provider
    completion is the recorded research event; request epoch is an additional
    guard so re-sealing/recovering an old batch cannot turn it into a new one.
    """
    boundary = transport.timestamp(cutoff)
    transport.require(transport.timestamp(context['request']['created_at']) >= boundary,
                      'research batch predates activation')
    completed = max(transport.timestamp(row['completed_at']) for row in context['entries'].values())
    transport.require(completed >= boundary, 'research completion predates activation')
    return completed.astimezone(timezone.utc).isoformat()


@contextmanager
def lock(methods):
    root = outbox(methods)
    transport.mkdirs(root)
    with (root/'worker.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def enqueue(seal_path, methods=ROOT, request=None):
    """A notification, not authorization to send. Idempotent by seal bytes."""
    methods = Path(methods).resolve()
    cfg = settings(methods)
    if not cfg['enabled']:
        return None
    path = Path(seal_path).resolve(strict=True)
    transport.require(path.parent == methods/'output/research_queue/sealed', 'event outside seal directory')
    raw = path.read_bytes()
    seal = json.loads(raw)
    # Supplements must never recursively create more third opinions.
    if seal.get('schema_version') not in {'research-sealed/v1','research-sealed/v2','research-sealed-recovery/v1'}:
        return None
    bound = Path(seal['request'])
    request_raw = bound.read_bytes()
    transport.require(transport.digest(request_raw) == seal['request_sha256'], 'event request hash changed')
    request = json.loads(request_raw)  # Never trust a caller's unbound request.
    if transport.timestamp(request['created_at']) < transport.timestamp(cfg['not_before']):
        return None
    key = transport.digest(raw)
    receipt = dict(schema_version='coze-sealed-event/v1', key=key, seal=str(path),
                   seal_sha256=key, request_sha256=seal['request_sha256'],
                   created_at=request['created_at'], task_id=seal['task_id'])
    # Immutable payload first, then a recoverable wake-up marker. Reconcile can
    # repair either crash gap without resetting any existing job or send claim.
    transport.immutable(outbox(methods)/'events'/f'{key}.json', transport.encoded(receipt))
    job_path = outbox(methods)/'jobs'/f'{key}.json'
    if not job_path.exists() or transport.read(job_path)['phase'] in {
            'ready','watching','blocked_dispatch','awaiting_result_review'}:
        transport.immutable(outbox(methods)/'pending'/key, b'event\n')
    return key


def reconcile(methods=ROOT):
    """Explicit low frequency repair, gated to the authorized activation epoch."""
    cfg = settings(methods)
    if not cfg['enabled']:
        return dict(disabled=True, repaired=0)
    count, errors = 0, []
    with lock(methods):
        for path in sorted((Path(methods)/'output/research_queue/sealed').glob('*.json')):
            try:
                if enqueue(path, methods) is not None:
                    count += 1
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append(dict(seal=path.name, error_type=type(exc).__name__))
        transport.atomic(outbox(methods)/'reconcile-errors.json', errors)
    return dict(repaired=count, errors=errors)


def approve(key, methods=ROOT, *, public_input_reviewed=False):
    valid_key(key)
    transport.require(public_input_reviewed is True, 'read the full frozen pack before approving')
    with lock(methods):
        path = outbox(methods)/'jobs'/f'{key}.json'
        job = transport.read(path)
        transport.require(job['phase'] == 'awaiting_public_review', 'job cannot be reapproved/retried')
        job.update(public_input_reviewed=True, phase='ready')
        transport.atomic(path, job)
        transport.immutable(outbox(methods)/'pending'/key, b'event\n')
        return job


def restore_job(context, methods, cli_cfg):
    """Rebuild derived job state from an existing, explicitly reviewed claim.

    Local atomic ledger reads only: recovery is never an auth/history call or
    a new review decision. In particular, a newer round cannot strand an
    accepted/unknown send merely because its derived job was lost.
    """
    intent_path = (Path(methods)/'output/research_queue/coze'/
                   (context['seal']['batch_id']+'-'+context['task']['task_id'])/'intent.json')
    if not intent_path.exists():
        return None
    intent = adapter.read(intent_path)
    if intent.get('transport') != 'cli':
        return None
    expected = dict(base_seal=str(context['path']), base_sha256=context['base_sha256'],
                    batch_id=context['seal']['batch_id'], task_id=context['task']['task_id'],
                    code=context['task']['code'], name=context['task']['name'],
                    valuation_date=context['request']['valuation_date'],
                    pack_sha256=context['task']['data_pack']['sha256'])
    transport.require(all(intent.get(k) == v for k, v in expected.items()), 'restored intent input changed')
    transport.require(all(intent.get(k) == cli_cfg[k] for k in ('state_dir','session_id','claw_id','user_id')),
                      'restored intent target changed')
    ledger_path = Path(intent['state_dir'])/'requests.json'
    if not ledger_path.exists():
        transport.require(not intent.get('request_id'), 'bound transport ledger missing; never recreate a send')
        return None
    ledger = transport.read(ledger_path)
    transport.require(ledger.get('schema_version') == transport.LEDGER_SCHEMA, 'unsupported CLI ledger')
    intent_key = context['base_sha256']+':'+context['task']['task_id']
    matches = [r for r in ledger['requests'].values() if r['intent_key'] == intent_key]
    if not matches:
        transport.require(not intent.get('request_id'), 'bound transport claim missing; never recreate a send')
        return None
    transport.require(len(matches) == 1, 'ambiguous restored transport claim')
    request = matches[0]
    transport.require(intent.get('request_id') in (None, request['request_id']), 'restored request binding changed')
    transport.require(all(request.get(k) == intent[k] for k in (
        'base_sha256','task_id','code','name','valuation_date','pack_sha256','session_id','claw_id','user_id')),
        'restored transport input/target changed')
    transport.require(request.get('public_input_reviewed') is True, 'restored pack was never reviewed')
    job = dict(intent=str(intent_path), pack_sha256=intent['pack_sha256'],
               public_input_reviewed=True, request_id=request['request_id'])
    if adapter.failed_request(intent) or transport.terminal(request):
        return dict(job, phase='failed')
    if intent['status'] == 'completed':
        return dict(job, phase='completed')
    transport.require((request['status'] == 'prepared' and request['attempts'] == 0) or
                      (request['status'] in {'sending','send_unknown','pending','partial','complete'} and
                       request['attempts'] == 1), 'invalid restored send claim')
    if not intent.get('request_id'):
        adapter.bind(intent_path, request['request_id'])
    return dict(job, phase=('ready' if request['status'] == 'prepared' else
                           'awaiting_result_review' if request['status'] == 'complete' else 'watching'))


@contextmanager
def submission_guard(key, intent_path, methods, exchange, prepared_config):
    """Revalidate mutable authorization after preflight, under queue.lock."""
    with adapter.current_cli_intent(intent_path, methods, exchange, prepared_config) as intent:
        cfg = settings(methods)
        transport.require(cfg['enabled'] and cfg['dispatch_enabled'], 'event submission disabled before send claim')
        current_config = transport.load_config(methods=methods)
        transport.require(current_config['enabled'], 'CLI submission disabled before send claim')
        transport.require(current_config == prepared_config, 'CLI configuration changed before send claim')
        context = adapter.load_base(intent['base_seal'], methods, exchange)
        transport.require(context['base_sha256'] == key, 'send claim belongs to another event')
        # Re-read hash-bound request/provider evidence rather than trusting a
        # previously approved job's epoch or the configuration before preflight.
        research_event_time(context, cfg['not_before'])
        yield


def step(key, methods, exchange, *, client_factory=transport.Client):
    """One bounded state transition, called under the worker lock."""
    root = outbox(methods)
    valid_key(key)
    event = transport.read(root/'events'/f'{key}.json')
    path = Path(event['seal']).resolve(strict=True)
    transport.require(path.parent == Path(methods).resolve()/'output/research_queue/sealed'
                      and transport.digest(path.read_bytes()) == event['seal_sha256'] == key,
                      'event seal changed')
    cfg = settings(methods)
    transport.require(cfg['enabled'] and transport.timestamp(event['created_at']) >= transport.timestamp(cfg['not_before']),
                      'event not in active epoch')
    job_path = root/'jobs'/f'{key}.json'
    job = transport.read(job_path) if job_path.exists() else dict(key=key, phase='new')
    transport.require(job.get('key') == key, 'job/event identity changed')
    if job['phase'] == 'new':
        context = adapter.load_base(path, methods, exchange)
        if not adapter.eligible(context):
            job.update(phase='ineligible')
        else:
            job['research_event_at'] = research_event_time(context, cfg['not_before'])
            job['time_basis'] = 'latest_verified_provider_completion'
            cli_cfg = transport.load_config(methods=methods)
            restored = restore_job(context, methods, cli_cfg)
            if restored is not None:
                job.update(restored)
                transport.atomic(job_path, job)
                return job
            rows = adapter.scan(methods, exchange, adapter.DEFAULT_MAIL_ROOT, cfg['not_before'],
                                cli_config=cli_cfg, only_seal=path)['intents']
            if not rows:
                job.update(phase='superseded')
            else:
                row = rows[0]
                if row.get('transport') != 'cli' or row['status'] in {'failed','completed'}:
                    job.update(phase='legacy_or_terminal')
                else:
                    job.update(phase='awaiting_public_review', intent=row['intent'],
                               pack_sha256=row['pack_sha256'])
        transport.atomic(job_path, job)
        return job
    if job['phase'] not in {'ready','watching','blocked_dispatch','awaiting_result_review'}:
        return job
    transport.require(transport.timestamp(job['research_event_at']) >= transport.timestamp(cfg['not_before']),
                      'verified research event predates activation')
    intent = adapter.read(job['intent'])
    transport.require(intent['base_sha256'] == key, 'job intent belongs to another event')
    transport.require(intent['pack_sha256'] == job['pack_sha256'], 'approved pack changed')
    # Manual review/publication owns acceptance. Converge the derived status
    # without remote collection, including the hourly repair after publication.
    if intent.get('status') == 'completed' or adapter.failed_request(intent):
        job.update(phase='completed' if intent['status'] == 'completed' else 'failed')
        transport.atomic(job_path, job)
        return job
    if job['phase'] == 'awaiting_result_review':
        return job
    # Disabling either switch stops further sending and collection. No hidden
    # approval, no auth/login/upgrade, and no automatic report acceptance.
    cli_cfg = transport.load_config(methods=methods)
    if not cfg['dispatch_enabled'] or not cli_cfg['enabled']:
        job.update(phase='blocked_dispatch')
        transport.atomic(job_path, job)
        return job
    transport.require(job.get('public_input_reviewed') is True, 'pack not reviewed')
    client = client_factory(cli_cfg)
    # prepare reuses an orphaned durable request after a crash before bind/job.
    request = client.get(intent['request_id']) if intent['request_id'] else None
    if request is None or request['status'] == 'prepared':
        try:
            if request is None:
                with adapter.current_cli_intent(job['intent'], methods, exchange, cli_cfg) as current:
                    request = client.prepare(current, public_input_reviewed=True)
                    if not transport.terminal(request):
                        adapter.bind(job['intent'], request['request_id'])
            if request['status'] == 'prepared':
                request = client.submit(request['request_id'], allow_submit=True,
                    claim_guard=lambda: submission_guard(key, job['intent'], methods, exchange, cli_cfg))
        except ValueError as exc:
            if str(exc) not in {'CLI intent is not the latest eligible round','CLI trigger changed'}:
                raise
            job.update(phase='superseded')
            transport.atomic(job_path, job)
            return job
    # sending/send_unknown are reconciled from real history, never re-submitted.
    if transport.terminal(request):
        job.update(phase='failed', request_id=request['request_id'])
    elif request['status'] == 'complete':
        job.update(phase='awaiting_result_review', request_id=request['request_id'])
    else:
        request = client.collect(request['request_id'])
        if transport.terminal(request):
            job.update(phase='failed', request_id=request['request_id'])
        elif (request.get('replies') and request.get('history_started_at') and
              transport.timestamp(request['history_started_at']) >= transport.started(request)+transport.BUDGET):
            job.update(phase='awaiting_result_review', request_id=request['request_id'])
        else:
            job.update(phase='watching', request_id=request['request_id'])
    transport.atomic(job_path, job)
    return job


def drain(methods=ROOT, exchange=None, *, once=False, sleeper=time.sleep):
    methods = Path(methods).resolve()
    exchange = exchange or methods.parent/'ai_investment/investment_rawdata/data_packs/research_exchange'
    if not settings(methods)['enabled']:
        return dict(disabled=True)
    while True:
        if not settings(methods)['enabled']:
            return dict(disabled=True)
        with lock(methods):
            pending = sorted((outbox(methods)/'pending').glob('*'))
            if not pending:
                return dict(status='idle')
            for marker in pending:
                try:
                    job = step(marker.name, methods, exchange)
                except Exception as exc:
                    # Leave the wake-up durable. History errors cannot become
                    # expiry; a live send claim remains in the transport ledger.
                    transport.atomic(outbox(methods)/'errors'/f'{marker.name}.json',
                                     dict(error_type=type(exc).__name__, at=transport.now().isoformat()))
                    continue
                if job['phase'] not in {'ready','watching'}:
                    marker.unlink(missing_ok=True)
                    transport.fsync_directory(marker.parent)
        if once:
            return dict(status='stepped')
        sleeper(10)  # Only active requests, never periodic candidate scanning.


def launchd_plan(methods=ROOT, python=sys.executable):
    """Return plans only. Do not install, enable or run launchd."""
    methods = Path(methods).resolve()
    transport.require(Path(python).is_absolute(), 'launchd Python must be an absolute path')
    common = dict(RunAtLoad=True, ThrottleInterval=30,
                  EnvironmentVariables={'PATH': LAUNCHD_PATH},
                  ProgramArguments=[python, str(methods/'scripts/coze_events.py'), '--methods',str(methods)])
    worker = dict(common, Label='com.investment-research-methods.coze-events',
                  QueueDirectories=[str(outbox(methods)/'pending')])
    worker['ProgramArguments'] = common['ProgramArguments']+['worker']
    recovery = dict(common, Label='com.investment-research-methods.coze-events-recovery',
                    StartInterval=settings(methods).get('recovery_interval_seconds',3600))
    recovery['ProgramArguments'] = common['ProgramArguments']+['reconcile']
    return worker, recovery


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--methods',type=Path,default=ROOT)
    parser.add_argument('--exchange',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('worker');sub.add_parser('reconcile');sub.add_parser('plan-launchd')
    p=sub.add_parser('approve');p.add_argument('--key',required=True);p.add_argument('--public-input-reviewed',action='store_true')
    args=parser.parse_args()
    if args.command=='worker':result=drain(args.methods,args.exchange)
    elif args.command=='reconcile':result=reconcile(args.methods)
    elif args.command=='approve':result=approve(args.key,args.methods,public_input_reviewed=args.public_input_reviewed)
    else:result=[plistlib.dumps(p).decode() for p in launchd_plan(args.methods)]
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
