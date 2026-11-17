"""Read-only reproduction of the frozen valuation. Python standard library only.

Run: python3 path/to/model.py [--output output/neutral-review/model-results.json]
The default prints results. --output refuses overwrite and is restricted to this
workspace's output/. No writes to inputs, original calculations or this model.
"""
from pathlib import Path
from decimal import Decimal, localcontext, ROUND_HALF_UP
from copy import deepcopy
from math import erf, sqrt, exp, log
import json, argparse

D = lambda v: Decimal(str(v))
NAMES = ('low','base','high')

def scenario(model, name):
    row = model['scenarios'][name]
    with localcontext() as ctx:
        ctx.prec = 50
        segments = []
        for s in row['segments']:
            rate = D(s['discount_rate']); flows=[]
            for y in s['years']:
                nopat=D(y['revenue'])*D(y['ebit_margin'])-D(y['cash_tax'])
                fcff=nopat+D(y['da'])-D(y['capex'])-D(y['delta_nwc'])
                pv=fcff/(1+rate)**(D(y['year'])+D(model['year_end_offset']))
                flows.append(dict(year=y['year'],nopat=nopat,fcff=fcff,pv=pv))
            t=s['terminal'];g=D(t['growth']);ic=D(t['invested_capital'])
            assert rate>g>=0
            nopat=D(s['years'][-1]['revenue'])*(1+g)*D(t['margin'])*(1-D(t['tax_rate']))
            reinvestment=ic*g; tf= nopat-reinvestment
            assert tf>0
            tv=tf/(rate-g);tpv=tv/(1+rate)**(D(len(flows))+D(model['year_end_offset']))
            explicit=sum(y['pv'] for y in flows)
            segments.append(dict(id=s['id'],flows=flows,explicit_pv=explicit,terminal_nopat=nopat,terminal_reinvestment=reinvestment,terminal_roic=nopat/ic,terminal_pv=tpv,ev=explicit+tpv))
        ev=sum(s['ev'] for s in segments)
        adj=sum(D(a['amount']) for a in row['equity_adjustments'])
        eq=ev+adj
        return dict(segments=segments,ev=ev,bridge=adj,equity=eq,value=eq*D(100000000)/D(model['shares'])*D(model['fx_to_quote']))

def option_value(spot,k,vol,t,rf):
    cdf=lambda x:(1+erf(x/sqrt(2)))/2
    d1=(log(spot/k)+(rf+vol*vol/2)*t)/(vol*sqrt(t))
    return spot*cdf(d1)-k*exp(-rf*t)*cdf(d1-vol*sqrt(t))

def regenerate(p):
    """Independently rebuild annual rows, productive capital and equity bridges."""
    m=deepcopy(p['valuation']); b=p['bridge_parameters']
    for j,name in enumerate(NAMES):
        c=p['configuration'][name]; row=m['scenarios'][name]
        for k,seg in enumerate(row['segments']):
            rev=c['r1'][k];prev=c['r0'][k];stock=c['assets'][k];cohorts=[];ys=[]
            for i in range(7):
                if i:rev*=1+c['growth'][k][i-1]
                old_da=150*c['assets'][k]/800*[.95,.85,.72,.60,.48,.36,.24][i]
                cohort_da=sum(v*(.7/7+.2/25+(.1/5 if i-y<5 else 0)) for y,v in cohorts)
                capex=(old_da+cohort_da+c['k'][k]*(rev-prev))/(1-.064)
                da=old_da+cohort_da+.064*capex
                margin=c['m0'][k]+(c['mt'][k]-c['m0'][k])*i/6
                ys.append(dict(year=i+1,revenue=rev,ebit_margin=margin,cash_tax=rev*margin*c['tax'][k],da=da,capex=capex,delta_nwc=(c['nwc']+c['cash'])*(rev-prev)))
                stock+=capex-da;cohorts.append((i,capex));prev=rev
            seg['years']=ys;seg['discount_rate']=c['wacc']
            seg['terminal']=dict(growth=.02,margin=c['mt'][k],tax_rate=c['tax'][k],invested_capital=stock+rev*(c['nwc']+c['cash']))
        r0=sum(c['r0']); rest=[a-v for a,v in zip(c['r0'],b['q3_segment_allocation'])]
        eb=sum(m*r for m,r in zip(c['m0'],rest))
        tax=sum(max(m*r,0)*t for m,r,t in zip(c['m0'],rest,c['tax']))
        fcff=eb-tax+b['q4_da'][j]-b['q4_capex'][j]+b['q3_core_nwc']-c['nwc']*r0
        amounts=[b['financial_assets'][j],-b['financial_debt'][j],-r0*b['minimum_cash_ratio'][j],b['associates'][j],-b['nci'][j],-b['fixed_prior_claims'],b['redemption_net'][j],b['oct_option_cash'],fcff/2,fcff/2/(1+c['wacc'])**m['year_end_offset'],0]
        for a,v in zip(row['equity_adjustments'],amounts):a['amount']=v
        preopt=float(scenario(m,name)['equity']);per=preopt*1e8/m['shares']
        for _ in range(b['option_iterations']):
            op=sum(n*option_value(per,k,b['option_volatility'][j],b['option_term'],b['option_rf']) for n,k in b['options'])/1e8
            per=(preopt-op)*1e8/m['shares']
        row['equity_adjustments'][-1]['amount']=-op
        row['equity_value']=float(scenario(m,name)['equity'])
    return m

