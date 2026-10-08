"""Preview or explicitly install the methods-owned macOS research dispatcher."""
import argparse
import os
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'com.investment-research-methods.research'


def service(python, codex, claude, root=ROOT):
    for value in (python, codex, claude):
        if not Path(value).is_absolute() or not os.access(value, os.X_OK):
            raise ValueError('Python and both CLI paths must be absolute executables')
    return dict(Label=LABEL,
                ProgramArguments=['/bin/zsh', str(root/'deploy/launchd/run_research.sh'), python, codex, claude],
                WorkingDirectory=str(root), StartInterval=900, RunAtLoad=True,
                ThrottleInterval=60, ExitTimeOut=45,
                StandardOutPath=str(root/'output/research_queue/service.log'),
                StandardErrorPath=str(root/'output/research_queue/service-error.log'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True)
    parser.add_argument('--codex-cli', required=True)
    parser.add_argument('--claude-cli', required=True)
    parser.add_argument('--install', action='store_true', help='Without this flag, only print the plist')
    args = parser.parse_args()
    raw = plistlib.dumps(service(args.python, args.codex_cli, args.claude_cli))
    if not args.install:
        sys.stdout.buffer.write(raw)
        return
    target = Path.home()/'Library/LaunchAgents'/f'{LABEL}.plist'
    if target.exists():
        raise ValueError('service already exists; bootout and remove its plist before replacement')
    (ROOT/'output/research_queue').mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    subprocess.run(['launchctl', 'bootstrap', f'gui/{os.getuid()}', str(target)], check=True)
    print(f'Installed {LABEL}; daily cap 4; writeback remains governed by ai_investment config')


if __name__ == '__main__':
    main()
