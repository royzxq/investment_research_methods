"""Reconcile exact model-visible source packets and Claude result usage."""
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research_evidence import Plan

load = lambda p: json.loads(p.read_text())
rows = lambda p: [json.loads(s) for s in p.read_text().splitlines() if s]
digest = lambda v: hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def tools(events):
    calls, returns = {}, {}
    for e in events:
        message = e.get('message', {})
        for block in message.get('content', []) if isinstance(message, dict) else []:
            if block.get('type') == 'tool_use': calls[block['id']] = block
            if block.get('type') == 'tool_result': returns[block['tool_use_id']] = block
    return calls, returns


def text_content(block):
    content = block.get('content', '')
    return content if isinstance(content, str) else '\n'.join(
        b.get('text', '') for b in content if isinstance(b, dict))


def payloads(returns):
    result = []
    for block in returns.values():
        for line in text_content(block).splitlines():
            try:
                value = json.loads(line)
                if isinstance(value, dict): result.append(value)
            except ValueError: pass
    return result


def count_usage(folder):
    doc = load(folder / 'usage.json')
    summary = doc['summary']
    u = summary['usage']
    if not isinstance(u, dict):
        partial = load(folder / 'partial-usage.json')
        p = partial['known_input_fields']
        noncache = p['input_tokens'] + p['cache_creation_input_tokens']
        total = noncache + p['cache_read_input_tokens']
        return dict(raw_fields={**p, 'output_tokens': None}, total_input=None,
            uncached_input=None, cache_read=None, output=None, input_plus_output=None,
            uncached_input_plus_output=None, status=partial['status'],
            lower_bounds=dict(total_input=total, uncached_input=noncache,
                cache_read=p['cache_read_input_tokens'], output=0,
                input_plus_output=total, uncached_input_plus_output=noncache),
            unknown_fields='Final output and any unreported pending request usage remain unknown, not zero.',
            scope='Known response inputs only; cross-validated with completed peers',
            source_event_lines=partial['source_event_lines'])
    fields = {key: u.get(key) for key in ['input_tokens', 'cache_creation_input_tokens',
              'cache_read_input_tokens', 'output_tokens']}
    if not all(type(v) is int and v >= 0 for v in fields.values()):
        raise ValueError('Missing Claude usage component; do not infer zero')
    return dict(raw_fields=fields, uncached_input=fields['input_tokens'] + fields['cache_creation_input_tokens'],
                cache_read=fields['cache_read_input_tokens'], output=fields['output_tokens'],
                total_input=sum(fields[k] for k in fields if k != 'output_tokens'),
                input_plus_output=sum(fields.values()),
                uncached_input_plus_output=fields['input_tokens'] + fields['cache_creation_input_tokens'] + fields['output_tokens'],
                modelUsage=summary.get('modelUsage'), source_event_lines=summary['event_lines'],
                status=summary['status'], provider_reported_cost=next((r['provider_fields'].get('total_cost_usd')
                    for r in doc['records'] if r['duplicate_of'] is None), None),
                cost_basis='CLI report only; gateway invoice and subscription effect unknown')


