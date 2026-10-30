from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))
from scripts.research_runner import stop_group
from scripts.research_usage import write_usage


def run(mode):
    setup=json.loads((BASE/'setup.json').read_text())
    cwd=Path(setup['arms'][mode]['cwd'])
    folder=BASE/mode
    args=['codex','--no-daemon','exec','--json','--ephemeral','--sandbox','workspace-write',
          '--skip-git-repo-check','-C',str(cwd),'--output-schema',str(folder/'schema.json'),
          '-o',str(folder/'answer.json'),'-']
    process=dict(generator='codex',task_id=mode,status='running',
        scope='actual model tool loop: locate, source returns, continuation, verification, reference audit and controlled failure recovery',
        model_reported_by_event=None,launched_at=datetime.now(timezone.utc).isoformat())
    start=time.monotonic()
    with (folder/'events.jsonl').open('xb') as out,(folder/'stderr.log').open('xb') as err:
        proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=out,stderr=err,cwd=cwd,start_new_session=True)
        process['pid']=proc.pid
        try:
            proc.communicate((folder/'prompt.txt').read_bytes(),timeout=900)
            process['status']='completed' if proc.returncode==0 else 'failed'
        except subprocess.TimeoutExpired:process['status']='timeout'
        finally:
            stop_group(proc)
            process.update(exit_code=proc.returncode,completed_at=datetime.now(timezone.utc).isoformat(),
                           execution_duration_seconds=time.monotonic()-start)
    for name in ['draft.json']:
        if (cwd/name).exists():shutil.copyfile(cwd/name,folder/name)
    if (cwd/'output').exists():shutil.copytree(cwd/'output',folder/'delivery')
    with (folder/'process.json').open('x') as f:json.dump(process,f,indent=2)
    write_usage(folder,'codex',process=process)
    print(json.dumps(process),flush=True)


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,['repeated','union']))
