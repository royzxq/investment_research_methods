#!/usr/bin/env python3
"""Frozen SMIC reassessment. Read model.json; print results; never write inputs.

Run: python3 -B model.py --check
Amounts: CNY 100 million; seven equal forward years; year-end offset 0.
The research segmentation is economic attribution, not reported segments.
"""
import argparse
import copy
import json
from decimal import Decimal as D, localcontext
from pathlib import Path


def dec(x):
    return x if isinstance(x, D) else D(str(x))


def evaluate(row, shares):
    details = []
    with localcontext() as ctx:
        ctx.prec = 50
        for seg in row['segments']:
            w = dec(seg['discount_rate'])
            flows = []
            for x in seg['years']:
                ebit = dec(x['revenue']) * dec(x['ebit_margin'])
                nopat = ebit - dec(x['cash_tax'])
                fcff = nopat + dec(x['da']) - dec(x['capex']) - dec(x['delta_nwc'])
                flows.append({'year': x['year'], 'ebit': ebit, 'nopat': nopat,
                              'fcff': fcff, 'pv': fcff / (1 + w) ** x['year']})
            t = seg['terminal']; g = dec(t['growth']); ic = dec(t['invested_capital'])
            nopat = dec(seg['years'][-1]['revenue']) * (1 + g) * dec(t['margin']) * (1 - dec(t['tax_rate']))
            reinvest = ic * g
            terminal_fcff = nopat - reinvest
            assert w > g and terminal_fcff > 0
            tv = terminal_fcff / (w - g)
            terminal_pv = tv / (1 + w) ** len(flows)
            explicit = sum(x['pv'] for x in flows)
            details.append(dict(id=seg['id'], flows=flows, explicit_pv=explicit,
                                terminal_nopat=nopat, terminal_reinvestment=reinvest,
                                terminal_fcff=terminal_fcff, terminal_roic=nopat/ic,
                                terminal_value=tv, terminal_pv=terminal_pv))
        ev = sum(x['explicit_pv'] + x['terminal_pv'] for x in details)
        adjustments = sum(dec(x['amount']) for x in row['equity_adjustments'])
        equity = ev + adjustments
        return dict(segments=details, enterprise_value=ev, equity_adjustments=adjustments,
                    equity_value=equity, per_share=equity * D(100000000) / dec(shares))


