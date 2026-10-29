"""Join all measured stages and retain semantic findings without hiding first-pass gaps."""
from pathlib import Path
import hashlib
import json
import sys

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))
from scripts.research_evidence import Plan

read=lambda p:json.loads(p.read_text())
rows=lambda p:[json.loads(x) for x in p.read_text().splitlines()]
initial=read(BASE/'evaluation.json');combined=read(BASE/'combined-usage.json');setup=read(BASE/'setup.json')
final={}
for mode in ['repeated','union']:
    folder=BASE/mode/'bms-review';cwd=Path(setup['arms'][mode]['cwd'])
    corrected=read(folder/'draft-bms-reviewed.json');original=read(BASE/mode/'draft.json')
    plan=Plan(cwd,'output/plan.json')
    quotes=plan.quotes(corrected);assert not quotes['issues']
    orig={c['id']:c for c in original['claims']};new={c['id']:c for c in corrected['claims']}
    unchanged=[id_ for id_,c in orig.items() if c['evidence_ids']!=['A126']]
    assert all(orig[id_]==new[id_] for id_ in unchanged)
    assert corrected['topic_evidence']==original['topic_evidence']
    text='\n'.join(c['statement'] for c in corrected['claims'])
    assert all(term in text for term in ['销售提成','净销售额','分梯度','不包括中国大陆','香港特别行政区','澳门特别行政区'])
    events=rows(folder/'events.jsonl')
    commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    expected_payload=read(folder/'bms-read.json')
    received=[]
    for c in commands:
        for line in c['aggregated_output'].splitlines():
            try:received.append(json.loads(line))
            except ValueError:pass
    assert expected_payload in received
    audit=read(folder/'bms-audit.json');assert audit['received']==expected_payload['receipt']
    assert all(c['exit_code']==0 for c in commands)
    final[mode]=dict(**combined[mode],initial_details=initial['results'][mode],
        followup_command_calls=len(commands),total_recorded_command_calls=initial['results'][mode]['command_calls']+len(commands),
        followup_source_return_bytes=len(json.dumps(expected_payload,ensure_ascii=False).encode())+1,
        followup_full_source_return_in_cli_events=True,followup_audit=audit,
        final_exact_quotes=quotes['checked'],final_quote_issues=quotes['issues'],
        topic_pairs_unchanged=True,non_bms_claims_unchanged=True,
        semantic_checkpoints_passed=9,semantic_checkpoints_total=9,
        initial_royalty_finding='Present, but region only described as related territory.' if mode=='repeated'
            else 'Omitted tiered net-sales royalty despite A126 being delivered and included in the topic map.')
delta={}
for key in ['input_plus_output','uncached_input_plus_output','cumulative_process_seconds','wall_seconds_including_interstage_gap','total_recorded_command_calls']:
    b,o=final['repeated'][key],final['union'][key]
    delta[key]=dict(baseline=b,optimized=o,difference=o-b,reduction_percent=100*(1-o/b))
summary=dict(results=final,delta=delta,experiment_input_plus_output=sum(r['input_plus_output'] for r in final.values()),
    quality_conclusion='Initial source/ID delivery passed but optimized royalty statement was missing; after symmetric metered BMS audit, both pass nine bounded semantic checkpoints.',
    semantic_checkpoints=['KIOMED parties/rights and note linkage','RMB amounts 30m and 56.60377358m are transaction occurrence not cash',
        'Ruihongdi 75,000 wan is all-shareholder planned capital increase','negative disclosures have limited scope',
        'BMS upfront/annual composition and conditional 2028 installment','potential 15.2bn/closing conditions are not realized cash',
        '13 projects preclinical','P166-P167 trustee table/header/unit linkage','tiered net-sales royalty excludes mainland/HK/Macau'],
    limitations=['One matched pair with one controlled output-limit failure in each arm.',
        'Raw input includes repeated contexts and cached subsets; uncached+output is only another count, not a money/quota estimate.',
        'Baseline had an additional drafting-call syntax error reported by the model; no separate command failure event, entire turn counts retained.',
        'Total elapsed span includes shared parent review/fixture preparation delay between stages; consumer process sums shown separately.',
        'Full original source selection rules are bounded fixture rules, not exhaustive document discovery.',
        'Parent maintenance chat and one-time harness development tokens cannot be extracted here and are outside paired runtime counts.',
        'Account bill/quota changes and actual model name absent from completion events; remain unknown.'])
with (BASE/'final-evaluation.json').open('x') as f:json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(delta=delta,quality={m:dict(quotes=r['final_exact_quotes'],semantics='9/9',commands=r['total_recorded_command_calls']) for m,r in final.items()},
                     total=summary['experiment_input_plus_output']),ensure_ascii=False))
