from pathlib import Path
from decimal import Decimal as D
from copy import deepcopy
import json,hashlib,sys,re
# Run from this worktree root; source repository is read-only. No sealing or quote writes.
root=Path(__file__).resolve().parents[5];sys.path.insert(0,str(root/'scripts'))
import research_consistency as c
import research_acceptance as ac
from stock_price_map import load_json,json_number,validate_monitoring_delivery
original=Path('/Users/xinquanzhou/Workspace/investment_research_methods')
out=root/'research/investment/studies/risk-capital-audit/2026-11-14'
manifest=[]
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=json_number)+'\n')
def capture(path,dest=None):
 raw=path.read_bytes();manifest.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest()))
 if dest:
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 return raw
results={}
for gen in ('codex','dsh'):
 rel=f'research/investment/companies/2026-11-12/SH-600988/investment-600988-2026-11-12-research-{gen}-r2.md'
 report=capture(original/rel,out/'evidence'/f'chifeng-original-{gen}.md').decode()
 doc=load_json(original/rel.replace('-research-','-price-map-').replace('.md','.json'))
 capture(original/rel.replace('-research-','-price-map-').replace('.md','.json'),out/'evidence'/f'chifeng-original-{gen}.json')
 a=c.extract_audit(report)
 oldresult=c.validate_report(report,doc,root=original,require_lifecycle=True,require_acceptance=True,expected_schema='stock-research-audit/v2')
 baseline=out/'evidence'/f'chifeng-baseline-{gen}.md'
 capture(original/a['baseline']['report_path'],baseline)
 a['baseline']['report_path']=baseline.relative_to(root).as_posix()
 a['schema_version']='stock-research-audit/v3'
 if gen=='codex':
  a['valuation']['horizon']='2027原情景固定，仅重编码；不是新的正式估值'
  a['valuation']['profit_basis']='保持原经常归母利润，不含新增现金利息；现金独立单列。净款为估计，K=0等条件未独立证实。'
 for label,pe in zip(c.SCENARIOS,(12,15,18)):
  row=a['valuation']['scenarios'][label];row['pe']=pe
  row['equity_adjustments']=([dict(id='NET_PROCEEDS',amount=D('78.620274'),reason='91.8亿HKD×0.85643；仅重演旧假设，非11/12银行余额证明',source='HKEX2026102201421_c.pdf PDF3；旧报告§5'),dict(id='COMPENSATION',amount=D('-.7805'),reason='已批准补偿上限；与预测经常利润分开，未擅计税盾',source='HKEX2026102201506_c.pdf PDF4–5；旧报告§5')] if gen=='codex' else [])
 title=f'chifeng-{gen}-audit-v3-replay'
 doc['meta']['report_path']=(out/(title+'.md')).relative_to(root).as_posix()
 unchanged=deepcopy(doc['price_map'])
 visible=c.render_report_block(a,doc,root=root)
 # Preserve acceptance claims; relocate exact source bytes into the isolated evidence bundle.
 pattern=re.escape(ac.START)+r'\s*```json\s*\n(.*?)\n```\s*'+re.escape(ac.END)
 claims=json.loads(re.search(pattern,report,re.S)[1],parse_float=D)
 for field in claims['r14']['inputs'].values():
  for src in field['sources']:
   dest=out/'evidence'/f"r14-{gen}-{hashlib.sha256(src['path'].encode()).hexdigest()[:12]}.txt"
   capture(original/src['path'],dest)
   src['path']=dest.relative_to(root).as_posix()
 body=f'# 赤峰 {gen} 历史输入的 audit-v3 算术重演\n\n本文件由Codex生成，{gen}只标明原研究来源；不是该端新研报。原经营/现金条件未被本次算术验收证明，无新正式报价。与原P1/V50/控制逐项相等；资金经济归属见同目录隔离复评。\n\n'+visible+'\n'+ac.render_block(claims,a,root=root)
 (out/(title+'.md')).write_text(body);save(out/(title+'.json'),doc)
 result=c.validate_report(body,doc,root=root,require_lifecycle=True,require_acceptance=True,expected_schema='stock-research-audit/v3')
 validate_monitoring_delivery(doc,quality=True)
 assert doc['price_map']==unchanged
 probes={}
 if gen=='codex':
  for name,mut in [('omit_cash',lambda aa:aa['valuation']['scenarios']['base']['equity_adjustments'].clear()),('fold_cash_into_pe',lambda aa:aa['valuation']['scenarios']['base'].update(pe=D('17.960187529793533'))),('duplicate_cash_id',lambda aa:aa['valuation']['scenarios']['base']['equity_adjustments'].append(deepcopy(aa['valuation']['scenarios']['base']['equity_adjustments'][0])))]:
   bad=deepcopy(a);mut(bad)
   try:c.validate_audit(bad,doc,root=root);probes[name]='UNEXPECTED PASS'
   except ValueError as exc:probes[name]='rejected: '+str(exc)
  assert all(v.startswith('rejected:') for v in probes.values())
 results[gen]=dict(old=oldresult,new=result,prices_unchanged=True,controls_unchanged=True,negative_probes=probes)
for gen in ('codex','claude'):
 capture(original/f'research/investment/companies/2026-10-15/HK-01810/investment-01810-2026-10-15-research-{gen}.md',out/'evidence'/f'xiaomi-original-{gen}.md')
xN=D('25.795090957');fx=D('.85688');cash=D('99.821148')-D('1.537029394')*fx-D(40);EV=D('19.34')*18/D('1.10');V=(EV+cash)/xN/fx
M=D('.7')*D('.97')*D('.9')*D('.97')*D('.92')
results['xiaomi']=dict(original_equity_bn=EV+cash,original_v50=V,original_p1=V*M,rv5_zero_only=V*M/D('.9'),terminal_zero_only=V*M/D('.92'),both_zero=V*M/D('.9')/D('.92'),all_three_zero=V*M/D('.9')/D('.92')/D('.7'),scope='conditional arithmetic only; no calibrated new P1')
results['chifeng_conditions']=[dict(K=k,codex_v50=(D('26.295555')*15+D('77.839774')-D(k))/D('22.11313909'),dsh_v50=(D('25.660634109375')*15+D('77.839774')-D(k))/D('22.11313909')) for k in ['0','4.369125595','7.011705595','39.310137','77.839774']]
for name in ('investment_framework.md','investment_framework_compact.md'):capture(root/'framework'/name)
save(out/'verification.json',results);save(out/'source-manifest.json',manifest)
print(json.dumps({k:v.get('new',v) if isinstance(v,dict) else v for k,v in results.items()},ensure_ascii=False,default=json_number))
