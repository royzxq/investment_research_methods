"""Freeze the existing matched Hengrui fixture for actual Claude Code consumers."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import tempfile

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
OLD = ROOT / 'research/investment/maintenance/2026-10-10/evidence/hengrui-end-to-end'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def workspace(mode, suffix=''):
    cwd = Path(tempfile.mkdtemp(prefix=f'hengrui-claude-{mode}{suffix}-', dir='/private/tmp'))
    (cwd / 'sources').mkdir()
    (cwd / 'scripts').mkdir()
    for name in ['finance', 'bms']:
        shutil.copyfile(OLD / 'sources' / f'{name}.txt', cwd / 'sources' / f'{name}.txt')
    for name in ['research_reader.py', 'research_evidence.py']:
        shutil.copyfile(ROOT / 'scripts' / name, cwd / 'scripts' / name)
    for name in ['bench_tool.py', 'bms_audit.py']:
        shutil.copyfile(OLD / 'harness-source' / name, cwd / name)
    config = dict(mode=mode, sources={name: dict(path=f'sources/{name}.txt',
                  sha256=sha(cwd / 'sources' / f'{name}.txt')) for name in ['finance', 'bms']})
    (cwd / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2))
    return cwd


if __name__ == '__main__':
    previous = runpy.run_path(str(OLD / 'harness-source/prepare.py'))
    prompt = previous['COMMON'].replace('通过 exec 工具', '通过 Bash 工具')
    prompt += '\n补充当前读取契约：原文含多项财务条款时逐项展开所有付款组成、销售提成、计算基础、地域及条件，不能用证据ID齐全代替语义覆盖。BMS事实条目单独使用evidence_ids=["A126"]，方便后续同范围独立核验。\n'
    setup = dict(generator='claude', default_model=True, arms={},
                 prompt_change='Host tool name plus current financial-composition checklist; both arms identical.',
                 source_archive=str(OLD))
    for mode in ['repeated', 'union']:
        folder = BASE / mode
        folder.mkdir()
        cwd = workspace(mode)
        instruction = ('读取组织：按licensing、related、cash分别读取。每个主题队列独立，相关原文会重复返回；这是待比较的原有主题交接基线。'
                       if mode == 'repeated' else
                       '读取组织：三主题共享同一份原文，合并同源重叠范围。完整收到后按各主题引用；这是待比较的优化流程。')
        (folder / 'prompt.txt').write_text(prompt + '\n' + instruction + '\n')
        (folder / 'schema.json').write_text(json.dumps(previous['SCHEMA']))
        setup['arms'][mode] = dict(cwd=str(cwd), prompt_sha256=sha(folder / 'prompt.txt'),
             files={str(p.relative_to(cwd)): sha(p) for p in cwd.rglob('*') if p.is_file()})
    (BASE / 'setup.json').write_text(json.dumps(setup, ensure_ascii=False, indent=2))
    print(json.dumps({'prepared': list(setup['arms']), 'source_hashes': {
        n: sha(OLD / 'sources' / f'{n}.txt') for n in ['finance', 'bms']}}))
