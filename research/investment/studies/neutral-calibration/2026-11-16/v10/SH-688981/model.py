"""Frozen SMIC reassessment; standard library only, read-only by default.

Run: python3 model.py --check
     python3 model.py --json > output/neutral-review/recomputed-model.json
Reads only the adjacent model.json. Never writes or updates source files.
Amounts: CNY 100 million; prices: CNY/share. Decimal arithmetic, 50 digits.
"""
import argparse
from copy import deepcopy
from decimal import Decimal as D, getcontext
import json
from pathlib import Path

getcontext().prec = 50


def dec(x):
    return x if isinstance(x, D) else D(str(x))


def convert(x):
    if isinstance(x, dict):
        return {k: convert(v) for k, v in x.items()}
    if isinstance(x, list):
        return [convert(v) for v in x]
    if isinstance(x, float):
        return dec(x)
    return x


def evaluate(scenario, shares):
    details = []
    for seg in scenario['segments']:
        w = dec(seg['discount_rate'])
        flows = []
        for row in seg['years']:
            nopat = dec(row['revenue']) * dec(row['ebit_margin']) - dec(row['cash_tax'])
            fcff = nopat + dec(row['da']) - dec(row['capex']) - dec(row['delta_nwc'])
            pv = fcff / (1 + w) ** row['year']
            flows.append(dict(year=row['year'], nopat=nopat, fcff=fcff, present_value=pv))
        term = seg['terminal']
        g = dec(term['growth'])
        nopat = dec(seg['years'][-1]['revenue']) * (1 + g) * dec(term['margin']) * (1 - dec(term['tax_rate']))
        reinvestment = dec(term['invested_capital']) * g
        fcff = nopat - reinvestment
        assert w > g and fcff > 0
        tv = fcff / (w - g)
        tpv = tv / (1 + w) ** len(flows)
        epv = sum(r['present_value'] for r in flows)
        details.append(dict(id=seg['id'], years=flows, explicit_pv=epv, terminal_pv=tpv,
                            terminal_nopat=nopat, terminal_reinvestment=reinvestment,
                            terminal_fcff=fcff, terminal_value=tv,
                            terminal_roic=nopat / dec(term['invested_capital']),
                            enterprise_value=epv + tpv))
    ev = sum(s['enterprise_value'] for s in details)
    adj = sum(dec(a['amount']) for a in scenario['equity_adjustments'])
    return dict(segments=details, explicit_pv=sum(s['explicit_pv'] for s in details),
                terminal_pv=sum(s['terminal_pv'] for s in details), enterprise_value=ev,
                equity_adjustments=adj, equity_value=ev + adj,
                per_share=(ev + adj) * D(100000000) / dec(shares))


