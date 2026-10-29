from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.research_runner import stop_group
from scripts.research_usage import write_usage

def run(name):
    folder=BASE/name
    with tempfile.TemporaryDirectory(prefix='jev-consumer-cost-') as cwd:
        args=['codex','--no-daemon','exec','--json','--ephemeral','--sandbox','read-only',
              '--skip-git-repo-check','-C',cwd,'--output-schema',str(folder/'schema.json'),
              '-o',str(folder/'answer.json'),'-']
        process=dict(generator='codex',task_id=name,status='running',
                     scope='ranking handoff + complete source reading + real-error fallback + evidence mapping',
                     configured_model='gpt-6.1-sol',configured_reasoning='low',configured_service_tier='priority',
                     billing_auth='ChatGPT (codex login status)', model_reported_by_event=None,
                     launched_at=datetime.now(timezone.utc).isoformat())
        start=time.monotonic()
        with (folder/'events.jsonl').open('xb') as stdout,(folder/'stderr.log').open('xb') as stderr:
            proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,cwd=cwd,start_new_session=True)
            process['pid']=proc.pid
            try:
                proc.communicate((folder/'prompt.txt').read_bytes(),timeout=600)
                process['status']='completed' if proc.returncode==0 else 'failed'
            except subprocess.TimeoutExpired:
                process['status']='timeout'
            finally:
                stop_group(proc)
                process.update(exit_code=proc.returncode,completed_at=datetime.now(timezone.utc).isoformat(),
                               execution_duration_seconds=time.monotonic()-start)
        with (folder/'process.json').open('x') as f:json.dump(process,f,indent=2)
        write_usage(folder,'codex',process=process)
        print(json.dumps(process),flush=True)

if __name__=='__main__':
    # Two matched arms together; datasets sequential. No user configuration changes.
    for kind in ['announcements','passages']:
        suffix='-recovery' if '--recovery' in sys.argv else ''
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[kind+'-direct'+suffix,kind+'-jev'+suffix]))
