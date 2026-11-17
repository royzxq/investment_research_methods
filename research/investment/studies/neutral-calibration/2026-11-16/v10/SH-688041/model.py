"""Frozen SH-688041 model. Read-only by default; python3 -B <this file>.

Amounts: CNY 100 million, shares: actual shares. No network or external input.
The declared input precision and original timing/cohort arithmetic are retained.
Optional --output is restricted to this workspace's output/ working directory.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from copy import deepcopy
from decimal import Decimal as D
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT))
from scripts import research_valuation as rv
from scripts.research_consistency import quote_round

CONFIG = json.loads((HERE / 'model.json').read_text())
SOURCE = ('input/evidence/sources/FIN-2026Q3.pages.txt pp6–12; '
          'FIN-2026H1.pages.txt pp80–83,93–94,106–107,111–119,124,133,136–142; '
          'FIN-2025FY.pages.txt pp31–32; B000 pp1–3; B025 pp4–7')


def amount(ident, value, reason):
    return dict(id=ident, amount=value, reason=reason, source=SOURCE)


def make_scenario(label, p, *, restricted=True, investments=True,
                  recovery=None, investment_recovery=None, investment_tax=None,
                  cohorts=None, terminal_ic_scale=1.0):
    cfg = CONFIG
    full_revenue = p['total26']
    revenue = [full_revenue - cfg['opening_bridge']['ytd_revenue']]
    for growth in p['growth']:
        full_revenue *= 1 + growth
        revenue.append(full_revenue)
    wc = [p['total26'] * p['wc'][0]] + [r*w for r,w in zip(revenue[1:],p['wc'][1:])]
    capex = [p['capex'][0]] + [r*c for r,c in zip(revenue[1:],p['capex'][1:])]
    cohorts = cfg['new_cohorts'] if cohorts is None else cohorts
    # Additions enter service in the following period. No new unobserved disposals.
    da = [old + sum(c*sum(z['weight']/z['life']*(i-j <= z['life']) for z in cohorts)
                   for j,c in enumerate(capex[:i]))
          for i,old in enumerate(cfg['legacy_da'])]
    fixed = cfg['opening_productive_fixed'] + sum(capex) - sum(da)
    years = [dict(year=i+1, revenue=r, ebit_margin=mar, capex=capex[i], da=da[i],
                  delta_nwc=wc[i]-(cfg['opening_nwc'] if i == 0 else wc[i-1]),
                  cash_tax=r*mar*tx)
             for i,(r,mar,tx) in enumerate(zip(revenue,p['margins'],p['tax']))]
    segment = dict(id='processor_consolidated', source=SOURCE,
        assumptions=f'{label}: consolidated processor cash flows; Q4 bridge then 2027–2033; no fabricated CPU/DCU split.',
        discount_rate=p['wacc'], years=years,
        terminal=dict(growth=p['g'],margin=p['tm'],tax_rate=p['tt'],
                      invested_capital=(wc[-1]+fixed)*terminal_ic_scale))
    calc = rv._segment(segment,label,input_bridges=True,
                       year_end_offset=D(str(cfg['timing']['year_end_offset'])))
    ev = float(calc['enterprise_value'])
    adj = [amount('cash_eq',cfg['opening_bridge']['cash_eq'],'9/30 cash equivalent balance; original model precision retained; interest income excluded from EBIT'),
           amount('deposits',p['deposits'],'deposit proxy excludes operating prepayments'),
           amount('financing',-cfg['opening_bridge']['financing'],'matched short/long/current debt and leases retained'),
           amount('op_reserve',-p['reserve'],'minimum operating liquidity stock, not forecast expenditure')]
    changes = cfg['capital_changes']
    recovery = changes['restricted_recovery'] if recovery is None else recovery
    investment_recovery = changes['outside_equity_recovery'] if investment_recovery is None else investment_recovery
    if restricted:
        adj.append(amount('restricted_asset_matched_debt',changes['restricted_monetary_assets']*recovery,
            'restricted monetary claim offsets financing already deducted; not immediately distributable cash; recovery proxy'))
    net_fin = sum(x['amount'] for x in adj)
    adj += [amount('nci',-p['nci']*(ev+net_fin),'NCI economic share proxy; no second deduction of book NCI'),
            amount('existing_award_claim',-p['award'],'existing unclosed employee rights; replacement future labour in EBIT'),
            amount('unfunded_equity_net',-p['claims_loss'],'subscription paid and acquired asset paired; scenario net loss only')]
    if investments:
        rate = changes['outside_equity_gain_tax_rate'] if investment_tax is None else investment_tax
        gross_gain = changes['parent_oci_after_tax'] / (1-changes['outside_equity_gain_tax_rate'])
        cost = changes['outside_equity_book']-gross_gain
        proceeds = changes['outside_equity_book']*investment_recovery
        tax = max(0,proceeds-cost)*rate
        adj.append(amount('parent_nonoperating_equity',proceeds-tax,
            'Q3 nonoperating equity book mark, paired with estimated gain income tax; parent OCI ownership proxy; not cash'))
    eq = ev+sum(x['amount'] for x in adj)
    return dict(segments=[segment],equity_adjustments=adj,equity_value=eq)


def valuation(*, cases=None, **kwargs):
    cfg = CONFIG
    return dict(kind='dcf_fcff',currency='CNY',amount_unit='100_million',
                shares=cfg['identity']['shares'],fx_to_quote=1,
                year_end_offset=cfg['timing']['year_end_offset'],
                scenarios={k:make_scenario(k,p,**kwargs) for k,p in (cases or cfg['cases']).items()})


def evaluate(v):
    return rv.evaluate_dcf(v,input_bridges=True)


def base_variant(patch=None, **kwargs):
    cases=deepcopy(CONFIG['cases'])
    cases['base'].update(patch or {})
    v=valuation(cases=cases,**kwargs)
    # Single-scenario diagnostics need not obey official low/base/high ordering.
    row=v['scenarios']['base']
    return D(str(row['equity_value']))*D(100000000)/D(CONFIG['identity']['shares'])


def capital_rows(v):
    out=[]
    for key,s in v['scenarios'].items():
        opening=CONFIG['opening_productive_fixed']
        for i,y in enumerate(s['segments'][0]['years']):
            closing=opening+y['capex']-y['da']
            out.append(dict(scope=key+' consolidated productive fixed/development assets',
                period='2026Q4' if i==0 else str(2026+i),opening=opening,
                capex=y['capex'],da=y['da'],other=0,closing=closing,
                other_reason='forecast no discrete disposals; cash CapEx equals additions proxy; historical noncash differences not forced to zero'))
            opening=closing
    return out


def calculate():
    old=valuation(cases=CONFIG['prior_cases'],restricted=False,investments=False)
    new=valuation()
    old_result=evaluate(old); new_result=evaluate(new)
    base=new_result['details']['base']; p=CONFIG['cases']['base']
    terminal_common=base['segments'][0]['terminal_pv']*(1-D(str(p['nci'])))
    losses=[terminal_common*(1-(1+D(str(p['wacc'])))**(-t)) for t in CONFIG['p1_timing_delay_years']]
    discounts=[v/base['equity_value'] for v in losses]
    p1=quote_round(new_result['values']['base']*(1-discounts[1]),'CNY')
    return dict(old=old_result,new=new_result,
                new_v50={k:quote_round(v,'CNY') for k,v in new_result['values'].items()},
                discount_range=discounts,terminal_delay_loss=losses,p1=p1,
                valuation=new,capital_rows=capital_rows(new))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=calculate()
    encoded=json.dumps(result,ensure_ascii=False,indent=2,default=str)
    if args.output:
        target=args.output.resolve()
        if not target.is_relative_to(ROOT/'output'):
            parser.error('--output must be under workspace output/; original inputs are read-only')
        target.write_text(encoded+'\n')
        print(json.dumps({k:result[k] for k in ('new_v50','discount_range','p1')},default=str))
    else:
        print(encoded)
