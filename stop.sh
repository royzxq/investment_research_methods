#!/bin/bash
# Pause the research schedule, retaining the installed plist and queue.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/research_service_control.py" stop "$@"
