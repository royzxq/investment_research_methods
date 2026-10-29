"""Audit real tool delivery, evidence coverage, reported usage and conditional prices."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
PARENT = BASE.parent
ROOT = BASE.parents[3]

def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalize(text):return ''.join(text.split())

gold_path=PARENT/'gold/gold.json'
gold=read(gold_path)
old=read(PARENT/'probes/comparison.json')
result={'schema':'codex-consumer-cost-audit/v1','date':'2026-10-10','timezone':'Asia/Shanghai',
        'gold_sha256':sha(gold_path),'pricing':{
            'codex_auth':'ChatGPT','actual_task_charge_usd':None,'actual_credit_debit':None,
            'actual_billing_unavailable_reason':'CLI reports tokens, not per-task subscription allowance, credit debit, or invoice',
            'configured_model':'gpt-6.1-sol','provider_reported_model':None,'configured_service_tier':'priority',
            'conditional_codex_rates_per_million':{
                'standard_credits':{'uncached_input':50,'cached_input':2.5,'output':250},
                'fast_credits':{'uncached_input':100,'cached_input':5,'output':500},
                'standard_api_usd_short_context':{'uncached_input':2,'cached_input':0.1,'cache_write_input':2.5,'output':10},
                'fast_api_usd_short_context':{'uncached_input':4,'cached_input':0.2,'cache_write_input':5,'output':20}},
            'jev_usd_per_million_input':0.042,'jev_output_price':0,
            'jev_failed_request_billing':None,'jev_invoice_charge_usd':None,
            'sources':['https://learn.chatgpt.com/docs/pricing','https://developers.openai.com/api/docs/pricing','https://docs.typesafe.ai/models'],
            'verified_at':'2026-10-10','cash_costs_are_conditional_estimates_not_invoices':True},'runs':{}}

def price(u,rates):
    if any(u.get(k) is None for k in ['input_tokens','cached_input_tokens','output_tokens']):return None
    uncached=u['input_tokens']-u['cached_input_tokens']
    # API reported cache writes, if present, are a subset of input. Credits have
    # no separate write fee. Missing write information cannot imply zero API cost.
    if 'cache_write_input' in rates:
        if u.get('cache_write_input_tokens') is None:return None
        writes=u['cache_write_input_tokens'];uncached-=writes
    else:writes=0
    if uncached<0:raise ValueError('inconsistent usage counters')
    return (uncached*rates['uncached_input']+u['cached_input_tokens']*rates['cached_input']+
            writes*rates.get('cache_write_input',0)+u['output_tokens']*rates['output'])/1e6

for kind in ['announcements','passages']:
    corpus=read(BASE/(kind+'-corpus.json'))
    source_text={}
    expected_outputs=[]
    for part in range(3):
        run=subprocess.run([sys.executable,str(BASE/'read_originals.py'),kind,str(part)],capture_output=True,text=True,check=True)
        expected_outputs.append(run.stdout)
        for line in run.stdout.splitlines():
            obj=json.loads(line)
            if 'id' in obj:source_text[obj['id']]=obj['text']
    if kind=='announcements':
        m=read(PARENT/'manifests/announcements.json')
        for i in m['items']:source_text[i['id']]=json.loads(i['text'])
        expected={t['id']:{a['item_id'] for a in gold['announcement_labels'] if t['id'] in a['must_route_topics']}
                  for t in m['topics']}
    else:expected={k:set(v) for k,v in gold['required_page_item_ids_by_topic'].items()}
    for arm in ['direct','jev','direct-recovery','jev-recovery']:
        name=kind+'-'+arm;folder=BASE/name
        process=read(folder/'process.json');usage=read(folder/'usage.json')
        answer=read(folder/'answer.json');handoff=read(folder/'handoff.json')
        events=[json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines() if line.strip()]
        completed=[e['item'] for e in events if e.get('type')=='item.completed']
        commands=[i for i in completed if i['type']=='command_execution']
        outputs=[i['aggregated_output'] for i in commands]
        log_delivery=(len(outputs)==3 and outputs==expected_outputs and all(i['exit_code']==0 for i in commands))
        recovery=arm.endswith('-recovery')
        if recovery:
            prompt=(folder/'prompt.txt').read_text()
            delivery=all(text in prompt for text in expected_outputs) and len(commands)==0
        else:
            # A complete aggregated_output does not prove complete model display.
            # Both live arms explicitly reported tool-output truncation.
            delivery=False
        other_tools=[i['type'] for i in completed if i['type'] not in ['command_execution','agent_message','reasoning']]
        seen={x['topic']:set(x['ids']) for x in answer['topic_evidence']}
        topic_coverage={t:{'expected':len(ids),'found':len(ids&seen.get(t,set())),
                           'missing':sorted(ids-seen.get(t,set()))} for t,ids in expected.items()}
        bad_ids=sorted({id_ for values in seen.values() for id_ in values if id_ not in source_text})
        quotes=[]
        for n, f in enumerate(answer['findings']):
            for q in f['quotes']:
                quotes.append({'finding':n,'id':q['id'],'exact':q['quote'] in source_text.get(q['id'],''),
                    'whitespace_normalized_match':normalize(q['quote']) in normalize(source_text.get(q['id'],''))})
        errors={e['id'] for e in handoff['errors']}
        handled={f['id'] for f in answer['fallback_review']}
        u=usage['summary']['usage']
        result['runs'][name]={
            'status':process['status'],'seconds':process['execution_duration_seconds'],
            'usage':u,'input_plus_output_tokens':u['input_tokens']+u['output_tokens'],
            'uncached_input_tokens':u['input_tokens']-u['cached_input_tokens'],
            'models_reported':usage['models'],
            'prices_conditional':{k:price(u,v) for k,v in result['pricing']['conditional_codex_rates_per_million'].items()},
            'actual_task_cash_usd':None,'actual_task_credits':None,
            'source_delivery':{'commands':len(commands),'complete_exact_delivery':delivery,
                               'raw_command_log_complete':log_delivery,
                               'delivery_method':'exact_full_text_in_input' if recovery else 'tool_output_truncated_for_model',
                               'read_items':sum(map(len,corpus['parts'])),'other_tool_types':other_tools,
                               'part_sha256':[hashlib.sha256(s.encode()).hexdigest() for s in (expected_outputs if recovery else outputs)]},
            'handoff_characters':len(json.dumps(handoff,ensure_ascii=False,separators=(',',':'))),
            'prompt_characters':len((folder/'prompt.txt').read_text()),
            'service_errors':sorted(errors),'unhandled_service_errors':sorted(errors-handled),
            'topic_coverage':topic_coverage,'unexpected_topic_ids':bad_ids,'quotes':quotes,
            'evidence_packages_all_delivered':delivery if kind=='passages' else None,
            'files_sha256':{p:sha(folder/p) for p in ['prompt.txt','handoff.json','answer.json','events.jsonl','process.json','usage.json']}}
        if not delivery or other_tools or errors-handled or bad_ids:
            result['runs'][name]['audit_warning']='Inspect delivery, tools, IDs or failure handling before interpreting savings.'

result['comparison']={}
for kind in ['announcements','passages']:
    direct=result['runs'][kind+'-direct-recovery'];jev=result['runs'][kind+'-jev-recovery']
    first_direct=result['runs'][kind+'-direct'];first_jev=result['runs'][kind+'-jev']
    prior=old[kind]
    # Successful Jev usage is from the separately timed live semantic run. It is
    # charged here for a cold run, even though this audit replays its fixed labels.
    # Older Codex single-stage results are not a same-session end-to-end baseline.
    def add(a,b):return {key:a[key]+b[key] for key in a if a[key] is not None and b.get(key) is not None}
    all_direct=add(first_direct['usage'],direct['usage']);all_jev=add(first_jev['usage'],jev['usage'])
    result['comparison'][kind]={'direct':direct['input_plus_output_tokens'],'jev_consumer':jev['input_plus_output_tokens'],
        'consumer_net_saved_tokens':direct['input_plus_output_tokens']-jev['input_plus_output_tokens'],
        'consumer_net_saved_fraction':1-jev['input_plus_output_tokens']/direct['input_plus_output_tokens'],
        'recovered_path_including_failed_attempt':{
            'direct_usage':all_direct,'jev_consumer_usage':all_jev,
            'direct_seconds':first_direct['seconds']+direct['seconds'],
            'jev_consumer_seconds':first_jev['seconds']+jev['seconds'],
            'direct_conditional_prices':{k:price(all_direct,v) for k,v in result['pricing']['conditional_codex_rates_per_million'].items()},
            'jev_consumer_conditional_prices':{k:price(all_jev,v) for k,v in result['pricing']['conditional_codex_rates_per_million'].items()}},
        'jev_cold_call_extra_usd_estimate':prior['jev_usage']['input_tokens']*0.042/1e6,
        'jev_cold_call_extra_seconds':prior['jev_wall_seconds'],
        'prior_semantic_probe':prior,
        'interpretation':'The complete recovery consumers are real matched full-input measurements. Recovered totals include failed tool-display attempts. Adding earlier semantic-stage usage/latency is component accounting, not a same-session end-to-end measurement.'}

result['experiment_total_codex_reported_usage']={k:sum(r['usage'][k] for r in result['runs'].values())
                                               for k in ['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens']}
result['experiment_new_jev_calls']=0

with (BASE/'evaluation.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:{n:v for n,v in r.items() if n in ['seconds','usage','prices_conditional','source_delivery','service_errors','unhandled_service_errors','topic_coverage','audit_warning']}
                  for k,r in result['runs'].items()},ensure_ascii=False,indent=2))
