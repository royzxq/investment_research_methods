"""Reload or pause the installed research schedule without cancelling research."""
import argparse
import os
from pathlib import Path
import plistlib
import re
import subprocess

try:
    from .install_research_service import LABEL
    from .research_scheduler import queue_lock
except ImportError:
    from install_research_service import LABEL
    from research_scheduler import queue_lock

ROOT = Path(__file__).resolve().parents[1]


def manage(action):
    if action not in {'start', 'stop'}:
        raise ValueError('unknown service action')
    domain = f'gui/{os.getuid()}'
    target = f'{domain}/{LABEL}'
    plist = Path.home() / 'Library/LaunchAgents' / f'{LABEL}.plist'
    if action == 'start' and not plist.is_file():
        raise ValueError('研究服务尚未安装，请先按 deploy/README.md 安装。')
    if plist.is_file():
        settings = plistlib.loads(plist.read_bytes())
        if (not isinstance(settings, dict)
                or settings.get('Label') != LABEL
                or settings.get('WorkingDirectory') != str(ROOT)
                or not isinstance(settings.get('ProgramArguments'), list)
                or settings['ProgramArguments'][:2] != ['/bin/zsh', str(ROOT / 'deploy/launchd/run_research.sh')]):
            raise ValueError('已安装 plist 不属于当前仓库，请按 deploy/README.md 重新安装。')
    if action == 'start':
        if (settings.get('RunAtLoad')
                or settings.get('KeepAlive') not in (None, False)
                or settings.get('StartCalendarInterval') != {'Hour': 5, 'Minute': 0}
                or 'StartInterval' in settings):
            raise ValueError('已安装 plist 不符合每日05:00排期，请按 deploy/README.md 重新安装。')
    try:
        # Prevent a scheduled invocation from claiming work between print and bootout.
        with queue_lock(ROOT / 'output/research_queue'):
            current = subprocess.run(['launchctl', 'print', target], capture_output=True,
                                     text=True, timeout=30)
            loaded = current.returncode == 0
            if not loaded and not (current.returncode == 113 and 'Could not find service' in current.stderr):
                raise RuntimeError(f'无法确认服务状态：{current.stderr.strip()}')
            if loaded:
                if re.search(r'^\s*(?:pid = [1-9]\d*|state = running)\s*$', current.stdout, re.M):
                    raise RuntimeError('研究仍在运行，本次未启停服务；请等待完成后重试。')
                subprocess.run(['launchctl', 'bootout', '--wait', target], check=True,
                               capture_output=True, text=True, timeout=30)
            if action == 'stop':
                return '研究定时服务已停止，plist和全部台账保留。' if loaded else '研究定时服务未加载，plist和全部台账保留。'
            subprocess.run(['launchctl', 'enable', target], check=True,
                           capture_output=True, text=True, timeout=30)
            subprocess.run(['launchctl', 'bootstrap', domain, str(plist)], check=True,
                           capture_output=True, text=True, timeout=30)
    except BlockingIOError as exc:
        raise RuntimeError('研究队列正在运行或被占用，本次未启停服务；请稍后重试。') from exc
    return f'研究定时服务已加载，每天北京时间05:00检查，不立即启动研究。\n日志：{ROOT / "output/research_queue/service.log"}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()
    try:
        print(manage(args.action))
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
