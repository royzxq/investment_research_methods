#!/bin/zsh
# Arguments are absolute paths captured by install_research_service.py.
set -eu
SCRIPT_PATH="${0:A}"
PROJECT_DIR="${SCRIPT_PATH:h:h:h}"
if [ -f "$HOME/.zshrc" ]; then
  # Match the existing ai_investment launchd environment bootstrap. Never echo.
  eval "$(grep -E '^[[:space:]]*export [A-Za-z_][A-Za-z0-9_]*=' "$HOME/.zshrc" 2>/dev/null)" 2>/dev/null || true
fi
cd "$PROJECT_DIR"
exec /usr/bin/caffeinate -i -s "$1" scripts/research_scheduler.py run --scheduled --codex-cli "$2" --claude-cli "$3"