def rounded(v):return float(D(v).quantize(D('.01'),rounding=ROUND_HALF_UP))

def diagnostics(p):
    m=p['valuation'];base=scenario(m,'base')['value'];results={}
    def run(label, modify):
        q=deepcopy(m);modify(q['scenarios']['base'])
        r=scenario(q,'base');results[label]={'value':r['value'],'p1':r['value']*D('.76'),'delta':r['value']-base}
    def change(r,w=0,tm=0,tax=0,g=None,ic=1,em=0):
        for s in r['segments']:
            s['discount_rate']+=w;s['terminal']['margin']+=tm
            s['terminal']['tax_rate']+=tax;s['terminal']['invested_capital']*=ic
            if g is not None:s['terminal']['growth']=g
            for y in s['years']:
                old=y['revenue']*y['ebit_margin'];y['ebit_margin']+=em
                y['cash_tax']+=max(old,0)*tax
                if em:y['cash_tax']=max(y['revenue']*y['ebit_margin'],0)*s['terminal']['tax_rate']
    for lab,kw in [('WACC+1pp',dict(w=.01)),('WACC-1pp',dict(w=-.01)),('terminal-margin-0.5pp',dict(tm=-.005)),('cash-tax+5pp',dict(tax=.05)),('g=1%',dict(g=.01)),('g=3%',dict(g=.03)),('terminal-IC+20%',dict(ic=1.2)),('V5:margin-1pp,WACC+2pp',dict(w=.02,tm=-.01,em=-.01)),('joint:WACC+1pp,terminal-margin-0.5pp',dict(w=.01,tm=-.005))]:
        run(lab,lambda r,kw=kw:change(r,**kw))
    def earlier_steady_state(r):
        # Joint horizon test: omit 2032-2033 expansion, apply mature margins
        # to 2031 revenue and use the matching 2031 capital stock. Keep the
        # original valuation date, discount convention and equity bridge.
        for s in r['segments']:
            s['years']=s['years'][:5]
            capital=p['production_bridge']['base'][s['id']][4]
            s['terminal']['invested_capital']=sum(capital[k] for k in ('closing_production','nwc','operating_cash'))
    run('horizon:5-year-earlier-steady-state',earlier_steady_state)
    # These are isolated diagnostics; equity adjustments are intentionally fixed.
    joint=results['joint:WACC+1pp,terminal-margin-0.5pp']['delta']
    interaction=joint-results['WACC+1pp']['delta']-results['terminal-margin-0.5pp']['delta']
    boundaries={}
    for n in NAMES:
        prices=[]
        for tm in [.085,.125]:
            q=deepcopy(m)
            q['scenarios'][n]['segments'][2]['terminal']['margin']=tm
            prices.append(scenario(q,n)['value'])
        implied=D('.085')+(D('50.02')-prices[0])/(prices[1]-prices[0])*D('.04')
        q=deepcopy(m);q['scenarios'][n]['segments'][2]['terminal']['margin']=float(implied)
        back=scenario(q,n)['value']
        boundaries[n]=dict(lower=.085,upper=.125,prices=prices,implied_margin=implied,within_bounds=D('.085')<=implied<=D('.125'),modeled_price=back,residual=back-D('50.02'))
    return dict(isolated_sensitivity=results,interaction=interaction,reverse_by_scenario=boundaries,scope='Sensitivities fix initial equity adjustments, including options and Q4 cash; they are not full revised scenarios.')

def run(p):
    result={n:scenario(p['valuation'],n) for n in NAMES}
    rebuilt=regenerate(p);validation={}
    for n in NAMES:
        rebuilt_value=scenario(rebuilt,n)['value']
        err=rebuilt_value-result[n]['value']
        assert abs(err)<D('0.00000001'),(n,err)
        assert abs(result[n]['equity']-D(p['expected']['equity_values'][n]))<D('.000001')
        assert rounded(result[n]['value'])==p['expected']['values'][n]
        validation[n]={'rebuilt_value':rebuilt_value,'difference':err}
    p1=result['base']['value']*D('.76')
    assert rounded(p1)==p['expected']['p1']
    return dict(values={k:v['value'] for k,v in result.items()},p1=p1,details=result,regeneration=validation,diagnostics=diagnostics(p))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args()
    here=Path(__file__).resolve().parent
    payload=json.loads((here/'model.json').read_text())
    result=run(payload)
    txt=json.dumps(result,ensure_ascii=False,indent=2,default=lambda o:str(o) if isinstance(o,Decimal) else o)+'\n'
    if args.output:
        root=next(p for p in here.parents if (p/'input/run-manifest.json').is_file())
        out=Path(args.output).resolve()
        out.relative_to(root/'output')
        with out.open('x') as f:f.write(txt)
        print(json.dumps({'values':{k:rounded(v) for k,v in result['values'].items()},'p1':rounded(result['p1']),'reproduction':'passed'},ensure_ascii=False))
    else:print(txt,end='')
