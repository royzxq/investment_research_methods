#!/usr/bin/env python3
"""Read only, standalone reproduction. Uses only the adjacent model.json.

Run: python3 <this file> > output/neutral-review/model-recalculated.json
No file is written by this program; no network or external imports are used.
Amounts: CNY 100 million, actual shares; prices: CNY/share.
"""
from copy import deepcopy
from decimal import Decimal, localcontext, ROUND_HALF_UP
from pathlib import Path
from math import erf, exp, log, sqrt
import json

D = lambda x: Decimal(str(x))


def calculate(model, scenario='base'):
    with localcontext() as ctx:
        ctx.prec = 50
        row = model['scenarios'][scenario]
        offset = D(model['year_end_offset'])
        explicit = terminal = D(0)
        flows, segments = [], []
        for s in row['segments']:
            rate = D(s['discount_rate'])
            epv = D(0)
            for y in s['years']:
                nopat = D(y['revenue']) * D(y['ebit_margin']) - D(y['cash_tax'])
                fcff = nopat + D(y['da']) - D(y['capex']) - D(y['delta_nwc'])
                pv = fcff / (1 + rate) ** (D(y['year']) + offset)
                epv += pv
                flows.append(dict(segment=s['id'], year=2026+y['year'], nopat=nopat, fcff=fcff, pv=pv))
            t = s['terminal']; g = D(t['growth'])
            assert rate > g
            nopat_t = D(s['years'][-1]['revenue'])*(1+g)*D(t['margin'])*(1-D(t['tax_rate']))
            investment = D(t['invested_capital'])*g
            fcff_t = nopat_t-investment
            assert fcff_t > 0
            tv = fcff_t/(rate-g)
            tpv = tv/(1+rate)**(D(len(s['years']))+offset)
            explicit += epv; terminal += tpv
            segments.append(dict(id=s['id'], explicit_pv=epv, terminal_pv=tpv, terminal_nopat=nopat_t,
                                 terminal_reinvestment=investment, terminal_ic=D(t['invested_capital']),
                                 terminal_roic=nopat_t/D(t['invested_capital'])))
        bridge = sum((D(a['amount']) for a in row['equity_adjustments']), D(0))
        equity = explicit+terminal+bridge
        price = equity*D(100000000)/D(model['shares'])*D(model['fx_to_quote'])
        return dict(price=price, explicit_pv=explicit, terminal_pv=terminal, enterprise_value=explicit+terminal,
                    equity_adjustments=bridge, equity_value=equity, flows=flows, segments=segments)


def quote(x):
    return float(D(x).quantize(D('.01'), rounding=ROUND_HALF_UP))


def adjustment(model, ident):
    return next(a for a in model['scenarios']['base']['equity_adjustments'] if a['id']==ident)


def rebuild_investment(model, config, k_scale=1.0, opening_scale=1.0, years=7):
    """Fixed operating output/tax; link capex, DA, production stock, terminal IC.

    70% equipment/7 years, 20% buildings/25, 10% software/5; half-year DA.
    Existing-stock DA rundown is retained. No automatic cash-tax shield.
    """
    for j,s in enumerate(model['scenarios']['base']['segments']):
        stock=config['assets'][j]*opening_scale
        prev=config['r0'][j]; cohorts=[]
        for i,y in enumerate(s['years']):
            old_da=150*config['assets'][j]/800*opening_scale*[.95,.85,.72,.60,.48,.36,.24][i]
            cohort_da=sum(v*(.7/7+.2/25+(.1/5 if i-yr<5 else 0)) for yr,v in cohorts)
            capex=(old_da+cohort_da+config['k'][j]*k_scale*(y['revenue']-prev))/(1-.064)
            da=old_da+cohort_da+.064*capex
            y['capex']=capex; y['da']=da; stock+=capex-da
            cohorts.append((i,capex)); prev=y['revenue']
        s['terminal']['invested_capital']=stock+prev*(config['nwc']+config['cash'])


def change_cash(model, config, nwc):
    change=nwc-config['nwc']
    for j,s in enumerate(model['scenarios']['base']['segments']):
        prev=config['r0'][j]
        for y in s['years']:
            y['delta_nwc'] += change*(y['revenue']-prev)
            prev=y['revenue']
        s['terminal']['invested_capital'] += change*prev
    # Q4 normalized release changes once; each half has the original timing.
    q4_change=-change*sum(config['r0'])
    adjustment(model,'stub-past')['amount']+=q4_change*.5
    adjustment(model,'stub-future')['amount']+=q4_change*.5/(1+config['wacc'])**model['year_end_offset']


def move_margin(model, amount, explicit=False):
    for s in model['scenarios']['base']['segments']:
        s['terminal']['margin']+=amount
        if explicit:
            for y in s['years']:
                y['ebit_margin']+=amount
                y['cash_tax']=max(0,y['revenue']*y['ebit_margin'])*s['terminal']['tax_rate']


def move_wacc(model, amount):
    # Include stub future discounting; no expected loss or other equity item changes.
    first=model['scenarios']['base']['segments'][0]
    old=first['discount_rate']
    adjustment(model,'stub-future')['amount'] *= ((1+old)/(1+old+amount))**model['year_end_offset']
    for s in model['scenarios']['base']['segments']: s['discount_rate']+=amount


