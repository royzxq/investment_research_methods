#!/usr/bin/env python3
"""Offline same-pack/date regression; diagnostic numbers never become quotes."""
from copy import deepcopy
from decimal import Decimal as D
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p/'scripts/research_consistency.py').exists())
sys.path[:0] = [str(REPO), str(REPO/'scripts')]
from scripts import research_valuation as calc, research_consistency as checks
from scripts.stock_price_map import json_number


def load(name):
    return json.loads((HERE/'frozen'/name).read_text(), parse_float=D)


def module(name, filename):
    spec=importlib.util.spec_from_file_location(name, HERE/'frozen'/filename)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


r4=module('isolated_r4', 'replay_r4.py')
legacy=module('isolated_legacy_dcf', 'legacy_research_valuation.py')


def dec(value): return D(str(value))


def flat(model, row):
    model['scenarios']={s:deepcopy(row) for s in ('low','base','high')}
    return model


def migrate_legacy(model):
    m=deepcopy(model);m['year_end_offset']=0
    for r in m['scenarios'].values():
        for s in r['segments']:
            for y in s['years']:
                y['cash_tax']=dec(y['revenue'])*dec(y['ebit_margin'])*dec(y.pop('tax_rate'))
            t=s['terminal'];n=dec(s['years'][-1]['revenue'])*(1+dec(t['growth']))*dec(t['margin'])*(1-dec(t['tax_rate']))
            t['invested_capital']=n/dec(t.pop('roic'))
    return m


def ali_model(case):
    original=load('09988/inputs.json')['model'];m=deepcopy(original);m['year_end_offset']=0
    row=deepcopy(m['scenarios']['base'])
    for original_seg, out in zip(row['segments'],case['segments']):
        t=original_seg['terminal'];g=dec(t['growth'])
        years=[dict(year=y['year'],revenue=dec(y['revenue'])*10,
                    ebit_margin=dec(y['ebit'])/dec(y['revenue']),cash_tax=dec(y['cash_tax'])*10,
                    da=dec(y['da'])*10,capex=dec(y['capex'])*10,delta_nwc=dec(y['delta_nwc'])*10)
               for y in out['years']]
        index=row['segments'].index(original_seg)
        changed=(index==0 and case['parameters']['net_recovery_by_y3'] is not None) or (index==1 and case['parameters']['labs'] is not None)
        terminal_ebit=(dec(out['years'][-1]['ebit'])*(1+g)*10 if changed else
                       dec(original_seg['years'][-1]['revenue'])*(1+g)*dec(t['margin']))
        terminal_nopat=dec(out['terminal_nopat'])*10
        effective_tax=1-terminal_nopat/terminal_ebit if terminal_ebit else D(0)
        ic=dec(out['terminal_reinvestment'])*10/g if g else terminal_nopat/dec(t['roic'])
        original_seg['years']=years
        original_seg['terminal']=dict(growth=g,margin=terminal_ebit/(years[-1]['revenue']*(1+g)),tax_rate=effective_tax,invested_capital=ic)
        original_seg['assumptions']='R4 conditional path; tax-entity mapping, cloud productive inputs and capital claims remain unresolved.'
    row['equity_value']=(dec(case['ev'])+dec(case['capital_before_unresolved_claims']))*10
    return flat(m,row)


def xiaomi_model(case):
    d=load('01810/inputs.json');f=d['facts'];rate=dec(case['discount_rate'])
    rent=(dec(f['h1_lease_cash'])-dec(f['h1_rou_da']))/dec(f['h1_revenue'])
    core_years=[dict(year=i,revenue=dec(y['revenue']),ebit_margin=dec(y['ebit'])/dec(y['revenue']),
                     cash_tax=dec(y['cash_tax']),da=dec(y['da']),capex=dec(y['capex']),delta_nwc=dec(y['delta_nwc']))
                for i,y in enumerate(case['years'],1)]
    core=dict(id='core',source='frozen/01810/inputs.json and R4 expense bridge',assumptions='Conditional aggregate gross profit less operating expenses and cash rent; no adoption',discount_rate=rate,
              years=core_years,terminal=dict(growth=D('.02'),margin=core_years[-1]['ebit_margin'],tax_rate=D('.20'),invested_capital=dec(case['terminal_invested_capital'])))
    src=next(s for s in d['scenario_config']['base']['segments'] if s['id']=='ev_ai');ys=[]
    for i,y in enumerate(src['rows'],1):
        revenue=dec(y['revenue']);margin=dec(y['reported_ebit_margin'])-rent
        ys.append(dict(year=i,revenue=revenue,ebit_margin=margin,cash_tax=max(revenue*margin,0)*dec(y['tax_rate']),
                       da=dec(y['da']),capex=dec(y['capex']),delta_nwc=dec(y['delta_nwc'])))
    margin=dec(src['terminal_reported_ebit_margin'])-rent;tax=dec(src['terminal_tax_rate']);g=dec(src['terminal_growth'])
    ic=ys[-1]['revenue']*(1+g)*margin*(1-tax)/dec(src['terminal_roic'])
    ev=dict(id='ev_ai',source='frozen/01810/inputs.json',assumptions='Retained R2 EV path, not newly verified',discount_rate=rate,years=ys,
            terminal=dict(growth=g,margin=margin,tax_rate=tax,invested_capital=ic))
    capital=dec(case['capital_before_unresolved_claims'])
    row=dict(segments=[core,ev],equity_adjustments=[dict(id='conditional_capital',amount=capital,reason='Original conditional capital bridge; unresolved claims are NOT zero',source='frozen/01810/results.json')],equity_value=dec(case['core_ev'])+dec(case['retained_ev_ai_value'])+capital)
    model=dict(kind='dcf_fcff',currency='CNY',amount_unit='100_million',shares=int(d['shares']),fx_to_quote=1/dec(d['cny_per_hkd']),year_end_offset=dec(d['year_end_offset']))
    return flat(model,row)


