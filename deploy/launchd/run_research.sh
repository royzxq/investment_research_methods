#!/bin/zsh
# Arguments are absolute paths captured by install_research_service.py.
set -eu
SCRIPT_PATH="${0:A}"
PROJECT_DIR="${SCRIPT_PATH:h:h:h}"
if [ -f "$HOME/.zshrc" ]; then
  # Match the existing ai_investment launchd environment bootstrap. Never echo.
  # Interactive exports may append to unset variables (e.g. PYTHONPATH).
  # Keep that normal shell behavior while loading them, then restore nounset.
  set +u
  eval "$(grep -E '^[[:space:]]*export [A-Za-z_][A-Za-z0-9_]*=' "$HOME/.zshrc" 2>/dev/null)" 2>/dev/null || true
  set -u
fi
cd "$PROJECT_DIR"
scheduler_args=("$1" scripts/research_scheduler.py run --scheduled --codex-cli "$2" --claude-cli "$3")
if [[ -n "${4:-}" ]]; then
  scheduler_args+=(--runtime-config "$4")
fi
if [[ -n "${5:-}" ]]; then
  scheduler_args+=(--dsh-cli "$5")
fi
exec /usr/bin/caffeinate -i -s "${scheduler_args[@]}"
