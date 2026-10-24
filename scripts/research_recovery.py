"""Explicit, finite recovery of failed seats; immutable supplements for normal consumption."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
from pathlib import Path
import re
import uuid

try:
    from . import research_runner as runner
    from .research_exchange import (_strict_json, _contained_path, load_request,
                                    load_results, seal_schema, _timestamp)
except ImportError:
    import research_runner as runner
    from research_exchange import (_strict_json, _contained_path, load_request,
                                   load_results, seal_schema, _timestamp)

ROOT = Path(__file__).resolve().parents[1]
SEAL_SCHEMA = 'research-sealed-recovery/v1'
INTENT_SCHEMA = 'research-seat-recovery/v1'
BASE_KEYS = {'schema_version', 'task_id', 'batch_id', 'event_key', 'request',
             'request_sha256', 'budget_date', 'results'}
EXTRA_KEYS = {'base_seal', 'recovery_seal', 'recovery_intent', 'recovered_generators'}
INTENT_KEYS = {'schema_version', 'recovery_id', 'created_at', 'authorized_at',
               'authorization', 'generator', 'max_attempts', 'timeout_seconds',
               'request', 'parents', 'parent_snapshot'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return _strict_json(Path(path).read_bytes(), str(path))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def descriptor(path, root):
    path, root = Path(path).resolve(strict=True), Path(root).resolve(strict=True)
    require(path.is_relative_to(root), 'recovery descriptor outside methods')
    return dict(path=path.relative_to(root).as_posix(), sha256=sha(path))


def bound(value, root):
    require(isinstance(value, dict) and set(value) == {'path', 'sha256'}, 'invalid recovery descriptor')
    path = _contained_path(Path(root).resolve(), value['path'], 'recovery descriptor')
    require(sha(path) == value['sha256'], 'recovery descriptor hash mismatch')
    return path


def require_failed(entry):
    require(entry.get('status') == 'failed' and entry.get('report') is None
            and entry.get('price_map') is None, 'recovery requires explicit failed seat without artifacts')


def validate_wrapper(value, base):
    require(isinstance(value, dict) and set(value) == BASE_KEYS | EXTRA_KEYS,
            'invalid recovery supplement fields')
    require(value['schema_version'] == SEAL_SCHEMA and value['recovered_generators'] == ['dsh'],
            'recovery supplement must restore exactly the dsh seat')
    require(all(value[key] == base[key] for key in BASE_KEYS - {'schema_version'}),
            'recovery supplement changed original seal identity or results')


def load_base(path, methods, exchange, *, private=False):
    methods, exchange = Path(methods).resolve(), Path(exchange).resolve()
    path = Path(path).resolve(strict=True)
    permitted = methods / ('output/research_recovery' if private else 'output/research_queue/sealed')
    require(path.is_relative_to(permitted), 'recovery base/private seal outside permitted directory')
    seal = read(path)
    require(isinstance(seal, dict) and set(seal) == BASE_KEYS, 'invalid original seal fields')
    request_path = Path(seal['request']).resolve(strict=True)
    require(request_path.is_relative_to(exchange), 'recovery request outside exchange')
    require(sha(request_path) == seal['request_sha256'], 'recovery request hash mismatch')
    request = load_request(request_path)
    require(seal['schema_version'] == seal_schema(request) and seal['batch_id'] == request['batch_id'],
            'recovery seal/request identity mismatch')
    task = next((t for t in request['tasks'] if t['task_id'] == seal['task_id']), None)
    require(task is not None and task['data_pack_meta'].get('research_trigger', {}).get('event_key') == seal['event_key'],
            'recovery task/event mismatch')
    require(isinstance(seal['results'], list) and sorted(x.get('generator', '') for x in seal['results'])
            == sorted(request['generators']), 'recovery provider set mismatch')
    entries = {}
    for item in seal['results']:
        require(isinstance(item, dict) and set(item) == {'generator', 'manifest', 'manifest_sha256', 'actual_model'},
                'invalid recovery result descriptor')
        manifest = bound(dict(path=item['manifest'], sha256=item['manifest_sha256']), methods)
        matches = [e for e in load_results(manifest, request_path, methods)['results']
                   if e['task_id'] == task['task_id'] and e['generator'] == item['generator']]
        require(len(matches) == 1, 'recovery provider entry missing or duplicated')
        entries[item['generator']] = matches[0]
    return dict(path=path, seal=seal, request=request, request_path=request_path, task=task, entries=entries)


def parent_run(context, methods):
    request = context['request']
    return Path(methods) / 'output/runs/investment' / request['valuation_date'] / request['batch_id']


def validate_failed_parent(context, methods):
    require(context['request']['generators'] == ['codex', 'dsh'], 'recovery requires original codex/dsh pair')
    require_failed(context['entries']['dsh'])
    require(context['entries']['codex']['status'] == 'completed', 'recovery must preserve a completed codex seat')
    result = next(x for x in context['seal']['results'] if x['generator'] == 'dsh')
    folder = bound(dict(path=result['manifest'], sha256=result['manifest_sha256']), methods).parent
    attempts = [runner.execution_folder(parent_run(context, methods), context['task'], 'dsh', n)
                for n in (1, 2)]
    require(folder in attempts, 'failed parent manifest outside original endpoint attempts')
    sealed_at = max(_timestamp(read(bound(dict(path=item['manifest'], sha256=item['manifest_sha256']), methods))['created_at'],
                               'original manifest created_at') for item in context['seal']['results'])
    for generator in context['request']['generators']:
        for n in (1, 2):
            attempt = runner.execution_folder(parent_run(context, methods), context['task'], generator, n)
            if not (attempt / 'launched.json').exists():
                require(not (attempt / 'process.json').exists(), 'original attempt has no durable claim')
                continue
            prior = read(attempt / 'process.json')
            prior_entry = read(attempt / 'entry.json')
            if generator == 'dsh':
                require_failed(prior_entry)
            require(all(prior.get(key) == prior_entry.get(key) for key in
                        ('task_id', 'generator', 'status', 'reason', 'started_at', 'completed_at'))
                    and prior.get('task_id') == context['task']['task_id']
                    and prior.get('generator') == generator and prior.get('completed_at') is not None
                    and prior.get('status') in {'completed', 'failed'},
                    'original attempt lacks matching terminal process evidence')
            claim = read(attempt / 'launched.json')
            require(claim.get('request_sha256') == context['seal']['request_sha256'],
                    'original attempt claim belongs to another request')
            claimed_at = _timestamp(claim.get('claimed_at'), 'original claim time')
            require(claimed_at <= _timestamp(prior['started_at'], 'original process start')
                    <= _timestamp(prior['completed_at'], 'original process end') <= sealed_at,
                    'original attempt terminal process chronology contradicts seal')
            if n == 2:
                first = read(attempt.parent / 'process.json')
                require(_timestamp(first['completed_at'], 'original first attempt end') <= claimed_at,
                        'original retry overlaps its first attempt')
    process = read(folder / 'process.json')
    entry = context['entries']['dsh']
    require(all(process.get(key) == entry.get(key) for key in
                ('task_id', 'generator', 'status', 'reason', 'started_at', 'completed_at')),
            'failed recovery seat lacks matching terminal process evidence')
    require(process.get('completed_at') is not None, 'recovery original seat still in flight')
    return process


def validate_completed(context, methods, folder):
    """Revalidate persisted success read-only, including native terminal evidence."""
    request, task = context['request'], context['task']
    entry = context['entries']['dsh']
    require(entry['status'] == 'completed', 'recovery attempt did not complete')
    folder = Path(folder).resolve(strict=True)
    run = parent_run(context, methods)
    require(folder in [runner.execution_folder(run, task, 'dsh', attempt).resolve()
                       for attempt in (1, 2)], 'recovery terminal attempt path mismatch')
    process = read(folder / 'process.json')
    require(all(process.get(key) == entry.get(key) for key in
                ('task_id', 'generator', 'status', 'reason', 'started_at', 'completed_at'))
            and process.get('exit_code') == 0 and type(process.get('pid')) is int
            and process['pid'] > 0, 'recovery entry lacks matching successful terminal process')
    require(read(folder / 'entry.json') == entry, 'recovery entry differs from persisted original attempt')
    require(read(folder / 'launched.json').get('request_sha256') == sha(context['request_path']),
            'recovery terminal claim belongs to another request')
    _, _, _, verified = runner.verify_prepared(run, context['request_path'].read_bytes(), methods)
    frozen = verified[(task['task_id'], 'dsh')]
    require(process.get('execution_profile') == frozen['execution_profile']
            and process.get('execution_plan_sha256') == frozen['execution_plan_sha256'],
            'recovery terminal execution profile changed')
    require(process.get('jev_runtime_prompt_sha256') == sha(folder / 'jev-runtime-prompt.txt'),
            'recovery runtime prompt changed')
    require(process.get('jev_config_sha256') == sha(folder / 'jev/config.json'),
            'recovery Jev routing configuration changed')
    adapter = runner.research_harness.get_adapter(frozen['execution_profile']['harness'])

    def already_written(path, raw):
        require(Path(path).read_bytes() == raw, 'recovery native receipt differs from original')

    receipt = adapter.receipt(folder, _strict_json, already_written, runner.encode)
    actual = runner.accepted_entry(receipt, request, task, 'dsh', entry['started_at'],
                                   entry['completed_at'], methods, frozen['frameworks'], frozen['targets'])
    require(actual == entry, 'recovery terminal receipt differs from result entry')
    if frozen['research_validation']:
        report = _contained_path(methods, entry['report']['path'], 'recovery report').read_bytes()
        price = read(_contained_path(methods, entry['price_map']['path'], 'recovery price'))
        runner.research_consistency.validate_report(report.decode(), price, root=methods,
            expected_baseline=frozen['research_baseline'],
            require_lifecycle=frozen['delivery'] in (runner.SCOPED_CONTROLS_CONTRACT,
                runner.ACCEPTANCE_CONTROLS_CONTRACT, runner.NEW_CONTRACT),
            require_acceptance=frozen['delivery'] in (runner.ACCEPTANCE_CONTROLS_CONTRACT, runner.NEW_CONTRACT))


def intent_claim(root, parent_descriptor):
    return Path(root) / 'output/research_recovery/claims' / (parent_descriptor['sha256'] + '-dsh.json')


def load_intent(path, methods, exchange):
    methods, exchange = Path(methods).resolve(), Path(exchange).resolve()
    path = Path(path).resolve(strict=True)
    value = read(path)
    require(isinstance(value, dict) and set(value) == INTENT_KEYS and value['schema_version'] == INTENT_SCHEMA,
            'invalid recovery intent')
    recovery_id = value['recovery_id']
    require(isinstance(recovery_id, str) and re.fullmatch('[0-9a-f]{32}', recovery_id), 'invalid recovery id')
    require(path == methods / 'output/research_recovery' / recovery_id / 'intent.json', 'recovery intent location mismatch')
    require(value['generator'] == 'dsh' and type(value['max_attempts']) is int and value['max_attempts'] in (1, 2)
            and type(value['timeout_seconds']) is int and 0 < value['timeout_seconds'] <= 3600,
            'invalid finite recovery limits')
    require(isinstance(value['authorization'], str) and value['authorization'].strip(), 'recovery requires explicit authorization')
    require(_timestamp(value['authorized_at'], 'recovery authorized_at') <= _timestamp(value['created_at'], 'recovery created_at'),
            'recovery authorization chronology mismatch')
    request_descriptor = value['request']
    require(isinstance(request_descriptor, dict) and set(request_descriptor) == {'path', 'sha256'}, 'invalid recovery request descriptor')
    request_path = Path(request_descriptor['path']).resolve(strict=True)
    require(request_path == exchange / 'recoveries' / recovery_id / 'request.json'
            and sha(request_path) == request_descriptor['sha256'], 'recovery child request binding mismatch')
    request = load_request(request_path)
    require(request['batch_id'] == recovery_id and request['generators'] == ['dsh'], 'recovery request must be dsh-only')
    require(isinstance(value['parents'], list) and value['parents'], 'recovery parents missing')
    contexts = []
    for parent in value['parents']:
        context = load_base(bound(parent, methods), methods, exchange)
        validate_failed_parent(context, methods)
        claim = read(intent_claim(methods, parent))
        require(claim == descriptor(path, methods), 'recovery authorization already claimed by another intent')
        contexts.append(context)
    require(len({c['task']['task_id'] for c in contexts}) == len(contexts), 'duplicate recovery parent task')
    require(len({c['request']['batch_id'] for c in contexts}) == 1, 'recovery cannot mix original rounds')
    original_run = parent_run(contexts[0], methods)
    require((original_run / 'request.json').read_bytes() == contexts[0]['request_path'].read_bytes(),
            'recovery original execution request changed')
    require(bound(value['parent_snapshot'], methods) == original_run / 'framework-snapshot/manifest.json',
            'recovery original frozen snapshot changed')
    runner.snapshot_hashes(original_run)
    require(request['tasks'] == [c['task'] for c in contexts]
            and all(request['valuation_date'] == c['request']['valuation_date'] for c in contexts),
            'recovery changed frozen task, pack, event or valuation date')
    require(_timestamp(request['created_at'], 'child created_at') >= _timestamp(value['authorized_at'], 'authorized_at'),
            'recovery request precedes authorization')
    return value, request_path, contexts


def validate_recovery_run(run, methods, exchange=None):
    """History reconstruction folds verified recovery into its original round."""
    run, methods = Path(run).resolve(), Path(methods).resolve()
    link = read(run / 'recovery-link.json')
    intent_path = bound(link, methods)
    if exchange is None:
        intent = read(intent_path)
        exchange = Path(intent['request']['path']).resolve().parents[2]
    intent, request_path, contexts = load_intent(intent_path, methods, exchange)
    require(run == methods / 'output/runs/investment' / contexts[0]['request']['valuation_date'] / intent['recovery_id'],
            'recovery execution location mismatch')
    require((run / 'request.json').read_bytes() == request_path.read_bytes(), 'recovery execution request changed')
    runner.verify_recovery_prepared(run, parent_run(contexts[0], methods), methods)
    return contexts


def load_supplement(path, methods, exchange):
    methods = Path(methods).resolve()
    path = Path(path).resolve(strict=True)
    require(path.is_relative_to(methods / 'output/research_queue/sealed'), 'recovery supplement outside queue')
    value = read(path)
    require(isinstance(value, dict) and set(value) == BASE_KEYS | EXTRA_KEYS, 'invalid recovery supplement fields')
    base_path = bound(value['base_seal'], methods)
    base = load_base(base_path, methods, exchange)
    validate_wrapper(value, base['seal'])
    intent_path = bound(value['recovery_intent'], methods)
    intent, request_path, parents = load_intent(intent_path, methods, exchange)
    require(base_path in [c['path'] for c in parents], 'recovery supplement parent outside authorization')
    recovery_path = bound(value['recovery_seal'], methods)
    require(recovery_path == intent_path.parent / 'seals' / (value['task_id'] + '.json'), 'private recovery seal location mismatch')
    recovered = load_base(recovery_path, methods, exchange, private=True)
    require(recovered['request_path'] == request_path and recovered['task'] == base['task'], 'recovery supplement changed task/request')
    require(recovered['entries']['dsh']['status'] == 'completed', 'failed recovery cannot supersede original seal')
    run = parent_run(recovered, methods)
    validate_recovery_run(run, methods, exchange)
    result = recovered['seal']['results'][0]
    folder = bound(dict(path=result['manifest'], sha256=result['manifest_sha256']), methods).parent
    validate_completed(recovered, methods, folder)
    return base_path, recovery_path, value


@contextmanager
def locked(methods):
    folder = Path(methods) / 'output/research_recovery'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'recovery.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def prepare(seals, exchange, methods=ROOT, *, authorization, authorized_at,
            recovery_id=None, max_attempts=2, timeout_seconds=3600):
    methods, exchange = Path(methods).resolve(), Path(exchange).resolve()
    with locked(methods):
        require(type(max_attempts) is int and max_attempts in (1, 2)
                and type(timeout_seconds) is int and 0 < timeout_seconds <= 3600,
                'invalid finite recovery limits')
        require(isinstance(authorization, str) and authorization.strip(), 'explicit recovery authorization required')
        _timestamp(authorized_at, 'recovery authorized_at')
        contexts = [load_base(p, methods, exchange) for p in seals]
        require(contexts, 'no recovery targets')
        require(len({c['task']['task_id'] for c in contexts}) == len(contexts)
                and len({c['request']['batch_id'] for c in contexts}) == 1,
                'recovery targets must be unique tasks from one original round')
        for context in contexts:
            validate_failed_parent(context, methods)
            for generator in context['request']['generators']:
                for n in (1, 2):
                    attempt = runner.execution_folder(parent_run(context, methods), context['task'], generator, n)
                    if (attempt / 'process.json').exists():
                        process = read(attempt / 'process.json')
                        if process.get('pid') is not None:
                            require(type(process['pid']) is int and process['pid'] > 0
                                    and not runner.group_alive(process['pid']), 'original process group still in flight')
        parents = [descriptor(c['path'], methods) for c in contexts]
        require(all(not intent_claim(methods, p).exists() for p in parents), 'failed seat recovery already authorized')
        recovery_id = recovery_id or uuid.uuid4().hex
        require(re.fullmatch('[0-9a-f]{32}', recovery_id) is not None, 'invalid recovery id')
        folder = methods / 'output/research_recovery' / recovery_id
        require(not folder.exists(), 'recovery id already exists')
        child_folder = exchange / 'recoveries' / recovery_id
        require(not child_folder.exists(), 'recovery request id already exists')
        original = contexts[0]['request']
        request = dict(original, batch_id=recovery_id, created_at=runner.stamp(), generators=['dsh'],
                       tasks=[c['task'] for c in contexts])
        for context in contexts:
            pack = context['request_path'].parent / context['task']['data_pack']['path']
            runner.write_new(child_folder / context['task']['data_pack']['path'], pack.read_bytes())
        request_path = child_folder / 'request.json'
        runner.write_new(request_path, runner.encode(request))
        load_request(request_path)
        value = dict(schema_version=INTENT_SCHEMA, recovery_id=recovery_id, created_at=runner.stamp(),
                     authorized_at=authorized_at, authorization=authorization, generator='dsh',
                     max_attempts=max_attempts, timeout_seconds=timeout_seconds,
                     request=dict(path=str(request_path), sha256=sha(request_path)), parents=parents,
                     parent_snapshot=descriptor(parent_run(contexts[0], methods) / 'framework-snapshot/manifest.json', methods))
        intent_path = folder / 'intent.json'
        runner.write_new(intent_path, runner.encode(value))
        for parent in parents:
            runner.write_new(intent_claim(methods, parent), runner.encode(descriptor(intent_path, methods)))
        load_intent(intent_path, methods, exchange)
        run = runner.prepare_recovery_request(request_path, parent_run(contexts[0], methods), methods)
        runner.write_new(run / 'recovery-link.json', runner.encode(descriptor(intent_path, methods)))
        validate_recovery_run(run, methods, exchange)
        return intent_path


def execute(intent_path, exchange, methods=ROOT, *, cli=None):
    methods = Path(methods).resolve()
    with locked(methods), runner.cancellation_scope() as cancelled:
        intent, request_path, parents = load_intent(intent_path, methods, exchange)
        request, raw, _ = runner.read_request(request_path)
        run = parent_run(dict(request=request), methods)
        validate_recovery_run(run, methods, exchange)
        summaries = []
        for task, base in zip(request['tasks'], parents):
            entry, last_folder = None, None
            _, _, _, verified = runner.verify_prepared(run, raw, methods)
            profile = verified[(task['task_id'], 'dsh')]['execution_profile']
            for attempt in range(1, intent['max_attempts'] + 1):
                folder = runner.execution_folder(run, task, 'dsh', attempt)
                if (folder / 'entry.json').exists():
                    entry = read(folder / 'entry.json')
                else:
                    require(not (folder / 'launched.json').exists(), 'incomplete recovery attempt requires audit; no duplicate launch')
                    endpoint_cli = cli or runner.default_cli('dsh', profile)
                    runner.run_provider(run, request, raw, task, 'dsh', endpoint_cli,
                                        methods, intent['timeout_seconds'], cancelled,
                                        launch_date=request['valuation_date'], attempt=attempt)
                    entry = read(folder / 'entry.json')
                last_folder = folder
                if entry['status'] == 'completed' or not runner.retryable_failure(folder) or cancelled.is_set():
                    break
            result_path = last_folder / 'recovery-result.json'
            if not result_path.exists():
                runner.write_new(result_path, runner.encode(runner.manifest(request, raw, [entry])))
            saved_result = load_results(result_path, request_path, methods)
            require(saved_result['results'] == [entry], 'recovery manifest differs from terminal attempt')
            seal = dict(schema_version=seal_schema(request), task_id=task['task_id'], batch_id=request['batch_id'],
                        event_key=base['seal']['event_key'], request=str(request_path), request_sha256=sha(request_path),
                        budget_date=base['seal']['budget_date'], results=[dict(generator='dsh',
                        manifest=result_path.relative_to(methods).as_posix(), manifest_sha256=sha(result_path),
                        actual_model=runner.observed_model(last_folder, 'dsh', profile))])
            private = Path(intent_path).parent / 'seals' / (task['task_id'] + '.json')
            if not private.exists():
                runner.write_new(private, runner.encode(seal))
            require(read(private) == seal, 'private recovery seal changed')
            supplement = None
            if entry['status'] == 'completed':
                recovered = load_base(private, methods, exchange, private=True)
                validate_completed(recovered, methods, last_folder)
                wrapper = dict(base['seal'], schema_version=SEAL_SCHEMA,
                               base_seal=descriptor(base['path'], methods), recovery_seal=descriptor(private, methods),
                               recovery_intent=descriptor(intent_path, methods), recovered_generators=['dsh'])
                supplement = methods / 'output/research_queue/sealed' / (base['path'].stem + '-recovery-' + intent['recovery_id'] + '.json')
                if not supplement.exists():
                    runner.write_new(supplement, runner.encode(wrapper))
                load_supplement(supplement, methods, exchange)
            summary = dict(task_id=task['task_id'], status=entry['status'], private_seal=str(private),
                           supplement=str(supplement) if supplement else None)
            summaries.append(summary)
            runner.emit(dict(event='recovery_task_finished', **summary))
        return summaries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'execute', 'check'])
    parser.add_argument('--exchange', required=True)
    parser.add_argument('--methods', default=str(ROOT))
    parser.add_argument('--seal', action='append', default=[])
    parser.add_argument('--intent')
    parser.add_argument('--authorization')
    parser.add_argument('--authorized-at')
    args = parser.parse_args(argv)
    if args.action == 'prepare':
        require(args.authorization and args.authorized_at, 'explicit authorization and time required')
        result = str(prepare(args.seal, args.exchange, args.methods, authorization=args.authorization,
                             authorized_at=args.authorized_at))
    elif args.action == 'execute':
        result = execute(args.intent, args.exchange, args.methods)
    else:
        value, _, _ = load_intent(args.intent, args.methods, args.exchange)
        result = dict(recovery_id=value['recovery_id'], valid=True)
    runner.emit(result)


if __name__ == '__main__':
    main()
