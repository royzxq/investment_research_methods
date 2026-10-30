"""Same metered, independent BMS financial-terms audit for both arms."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from scripts.research_evidence import Plan
from scripts.research_reader import wire_size

ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()


def save(path,data):
    with path.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)


def read_payload():
    review_raw=(ROOT/'draft.json').read_bytes();review=json.loads(review_raw)
    source=(ROOT/'sources/bms.txt').read_bytes()
    payload=dict(status='source_for_independent_bms_review',source_id='A126',source_sha256=sha(source),
        review_sha256=sha(review_raw),source_text=source.decode(),
        current_claims=[dict(id=c['id'],statement=c['statement']) for c in review['claims'] if c['evidence_ids']==['A126']],
        limitations=review['limitations'],scope='仅复核A126财务条款，其余已核验条目保持原记录，不声称本上下文重读过。')
    payload['receipt']=sha(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode())
    return payload


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['read','apply'])
    p.add_argument('--received');p.add_argument('--patch',default='bms-patch.json');a=p.parse_args()
    payload=read_payload()
    if a.command=='read':
        assert wire_size(payload)<=11000
        record=ROOT/'output/bms-read.json'
        if not record.exists():save(record,payload)
        print(json.dumps(payload,ensure_ascii=False));return 0
    if not (ROOT/'output/bms-read.json').exists() or a.received!=payload['receipt']:
        raise ValueError('current source and draft must be fully received before applying a patch')
    patch=json.loads((ROOT/a.patch).read_text())
    review=json.loads((ROOT/'draft.json').read_text())
    before={c['id']:json.dumps(c,sort_keys=True,ensure_ascii=False) for c in review['claims'] if c['evidence_ids']!=['A126']}
    known={c['id']:c for c in review['claims']}
    seen=set()
    for replacement in patch['replacements']:
        id_=replacement['id']
        if id_ in seen or id_ not in known or known[id_]['evidence_ids']!=['A126']:
            raise ValueError('only unique BMS-only existing claims may be replaced')
        seen.add(id_)
        if set(replacement)!=set(known[id_]) or replacement['evidence_ids']!=['A126']:
            raise ValueError('preserve claim schema and source identity')
        review['claims'][review['claims'].index(known[id_])]=replacement
    after={c['id']:json.dumps(c,sort_keys=True,ensure_ascii=False) for c in review['claims'] if c['evidence_ids']!=['A126']}
    assert before==after
    plan=Plan(ROOT,'output/plan.json');quotes=plan.quotes(review)
    if quotes['issues']:
        print(json.dumps(dict(status='quote_error',issues=quotes['issues']),ensure_ascii=False));return 2
    save(ROOT/'draft-bms-reviewed.json',review)
    record=dict(status='bms_terms_reviewed',received=a.received,source_sha256=payload['source_sha256'],
        previous_draft_sha256=payload['review_sha256'],changed_claim_ids=list(seen),quotes_checked=quotes['checked'],
        other_claims_unchanged=True,scope='model semantic review of BMS financial terms; exact quote check by program',
        revised_review_sha256=sha((ROOT/'draft-bms-reviewed.json').read_bytes()))
    save(ROOT/'output/bms-audit.json',record)
    print(json.dumps(record,ensure_ascii=False));return 0


if __name__=='__main__':sys.exit(main())