def scenario(p, constants, *, correct_nwc=True):
    c = {k: dec(v) for k, v in constants.items()}
    p = copy.deepcopy(p)
    for k, v in p.items():
        p[k] = [dec(z) for z in v] if isinstance(v, list) else dec(v)
    r = p['r']; previous_k = c['opening_fixed_capital']; previous_n = c['opening_nwc']
    active_previous = c['opening_active_capital']
    # The original first-year allocation implicitly assumes the first-year mix
    # also for opening NWC. Preserve that convention; correct years 2 onward.
    previous_j = p['j'][0]
    groups = [[], []]; raw = []
    for i in range(7):
        if i:
            r *= 1 + p['g'][i - 1]
        k = max(p['ramp'][i], p['k'] * r) if i < 3 else p['k'] * r
        cip = max(k * D('.12'), [D(500), D(420), D(350), D(0), D(0), D(0), D(0)][i])
        active = k - cip
        da = (active_previous + active) / 2 * (D('.9')/D('4.5') + D('.1')/D('12.5')) + 2
        capex = da + k - previous_k
        nwc = p['n'] * r; delta_n = nwc - previous_n; j = p['j'][i]
        tax = D('.125') if i < 3 else D('.15')
        for z, own, share, capital_share, margin in (
                (0, D(1), 1-j, 1-p['km'], p['whole'][i]),
                (1, p['own'], j, p['km'], p['joint'][i])):
            old_share = previous_j if z else 1 - previous_j
            dn = (nwc * share - previous_n * old_share) * own if correct_nwc else delta_n * share * own
            groups[z].append(dict(year=i+1, revenue=r*share*own, ebit_margin=margin,
                                 cash_tax=r*share*margin*tax*own, da=da*capital_share*own,
                                 capex=capex*capital_share*own, delta_nwc=dn))
        raw.append(dict(year=i+1, revenue=r, joint_revenue_share=j, fixed_capital=k,
                        construction=cip, nwc=nwc, da=da, maintenance_capex=da,
                        growth_capex=k-previous_k, capex=capex, delta_nwc=delta_n,
                        core_ebit=r*((1-j)*p['whole'][i]+j*p['joint'][i]),
                        wholly_nwc=nwc*(1-j), joint_nwc_before_attribution=nwc*j))
        previous_k=k; previous_n=nwc; previous_j=j; active_previous=active
    segments=[]
    for z, ident, own, share, capital_share, margin in (
            (0, 'WHOLLY', D(1), 1-p['j'][-1], 1-p['km'], p['whole'][-1]),
            (1, 'JV_ATTRIBUTABLE', p['own'], p['j'][-1], p['km'], p['joint'][-1])):
        segments.append(dict(id=ident,
            source='input/evidence/sources/S3-2026H1-CAS.pdf PDF143–146；S1-2026Q3-CAS.pdf PDF12；S2-2026Q3-IFRS.pdf PDF2/5/6；本报告§5',
            assumptions='研究经济归属组，非披露分部。收入/资本/归属沿用经复核的有界假设；各组ΔNWC为期末存量减期初存量；SBC保留成本；经营补贴不外推。',
            discount_rate=p['w'], years=groups[z], terminal=dict(growth=D('.02'), margin=margin,
            tax_rate=D('.15'), invested_capital=(previous_k*capital_share+previous_n*share)*own)))
    fx = c['cas_nci_thousand'] / c['ifrs_nci_thousand']
    cash = c['funds_usd_thousand']/D(100000)*fx
    debt = c['debt_usd_thousand']/D(100000)*fx
    investment = (c['associates_cny_thousand']+c['noncurrent_financial_cny_thousand'])/D(100000)
    derivatives = (c['derivative_asset_cny_thousand']-c['derivative_liability_cny_thousand'])/D(100000)
    adjustments=[]
    rows=[
        ('CASH', cash*p['cashp'], '库存资金独立归属代理；不计经营利息收益', 'S2 PDF8；S3 PDF143–146'),
        ('DEBT', -debt*p['debtp'], '含租赁有息债务；与现金归属分别测试', 'S2 PDF8'),
        ('INVESTMENTS', investment*p['ip']*p['iv'], '非经营投资独立计价，其收益从经营利润剔除', 'S1 PDF11–12'),
        ('OPERATING_CASH', -p['reserve']*p['cashp'], '必要现金不在NWC内，不再扣同笔工程预留', 'S2 PDF6；报告§5现金成本尺度'),
        ('OPENING_EQUIPMENT_PAYABLE', -p['payable']*p['debtp'], '已入期初固定资产的设备应付仅在此支付一次', 'S5 PDF68'),
        ('DERIVATIVE_NET', derivatives*p['cashp'], '未计经营流的期初衍生净资产', 'S1 PDF11–12'),
        ('BALANCE_LAG', p['lag'], '保留9/30余额至估值日过渡条件，不造期后事实', 'S1余额日；报告§5'),
        ('EXERCISE_PROCEEDS', c['exercise_proceeds'], '现存工具全稀释分母对应条件行权款，非现有现金', 'S5 PDF68–69；S6；S7')]
    for ident, amount, reason, source in rows:
        adjustments.append(dict(id=ident, amount=amount, reason=reason, source='input/evidence/sources/ '+source))
    row=dict(segments=segments, equity_adjustments=adjustments, equity_value=0)
    detail=evaluate(row, c['shares']);row['equity_value']=detail['equity_value']
    return row, raw, detail


def build(inputs, *, correct_nwc=True):
    model=dict(kind='dcf_fcff',currency='CNY',amount_unit='100_million',shares=int(inputs['constants']['shares']),
               fx_to_quote=1,year_end_offset=0,scenarios={})
    raw={}; details={}
    for name in ('low','base','high'):
        model['scenarios'][name],raw[name],details[name]=scenario(inputs['params'][name],inputs['constants'],correct_nwc=correct_nwc)
    return model,raw,details


def number(x):
    return float(x) if isinstance(x,D) else x


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--compare', action='store_true', help='also reproduce the old NWC allocation and value bridge')
    args=parser.parse_args()
    path=Path(__file__).with_name('model.json')
    saved=json.loads(path.read_text(),parse_float=D)
    model,raw,details=build(saved['inputs'])
    if args.check:
        for name in ('low','base','high'):
            actual=evaluate(saved['valuation']['scenarios'][name],saved['valuation']['shares'])
            assert abs(actual['per_share']-details[name]['per_share'])<D('0.000000001'),name
            assert abs(details[name]['equity_value']-dec(saved['valuation']['scenarios'][name]['equity_value']))<D('0.00000001'),name
        print('PASS: independently rebuilt three paths equal saved valuation; no files written.')
    result=details if args.full else {k:v['per_share'] for k,v in details.items()}
    if args.compare:
        _,_,old=build(saved['inputs'],correct_nwc=False)
        result={'new':result, 'old':{k:v['per_share'] for k,v in old.items()},
                'correction_delta':{k:details[k]['per_share']-old[k]['per_share'] for k in details}}
    print(json.dumps(result,ensure_ascii=False,indent=2,default=number))


if __name__=='__main__':
    main()
