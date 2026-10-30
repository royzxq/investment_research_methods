"""Meter whole Claude CLI runs, including every model tool and recovery turn."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import runpy
import shutil
import signal
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research_usage import write_usage


def stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)


def run(mode, review=False):
    setup = json.loads((BASE / 'setup.json').read_text())
    cwd = Path(setup['arms'][mode]['cwd'])
    folder = BASE / mode
    if review:
        folder /= 'bms-review'
        folder.mkdir()
        old = Path(setup['source_archive'])
        previous = runpy.run_path(str(old / 'harness-source/run_bms_review.py'))
        prompt = previous['PROMPT'].replace('定向的BMS财务条款审阅', '定向的KIOMED交易状态和BMS财务条款审阅')
        prompt = prompt.replace('完整A126原文和当前相关陈述', '完整A126、P65/P165/P166原文和当前相关陈述')
        prompt = prompt.replace('只替换需要调整的原有BMS条目', '只替换需要调整的原有KIOMED或BMS条目，并保留每条原有evidence_ids')
        prompt += '\n对KIOMED条目同时核对是否保留拟签/将继受的交易状态，是否从关联方名单过度推出已确定的关联认定路径。会议日与披露日分别表述，不能无证据称原文日期为笔误。必要时修改相应现有条目，不能改未授权条目。source_text与additional_sources都须实际完整收到后才能确认receipt；若截断则停止并披露。\n'
        (folder / 'prompt.txt').write_text(prompt)
        (folder / 'schema.json').write_text(json.dumps(previous['SCHEMA']))
        shutil.copyfile(BASE / 'harness-source/bms_audit.py', cwd / 'bms_audit.py')
    args = ['claude', '-p', '--permission-mode', 'auto', '--permission-prompts', 'none',
            '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--tools', 'Bash,Write,Edit', '--allowedTools', 'Bash,Write,Edit',
            '--json-schema', (folder / 'schema.json').read_text()]
    process = dict(generator='claude', task_id=mode + ('-bms-review' if review else ''),
                   status='running', scope='complete actual Claude tool loop with controlled failure and explicit receipts',
                   launched_at=datetime.now(timezone.utc).isoformat(), cli='Claude Code 2.1.296',
                   cli_arguments=args, configured_model='CLI default', jev_calls=0)
    start = time.monotonic()
    with (folder / 'events.jsonl').open('xb') as out, (folder / 'stderr.log').open('xb') as err:
        proc = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE, stdout=out,
                                stderr=err, start_new_session=True)
        process['pid'] = proc.pid
        try:
            proc.communicate((folder / 'prompt.txt').read_bytes(), timeout=900 if not review else 400)
            process['status'] = 'completed' if proc.returncode == 0 else 'failed'
        except subprocess.TimeoutExpired:
            process['status'] = 'timeout'
        finally:
            stop(proc)
            process.update(exit_code=proc.returncode, completed_at=datetime.now(timezone.utc).isoformat(),
                           execution_duration_seconds=time.monotonic() - start)
    events = []
    for line in (folder / 'events.jsonl').read_text().splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    results = [e for e in events if e.get('type') == 'result']
    if results:
        result = results[-1]
        process['result_subtype'] = result.get('subtype')
        process['result_is_error'] = result.get('is_error')
        process['model_usage_keys'] = list(result.get('modelUsage', {}))
        if result.get('is_error'): process['status'] = 'failed'
        if isinstance(result.get('structured_output'), dict):
            (folder / 'answer.json').write_text(json.dumps(result['structured_output'], ensure_ascii=False, indent=2))
    names = (['bms-patch.json', 'draft-bms-reviewed.json', 'output/bms-read.json', 'output/bms-audit.json']
             if review else ['draft.json'])
    for name in names:
        if (cwd / name).exists(): shutil.copyfile(cwd / name, folder / Path(name).name)
    if not review and (cwd / 'output').exists():
        shutil.copytree(cwd / 'output', folder / 'delivery')
    (folder / 'process.json').write_text(json.dumps(process, ensure_ascii=False, indent=2))
    write_usage(folder, 'claude', process=process)
    print(json.dumps({k: process.get(k) for k in ['task_id', 'status', 'exit_code',
        'execution_duration_seconds', 'result_subtype', 'model_usage_keys']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--review', action='store_true')
    a = p.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda mode: run(mode, a.review), ['repeated', 'union']))
