#!/usr/bin/env python3
"""Incremental R4 conditional calculations; not a production quote generator.

Alibaba amounts: CNY bn. Xiaomi amounts: CNY100m. All prices HKD.
Original valuation dates, share counts, FX, capital bridges are frozen.
Unclosed claims are disclosed rather than imputed as zero or a new haircut.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT/name).read_text())


def commerce_profit(year, net_recovery, later_growth):
    # Current run-rate annualization and SBC/amortization allocation remain assumptions.
    anchor = 39.749 * 4 - 7 - 2
    return anchor + net_recovery * [.25, .6, 1][year-1] if year <= 3 else (anchor+net_recovery)*(1+later_growth)**(year-3)


def positive_tax(cloud, labs, rate):
    return (max(cloud, 0)+max(labs, 0))*rate


def labs_path(revenue_growth, year3_cost, later_cost_growth):
    rows=[]
    for year in range(1,11):
        cost = 70.296 + (year3_cost-70.296)*year/3 if year<=3 else year3_cost*(1+later_cost_growth)**(year-3)
        revenue=13.352*(1+revenue_growth)**year
        rows.append(dict(year=year,revenue=revenue,cost=cost,ebit=revenue-cost))
    return rows


def one_cohort_cost_change(delta_capex, short_share, short_life, long_life, tax, rate):
    # Same productive output, one cohort procurement-cost change at end Y1.
    # No free operating upside; economic depreciation changes tax, not EBITDA.
    pv=-delta_capex/(1+rate)
    for share,life in [(short_share,short_life),(1-short_share,long_life)]:
        pv+=sum(delta_capex*share/life*tax/(1+rate)**year for year in range(2,life+2))
    return pv


def alibaba_case(recovery=None, later_growth=None, labs=None, commerce_tax=.25):
    d=read('09988/inputs.json');model=d['model'];scenario=model['scenarios']['base']
    factor=1e9/model['shares']*model['fx_to_quote']; parts=d['ai_decomposition_cny_billion']['base']
    lab_rows=labs_path(*labs) if labs else None
    out=[]
    for si,seg in enumerate(scenario['segments']):
        rows=[];pv=0
        for j,y in enumerate(seg['years']):
            year=j+1;revenue=y['revenue']/10;ebit=revenue*y['ebit_margin'];tax=ebit*y['tax_rate']
            nwc=y['delta_nwc']/10
            if si==0:
                if recovery is not None:ebit=commerce_profit(year,recovery,later_growth)-revenue*3.376/823.448
                tax=max(ebit,0)*commerce_tax
            elif si==1:
                cloud=parts[j]['cloud_ebit'];lab=lab_rows[j]['ebit'] if labs else parts[j]['labs_ebit']
                if labs:
                    revenue=parts[j]['cloud_revenue']+lab_rows[j]['revenue']
                    previous_revenue=rows[-1]['revenue'] if rows else 193.748+13.352
                    nwc=(revenue-previous_revenue)*.03
                ebit=cloud+lab;tax=positive_tax(cloud,lab,.25)
            flow=ebit-tax+(y['da']-y['capex'])/10-nwc
            discounted=flow/(1+seg['discount_rate'])**year;pv+=discounted
            rows.append(dict(year=year,revenue=revenue,ebit=ebit,cash_tax=tax,da=y['da']/10,capex=y['capex']/10,delta_nwc=nwc,fcff=flow,pv=discounted))
        t=seg['terminal'];g=t['growth'];tebit=seg['years'][-1]['revenue']/10*(1+g)*t['margin']
        ttax=tebit*t['tax_rate']
        if si==0:
            if recovery is not None:tebit=rows[-1]['ebit']*(1+g)
            ttax=max(tebit,0)*commerce_tax
        elif si==1 and labs:
            cloud=parts[-1]['cloud_ebit']*(1+g);lab=lab_rows[-1]['ebit']*(1+g)
            tebit=cloud+lab;ttax=positive_tax(cloud,lab,.25)
        nopat=tebit-ttax;reinvestment=nopat*g/t['roic']
        if si==0:
            # Tax-only sensitivity holds productive capital at the 25% tax case.
            reinvestment=(tebit-max(tebit,0)*.25)*g/t['roic']
        terminal_pv=(nopat-reinvestment)/(seg['discount_rate']-g)/(1+seg['discount_rate'])**len(rows)
        out.append(dict(id=seg['id'],years=rows,explicit_pv=pv,terminal_nopat=nopat,terminal_reinvestment=reinvestment,terminal_pv=terminal_pv,ev=pv+terminal_pv))
    ev=sum(x['ev'] for x in out);capital=sum(x['amount']/10 for x in scenario['equity_adjustments']);v=(ev+capital)*factor
    return dict(parameters=dict(net_recovery_by_y3=recovery,later_profit_growth=later_growth,labs=labs,commerce_tax=commerce_tax),segments=out,ev=ev,capital_before_unresolved_claims=capital,conditional_v50=v,conditional_p1_at_legacy25=v*.75,
                conditions='R2 cloud growth/capex/DA/ROIC and financial bridge remain fixed, not newly certified. Cloud/Labs taxes separate, no prospective loss offset. Combined positive terminal NOPAT uses retained ROIC; a loss-making Labs tail is a conditional ongoing strategic subsidy, not verified sustainable cash flow. No neutral adoption.')


def xiaomi_core(expense_ratio, rate=.095):
    d=read('01810/inputs.json');old=read('01810/results.json');cfg=d['scenario_config']['base'];f={k:float(v) for k,v in d['facts'].items()}
    core=[s for s in cfg['segments'] if s['id']!='ev_ai'];evseg=next(s for s in cfg['segments'] if s['id']=='ev_ai')
    margins={'phone':80.75871/863.92014,'iot':124.87854/559.59160,'internet':141.48315/185.12009,'other':-.78855/24.39791}
    rent=(f['h1_lease_cash']-f['h1_rou_da'])/f['h1_revenue'];offset=float(d['year_end_offset']);rows=[];pv=0
    for j in range(6):
        ys=[s['rows'][j] for s in core];rev=sum(float(y['revenue']) for y in ys)
        gp=sum(float(s['rows'][j]['revenue'])*margins[s['id']] for s in core)
        expenses=rev*expense_ratio;rent_cost=sum(float(s['rows'][j]['revenue'])*rent for s in core if s['id']!='other')
        ebit=gp-expenses-rent_cost;tax=max(ebit,0)*.20
        da=sum(float(y['da']) for y in ys);capex=sum(float(y['capex']) for y in ys);nwc=sum(float(y['delta_nwc']) for y in ys)
        fcff=ebit-tax+da-capex-nwc;value=fcff/(1+rate)**(j+1+offset);pv+=value
        rows.append(dict(year=ys[0]['year'],revenue=rev,gross_profit=gp,operating_expenses=expenses,ebit_before_rent=gp-expenses,cash_rent_adjustment=rent_cost,ebit=ebit,cash_tax=tax,da=da,capex=capex,delta_nwc=nwc,fcff=fcff,pv=value))
    # Same productive capital as R2, rather than earning an artificial higher ROIC
    # when expense allocations are changed. This retained capital need is conditional.
    ic=0
    for s in core:
        rev=float(s['rows'][-1]['revenue'])*1.02
        margin=float(s['terminal_reported_ebit_margin'])-(rent if s['id']!='other' else 0)
        ic+=rev*margin*(1-float(s['terminal_tax_rate']))/float(s['terminal_roic'])
    tn=rows[-1]['ebit']*.8*1.02;reinvest=ic*.02;tpv=(tn-reinvest)/(rate-.02)/(1+rate)**(6+offset)
    evpv=0;evrows=[]
    for j,y in enumerate(evseg['rows']):
        rev=float(y['revenue']);ebit=rev*(float(y['reported_ebit_margin'])-rent);tax=max(ebit,0)*float(y['tax_rate'])
        flow=ebit-tax+float(y['da'])-float(y['capex'])-float(y['delta_nwc']);evpv+=flow/(1+rate)**(j+1+offset)
        evrows.append(dict(year=y['year'],fcff=flow))
    evn=rev*1.02*(float(evseg['terminal_reported_ebit_margin'])-rent)*(1-float(evseg['terminal_tax_rate']))
    evt=evn*(1-.02/float(evseg['terminal_roic']))/(rate-.02)/(1+rate)**(6+offset)
    capital=float(old['new_scenarios']['base']['capital_bridge']['total']);total=pv+tpv+evpv+evt
    factor=1e8/float(d['shares'])/float(d['cny_per_hkd']);v=(total+capital)*factor
    return dict(expense_ratio=expense_ratio,discount_rate=rate,years=rows,explicit_pv=pv,terminal_invested_capital=ic,terminal_reinvestment=reinvest,terminal_pv=tpv,core_ev=pv+tpv,retained_ev_ai_value=evpv+evt,capital_before_unresolved_claims=capital,conditional_value=v,
                caveat='Core historical category gross margins and recent reported aggregate expense ratios constrain this counterfactual. Future revenues/capex/terminal productive capital and EV assumptions are R2 conditions, not new facts. Unsettled ownership/tax/liquidity claims are outside this numeric bridge.')


def build():
    a0=alibaba_case();a_cases=[]
    for recovery,g in [(10,.01),(15,.02),(25,.03)]:
        a_cases.append(alibaba_case(recovery,g,labs=(.25,67.5,.07)))
    alabs=[alibaba_case(15,.02,labs=p) for p in [(.20,75,.08),(.25,67.5,.07),(.25,65,.06)]]
    atax=[alibaba_case(15,.02,labs=(.25,67.5,.07),commerce_tax=t) for t in [.15,.20,.25]]
    d=read('09988/inputs.json');afactor=1e9/d['model']['shares']*d['model']['fx_to_quote']
    caps=[dict(first_year_cash_capex=c,usable_tax_rate=tax,delta_enterprise_value_cny_bn=one_cohort_cost_change(c-220,.7,5,20,tax,.11),delta_v50=one_cohort_cost_change(c-220,.7,5,20,tax,.11)*afactor,
               conditions='One cohort only; output/EBITDA held fixed. Tax=25% requires economic and tax depreciation to coincide and the owning entity to have sufficient taxable profit; tax=0 assumes no usable shield. Neither case proves actual future cash tax or the full cloud capital path.') for c in [180,200,230] for tax in [0,.25]]
    xcases=[xiaomi_core(e) for e in [.142,.1455,.149]]
    tail_source=read('01810/results.json')['identified_india_tail']
    tail=float(tail_source['additional_one_case_full_loss_reserve']);xinput=read('01810/inputs.json');xfactor=1e8/float(xinput['shares'])/float(xinput['cny_per_hkd'])
    hurdle=[dict(expense_ratio=e,required_operating_return=rate,conditional_value_before_claims=xiaomi_core(e,rate)['conditional_value'],after_one_india_full_loss_only=xiaomi_core(e,rate)['conditional_value']-tail*xfactor) for e in [.142,.149] for rate in [.12,.14]]
    return dict(schema='isolated-incremental-evidence-r4/v1',execution_date='2026-11-15',production_eligible=False,full_research_started=False,
                stocks={'09988':dict(valuation_date='2026-11-09',r3_replay=a0,commerce_only_bridge=alibaba_case(15,.02),commerce_profit_bridge_cases=a_cases,labs_cost_cases=alabs,commerce_tax_cases=atax,one_capex_cohort_cases=caps,adopted_neutral_v50_range=None,adopted_p1_range=None,
                                    range_status='Evidence supports narrower mechanisms and testable conditional paths, not probability coverage or full neutral equity interval. Do not combine single-variable extremes into a quote.'),
                        '01810':dict(valuation_date='2026-11-08',core_expense_cases=xcases,conditional_operating_band_before_unresolved_claims=[min(x['conditional_value'] for x in xcases),max(x['conditional_value'] for x in xcases)],hurdle_diagnostics=hurdle,inherited_india_stress_conditions=tail_source,hurdle_conditions='12%/14% are research operating-asset required returns, not investor instructions or equity IRRs. No second d_base multiplier. Equity capital bridge and all unresolved claims remain conditional; a single adverse legal case is not an aggregate risk reserve.',adopted_neutral_v50_range=None,adopted_p1_range=None,finance_option_current_value=None,residual_discounts={k:None for k in ['d_base','r_chip','r_v5','r_gov','r_terminal']},
                                     range_status='Aggregate expense allocation is improved, but capital ownership and residual losses remain unresolved. This band is conditional, not an adopted neutral V50/P1 range.')})


if __name__=='__main__':
    out=build();(ROOT/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    a=out['stocks']['09988'];x=out['stocks']['01810']
    print(json.dumps({'alibaba_r3_replay':a['r3_replay']['conditional_v50'],'alibaba_profit_bridge':[v['conditional_v50'] for v in a['commerce_profit_bridge_cases']],'alibaba_labs':[v['conditional_v50'] for v in a['labs_cost_cases']],'alibaba_tax':[v['conditional_v50'] for v in a['commerce_tax_cases']],'xiaomi_conditional_operating_band':x['conditional_operating_band_before_unresolved_claims'],'hurdle_diagnostics':x['hurdle_diagnostics'],'adopted_prices':None},ensure_ascii=False,indent=2))
