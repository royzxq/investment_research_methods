"""Independent declared-DCF arithmetic and exact, ordered PV attribution.
No hypothesis selection, trading or price calibration.
"""
from decimal import Decimal, localcontext
from copy import deepcopy
D=lambda x:Decimal(str(x))
KEYS=('operating_profit','cash_tax','net_investment','working_capital','terminal','equity_bridge')

def components(model, scenario='base', rate=None):
 with localcontext() as ctx:
  ctx.prec=45
  sc=model['scenarios'][scenario];out={k:Decimal(0) for k in KEYS};schedule=[];term=[]
  offset=D(model.get('year_end_offset',0));den=D(model['shares'])/D(100000000)/D(model['fx_to_quote'])
  for s in sc['segments']:
   r=D(s['discount_rate']) if rate is None else D(rate)
   for row in s['years']:
    t=D(row['year'])+offset;disc=(1+r)**t;rev=D(row['revenue']);ebit=rev*D(row['ebit_margin'])
    tax=D(row['cash_tax']);net=D(row['capex'])-D(row['da']);wc=D(row['delta_nwc'])
    for k,v in [('operating_profit',ebit),('cash_tax',-tax),('net_investment',-net),('working_capital',-wc)]:out[k]+=v/disc/den
    schedule.append(dict(segment=s['id'],time=t,revenue=rev,ebit=ebit,cash_tax=tax,capex=D(row['capex']),da=D(row['da']),delta_nwc=wc,fcff=ebit-tax-net-wc))
   x=s['terminal'];g=D(x['growth']);rev=D(s['years'][-1]['revenue']);nopat=rev*(1+g)*D(x['margin'])*(1-D(x['tax_rate']));ic=D(x['invested_capital']);cf=nopat-ic*g;t=D(s['years'][-1]['year'])+offset
   pv=cf/(r-g)/(1+r)**t/den;out['terminal']+=pv
   term.append(dict(segment=s['id'],discount_rate=r,growth=g,terminal_margin=D(x['margin']),terminal_tax_rate=D(x['tax_rate']),terminal_ic=ic,terminal_nopat=nopat,terminal_fcff=cf,time=t,pv_per_share=pv))
  out['equity_bridge']=sum((D(v['amount']) for v in sc['equity_adjustments']),Decimal(0))/den
  return dict(price=sum(out.values()),components=out,schedule=schedule,terminal=term,denominator=den)


def bridge(old,new):
 a=components(old);b=components(new);rates={D(s['discount_rate']) for s in old['scenarios']['base']['segments']}
 if len(rates)==1:
  rate=next(iter(rates));fixed=components(new,rate=rate)
  changes={k:fixed['components'][k]-a['components'][k] for k in KEYS}
  changes['capital_cost']=b['price']-fixed['price']
  convention='First replace all operating/terminal/ownership components at the old uniform capital cost; capital-cost replacement is last. Interactions are allocated by this declared order, not independent additive sensitivities.'
 else:
  changes={k:b['components'][k]-a['components'][k] for k in KEYS}
  convention='Segment capital costs differ; each PV component includes its own rate effect. No separate WACC attribution claimed.'
 assert abs(sum(changes.values())-(b['price']-a['price']))<D('1e-25')
 return dict(old_price=a['price'],new_price=b['price'],delta=b['price']-a['price'],changes=changes,convention=convention,scope_note='Amounts follow each model economic ownership scope; group and parent figures are not automatically equivalent. Terminal includes horizon, growth, margin, cash tax and IC effects. Single-run differences are not framework-only causal estimates.')

if __name__ == '__main__':
    import json
    from pathlib import Path
    m=json.loads(Path(__file__).with_name('reviewed-model.json').read_text())
    values={k:components(m,k) for k in ('low','base','high')}
    print(json.dumps({'reviewed_v50':{k:round(float(v['price']),2) for k,v in values.items()}, 'reviewed_p1':round(float(values['base']['price']*D('.8')*D('.95')),2), 'details':values},ensure_ascii=False,indent=2,default=float))