def reprice_options(model):
    opt=adjustment(model,'existing-option-claim')
    opt['amount']=0
    pre=float(calculate(model)['equity_value'])
    shares=model['shares']; price=pre*1e8/shares
    for _ in range(100):
        claim=0
        for n,k in [(12397710,34.72),(60860994,29.31),(189480319,24.74)]:
            sigma=.32; t=2.5; rf=.018
            d1=(log(price/k)+(rf+sigma*sigma/2)*t)/(sigma*sqrt(t))
            cdf=lambda z:(1+erf(z/sqrt(2)))/2
            claim+=n*(price*cdf(d1)-k*exp(-rf*t)*cdf(d1-sigma*sqrt(t)))/1e8
        new=(pre-claim)*1e8/shares
        if abs(new-price)<1e-13: break
        price=new
    opt['amount']=-claim
    return claim


def replay_adopted_bridge(data):
    """Recompute the correction and original eight-step option feedback.

    This independently checks the serialized bridge; it does not infer a
    correction amount from the desired final price.
    """
    result = {}
    for scenario, sigma in [('low', .40), ('base', .32), ('high', .25)]:
        x = deepcopy(data['baseline_model'])
        row = x['scenarios'][scenario]
        old = calculate(x, scenario)['price']
        option = next(a for a in row['equity_adjustments'] if a['id'] == 'existing-option-claim')
        old_claim = -option['amount']
        fv = (1182472303.60 + 69046937.09) / 1e8
        row['equity_adjustments'].append(dict(id='fv-correction', amount=fv))
        fixed = calculate(x, scenario)['price']
        option['amount'] = 0
        pre = float(calculate(x, scenario)['equity_value'])
        price = pre * 1e8 / x['shares']
        for _ in range(8):
            claim = 0
            for n, k in [(12397710, 34.72), (60860994, 29.31), (189480319, 24.74)]:
                t, rf = 2.5, .018
                d1 = (log(price / k) + (rf + sigma * sigma / 2) * t) / (sigma * sqrt(t))
                cdf = lambda z: (1 + erf(z / sqrt(2))) / 2
                claim += n * (price * cdf(d1) - k * exp(-rf * t) * cdf(d1 - sigma * sqrt(t))) / 1e8
            price = (pre - claim) * 1e8 / x['shares']
        option['amount'] = -claim
        new = calculate(x, scenario)['price']
        assert abs(new - calculate(data['valuation'], scenario)['price']) < D('1e-12')
        result[scenario] = dict(old=old, fv_only_fixed_options=fixed, new=new,
                                fv_asset_delta=fixed-old, option_feedback_delta=new-fixed,
                                total_delta=new-old, old_option_claim=old_claim, new_option_claim=claim)
    return result


def sensitivity(model, name, transform):
    altered=deepcopy(model); transform(altered)
    x=calculate(altered)['price']; b=calculate(model)['price']
    return dict(name=name, value=x, quoted=quote(x), delta=x-b)


