"""Isolated paired model study. No production writer, network or latest update."""
from copy import deepcopy
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
import itertools
import json
import math
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from scripts import research_consistency as audit_checks
from scripts.research_valuation import evaluate_dcf, solve_reverse_dcf, ReverseNoSolutionError
from scripts.stock_price_map import json_number
D = lambda x: Decimal(str(x))
LABELS = ('low', 'base', 'high')
MODEL_KEYS = ('kind','currency','amount_unit','shares','fx_to_quote','scenarios')

def load(path):
    return json.loads(path.read_text(), parse_float=Decimal)

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=json_number, allow_nan=False)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compute(model, label):
    """Independent study arithmetic; the audit engine separately verifies declarations."""
    row = model['scenarios'][label]
    ev = D(0)
    for seg in row['segments']:
        r = D(seg['discount_rate'])
        for y in seg['years']:
            cf = D(y['revenue'])*D(y['ebit_margin'])*(1-D(y['tax_rate'])) + D(y['da'])-D(y['capex'])-D(y['delta_nwc'])
            ev += cf/(1+r)**y['year']
        t = seg['terminal']; g = D(t['growth'])
        n = len(seg['years'])
        nopat = D(seg['years'][-1]['revenue'])*(1+g)*D(t['margin'])*(1-D(t['tax_rate']))
        ev += nopat*(1-g/D(t['roic']))/(r-g)/(1+r)**n
    equity = ev + sum((D(x['amount']) for x in row['equity_adjustments']),D(0))
    return equity, equity*D(100_000_000)/D(model['shares'])*D(model['fx_to_quote'])

def seal_model(raw):
    model = {k:deepcopy(raw[k]) for k in MODEL_KEYS}
    for label in LABELS:
        raw_case=model['scenarios'][label]
        model['scenarios'][label]={k:raw_case[k] for k in ('segments','equity_adjustments','equity_value')}
        model['scenarios'][label]['segments']=[{k:s[k] for k in ('id','source','assumptions','discount_rate','years','terminal')} for s in raw_case['segments']]
        for seg in model['scenarios'][label]['segments']:
            seg['years']=[{k:y[k] for k in ('year','revenue','ebit_margin','tax_rate','da','capex','delta_nwc')} for y in seg['years']]
        model['scenarios'][label]['equity_value'] = compute(model,label)[0]
    result = evaluate_dcf(model)
    return model, result

def align_segments(locked, updated, equal_split=False):
    """Exact-value split of Alibaba aggregate into comparable segment IDs.

    This is algebra only; same margins/discounts/terminal and proportional cash
    inputs preserve the frozen aggregate DCF. It does not claim historical segment facts.
    """
    result = deepcopy(locked)
    for label in LABELS:
        old = locked['scenarios'][label]['segments']
        new = updated['scenarios'][label]['segments']
        if [s['id'] for s in old] == [s['id'] for s in new]:
            continue
        assert len(old)==1
        total = sum(D(s['years'][0]['revenue']) for s in new)
        split=[]
        for s in new:
            weight=D(1)/D(len(new)) if equal_split else D(s['years'][0]['revenue'])/total
            part=deepcopy(old[0]);part['id']=s['id']
            for row in part['years']:
                for k in ('revenue','da','capex','delta_nwc'):row[k]=D(row[k])*weight
            split.append(part)
        result['scenarios'][label]['segments']=split
        assert abs(compute(result,label)[1]-compute(locked,label)[1])<D('1e-20')
    return result

GROUPS=('revenue','margin_tax','reinvestment','terminal','discount_rate')
def hybrid(locked, updated, keys):
    model=deepcopy(locked)
    for label in LABELS:
        for old,new in zip(model['scenarios'][label]['segments'],updated['scenarios'][label]['segments']):
            assert old['id']==new['id']
            if 'discount_rate' in keys:old['discount_rate']=new['discount_rate']
            if 'terminal' in keys:old['terminal']=deepcopy(new['terminal'])
            for a,b in zip(old['years'],new['years']):
                fields=[]
                if 'revenue' in keys:fields+=['revenue']
                if 'margin_tax' in keys:fields+=['ebit_margin','tax_rate']
                if 'reinvestment' in keys:fields+=['da','capex','delta_nwc']
                for k in fields:a[k]=b[k]
    return model

