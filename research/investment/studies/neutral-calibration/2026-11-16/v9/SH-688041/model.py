"""Read-only, standard-library reproduction of model.json. Run: python3 model.py.

No network, no repository imports, no output file writes. All amounts in CNY 100m;
all values per ordinary economic share. This is an arithmetic check, not a test of
the economic assumptions or original disclosures.
"""
from decimal import Decimal as D, localcontext, ROUND_HALF_UP
from pathlib import Path
import json

def evaluate(model):
    out={}
    with localcontext() as ctx:
        ctx.prec=50
        for label,case in model['scenarios'].items():
            explicit=tv=0; flows=[]
            for seg in case['segments']:
                r=seg['discount_rate']; t=seg['terminal']
                for y in seg['years']:
                    ebit=y['revenue']*y['ebit_margin']
                    nopat=ebit-y['cash_tax']
                    fcff=nopat+y['da']-y['capex']-y['delta_nwc']
                    years=D(y['year'])+model['year_end_offset']
                    pv=fcff/(1+r)**years
                    explicit+=pv
                    flows.append(dict(year=y['year'],exponent=years,ebit=ebit,nopat=nopat,fcff=fcff,pv=pv))
                terminal_nopat=seg['years'][-1]['revenue']*(1+t['growth'])*t['margin']*(1-t['tax_rate'])
                reinvestment=t['invested_capital']*t['growth']
                terminal_fcff=terminal_nopat-reinvestment
                tv+=terminal_fcff/(r-t['growth'])/(1+r)**(D(len(seg['years']))+model['year_end_offset'])
            ev=explicit+tv
            eq=ev+sum(a['amount'] for a in case['equity_adjustments'])
            assert abs(eq-case['equity_value']) < D('.00000001')
            value=eq*D('100000000')/D(model['shares'])*model['fx_to_quote']
            out[label]=dict(enterprise_value=ev,explicit_pv=explicit,terminal_pv=tv,equity_value=eq,
                terminal_nopat=terminal_nopat,terminal_reinvestment=reinvestment,terminal_fcff=terminal_fcff,
                v50_unrounded=value,v50=value.quantize(D('.01'),rounding=ROUND_HALF_UP),flows=flows)
    return out

def main():
    doc=json.loads(Path(__file__).with_name('model.json').read_text(),parse_float=D,parse_int=D)
    result=evaluate(doc['valuation'])
    with localcontext() as ctx:
        ctx.prec=50
        b=result['base']; p=doc['parameters']['base']
        common_terminal=b['terminal_pv']*(1-p['nci'])
        dr=[common_terminal/b['equity_value']*(1-(1+p['wacc'])**(-n)) for n in (1,2)]
        p1=(b['v50_unrounded']*(1-dr[1])).quantize(D('.01'),rounding=ROUND_HALF_UP)
        assert p1==doc['expected_p1']
        for k in result: assert result[k]['v50']==doc['expected_v50'][k]
        result['price_map_check']=dict(d_base_range=dr,p1=p1,t1='接近V50上沿时复核',mode='frozen')
    print(json.dumps(result,ensure_ascii=False,indent=2,default=str))

if __name__=='__main__': main()
