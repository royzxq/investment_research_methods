"""One metered recovery using saved reviewed facts and a plain JSON receipt."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research_usage import write_usage

if __name__ == '__main__':
    setup = json.loads((BASE / 'setup.json').read_text())
    old_cwd = Path(setup['arms']['union']['cwd'])
    folder = BASE / 'union/bms-review/retry-1'
    folder.mkdir()
    cwd = Path(tempfile.mkdtemp(prefix='hengrui-claude-review-recovery-', dir='/private/tmp'))
    for name in ['sources', 'scripts']:
        shutil.copytree(old_cwd / name, cwd / name, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(old_cwd / 'bms_audit.py', cwd / 'bms_audit.py')
    shutil.copyfile(old_cwd / 'config.json', cwd / 'config.json')
    shutil.copyfile(old_cwd / 'draft-bms-reviewed.json', cwd / 'draft.json')
    (cwd / 'output').mkdir()
    shutil.copyfile(old_cwd / 'output/plan.json', cwd / 'output/plan.json')
    prompt = '''这是已有恒瑞材料端到端对照的失败恢复阶段，上次独立复核已保存修订稿并通过引文审计，但CLI在最终用量事件前超时。本次工作区的draft.json为该已保存修订稿；本次新上下文仍须实际读取原文，不继承旧receipt。不联网、不调用Jev或子代理、不读工作区以外资料。
使用Bash运行 /Users/xinquanzhou/miniconda3/bin/python3 bms_audit.py read ，完整收到source_text、additional_sources和当前陈述后，核对KIOMED拟签状态与附注连接、发生额与已支付的区别，以及BMS全部付款组成、销售提成、地域、条件、交割与项目阶段。原文乱码保持缺口，不补未披露参数。
直接用Write写bms-patch.json，格式为{"replacements":[]}；若已保存的陈述正确就保持空数组，不重新写长文。确有错误时仅替换相关现有条目、保留schema及各条evidence_ids。不要预读工具源码或为格式另写生成脚本；现有流程已给出完整原文和条目。
再用Bash运行 /Users/xinquanzhou/miniconda3/bin/python3 bms_audit.py apply --received <你刚刚完整收到的receipt> --patch bms-patch.json 。失败时按实际错误恢复并保留缺口。
最后只输出一个JSON对象，不用Markdown、不再写总结：{"review_file":"draft-bms-reviewed.json","changed_claim_ids":[],"remaining_gaps":["实际仍未解决的缺口"]}。这是恢复交接的文本JSON路径，程序会严格校验回执，全部模型调用计量。
'''
    (folder / 'prompt.txt').write_text(prompt)
    (folder / 'recovery-input.json').write_text(json.dumps(dict(cwd=str(cwd),
        previous_review_sha256=hashlib.sha256((old_cwd / 'draft-bms-reviewed.json').read_bytes()).hexdigest(),
        recovery_mode='fresh context source verification of saved corrections; plain JSON receipt avoids structured-output round',
        prior_attempt='../process.json'), indent=2))
    args = ['claude', '-p', '--permission-mode', 'auto', '--permission-prompts', 'none',
            '--output-format', 'stream-json', '--verbose', '--include-partial-messages',
            '--no-session-persistence', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--tools', 'Bash,Write,Edit', '--allowedTools', 'Bash,Write,Edit']
    process = dict(generator='claude', task_id='union-review-recovery', attempt=2,
        status='running', launched_at=datetime.now(timezone.utc).isoformat(), cwd=str(cwd),
        cli_arguments=args, scope='whole failed-stage recovery, including fresh source read and verification')
    start = time.monotonic()
    with (folder / 'events.jsonl').open('xb') as out, (folder / 'stderr.log').open('xb') as err:
        proc = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True)
        process['pid'] = proc.pid
        try:
            proc.communicate(prompt.encode(), timeout=900)
            process['status'] = 'completed' if proc.returncode == 0 else 'failed'
        except subprocess.TimeoutExpired:
            process['status'] = 'timeout'
            os.killpg(proc.pid, signal.SIGINT)
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL); proc.wait(timeout=5)
        process.update(exit_code=proc.returncode, completed_at=datetime.now(timezone.utc).isoformat(),
                       execution_duration_seconds=time.monotonic() - start)
    events = [json.loads(s) for s in (folder / 'events.jsonl').read_text().splitlines() if s]
    result = next((e for e in reversed(events) if e.get('type') == 'result'), None)
    if result:
        process['result_subtype'] = result.get('subtype')
        try:
            receipt = json.loads(result['result'])
            assert set(receipt) == {'review_file', 'changed_claim_ids', 'remaining_gaps'}
            assert receipt['review_file'] == 'draft-bms-reviewed.json'
            assert isinstance(receipt['changed_claim_ids'], list) and isinstance(receipt['remaining_gaps'], list)
            (folder / 'answer.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        except (ValueError, KeyError, AssertionError): process['receipt_valid'] = False
        else: process['receipt_valid'] = True
    for name in ['draft.json', 'draft-bms-reviewed.json', 'bms-patch.json', 'output/bms-read.json', 'output/bms-audit.json']:
        if (cwd / name).exists(): shutil.copyfile(cwd / name, folder / Path(name).name)
    (folder / 'process.json').write_text(json.dumps(process, ensure_ascii=False, indent=2))
    write_usage(folder, 'claude', process=process)
    print(json.dumps({k: process.get(k) for k in ['status', 'exit_code', 'execution_duration_seconds', 'result_subtype', 'receipt_valid']}))
