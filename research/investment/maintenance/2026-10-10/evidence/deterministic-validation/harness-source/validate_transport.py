"""Offline simulated delivery: never a production acknowledgement or fact check."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scripts.research_evidence import Plan
from scripts.research_reader import wire_size

plan=Plan(ROOT,BASE/'plan.json')
runs=[]
for budget in [9000,3000]:
    state={'contexts':{}}
    context=f'offline-simulated-consumer-{budget}'
    receipt=None
    delivered=defaultdict(list)
    sizes=[]
    receipts=[]
    while True:
        packet=plan.next(state,context,receipt,max_bytes=budget)
        if packet['status']=='all_received_in_this_context': break
        assert wire_size(packet)<=budget
        if not receipts:
            # A lost/truncated first delivery with NO ack must reappear exactly.
            assert plan.next(state,context,max_bytes=budget)==packet
        a,b=packet['returned']['start'],packet['returned']['end']
        assert packet['content']==plan.docs[packet['path']].text[a:b]
        delivered[packet['path']].append((a,b,packet['content']))
        sizes.append(wire_size(packet));receipts.append(packet['receipt'])
        receipt=packet['receipt']
    for path,ranges in plan.ranges.items():
        wanted=''.join(plan.docs[path].text[a:b] for a,b in ranges)
        got=''.join(text for _,_,text in delivered[path])
        assert got==wanted
        assert sum(b-a for a,b,_ in delivered[path])==sum(b-a for a,b in ranges)
    review={'topic_evidence':[dict(topic=t,ids=ids) for t,ids in plan.topics.items()]}
    audit=plan.check(state,context,review)
    assert not audit['coverage_complete'] and audit['gaps']  # real extraction limits retained
    assert all(not x['pending_delivery'] and not x['missing_from_review'] for x in audit['topics'].values())
    mutations=[]
    for topic,id_ in [('licensing','HRH1-P64'),('licensing','HRH1-P165'),('cash','A126')]:
        broken=json.loads(json.dumps(review))
        row=next(x for x in broken['topic_evidence'] if x['topic']==topic)
        row['ids'].remove(id_)
        flagged=plan.check(state,context,broken)
        assert flagged['topics'][topic]['missing_from_review']==[id_]
        assert not flagged['coverage_complete']
        mutations.append(dict(topic=topic,removed=id_,detected=True))
    other=plan.check(state,context+'-new-epoch',review)
    assert all(x['pending_delivery'] for x in other['topics'].values())
    runs.append(dict(max_bytes=budget,packets=len(sizes),largest_packet_bytes=max(sizes),
        total_serialized_bytes=sum(sizes),unique_characters=sum(len(t) for v in delivered.values() for _,_,t in v),
        repeated_first_packet_without_ack=True,all_spans_lossless=True,no_duplicate_source_characters=True,
        mutation_checks=mutations,new_context_requires_originals=True,audit=audit,
        scope='offline exact-text simulated delivery; does not prove model receipt or factual correctness'))
with (BASE/'transport-validation.json').open('x') as f:json.dump(runs,f,ensure_ascii=False,indent=2)
print(json.dumps([{k:v for k,v in r.items() if k not in ['audit','mutation_checks']} for r in runs],ensure_ascii=False))
