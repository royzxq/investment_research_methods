"""Narrow, matched evidence-delivery harness. No model calls or expected answers.

Used inside a disposable workspace. All source access is to frozen full-text
copies; the first read is a clearly labelled simulated transport failure.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import sys
import time

from scripts import research_reader as reader
from scripts.research_evidence import Plan, SCHEMA

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
CONFIG=json.loads((ROOT/'config.json').read_text())
MODE=CONFIG['mode']


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def locate():
    docs={name:reader.Document(ROOT,s['path'],s['sha256']) for name,s in CONFIG['sources'].items()}
    finance=docs['finance']
    indexed={p['page']:p for p in finance.outline() if p['kind']=='page'}
    # Search the full annual text, not preloaded gold page offsets.
    hits={q:list(finance.locate(q)) for q in ['KIOMED PHARMA SA','十四、关联方及关联交易']}
    license_pages=sorted({h['page'] for h in hits['KIOMED PHARMA SA']})
    definition_pages=sorted({h['page'] for h in hits['十四、关联方及关联交易']})
    if len(license_pages)!=1 or len(definition_pages)!=1:
        raise ValueError('ambiguous locator anchors; manual source review required')
    lic, definition=license_pages[0],definition_pages[0]
    # Fixed small-scope structural expansion, equal in both arms. It is NOT an
    # exhaustive discovery rule for stock research. Full-page ends remain intact.
    pages=[lic-1,lic,lic+1,definition,definition+1,definition+2]
    if len(set(pages))!=6 or any(p not in indexed for p in pages):
        raise ValueError('expected structural neighborhood missing')
    id_=lambda p:f'HRH1-P{p}'
    links={lic:[(lic-1,'重要事项前页的否定范围'),(lic+1,'重大关联交易的续页'),
                (definition+1,'同一议案的财务附注交叉引用')],
           lic+1:[(definition,'关联主体定义')],
           definition+1:[(definition,'交易主体定义'),(definition+2,'本页末表头续表')]}
    units=[dict(id=id_(p),path='sources/finance.txt',sha256=finance.sha256,
        start=indexed[p]['start'],end=indexed[p]['end'],
        requires=[dict(id=id_(other),reason=reason) for other,reason in links.get(p,[])]) for p in pages]
    bms=docs['bms']
    units.append(dict(id='A126',path='sources/bms.txt',sha256=bms.sha256,start=0,end=len(bms.text),requires=[]))
    gaps=['BMS附件前两页提取乱码；不能声称核验了乱码内容。',
          '仅核对已有提取文本；未重新联网检验更正、原PDF版式或实际收付款。']
    data=dict(schema=SCHEMA,units=units,gaps=gaps,topics=[
        dict(id='licensing',units=[id_(lic),'A126']),
        dict(id='related',units=[id_(lic)]),
        dict(id='cash',units=[id_(lic+1),'A126'])])
    path=OUT/'plan.json'
    if path.exists():
        if json.loads(path.read_text())!=data:raise ValueError('source plan changed')
    else:save(path,data)
    plan=Plan(ROOT,path)
    if MODE=='repeated':
        for topic, ids in plan.topics.items():
            subset=dict(data,units=[u for u in units if u['id'] in ids],
                        topics=[t for t in data['topics'] if t['id']==topic])
            path=OUT/f'plan-{topic}.json'
            if not path.exists():save(path,subset)
    return dict(status='located_not_read',source_meta={k:d.meta() for k,d in docs.items()},
        queries={q:[dict(page=h['page'],start=h['start'],end=h['end']) for h in rows] for q,rows in hits.items()},
        structural_expansion='许可事项前后页、关联方定义及后续表格页；只约束本次小样本，非全文穷尽。',
        source_units=[{k:u[k] for k in ['id','path','sha256','start','end']} for u in units],
        **plan.outline())


def queue_plans():
    if MODE=='union':return [('shared',Plan(ROOT,OUT/'plan.json'))]
    return [(t,Plan(ROOT,OUT/f'plan-{t}.json')) for t in ['licensing','related','cash']]


def read(ack,max_bytes):
    if not (OUT/'plan.json').exists():raise ValueError('run locate first')
    fault=OUT/'fault-injected.json'
    if not fault.exists():
        if ack:raise ValueError('first read cannot acknowledge unseen text')
        save(fault,dict(kind='controlled_transport_fault',source_text_returned=False))
        return dict(status='controlled_transport_failure',fault_injected=True,
            error='本测试首个正文返回被运输层拒绝，未送达正文或receipt。后续通道上限6000字节。',
            recovery='read --max-bytes 6000；此次不可ack，继续检查真实正文。'),75
    if max_bytes>6000:raise ValueError('transport max_bytes is 6000 after controlled failure')
    if max_bytes<1800:raise ValueError('max_bytes too small for this evidence metadata')
    queues=queue_plans()
    with reader.ledger_file(ROOT,'output/reads.json') as state:
        if ack:
            pending=[]
            for queue,plan in queues:
                entries=plan.entries(state,f'consumer-{queue}-epoch1')
                pending.extend(e for e in entries.values() if ack in e['pending'])
            if len(pending)!=1:raise ValueError('unknown/ambiguous receipt; no automatic acknowledgement')
            reader.acknowledge(pending[0],ack)
        for queue,plan in queues:
            packet=plan.next(state,f'consumer-{queue}-epoch1',max_bytes=max_bytes-128)
            if packet['status']=='all_received_in_this_context':continue
            packet['queue']=queue
            assert reader.wire_size(packet)<=max_bytes
            return packet,0
        return dict(status='all_received_in_this_context',evidence_status='unverified',
                    research_complete=False,queues=len(queues),
                    next='核验事实并写draft.json，再check --review draft.json；不要重复抄录全文。'),0


def check(path):
    review_path=(ROOT/path).resolve()
    if not review_path.is_relative_to(ROOT):raise ValueError('review escapes workspace')
    review=json.loads(review_path.read_text())
    full=Plan(ROOT,OUT/'plan.json')
    with reader.ledger_file(ROOT,'output/reads.json') as state:
        if MODE=='union':audit=full.check(state,'consumer-shared-epoch1',review)
        else:
            # Baseline queues really return repeated text. Check each topic's
            # own delivery, without granting it another queue's acknowledgements.
            audits={q:full.check(state,f'consumer-{q}-epoch1',review) for q,_ in queue_plans()}
            audit=dict(audits['licensing'],topics={q:audits[q]['topics'][q] for q in audits})
        missing=sum(len(t['missing_from_review']) for t in audit['topics'].values())
        unread=sum(len(t['pending_delivery']) for t in audit['topics'].values())
        quotes=len(audit['quote_audit']['issues'])
        path=OUT/f'audit-{len(list(OUT.glob("audit-*.json")))+1}.json'
        save(path,audit)
        return dict(status='scoped_delivery_and_reference_check',
            delivery_complete=unread==0,declared_pairs_complete=missing==0,
            quote_issues=audit['quote_audit']['issues'],quotes_checked=audit['quote_audit']['checked'],
            topics=audit['topics'],gaps=audit['gaps'],
            coverage_complete=False,evidence_status='unverified',research_complete=False,
            interpretation='事实语义仍由你核验；已知样本范围缺口不通过重复读取关闭。',audit_path=str(path)), 2 if (missing or unread or quotes) else 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['locate','read','check'])
    p.add_argument('--ack');p.add_argument('--max-bytes',type=int,default=9000)
    p.add_argument('--review',default='draft.json');a=p.parse_args()
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    try:
        if a.command=='locate':result,code=locate(),0
        elif a.command=='read':result,code=read(a.ack,a.max_bytes)
        else:result,code=check(a.review)
        if reader.wire_size(result)>9000:raise ValueError('harness output above safe host budget')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        result,code=dict(status='not_verified',error=str(exc)),2
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=a.command,ack=a.ack,
        max_bytes=a.max_bytes,code=code,elapsed_seconds=time.monotonic()-start,
        stdout_bytes=reader.wire_size(result),result=result)
    with (OUT/'transport.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False));return code


if __name__=='__main__':sys.exit(main())
