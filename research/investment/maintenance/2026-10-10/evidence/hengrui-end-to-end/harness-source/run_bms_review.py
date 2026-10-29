from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))
from scripts.research_runner import stop_group
from scripts.research_usage import write_usage

PROMPT='''请对同一小范围恒瑞取证任务做一次独立、定向的BMS财务条款审阅。这是原流程的质量检查和必要修正，所有调用计量。只读本工作区，不联网、不调用其他模型，不扩大为公司估值。
先真实调用 /Users/xinquanzhou/miniconda3/bin/python3 bms_audit.py read ，输出预算至少6000 token。工具一次给出完整A126原文和当前相关陈述，不要读其他报告或预期答案。
逐项核对原文财务条款的付款组成、条件、首付/周年/潜在总额的边界、销售提成的计算基础及地域范围；同时确认交易状态和项目阶段没有误写。不能仅因为首付和里程碑数字正确就认为完整。原文前两页乱码继续保持缺口；不要推断已经到账或交割。其它来源条目在本上下文未读，保留原记录。
完整收到并作语义复核后，用工具写bms-patch.json，格式{"replacements":[{"id":"原有BMS条目的ID","statement":"修正后的完整陈述","evidence_ids":["A126"],"quotes":[{"unit_id":"A126","text":"短小逐字引文"}]}]}。只替换需要调整的原有BMS条目；已完整正确可replacements空数组。逐字引文保留换行；只修原文支持的内容，不补填具体提成率或未披露条件。
调用 /Users/xinquanzhou/miniconda3/bin/python3 bms_audit.py apply --received <实际完整收到的receipt> --patch bms-patch.json 。如有引文问题，定向修复后再调用，不隐瞒重试。原始draft.json保留，修正版由程序另存draft-bms-reviewed.json。最后只返回schema规定的小回执，不能重写整篇。
'''
SCHEMA=dict(type='object',additionalProperties=False,required=['review_file','changed_claim_ids','remaining_gaps'],properties={
    'review_file':dict(type='string'),'changed_claim_ids':dict(type='array',items=dict(type='string')),
    'remaining_gaps':dict(type='array',items=dict(type='string'))})


def run(mode):
    setup=json.loads((BASE/'setup.json').read_text());cwd=Path(setup['arms'][mode]['cwd'])
    shutil.copyfile(BASE/'bms_audit.py',cwd/'bms_audit.py')
    folder=BASE/mode/'bms-review';folder.mkdir()
    (folder/'prompt.txt').write_text(PROMPT);(folder/'schema.json').write_text(json.dumps(SCHEMA))
    args=['codex','--no-daemon','exec','--json','--ephemeral','--sandbox','workspace-write',
          '--skip-git-repo-check','-C',str(cwd),'--output-schema',str(folder/'schema.json'),'-o',str(folder/'answer.json'),'-']
    process=dict(generator='codex',task_id=mode+'-bms-review',status='running',
        scope='symmetric fresh-context semantic audit/repair of BMS terms after initial consumer turns',
        model_reported_by_event=None,launched_at=datetime.now(timezone.utc).isoformat())
    start=time.monotonic()
    with (folder/'events.jsonl').open('xb') as out,(folder/'stderr.log').open('xb') as err:
        proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=out,stderr=err,cwd=cwd,start_new_session=True)
        process['pid']=proc.pid
        try:
            proc.communicate(PROMPT.encode(),timeout=300)
            process['status']='completed' if proc.returncode==0 else 'failed'
        except subprocess.TimeoutExpired:process['status']='timeout'
        finally:
            stop_group(proc)
            process.update(exit_code=proc.returncode,completed_at=datetime.now(timezone.utc).isoformat(),
                execution_duration_seconds=time.monotonic()-start)
    for name in ['bms-patch.json','draft-bms-reviewed.json','output/bms-read.json','output/bms-audit.json']:
        if (cwd/name).exists():shutil.copyfile(cwd/name,folder/Path(name).name)
    with (folder/'process.json').open('x') as f:json.dump(process,f,indent=2)
    write_usage(folder,'codex',process=process)
    print(json.dumps(process),flush=True)


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,['repeated','union']))