def shapley(locked, updated, equal_split=False):
    aligned=align_segments(locked,updated,equal_split)
    assert aligned['scenarios']['base']['equity_adjustments']==updated['scenarios']['base']['equity_adjustments']
    cache={}
    for size in range(6):
        for subset in itertools.combinations(GROUPS,size):
            cache[frozenset(subset)]=compute(hybrid(aligned,updated,subset),'base')[1]
    out={}
    for k in GROUPS:
        out[k]=D(0)
        for subset,v in cache.items():
            if k in subset:continue
            weight=D(math.factorial(len(subset))*math.factorial(4-len(subset)))/D(math.factorial(5))
            out[k]+=weight*(cache[subset|{k}]-v)
    assert abs(sum(out.values())-(compute(updated,'base')[1]-compute(locked,'base')[1]))<D('1e-18')
    return out

def discount_audit(code, model, values, factor, reverse, market, *, tag="updated", version="stock-research-audit/v4"):
    discounts={'d_base':D('.25'),'r_chip':D(0),'r_v5':D(0),'r_gov':D(0),'r_terminal':D(0)} if code=='09988' else dict(zip(audit_checks.DISCOUNTS,map(D,('.30','.03','.10','.03','.08'))))
    pe_crosscheck='旧阿里普通股利润PE为12/15/18倍；旧小米是EV/NOPAT资本化16/18/20倍再除1.10，不得标为归母PE。'
    if model['kind']=='dcf_fcff':
        base=evaluate_dcf(model)['details']['base']
        nopat=sum(s['years'][0]['nopat'] for s in base['segments'])
        pe_crosscheck+=f"本DCF基准经营EV={base['enterprise_value']:.4f}亿元、Y1 NOPAT={nopat:.4f}亿元，隐含EV/NOPAT={base['enterprise_value']/nopat:.4f}倍；含恢复预期，非同业事实或正当性证明。"
    doc={'meta':dict(schema_version='stock-research/v4',code=code+'.HK',name='阿里巴巴-W' if code=='09988' else '小米集团-W',valuation_date='2026-10-31',currency='HKD',generator='codex',report_path=str((HERE/f'{code}-{tag}-isolated-audit.md').relative_to(ROOT))),
         'price_map':dict(mode='tracking',reason='隔离条件估值；资本归属未闭合，不构成新买入资格',v50={k:float(audit_checks.quote_round(v,'HKD')) for k,v in values.items()},p1={'base':float(audit_checks.quote_round(values['base']*factor,'HKD'))},t1={'price_condition':'接近V50上沿时复核'}),
         'monitoring':[], 'research_controls':{s:dict(status='unknown',refs=['CAPITAL_UNRESOLVED']) for s in ('entry','add')}}
    doc['research_controls']['holding']=dict(status='unknown',refs=['HOLDING_NOT_REASSESSED'])
    audit={'schema_version':version,'identity':{k:doc['meta'][k] for k in ('code','generator','valuation_date','currency')},'valuation':model,'baseline':None,
      'valuation_review':dict(base_case='同包条件截面；经营假设见inputs/evidence与assumptions；非概率中位数，资产归属仍未闭合',method_choice='这是模型实验，不是完整生产研究；本组严格采用valuation.kind所声明的资本化法或分业务FCFF，新增假设分拆披露。',pe_crosscheck=pe_crosscheck,market_check=dict(price=market,as_of='2026-10-30',source='冻结2026-10-31原始数据包',explanation='独立预测后反解；未闭合资金/投资NAV均条件化，市价不用于拟合基准'),reverse_dcf=reverse),
      'discounts':{k:dict(value=v,range=[v,v],risk_ids=[k] if v else [],reason='固定历史折扣仅为控制实验，非本轮重新认可其经济有效性',change=dict(kind='initial',reason='实验基线原文另在inputs；不是正式增量研究交付',evidence=[])) for k,v in discounts.items()},
      'risks':[dict(id=k,description='固定旧折扣作算术控制；是否与DCF重复须见未决项',owner=k,scope='此审计仅证明算术；旧风险未量化无法声称经济去重完成',source='同日/最近正式Codex报告§7，inputs/evidence定位') for k,v in discounts.items() if v],
      'constraints':[dict(id='CAPITAL_UNRESOLVED',scope=['entry','add'],action='eligibility',status='unknown',lifecycle='persistent',reason='现金与投资净归属缺口；隔离实验无正式资格裁决',release_conditions=['核实资本桥并完整复评'])],
      'release_all_of':dict(entry=['CAPITAL_UNRESOLVED'],add=['CAPITAL_UNRESOLVED'],holding=['HOLDING_NOT_REASSESSED']),'p1_basis':dict(base='base')}
    if version != 'stock-research-audit/v4':
        audit.pop('valuation_review')
    if version == 'stock-research-audit/v2' and model['kind']=='profit_pe':
        audit['valuation']=deepcopy(model)
        for row in audit['valuation']['scenarios'].values():row.pop('equity_adjustments')
    audit['constraints'].append(dict(id='HOLDING_NOT_REASSESSED',scope=['holding'],action='review_holding',status='unknown',lifecycle='persistent',reason='隔离估值实验未形成新的持仓判断',release_conditions=['完成持仓逻辑复评']))
    text='# 隔离算术审计，不是正式投研交付\n\n保留旧折扣作控制变量，算术通过不证明折扣经济独立；未运行完整Gate/来源验收，不可发布。\n\n'+audit_checks.render_report_block(audit,doc)
    (HERE/f'{code}-{tag}-isolated-audit.md').write_text(text)
    write(HERE/f'{code}-{tag}-isolated-map.json',doc)
    return audit_checks.validate_report(text,doc,expected_schema=version,require_lifecycle=True)

