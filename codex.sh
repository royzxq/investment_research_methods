#!/usr/bin/env bash
# 本仓库专用入口：./codex.sh [Codex CLI 参数或子命令]
# 仅通过会话参数禁用第一批 34 个技能，保留本仓库研究技能、通用投研技能及全局配置。
# 使用独立进程，避免复用其他项目的共享 app-server。
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd -- "$repo_root"

# 与定时研究适配器共用同一份名单；按本入口所在仓库读取，兼容 worktree。
skill_config="$(python3 -c \
    'import runpy, sys; print(runpy.run_path(sys.argv[1])["CODEX_SKILL_FILTER"])' \
    "$repo_root/scripts/research_harness.py")"

# 可指定应用内 CLI；值是单个可执行文件路径，额外参数仍通过 "$@" 传入。
codex_cli="${CODEX_CLI:-codex}"
exec "$codex_cli" --no-daemon --cd "$repo_root" -c "$skill_config" "$@"
