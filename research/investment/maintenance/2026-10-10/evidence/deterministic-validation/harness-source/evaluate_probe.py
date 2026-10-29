"""Keep raw answers immutable; audit IDs/quotes separately from human semantics."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scripts.research_evidence import Plan

plan=Plan(ROOT,BASE/'plan.json')
expected_pairs={(t,u) for t,ids in plan.topics.items() for u in ids}
results={}
for mode in ['repeated','union']:
    folder=BASE/mode
    raw=(folder/'answer.json').read_bytes()
    answer=json.loads(raw)
    quote_audit=plan.quotes(answer)
    corrected=json.loads(raw)
    repairs=[]
    for issue in quote_audit['issues']:
        suggestion=issue['suggestion']
        if not suggestion or suggestion['kind']!='unique_whitespace_only':continue
        quote=corrected['claims'][issue['claim_index']]['quotes'][issue['quote_index']]
        repairs.append(dict(**issue,previous_text=quote['text']))
        quote['text']=suggestion['original_text']
    corrected_audit=plan.quotes(corrected)
    with (folder/'review-corrected.json').open('x') as f:json.dump(corrected,f,ensure_ascii=False,indent=2)
    observed={(r['topic'],u) for r in answer['topic_evidence'] for u in r['ids']}
    usage=json.loads((folder/'usage.json').read_text())['summary']['usage']
    process=json.loads((folder/'process.json').read_text())
    events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines() if x]
    commands=[e for e in events if e.get('item',{}).get('type')=='command_execution']
    results[mode]=dict(usage=usage,observed_input_plus_output=usage['input_tokens']+usage['output_tokens'],
        duration_seconds=process['execution_duration_seconds'],process_status=process['status'],
        completed_turns=sum(e['type']=='turn.completed' for e in events), tool_commands=len(commands),
        input_complete_reported=answer['input_complete'],
        covered_pairs=len(observed&expected_pairs),required_pairs=len(expected_pairs),
        missing_pairs=sorted(expected_pairs-observed),extra_pairs=sorted(observed-expected_pairs),
        quote_audit_raw=quote_audit,quote_audit_corrected=corrected_audit,local_whitespace_repairs=repairs,
        raw_answer_sha256=hashlib.sha256(raw).hexdigest(),
        semantic_review='Performed separately by the parent against all seven original units; not inferred from IDs or quotes.')
ref,changed=results['repeated'],results['union']
delta=dict(input_tokens=changed['usage']['input_tokens']-ref['usage']['input_tokens'],
    input_reduction_percent=100*(1-changed['usage']['input_tokens']/ref['usage']['input_tokens']),
    input_plus_output=changed['observed_input_plus_output']-ref['observed_input_plus_output'],
    input_plus_output_reduction_percent=100*(1-changed['observed_input_plus_output']/ref['observed_input_plus_output']),
    duration_change_percent=100*(changed['duration_seconds']/ref['duration_seconds']-1))
evaluation=dict(scope='Two fixed-input CLI consumer turns, including shared instructions, source metadata and complete originals. '
    'Excludes this maintenance chat, locating/authoring plans and real multi-turn tool orchestration. No Jev or model retry. '
    'Offline transport is reported separately. Actual monetary bill and account quota impact unknown.',
    results=results,delta=delta,total_probe_input_plus_output=sum(x['observed_input_plus_output'] for x in results.values()))
with (BASE/'evaluation.json').open('x') as f:json.dump(evaluation,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(delta=delta,arms={m:dict(usage=r['usage'],quotes=r['quote_audit_raw']['checked'],
      raw_quote_issues=len(r['quote_audit_raw']['issues']),corrected_quote_issues=len(r['quote_audit_corrected']['issues']),
      pairs=f"{r['covered_pairs']}/{r['required_pairs']}") for m,r in results.items()},
      total_probe_input_plus_output=evaluation['total_probe_input_plus_output']),ensure_ascii=False))