def inspect(mode, initial):
    folder = BASE / mode
    cwd = Path(initial['cwd'])
    events = rows(folder / 'events.jsonl')
    calls, returns = tools(events)
    visible = Counter(digest(v) for v in payloads(returns))
    response_ids = defaultdict(list)
    for id_, block in returns.items():
        for line in text_content(block).splitlines():
            try:
                value = json.loads(line)
                if isinstance(value, dict): response_ids[digest(value)].append(id_)
            except ValueError: pass
    trace = rows(folder / 'delivery/transport.jsonl')
    unmatched = []
    for i, record in enumerate(trace):
        key = digest(record['result'])
        if not visible[key]: unmatched.append(i)
        else: visible[key] -= 1
    packets = [r for r in trace if 'content' in r['result']]
    source_response_ids = [response_ids[digest(r['result'])][0] for r in packets]
    assert len(set(source_response_ids)) == len(packets), 'Source packets must arrive in separate model tool responses'
    by_queue = defaultdict(lambda: defaultdict(list))
    for record in packets:
        p = record['result']; raw = Path(p['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == p['sha256']
        start, end = p['returned']['start'], p['returned']['end']
        assert raw.decode()[start:end] == p['content']
        assert record['stdout_bytes'] <= 6000
        by_queue[p['queue']][p['path']].append((start, end, p['content']))
    full = Plan(cwd, cwd / 'output/plan.json')
    state = load(folder / 'delivery/reads.json')
    delivery = {}
    for queue, paths in by_queue.items():
        plan = full if mode == 'union' else Plan(cwd, cwd / f'output/plan-{queue}.json')
        for path, ranges in plan.ranges.items():
            assert ''.join(p[2] for p in paths[path]) == ''.join(plan.docs[path].text[a:b] for a, b in ranges)
        received = plan.received(plan.entries(state, f'consumer-{queue}-epoch1'))
        delivery[queue] = dict(all_units_received=all(received.values()), received_units=received)
    review = load(folder / 'draft.json')
    required = {(t, u) for t, ids in full.topics.items() for u in ids}
    present = {(t['topic'], u) for t in review['topic_evidence'] for u in t['ids']}
    audits = [load(p) for p in sorted((folder / 'delivery').glob('audit-*.json'),
               key=lambda p: int(p.stem.split('-')[-1]))]
    initial_result = dict(process=load(folder / 'process.json'), usage=count_usage(folder),
        program_calls=dict(Counter(r['command'] for r in trace)), tool_calls=len(calls),
        tool_returns=len(returns), model_visible_program_returns=len(trace) - len(unmatched),
        unmatched_program_returns=unmatched, controlled_failures=sum(r['result'].get('fault_injected', False) for r in trace),
        other_program_errors=[dict(command=r['command'], result=r['result']) for r in trace
              if r['code'] and not r['result'].get('fault_injected')],
        tool_result_errors=sum(bool(b.get('is_error')) for b in returns.values()),
        api_retries=sum(e.get('type') == 'system' and e.get('subtype') == 'api_retry' for e in events),
        source_packets=len(packets), source_characters=sum(len(r['result']['content']) for r in packets),
        distinct_source_tool_responses=len(set(source_response_ids)),
        source_return_bytes=sum(r['stdout_bytes'] for r in packets),
        all_tool_return_bytes=sum(len(text_content(b).encode()) for b in returns.values()),
        source_delivery=delivery, required_pairs=len(required), covered_pairs=len(present & required),
        missing_pairs=sorted(required - present), exact_quotes=full.quotes(review),
        audit_attempts=len(audits), quote_issues_by_audit=[len(a['quote_audit']['issues']) for a in audits],
        final_gaps=audits[-1]['gaps'] if audits else None)
    followup = folder / 'bms-review'
    stages = [initial_result]
    if followup.exists() and (followup / 'usage.json').exists():
        f_events = rows(followup / 'events.jsonl')
        f_calls, f_returns = tools(f_events)
        f_payloads = payloads(f_returns)
        delivered = load(followup / 'bms-read.json')
        final_review = load(followup / 'draft-bms-reviewed.json')
        stages.append(dict(process=load(followup / 'process.json'), usage=count_usage(followup),
            tool_calls=len(f_calls), tool_returns=len(f_returns),
            tool_result_errors=sum(bool(b.get('is_error')) for b in f_returns.values()),
            api_retries=sum(e.get('type') == 'system' and e.get('subtype') == 'api_retry' for e in f_events),
            full_source_delivered_in_cli_events=any(digest(p) == digest(delivered) for p in f_payloads),
            audit=load(followup / 'bms-audit.json'), exact_quotes=full.quotes(final_review)))
        retry = followup / 'retry-1'
        if (retry / 'process.json').exists():
            r_calls, r_returns = tools(rows(retry / 'events.jsonl'))
            r_read = load(retry / 'bms-read.json')
            r_review = load(retry / 'draft-bms-reviewed.json')
            stages.append(dict(process=load(retry / 'process.json'), usage=count_usage(retry),
                tool_calls=len(r_calls), tool_returns=len(r_returns),
                tool_result_errors=sum(bool(b.get('is_error')) for b in r_returns.values()),
                full_source_delivered_in_cli_events=any(digest(p) == digest(r_read) for p in payloads(r_returns)),
                audit=load(retry / 'bms-audit.json'), exact_quotes=full.quotes(r_review),
                receipt=load(retry / 'answer.json')))
    keys = ['total_input', 'cache_read', 'uncached_input', 'output', 'input_plus_output', 'uncached_input_plus_output']
    total = {key: sum(s['usage'][key] for s in stages) if all(type(s['usage'][key]) is int for s in stages) else None
             for key in keys}
    lower_bounds = {key: sum(s['usage'][key] if type(s['usage'][key]) is int else s['usage']['lower_bounds'][key]
                   for s in stages) for key in keys}
    total['cumulative_process_seconds'] = sum(s['process']['execution_duration_seconds'] for s in stages)
    start = datetime.fromisoformat(stages[0]['process']['launched_at'])
    end = datetime.fromisoformat(stages[-1]['process']['completed_at'])
    total['elapsed_span_seconds'] = (end - start).total_seconds()
    total['tool_calls'] = sum(s['tool_calls'] for s in stages)
    return dict(stages=stages, total=total, token_lower_bounds=lower_bounds, jev_calls=0)


if __name__ == '__main__':
    setup = load(BASE / 'setup.json')
    results = {mode: inspect(mode, initial) for mode, initial in setup['arms'].items()}
    baseline, optimized = [results[m]['total'] for m in ['repeated', 'union']]
    delta = {}
    for k in baseline:
        if baseline[k] == 0: continue
        if optimized[k] is None:
            floor = results['union']['token_lower_bounds'][k]
            delta[k] = dict(baseline=baseline[k], optimized=None, optimized_lower_bound=floor,
                minimum_difference=floor - baseline[k], reduction_percent=None,
                minimum_increase_percent=max(0, 100 * (floor / baseline[k] - 1)))
        else:
            delta[k] = dict(baseline=baseline[k], optimized=optimized[k],
                difference=optimized[k] - baseline[k], reduction_percent=100 * (1 - optimized[k] / baseline[k]))
    evaluation = dict(generator='claude', results=results, delta=delta,
        measurement='single final CLI result per stage; usage and modelUsage never added together; all attempts retained',
        quality_note='Delivery, quote matching and evidence IDs are not semantic verification; parent checks separately.',
        experiment_input_plus_output=None,
        experiment_input_plus_output_lower_bound=sum(r['token_lower_bounds']['input_plus_output'] for r in results.values()))
    (BASE / 'evaluation.json').write_text(json.dumps(evaluation, ensure_ascii=False, indent=2))
    print(json.dumps({'delta': delta, 'quality': {m: {'pairs': [r['stages'][0]['covered_pairs'], r['stages'][0]['required_pairs']],
        'unmatched_returns': r['stages'][0]['unmatched_program_returns'], 'quote_issues':
        [len(s['exact_quotes']['issues']) for s in r['stages']]} for m, r in results.items()}}, ensure_ascii=False))
