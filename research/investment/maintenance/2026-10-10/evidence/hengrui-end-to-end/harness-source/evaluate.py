"""Reconcile full-turn usage, actual tool calls, source delivery and final evidence."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib
import json
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))
from scripts.research_evidence import Plan
from scripts import research_reader as reader


def read(path):return json.loads(path.read_text())
def rows(path):return [json.loads(x) for x in path.read_text().splitlines() if x]
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()


setup=read(BASE/'setup.json')
results={}
expected=read(ROOT/'output/deep-research/2026-10-10-deterministic-validation/outline.json')['topics']
required={(t,u) for t,ids in expected.items() for u in ids}
for mode,initial in setup['arms'].items():
    folder=BASE/mode
    process=read(folder/'process.json')
    events=rows(folder/'events.jsonl')
    usage=read(folder/'usage.json')['summary']['usage']
    calls=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    trace=rows(folder/'delivery/transport.jsonl')
    model_outputs=[]
    for c in calls:
        for line in c.get('aggregated_output','').splitlines():
            try:
                value=json.loads(line)
                if isinstance(value,dict):model_outputs.append(value)
            except ValueError:pass
    outputs=Counter(digest(x) for x in model_outputs)
    missing_stdout=[]
    for i,record in enumerate(trace):
        key=digest(record['result'])
        if not outputs[key]:missing_stdout.append(i)
        else:outputs[key]-=1
    packets=[r for r in trace if 'content' in r['result']]
    by_queue=defaultdict(lambda:defaultdict(list))
    for record in packets:
        packet=record['result'];where=packet['returned'];a,b=where['start'],where['end']
        path=Path(packet['path']);data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==packet['sha256']
        assert data.decode()[a:b]==packet['content']
        assert record['stdout_bytes']<=6000
        by_queue[packet['queue']][packet['path']].append((a,b,packet['content']))
    cwd=Path(initial['cwd'])
    plan=Plan(cwd,cwd/'output/plan.json')
    state=read(folder/'delivery/reads.json')
    delivery={}
    for queue,paths in by_queue.items():
        qplan=plan if mode=='union' else Plan(cwd,cwd/f'output/plan-{queue}.json')
        for path,ranges in qplan.ranges.items():
            assert ''.join(x[2] for x in paths[path])==''.join(qplan.docs[path].text[a:b] for a,b in ranges)
        received=qplan.received(qplan.entries(state,f'consumer-{queue}-epoch1'))
        delivery[queue]=dict(all_units_received=all(received.values()),received_units=received,
                            original_characters=sum(len(c) for r in paths.values() for _,_,c in r))
    answer=read(folder/'answer.json');review=read(folder/'draft.json')
    pairs={(r['topic'],id_) for r in review['topic_evidence'] for id_ in r['ids']}
    audits=[read(p) for p in sorted((folder/'delivery').glob('audit-*.json'),key=lambda p:int(p.stem.split('-')[-1]))]
    results[mode]=dict(process=process,usage=usage,
        input_plus_output=usage['input_tokens']+usage['output_tokens'],
        uncached_input=usage['input_tokens']-usage['cached_input_tokens'],
        completed_turns=sum(e['type']=='turn.completed' for e in events),
        command_calls=len(calls),program_calls=dict(Counter(r['command'] for r in trace)),
        command_failures=sum(c['exit_code']!=0 for c in calls),
        controlled_failures=sum(r['result'].get('fault_injected',False) for r in trace),
        other_program_failures=[dict(command=r['command'],result=r['result']) for r in trace
                                if r['code'] and not r['result'].get('fault_injected')],
        source_packets=len(packets),source_characters=sum(len(r['result']['content']) for r in packets),
        source_packet_stdout_bytes=sum(r['stdout_bytes'] for r in packets),
        all_tool_stdout_bytes=sum(len(c.get('aggregated_output','').encode()) for c in calls),
        source_packets_with_partial_requested_range=sum(not r['result']['requested_text_returned'] for r in packets),
        complete_program_payloads_in_cli_events=len(trace)-len(missing_stdout),unmatched_program_payload_indices=missing_stdout,
        source_delivery=delivery,model_reports_input_complete=answer['input_complete'] and review['input_complete'],
        required_pairs=len(required),covered_pairs=len(pairs&required),missing_pairs=sorted(required-pairs),
        extra_pairs=sorted(pairs-required),final_quote_audit=plan.quotes(review),
        audit_attempts=len(audits),quote_issues_by_audit=[len(a['quote_audit']['issues']) for a in audits],
        final_check_gaps=audits[-1]['gaps'] if audits else None,
        facts_checked_by='Parent semantic comparison with actual source texts; not inferred from IDs or quotes alone')

b,o=results['repeated'],results['union']
delta={}
for name,get in [('input_tokens',lambda r:r['usage']['input_tokens']),('output_tokens',lambda r:r['usage']['output_tokens']),
                 ('input_plus_output',lambda r:r['input_plus_output']),
                 ('duration_seconds',lambda r:r['process']['execution_duration_seconds']),
                 ('command_calls',lambda r:r['command_calls'])]:
    delta[name]=dict(baseline=get(b),optimized=get(o),difference=get(o)-get(b),
                    reduction_percent=100*(1-get(o)/get(b)))
evaluation=dict(scope=read(BASE/'protocol.json'),results=results,delta=delta,
    experiment_input_plus_output=sum(r['input_plus_output'] for r in results.values()),
    cost_usd=None,quota_change=None,
    billing_note='Provider token counts are observed; cached subsets are not extra tokens. Actual bill and account quota impact unavailable.')
with (BASE/'evaluation.json').open('x') as f:json.dump(evaluation,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(delta=delta,quality={m:dict(pairs=f"{r['covered_pairs']}/{r['required_pairs']}",
    quotes=r['final_quote_audit']['checked'],quote_issues=len(r['final_quote_audit']['issues']),
    unmatched_tool_returns=r['unmatched_program_payload_indices'],audits=r['audit_attempts'],
    faults=r['command_failures']) for m,r in results.items()},total=evaluation['experiment_input_plus_output']),ensure_ascii=False))