def build(data, params, correct_nwc=True):
    p = convert(deepcopy(params))
    c = convert(data['constants'])
    years = p.get('years', 7)
    revenue = dec(p['r'])
    kprev = dec(c['opening_fixed_capital'])
    nprev = dec(p.get('opening_nwc', c['opening_nwc']))
    activeprev = dec(c['opening_active_capital'])
    jprev = p['j'][0]
    groups = [[], []]
    raw = []
    for i in range(years):
        if i:
            revenue *= 1 + (p['g'][i-1] if i-1 < len(p['g']) else D('.02'))
        j = p['j'][min(i, len(p['j'])-1)]
        km = p['km']
        own = p['own']
        k = max(p['ramp'][i], p['k'] * revenue) if i < 3 else p['k'] * revenue
        cip = max(k * D('.12'), [D(500), D(420), D(350), D(0)][min(i, 3)])
        active = k - cip
        da = (activeprev + active) / 2 * (D('.9') / dec(p.get('machine_remaining_life', 4.5)) + D('.1') / D('12.5')) + 2
        capex = da + k - kprev
        nwc = p['n'] * revenue
        tax = dec(p.get('cash_tax_rate', D('.125') if i < 3 else D('.15')))
        margins = [p['whole'][min(i, len(p['whole'])-1)], p['joint'][min(i, len(p['joint'])-1)]]
        group_rows = []
        for z, weight, rs, prev_rs, ks in [(0, D(1), 1-j, 1-jprev, 1-km), (1, own, j, jprev, km)]:
            dn = (nwc * rs - nprev * prev_rs if correct_nwc else (nwc - nprev) * rs) * weight
            row = dict(year=i+1, revenue=revenue*rs*weight, ebit_margin=margins[z],
                       cash_tax=revenue*rs*weight*margins[z]*tax, da=da*ks*weight,
                       capex=capex*ks*weight, delta_nwc=dn)
            groups[z].append(row)
            group_rows.append(dict(id=['WHOLLY', 'JV_ATTRIBUTABLE'][z],
                                   opening_fixed=kprev*ks*weight, capex=capex*ks*weight,
                                   da=da*ks*weight, other=D(0), closing_fixed=k*ks*weight,
                                   opening_nwc=nprev*prev_rs*weight,
                                   closing_nwc=nwc*rs*weight, delta_nwc=dn))
        raw.append(dict(year=i+1, revenue=revenue, joint_revenue_share=j,
                        whole_margin=margins[0], joint_margin=margins[1],
                        opening_fixed=kprev, capex=capex, da=da, other=D(0), fixed_capital=k,
                        construction=cip, active_capital=active, opening_nwc=nprev, nwc=nwc,
                        delta_nwc=nwc-nprev, core_ebit=revenue*((1-j)*margins[0]+j*margins[1]),
                        cash_tax=revenue*((1-j)*margins[0]+j*margins[1])*tax,
                        group_balances=group_rows))
        kprev, nprev, activeprev, jprev = k, nwc, active, j
    segments = []
    for z, ident, weight, rs, ks in [(0, 'WHOLLY', D(1), 1-j, 1-km), (1, 'JV_ATTRIBUTABLE', own, j, km)]:
        segments.append(dict(id=ident,
            source='input/evidence/sources/S1-2026Q3-CAS.pdf PDF12; S2-2026Q3-IFRS.pdf PDF2/5/6; S3-2026H1-CAS.pdf PDF85/112–114/143–146; report §5',
            assumptions='研究经济归属组，非公司报告分部；收入/利润率/资本强度/母份额为有界假设；保留SBC等价报酬成本，排除投资收益及未来未证明补贴；营运资本由各组相邻余额差计算。',
            discount_rate=p['w'], years=groups[z],
            terminal=dict(growth=dec(p.get('terminal_growth', '.02')),
                          margin=groups[z][-1]['ebit_margin'],
                          tax_rate=dec(p.get('cash_tax_rate', '.15')),
                          invested_capital=(kprev*ks+nprev*rs)*weight)))
    fx = D(88098312) / D(13068833)
    cash, debt = D(13406216)/100000*fx, D(14904184)/100000*fx
    investment, deriv = D(34679469)/100000, D(83044)/100000
    entries = [
        ('CASH', cash*p['cashp'], '库存资金按普通股代理；经营中不含该利息收入', 'S2 PDF8; S3 PDF143–146'),
        ('DEBT', -debt*p['debtp'], '借款租赁与现金成对归属，非直接归母全部承担', 'S2 PDF8'),
        ('INVESTMENTS', investment*p['ip']*p['iv'], '已剔投资收益后的非经营资产；持股和价值为代理', 'S1 PDF11–12; S3 PDF143–146'),
        ('OPERATING_CASH', -p['reserve']*p['cashp'], '必要营运现金，不作为工程预留重扣', 'S2 PDF6/8'),
        ('OPENING_EQUIPMENT_PAYABLE', -p['payable']*p['debtp'], '期初已形成资产的设备应付只清偿一次；新增CapEx按资产增加代理', 'S5 PDF68'),
        ('DERIVATIVE_NET', deriv*p['cashp'], '现有衍生净额，与融资匹配', 'S1 PDF11–12'),
        ('BALANCE_LAG', p['lag'], '余额时点条件项；基准0不表示已核9/30后无变动', 'S1 2026-09-30'),
        ('EXERCISE_PROCEEDS', dec(p.get('exercise_proceeds', '1.45')), '现存权益工具全稀释代理的条件行权款，非已收现金', 'S5 PDF68–69; S6/S7')]
    adj = [dict(id=i, amount=a, reason=r, source='input/evidence/sources/'+s) for i,a,r,s in entries]
    scenario = dict(segments=segments, equity_adjustments=adj, equity_value=0)
    result = evaluate(scenario, c['shares'])
    scenario['equity_value'] = result['equity_value']
    return scenario, raw, result


