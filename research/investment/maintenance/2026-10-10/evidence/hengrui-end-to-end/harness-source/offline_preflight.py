"""Exercise fixture mechanics without touching a real consumer's ledger."""
from pathlib import Path
import json
import shutil
import subprocess
from prepare import workspace, PYTHON, BASE

results=[]
for mode in ['repeated','union']:
    cwd=workspace(mode,'-offline')
    def call(*args):
        r=subprocess.run([PYTHON,'bench_tool.py',*args],cwd=cwd,text=True,capture_output=True)
        if not r.stdout:raise AssertionError(r.stderr)
        return r.returncode,json.loads(r.stdout)
    try:
        code,located=call('locate');assert code==0,(code,located)
        code,fault=call('read');assert code==75 and fault['fault_injected']
        ack=None;packets=[]
        while True:
            args=['read','--max-bytes','6000']+(['--ack',ack] if ack else [])
            code,packet=call(*args);assert code==0,(code,packet)
            if packet['status']=='all_received_in_this_context':break
            packets.append(packet);ack=packet['receipt']
        text_chars=sum(len(p['content']) for p in packets)
        assert text_chars==({'repeated':15503,'union':6988}[mode]),text_chars
        assert all(len(json.dumps(p,ensure_ascii=False).encode())+1<=6000 for p in packets)
        review=dict(topic_evidence=[dict(topic=t,ids=ids) for t,ids in located['topics'].items()])
        (cwd/'draft.json').write_text(json.dumps(review))
        code,audit=call('check');assert code==0 and audit['delivery_complete'] and audit['declared_pairs_complete']
        assert audit['coverage_complete'] is False
        results.append(dict(mode=mode,original_characters=text_chars,packets=len(packets),
                            tool_calls=1+1+len(packets)+1+1,controlled_failures=1,passed=True))
    finally:shutil.rmtree(cwd)
with (BASE/'preflight.json').open('x') as f:json.dump(results,f,indent=2)
print(json.dumps(results))
