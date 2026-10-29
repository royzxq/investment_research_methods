"""Matched independent license-state and BMS financial-terms review."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from scripts.research_evidence import Plan
from scripts.research_reader import wire_size

ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()


def eligible(claim):
    return claim['evidence_ids']==['A126'] or 'KIOMED' in claim['statement']


def save(path,data):
    with path.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)


def read_payload():
    review_raw=(ROOT/'draft.json').read_bytes();review=json.loads(review_raw)
    source=(ROOT/'sources/bms.txt').read_bytes()
    payload=dict(status='source_for_independent_bms_review',source_id='A126',source_sha256=sha(source),
        review_sha256=sha(review_raw),source_text=source.decode(),
        current_claims=[dict(id=c['id'],statement=c['statement'],evidence_ids=c['evidence_ids']) for c in review['claims'] if eligible(c)],
        limitations=review['limitations'],scope='仅复核KIOMED交易状态/附注连接及A126财务条款，其余条目保留原记录。')
    plan=Plan(ROOT,'output/plan.json')
    payload['additional_sources']=[dict(id=id_,sha256=unit['sha256'],text=plan.docs[unit['path']].text[unit['start']:unit['end']])
        for id_,unit in plan.units.items() if id_ in ['HRH1-P65','HRH1-P165','HRH1-P166']]
    payload['receipt']=sha(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode())
    return payload


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['read','apply'])
    p.add_argument('--received');p.add_argument('--patch',default='bms-patch.json');a=p.parse_args()
    payload=read_payload()
    if a.command=='read':
        assert wire_size(payload)<=45000
        record=ROOT/'output/bms-read.json'
        if not record.exists():save(record,payload)
        print(json.dumps(payload,ensure_ascii=False));return 0
    if not (ROOT/'output/bms-read.json').exists() or a.received!=payload['receipt']:
        raise ValueError('current source and draft must be fully received before applying a patch')
    patch=json.loads((ROOT/a.patch).read_text())
    review=json.loads((ROOT/'draft.json').read_text())
    before={c['id']:json.dumps(c,sort_keys=True,ensure_ascii=False) for c in review['claims'] if not eligible(c)}
    known={c['id']:c for c in review['claims']}
    seen=set()
    for replacement in patch['replacements']:
        id_=replacement['id']
        if id_ in seen or id_ not in known or not eligible(known[id_]):
            raise ValueError('only unique selected license/BMS claims may be replaced')
        seen.add(id_)
        if set(replacement)!=set(known[id_]) or replacement['evidence_ids']!=known[id_]['evidence_ids']:
            raise ValueError('preserve claim schema and source identity')
        review['claims'][review['claims'].index(known[id_])]=replacement
    after={c['id']:json.dumps(c,sort_keys=True,ensure_ascii=False) for c in review['claims'] if not eligible(c)}
    assert before==after
    plan=Plan(ROOT,'output/plan.json');quotes=plan.quotes(review)
    if quotes['issues']:
        print(json.dumps(dict(status='quote_error',issues=quotes['issues']),ensure_ascii=False));return 2
    save(ROOT/'draft-bms-reviewed.json',review)
    record=dict(status='bms_terms_reviewed',received=a.received,source_sha256=payload['source_sha256'],
        previous_draft_sha256=payload['review_sha256'],changed_claim_ids=list(seen),quotes_checked=quotes['checked'],
        other_claims_unchanged=True,scope='model semantic review of license status and BMS terms; exact quote check by program',
        revised_review_sha256=sha((ROOT/'draft-bms-reviewed.json').read_bytes()))
    save(ROOT/'output/bms-audit.json',record)
    print(json.dumps(record,ensure_ascii=False));return 0


if __name__=='__main__':sys.exit(main())