def full_results(data):
    scenarios, rows, details = {}, {}, {}
    for name in ('low', 'base', 'high'):
        scenarios[name], rows[name], details[name] = build(data, data['parameters'][name])
    legacy = {n: evaluate(convert(s), data['constants']['shares']) for n,s in data['legacy_valuation']['scenarios'].items()}
    reconstructed_legacy = {n: build(data, data['parameters'][n], False)[2] for n in ('low','base','high')}
    valuation = dict(kind='dcf_fcff', currency='CNY', amount_unit='100_million',
                     shares=data['constants']['shares'], fx_to_quote=1, year_end_offset=0, scenarios=scenarios)
    base = details['base']['per_share']
    specs = [
        ('investment', '固定资本/收入 2.20→1.95', {'k':1.95}),
        ('investment', '固定资本/收入 2.20→2.50', {'k':2.5}),
        ('investment', '机器混合剩余寿命 4.5→5.5年，EBIT和净资产路径固定', {'machine_remaining_life':5.5}),
        ('cash_recovery', '首年收入950→900，后续增速不变，资本与NWC联动', {'r':900}),
        ('cash_recovery', '首年收入950→1000，后续增速不变，资本与NWC联动', {'r':1000}),
        ('cash_recovery', '两组全期及终值EBIT率各减2个百分点', {'whole':[.18]*7,'joint':[.10,.11,.125,.14,.15,.152,.152]}),
        ('cash_recovery', '两组全期及终值EBIT率各加2个百分点', {'whole':[.22]*7,'joint':[.14,.15,.165,.18,.19,.192,.192]}),
        ('cash_recovery', 'NWC/收入30%→27%', {'n':.27}),
        ('cash_recovery', 'NWC/收入30%→33%', {'n':.33}),
        ('cash_recovery', '期初NWC250→225亿元', {'opening_nwc':225}),
        ('cash_recovery', '期初NWC250→302亿元', {'opening_nwc':302}),
        ('cash_recovery', '纯现金税5%，固定产出及生产性资本', {'cash_tax_rate':.05}),
        ('cash_recovery', '纯现金税25%，固定产出及生产性资本', {'cash_tax_rate':.25}),
        ('terminal', '稳态增长2%→1%，同步改变首年终值利润及再投资', {'terminal_growth':.01}),
        ('terminal', '稳态增长2%→3%，同步改变首年终值利润及再投资', {'terminal_growth':.03}),
        ('terminal', '第5期末进入2%稳态，截短原过渡路径', {'years':5}),
        ('terminal', '原7期后再显式列两年2%稳态，等价展开', {'years':9}),
        ('capital_cost', 'WACC9%→8%', {'w':.08}),
        ('capital_cost', 'WACC9%→10%', {'w':.10}),
        ('capital_cost', '人民币债务1.79%替换旧混合2.4583%，保持原隐含Ke及25%债重', {'w':.09-.25*(float(D('91597')*4/D('14904184'))-.0179)*.85}),
        ('capital_scope', '非全资组母份额48.5%→40.90%', {'own':.409}),
        ('capital_scope', '非全资组母份额48.5%→66.45%', {'own':.6645}),
        ('capital_scope', '设备应付140→170亿元', {'payable':170}),
        ('capital_scope', '现金60%、债务75%、投资40.9%分别归属', {'cashp':.60,'debtp':.75,'ip':.409}),
        ('capital_scope', '现金75%、债务60%、投资100%分别归属', {'cashp':.75,'debtp':.60,'ip':1}),
        ('joint_case', '仅资本效率1.95及WACC8%的诊断组合', {'k':1.95,'w':.08}),
        ('joint_case', '仅资本效率2.50及WACC10%的诊断组合', {'k':2.5,'w':.10})]
    sensitivities = []
    for topic,label,changes in specs:
        p=deepcopy(data['parameters']['base']); p.update(changes)
        s, _, r = build(data,p)
        sensitivities.append(dict(topic=topic,change=label,changes=changes,base_v50=base,
                                  alternative_v50=r['per_share'],delta=r['per_share']-base,
                                  model=s))
    pressure, pressure_rows, pressure_result = build(data,data['parameters']['v5'])
    reverse = []
    for name in ('low','base','high'):
        for sid in ('WHOLLY','JV_ATTRIBUTABLE'):
            prices=[]
            for margin in (D('.1'),D('.35')):
                s=deepcopy(scenarios[name]);next(g for g in s['segments'] if g['id']==sid)['terminal']['margin']=margin
                prices.append(evaluate(s,data['constants']['shares'])['per_share'])
            reverse.append(dict(scenario=name,segment_id=sid,lower=D('.1'),upper=D('.35'),prices=prices,
                                target=D('110.50'),has_solution=prices[0]<=D('110.50')<=prices[1]))
    return dict(valuation=valuation, rows=rows, details=details, legacy=legacy,
                reconstructed_legacy=reconstructed_legacy, sensitivities=sensitivities,
                v5=dict(model=pressure,rows=pressure_rows,result=pressure_result), reverse=reverse)


def encode(x):
    if isinstance(x,D):
        return float(x)
    raise TypeError(type(x))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    data=json.loads(Path(__file__).with_name('model.json').read_text())
    results=full_results(data)
    for n in ('low','base','high'):
        old=results['legacy'][n]['per_share'];again=results['reconstructed_legacy'][n]['per_share']
        assert abs(old-again)<D('1e-10'), ('legacy reproduction mismatch',n)
        assert abs(results['details'][n]['per_share']-dec(data['expected_values'][n]))<D('1e-10')
        for row in results['rows'][n]:
            assert abs(row['opening_fixed']+row['capex']-row['da']+row['other']-row['fixed_capital'])<D('1e-35')
            for group in row['group_balances']:
                assert abs(group['closing_nwc']-group['opening_nwc']-group['delta_nwc'])<D('1e-35')
    if args.json:
        print(json.dumps(results,ensure_ascii=False,indent=2,default=encode))
    else:
        print(json.dumps({'checked':True,'old_values':{n:results['legacy'][n]['per_share'] for n in ('low','base','high')},
                          'new_values':{n:results['details'][n]['per_share'] for n in ('low','base','high')},
                          'v5_diagnostic_raw_per_share':results['v5']['result']['per_share']},default=encode))


if __name__=='__main__':
    main()