def main():
    manifest_path=HERE/'manifest.json'
    manifest=load(manifest_path if manifest_path.exists() else ROOT/'output/dcf-study/manifest.json')
    out={}
    for code,market,factor in [('09988',D('97.05'),D('.75')),('01810',D('26.48'),D('.54534564'))]:
        src=ROOT/'output/dcf-study'/code
        dest=HERE/'inputs'/code;dest.mkdir(parents=True,exist_ok=True)
        for name in ('data-pack.md','assumptions.json','evidence.md'):
            target=dest/name
            if not target.exists():shutil.copyfile(src/name,target)
            expected=manifest.get('inputs',{}).get(code,{}).get(name)
            assert expected is None or sha(target)==expected, f'frozen input changed: {target}'
        data=load(dest/'assumptions.json')
        locked,lres=seal_model(data['models']['locked_assumptions_dcf'])
        updated,ures=seal_model(data['models']['evidence_updated_dcf'])
        old=data['models']['old_multiple_baseline'] if code=='09988' else data['old_multiple_baseline']
        scale=D(100_000_000)/D(old['shares'])*D(old['fx_to_quote'])
        ov={k:D(v['equity_value'] if code=='09988' else v['raw_legacy_equity_value'])*scale for k,v in old['scenarios'].items()}
        if code=='09988':
            old_audit_model=dict(kind='profit_pe',currency='CNY',amount_unit='100_million',shares=old['shares'],fx_to_quote=old['fx_to_quote'],horizon='same 2026-10-31 forward ordinary profit',profit_basis='legacy normalized ordinary earnings includes finance/investment returns',scenarios={k:dict(revenue=v['revenue'],net_margin=v['net_margin'],adjustments=[],profit=v['normalized_ordinary_profit'],pe=v['pe'],equity_adjustments=[],equity_value=v['equity_value']) for k,v in old['scenarios'].items()})
        else:
            old_audit_model=dict(kind='other',reason='legacy EV/NOPAT capitalization /1.10 plus raw capital bridge; original arithmetic in inputs, not FCFF',unrounded_v50=ov)
        no_reverse=dict(status='not_applicable',reason='old capitalization model retained for rule-only replay; new DCF analyzed separately',cases=[])
        old_check=discount_audit(code,old_audit_model,ov,factor,no_reverse,market,tag='old-rule',version='stock-research-audit/v2')
        tax_correction={k:D(0) for k in LABELS}
        if code=='01810':
            for k,row in old['scenarios'].items():
                assumed_refund=sum((min(D(0),D(seg['revenue'])*D(seg['ebit_margin'])) for seg in row['segments']),D(0))*D(row['tax_rate'])
                tax_correction[k]=assumed_refund*D(row['capitalization_multiple'])/D(row['discount_divisor'])*scale
        fixed_values={k:v+tax_correction[k] for k,v in ov.items()}
        fixed_model=deepcopy(old_audit_model)
        if code=='01810':fixed_model['unrounded_v50']=fixed_values
        fixed_check=discount_audit(code,fixed_model,fixed_values,factor,no_reverse,market,tag='fixed-input-new-rule')
        # Keep every assumption fixed in the rule-only replay: rules cannot invent
        # a new residual loss or a cash allocation when the evidence is unknown.
        rules_only=fixed_values
        normalized={k:(D(v['equity_value']) if code=='09988' else D(v['operating_ev'])+D(v['common_bridge_equity_adjustment']))*scale+tax_correction[k] for k,v in old['scenarios'].items()}
        attrs=shapley(locked,updated)
        alt_attrs=shapley(locked,updated,equal_split=True) if code=='09988' else None
        cases=[];sens=[]
        segment='ai_cloud_labs' if code=='09988' else 'ev_ai'
        reverse_input=dict(scenario='base',segment_id=segment,variable='terminal_margin',target_price=market,lower=0,upper=D('.5'))
        try:
            solved=solve_reverse_dcf(updated,**reverse_input)
            reverse=dict(status='solved',reason='冻结显式期与其它业务，仅反解指定业务终值利润率；不是唯一业务天花板',cases=[dict(reverse_input,**solved)])
        except ReverseNoSolutionError as exc:
            reverse=dict(status='no_solution',reason=str(exc),cases=[reverse_input])
        for delta in (D('-.01'),D(0),D('.01')):
            m=deepcopy(updated)
            for s in m['scenarios']['base']['segments']:s['discount_rate']=D(s['discount_rate'])+delta
            # Align scenarios solely for sensitivity calculation, not new quoted bands.
            m['scenarios']={k:deepcopy(m['scenarios']['base']) for k in LABELS}
            m,_=seal_model(m)
            try:result=dict(status='solved',**solve_reverse_dcf(m,**reverse_input))
            except ReverseNoSolutionError as exc:result=dict(status='no_solution',reason=str(exc))
            sens.append(dict(wacc_shift=delta,model=m,result=result))
        write(HERE/f'{code}-locked-dcf.json',locked)
        write(HERE/f'{code}-updated-dcf.json',updated)
        write(HERE/f'{code}-reverse-sensitivity.json',sens)
        check=discount_audit(code,updated,ures['values'],factor,reverse,market)
        non_dcf = ov['base']
        diffs=dict(tax_loss_normalization=rules_only['base']-non_dcf,capital_representation=normalized['base']-rules_only['base'],dcf_expansion_and_added_long_term_assumptions=lres['values']['base']-normalized['base'],**attrs)
        assert abs(sum(diffs.values())-(ures['values']['base']-ov['base']))<D('1e-18')
        bridge=ures['details']['base']['equity_adjustments']*scale
        terminal_pv=sum(s['terminal_pv'] for s in ures['details']['base']['segments'])*scale
        out[code]=dict(market_price=market,market_date='2026-10-30',raw_old_v50=ov,rules_only_v50=rules_only,normalized_multiple_v50=normalized,locked_dcf_v50=lres['values'],updated_dcf_v50=ures['values'],legacy_discount_factor=factor,
          old_p1=ov['base']*factor,updated_conditional_p1_at_legacy_discount=ures['values']['base']*factor,v50_contributions=diffs,p1_contributions={k:v*factor for k,v in diffs.items()},rule_repair_final_p1=None,
          rule_repair_note='仅明确取消无依据的即时亏损税盾，折扣不自动取新值；规则不自动决定损失金额/资产归属，唯一正式修复后P1无法确定。',alternative_segment_split_contributions=alt_attrs,
          bridge_per_share=bridge,terminal_pv_per_share=terminal_pv,explicit_pv_per_share=ures['values']['base']-bridge-terminal_pv,
          reverse=reverse,reverse_sensitivity=[dict(wacc_shift=s['wacc_shift'],result=s['result']) for s in sens],audit=check,
          conditional_discount_sensitivity=[dict(remove=k,p1=ures['values']['base']*factor/(1-D(v['value']))) for k,v in data.get('old_risk_discounts',{}).items() if isinstance(v,dict) and 'value' in v],
          old_rule_audit=old_check,fixed_input_new_rule_audit=fixed_check,input_hashes={name:sha(dest/name) for name in ('data-pack.md','assumptions.json','evidence.md')})
    write(HERE/'results.json',out)
    manifest['production_missing']=[p for p in manifest['production_before'] if not Path(p).is_file()]
    manifest['production_after']={p:sha(Path(p)) for p in manifest['production_before'] if Path(p).is_file()}
    manifest['production_unchanged']=None if manifest['production_missing'] else manifest['production_before']==manifest['production_after']
    assert manifest['production_unchanged'] is not False, 'production input changed; inspect without overwriting baseline'
    manifest['inputs']={code:data['input_hashes'] for code,data in out.items()}
    for code in out:manifest['packs'][code]['frozen']=str((HERE/'inputs'/code/'data-pack.md').relative_to(ROOT))
    manifest['code_hashes']={p:sha(ROOT/p) for p in ('scripts/research_valuation.py','scripts/research_consistency.py','scripts/research_runner.py','scripts/research_recovery.py','framework/investment_framework.md','framework/investment_framework_compact.md',str((HERE/'replay.py').relative_to(ROOT)))}
    write(HERE/'manifest.json',manifest)
    print(json.dumps({code:{k:v for k,v in d.items() if k in ('raw_old_v50','locked_dcf_v50','updated_dcf_v50','v50_contributions','reverse','old_p1','updated_conditional_p1_at_legacy_discount')} for code,d in out.items()},ensure_ascii=False,indent=2,default=json_number))

if __name__=='__main__':
    with localcontext() as context:
        context.prec=50
        main()
