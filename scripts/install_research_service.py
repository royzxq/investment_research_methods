"""Preview or explicitly install the methods-owned macOS research dispatcher."""
import argparse
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import time
import re

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'com.investment-research-methods.research'


def service(python, codex, claude, root=ROOT):
    for value in (python, codex, claude):
        if not Path(value).is_absolute() or not os.access(value, os.X_OK):
            raise ValueError('Python and both CLI paths must be absolute executables')
    return dict(Label=LABEL,
                ProgramArguments=['/bin/zsh', str(root/'deploy/launchd/run_research.sh'), python, codex, claude],
                WorkingDirectory=str(root), StartCalendarInterval={'Hour':5,'Minute':0},
                EnvironmentVariables={'TZ':'Asia/Shanghai'},
                ThrottleInterval=60, ExitTimeOut=45,
                StandardOutPath=str(root/'output/research_queue/service.log'),
                StandardErrorPath=str(root/'output/research_queue/service-error.log'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True)
    parser.add_argument('--codex-cli', required=True)
    parser.add_argument('--claude-cli', required=True)
    parser.add_argument('--install', action='store_true', help='Without this flag, only print the plist')
    parser.add_argument('--replace-when-idle',action='store_true',help='Wait for an existing run to finish before replacing its schedule')
    args = parser.parse_args()
    raw = plistlib.dumps(service(args.python, args.codex_cli, args.claude_cli))
    if not args.install:
        sys.stdout.buffer.write(raw)
        return
    target = Path.home()/'Library/LaunchAgents'/f'{LABEL}.plist'
    from research_scheduler import journal
    event_log=ROOT.parent/'ai_investment/logs/research_loop/events.jsonl'
    journal(event_log,'service_install_requested',details={'time':'05:00','replace_when_idle':args.replace_when_idle})
    if target.exists():
        if not args.replace_when_idle:
            raise ValueError('service already exists; use --replace-when-idle to preserve active research')
        target.with_suffix('.plist.bak').write_bytes(target.read_bytes())
        pending=target.with_suffix('.plist.partial')
        pending.write_bytes(raw)
        pending.replace(target)  # A reboot also loads the new schedule while we wait.
        domain=f'gui/{os.getuid()}'
        while True:
            current=subprocess.run(['launchctl','print',f'{domain}/{LABEL}'],capture_output=True,text=True)
            if not re.search(r'^\s*pid = \d+',current.stdout,re.M):
                break
            print('Waiting for active research to finish before schedule replacement',flush=True)
            time.sleep(30)
        subprocess.run(['launchctl','bootout','--wait',f'{domain}/{LABEL}'],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    (ROOT/'output/research_queue').mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary=target.with_suffix('.plist.partial')
    temporary.write_bytes(raw)
    temporary.replace(target)
    subprocess.run(['launchctl','enable',f'gui/{os.getuid()}/{LABEL}'],check=True)
    subprocess.run(['launchctl', 'bootstrap', f'gui/{os.getuid()}', str(target)], check=True)
    journal(event_log,'service_installed',details={'time':'05:00','plist':str(target)})
    print(f'Installed {LABEL}; daily check 05:00 Asia/Shanghai; daily cap 4',flush=True)


if __name__ == '__main__':
    main()