def audit_gap(code, day, gaps):
    # Isolated non-quotation document. It is not a formal company completion.
    controls={s:dict(status='unknown',refs=['VALUATION_INPUTS']) for s in ('entry','add')}
    controls['holding']=dict(status='unknown',refs=['HOLDING_NOT_REASSESSED'])
    doc=dict(meta=dict(schema_version='stock-research/v4',code=code+'.HK',name={'09988':'阿里巴巴','01810':'小米集团'}[code],valuation_date=day,currency='HKD',generator='codex',report_path=f'research/investment/studies/valuation-revisions/2026-11-15-r5/{code}-audit.md'),
             price_map=dict(mode='unavailable',reason='隔离回归，关键资本/经营假设未闭合',v50=None,p1=None,t1=dict(price_condition='未形成新报价；原持仓与卖出控制留在原报告，本隔离件不接执行')),
             research_controls=controls,monitoring=[])
    basis={key:dict(status='unresolved',affects='p1' if key=='residual_discount' else 'v50',evidence=[],explanation='原冻结输入及R4补证不能消除以下重要缺口；条件数字仅供诊断',gaps=[value]) for key,value in gaps.items()}
    a=dict(schema_version='stock-research-audit/v5',identity={k:doc['meta'][k] for k in ('code','generator','valuation_date','currency')},
           valuation=dict(kind='unavailable',reason='影响中性权益价值的核心证据未决'),baseline=None,
           valuation_review=dict(base_case='尚无可采纳中性路径；诊断保留原包及日期',method_choice='分部FCFF诊断，采用值暂不可定',pe_crosscheck='既有倍数与利润路径仅作具名条件，不用旧价或现价校准',market_check=dict(price=None,as_of=None,source='本轮不刷新行情',explanation='沿用原包，不产生当前行情断言'),reverse_dcf=dict(status='unavailable',reason='无可采纳主模型，条件模型另存',cases=[]),input_basis=basis),
           discounts={k:dict(value=None,range=None,risk_ids=[k],reason='未闭合残余金额，未知不当作0',change=dict(kind='initial',reason='隔离未决参数，无正式折扣采纳',evidence=[])) for k in checks.DISCOUNTS},
           risks=[dict(id=k,economic_key=f'{code}:residual:{k}',description='残余归属待定，禁止把未知当零',owner=k,scope='范围尚待原文核实，无实际数值扣减',source='R4 gap inventory') for k in checks.DISCOUNTS],
           constraints=[dict(id='VALUATION_INPUTS',scope=['entry','add'],status='unknown',action='unavailable',reason='隔离结果不可作为新报价',release_conditions=['完成利润/投入/税/普通股资本及残余风险证据闭合'],lifecycle='persistent'),
                        dict(id='HOLDING_NOT_REASSESSED',scope=['holding'],status='unknown',action='review_holding',reason='本隔离件不复评持仓控制，不宣告原风险解除；执行继续读原正式报告',release_conditions=['独立完成适用持仓复评'],lifecycle='persistent')],
           release_all_of=dict(entry=['VALUATION_INPUTS'],add=['VALUATION_INPUTS'],holding=['HOLDING_NOT_REASSESSED']),p1_basis={})
    return a,doc


