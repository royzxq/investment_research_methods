#!/bin/bash
# Reload the installed daily schedule without starting research immediately.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/research_service_control.py" start "$@"