def main():
    data=json.loads(Path(__file__).with_name('model.json').read_text())
    m=data['valuation']; c=data['construction']['configs']['base']
    result={k:calculate(m,k) for k in ('low','base','high')}
    for k,x in result.items():
        assert abs(x['equity_value']-D(m['scenarios'][k]['equity_value']))<D('.000001')
    b=result['base']['price']
    alternatives=[]
    add=lambda name,f:alternatives.append(sensitivity(m,name,f))
    add('investment_k_minus20pct',lambda x:rebuild_investment(x,c,.8))
    add('investment_k_plus20pct',lambda x:rebuild_investment(x,c,1.2))
    add('opening_production_plus10pct',lambda x:rebuild_investment(x,c,1,1.1))
    add('opening_production_minus10pct',lambda x:rebuild_investment(x,c,1,.9))
    add('cash_nwc_6pct',lambda x:change_cash(x,c,.06))
    add('cash_nwc_10pct',lambda x:change_cash(x,c,.10))
    add('terminal_margin_minus50bp',lambda x:move_margin(x,-.005))
    add('terminal_margin_plus50bp',lambda x:move_margin(x,.005))
    add('capital_cost_plus100bp',lambda x:move_wacc(x,.01))
    add('capital_cost_minus100bp',lambda x:move_wacc(x,-.01))
    add('capital_cost_minus50bp',lambda x:move_wacc(x,-.005))
    add('capital_nci_low_claim',lambda x:adjustment(x,'minority-claim').update(amount=-155.76518031))
    add('capital_nci_high_claim',lambda x:adjustment(x,'minority-claim').update(amount=-255.65365936))
    add('capital_associate_annualized_earnings_zero_growth',lambda x:adjustment(x,'associate-book-value').update(amount=39.4508994447*4/3/.112))
    add('capital_mixed_deposits_H1_absolute_split',lambda x:adjustment(x,'gross-financial-assets').update(amount=1562.1001872338))
    add('capital_fv_investments_minus20pct',lambda x:adjustment(x,'separately-reported-fv-equity-investments').update(amount=12.5151924069*.8))
    def tax_plus(x):
        for s in x['scenarios']['base']['segments']:
            for y in s['years']: y['cash_tax']+=y['revenue']*y['ebit_margin']*.05
            s['terminal']['tax_rate']+=.05
    add('cash_tax_plus5pp',tax_plus)
    for growth in (.01,.03):
        add('terminal_g_'+str(growth),lambda x,g=growth:[s['terminal'].update(growth=g) for s in x['scenarios']['base']['segments']])
    def extend(x):
        for s in x['scenarios']['base']['segments']:
            # Alternative mature stage has the same 2% economics; at the last year-
            # end offsets this is an identity test, not evidence of extra growth.
            for n in (8,9):
                prev=s['years'][-1]; t=s['terminal']; rev=prev['revenue']*(1+t['growth'])
                reinv=t['invested_capital']*t['growth']
                s['years'].append(dict(year=n,revenue=rev,ebit_margin=t['margin'],cash_tax=rev*t['margin']*t['tax_rate'],da=prev['da']*(1+t['growth']),capex=prev['da']*(1+t['growth'])+reinv,delta_nwc=0))
                t['invested_capital']*=1+t['growth']
    add('terminal_identical_steady_state_extend2y',extend)
    def v5(x): move_margin(x,-.01,True); move_wacc(x,.02)
    add('V5_margin_minus100bp_WACC_plus200bp',v5)
    def demand(x):
        for j,s in enumerate(x['scenarios']['base']['segments']):
            if s['id'] not in ('consumer','auto'): continue
            # First explicit year only; lost demand then recovers. Revenue and
            # taxes scale; NWC releases first year then reabsorbs in year two.
            y=s['years'][0]; lost=y['revenue']*.05
            y['revenue']-=lost; y['cash_tax']*=.95
            y['delta_nwc']-=lost*(c['nwc']+c['cash'])
            s['years'][1]['delta_nwc']+=lost*(c['nwc']+c['cash'])
            # Committed capex/DA unchanged; no free capacity reduction.
    add('R20_consumer_auto_firstyear_minus5pct',demand)
    joints=[]
    recipes={
        'efficiency_recovery': [('investment',lambda x:rebuild_investment(x,c,.8)),('cash_recovery',lambda x:change_cash(x,c,.06)),('terminal',lambda x:move_margin(x,.005)),('capital_cost',lambda x:move_wacc(x,-.005)),('capital_scope',lambda x:adjustment(x,'minority-claim').update(amount=-155.76518031))],
        'slow_recovery': [('investment',lambda x:rebuild_investment(x,c,1.2)),('cash_recovery',lambda x:change_cash(x,c,.10)),('terminal',lambda x:move_margin(x,-.005)),('capital_cost',lambda x:move_wacc(x,.01)),('capital_scope',lambda x:adjustment(x,'minority-claim').update(amount=-255.65365936))]
    }
    for name,recipe in recipes.items():
        x=deepcopy(m); steps=[]; isolated=[]; previous=b
        for topic,f in recipe:
            iso=sensitivity(m,topic,f); isolated.append(iso)
            f(x); price=calculate(x)['price']
            steps.append(dict(topic=topic,price=price,sequential_delta=price-previous));previous=price
        before=calculate(x)['price']; sumsingle=sum((i['delta'] for i in isolated),D(0))
        interaction=before-b-sumsingle
        opt=reprice_options(x); after=calculate(x)['price']
        joints.append(dict(name=name,order=[v[0] for v in recipe],isolated=isolated,steps=steps,
                           combined_fixed_options=before,arithmetic_sum_single_deltas=sumsingle,
                           interaction_fixed_options=interaction,option_claim=opt,
                           option_interaction=after-before,combined_repriced_options=after,
                           total_change=after-b))
    reverse=[]
    for rate in (.085,.10,.125):
        x=deepcopy(m);x['scenarios']['base']['segments'][2]['terminal']['margin']=rate
        reverse.append(dict(margin=rate,price=calculate(x)['price']))
    slope=(reverse[-1]['price']-reverse[0]['price'])/D('.04')
    diagnostic_margin=D('.085')+(D('50.02')-reverse[0]['price'])/slope
    old={k:calculate(data['baseline_model'],k)['price'] for k in ('low','base','high')}
    out=dict(values={k:quote(v['price']) for k,v in result.items()},unrounded={k:v['price'] for k,v in result.items()},
             old_recomputed=old,adopted_change_bridge=replay_adopted_bridge(data),
             p1=quote(b*D('.8')*D('.95')),results=result,sensitivities=alternatives,joint_cases=joints,
             reverse=dict(admissible_interval=[.085,.125],points=reverse,unconstrained_margin=diagnostic_margin,status='no_solution'),
             limitations='Sensitivities fix existing option claim unless explicitly repriced; values are conditional, not probability estimates. Model is a reproducible research estimate, not audited financial guidance.')
    print(json.dumps(out,ensure_ascii=False,indent=2,default=lambda x:float(x) if isinstance(x,Decimal) else x))


if __name__=='__main__': main()