def build():
    for item in load('manifest.json'):
        assert hashlib.sha256((HERE/'frozen'/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
    original=load('09988/inputs.json')['model']
    old=legacy.evaluate_dcf(original)['values']['base'];migrated=migrate_legacy(original)
    same=calc.evaluate_dcf(migrated,input_bridges=True)['values']['base']
    models={'09988-equivalent':migrated};stages=[]
    cases=[('tax_no_cross_entity_offset',r4.alibaba_case()),('commerce_recovery_assumption',r4.alibaba_case(15,.02)),('labs_cost_assumption',r4.alibaba_case(15,.02,labs=(.25,67.5,.07)))]
    previous=old
    for name,case in cases:
        m=ali_model(case);v=calc.evaluate_dcf(m,input_bridges=True)['values']['base'];models['09988-'+name]=m
        assert abs(v-dec(case['conditional_v50']))<D('.000001')
        stages.append(dict(stage=name,conditional_v50=v,delta_v50=v-previous,diagnostic_p1_at_unchanged25=v*D('.75'),delta_p1_at_unchanged25=(v-previous)*D('.75')));previous=v
    xc=[]
    for expense in (.142,.1455,.149):
        case=r4.xiaomi_core(expense);m=xiaomi_model(case);v=calc.evaluate_dcf(m,input_bridges=True)['values']['base']
        assert abs(v-dec(case['conditional_value']))<D('.000001')
        models['01810-expense-'+str(expense)]=m;xc.append(dict(expense_ratio=expense,conditional_v50=v,equivalent_migration_delta=v-dec(case['conditional_value'])))
    tax=[]
    for rate in (.15,.20,.25):
        case=r4.alibaba_case(15,.02,labs=(.25,67.5,.07),commerce_tax=rate);m=ali_model(case)
        result=calc.evaluate_dcf(m,input_bridges=True);tax.append(dict(tax_rate=rate,conditional_v50=result['values']['base'],commerce_reinvestment=result['details']['base']['segments'][0]['terminal_reinvestment']))
    xold=load('01810/results.json');old_factor=D(1)
    for v in load('01810/inputs.json')['original']['codex']['discounts'].values(): old_factor*=1-dec(v)
    midpoint=xc[1]['conditional_v50'];r2=dec(xold['new_scenarios']['base']['v50']) if 'v50' in xold['new_scenarios']['base'] else dec(xold['waterfall']['codex'][3]['v50'])
    output=dict(schema='isolated-input-bridges/v1',production_eligible=False,full_research_started=False,
        stocks={'09988':dict(valuation_date='2026-11-09',pack_sha256='8816b3490e0597bd0f17641b88f7def6fad01f839261550d1e84dbb7e88be76b',original_v50=dec(load('09988/results.json')['original_v50']),original_p1=dec(load('09988/results.json')['original_p1']),old_r2_conditional_v50=old,equivalent_migration_delta=same-old,stages=stages,pure_tax_sensitivity=tax,adopted_v50=None,adopted_p1=None),
                '01810':dict(valuation_date='2026-11-08',pack_sha256='4c53ea20a25e661b8583382093f7297e95f7d39c0393469bb3501b144eb62264',original=xold['original_replay'],historical_waterfall=xold['waterfall'],old_r2_conditional_v50=r2,expense_cases=xc,expense_assumption_delta=midpoint-r2,diagnostic_p1_at_old_discounts=midpoint*old_factor,old_discount_factor=old_factor,adopted_residual_discounts={k:None for k in checks.DISCOUNTS},adopted_v50=None,adopted_p1=None)},
        caveats=['迁移等价不是新估值准确性证明','税纠错以既有25%及无跨主体抵扣条件为前提；真实法律主体税仍未决','小米资本桥/回报门槛均条件；无新增可确认资本归属收益','顺序分解有路径依赖，DCF、利润路径、折扣不可都记成规则纠错','条件P1保留旧折扣仅供影响分解，禁止采纳'])
    return output,models


def write():
    out,models=build()
    for name,obj in [('results.json',out),('diagnostic-models.json',models)]:
        (HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=json_number)+'\n')
    gaps={
      '09988':dict(profit='长期竞争恢复与Labs成本补贴持续性未证',investment='云资产投用/寿命/利用率与完整CapEx、DA路径未闭合',tax='分部与法律税务主体、可用亏损/抵扣和终值有效税率未核全',capital='估值日金融资产、NCI/夹层、权益法范围及预提税未闭合',residual_discount='保留25%仅为敏感性，不能证明当前充分性'),
      '01810':dict(profit='总费用率有历史约束但未来组合/EV利润路径仍条件',investment='生产性资本、营运资本与金融业务资金需求未闭合',tax='法律实体税负及实际分配预提税未核全',capital='金融期权现值/标的价值重叠、限制资金/保证金、普通股分配归属未决',residual_discount='印度案件重叠、既有准备覆盖及其余独立残余未约束')}
    for code,gs in gaps.items():
        a,d=audit_gap(code,out['stocks'][code]['valuation_date'],gs)
        (HERE/f'{code}-price-map-isolated.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        (HERE/f'{code}-audit.md').write_text('# 隔离输入审计；不接正式报价或完成登记\n\n'+checks.render_report_block(a,d))
    print(json.dumps({c:{k:v for k,v in s.items() if k in ('equivalent_migration_delta','expense_assumption_delta','stages','expense_cases','adopted_v50','adopted_p1')} for c,s in out['stocks'].items()},ensure_ascii=False,indent=2,default=json_number))

if __name__=='__main__': write()
