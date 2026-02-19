#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"

if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install --upgrade setuptools wheel
"$VENV_PYTHON" -m pip install --no-build-isolation -e "$SCRIPT_DIR"
"$VENV_PYTHON" -m -u ucb_to_testflight.upload_to_testflight_cmd_entry "$@"
