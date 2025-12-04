#!/usr/bin/env bash
set -euo pipefail

# dev-setup.sh - Prepare local dev environment and venv (Unix-like)
# Usage: ./scripts/dev-setup.sh [--force]

FORCE=0
while [[ "$#" -gt 0 ]]; do case "$1" in
  --force) FORCE=1; shift;;
  -h|--help) echo "Usage: $0 [--force]"; exit 0;;
  *) echo "Unknown argument $1"; exit 1;;
esac; done

PY_BIN=$(command -v python || command -v python3 || true)
if [[ -z "$PY_BIN" ]]; then
  echo "Could not find 'python' in PATH. Install Python 3.11 and ensure 'python' or 'python3' points to it." >&2
  exit 1
fi

PY_VER=$($PY_BIN -c 'import sys, json; print(json.dumps({"major":sys.version_info.major, "minor":sys.version_info.minor, "micro":sys.version_info.micro}))')
MAJOR=$(echo "$PY_VER" | python -c 'import sys, json; print(json.load(sys.stdin)["major"])')
MINOR=$(echo "$PY_VER" | python -c 'import sys, json; print(json.load(sys.stdin)["minor"])')
echo "Detected Python version: $MAJOR.$MINOR"
if [[ "$MAJOR" -ne 3 || "$MINOR" -ne 11 ]] && [[ "$FORCE" -eq 0 ]]; then
  echo "Recommended Python version is 3.11.x (CI uses Python 3.11). Run with --force to override or install 3.11 and re-run this script." >&2
  exit 1
fi

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
VENV_DIR="$ROOT_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment at $VENV_DIR..."
  $PY_BIN -m venv "$VENV_DIR"
fi

PIP="$VENV_DIR/bin/pip"
if [[ ! -f "$PIP" ]]; then
  PIP="$PY_BIN -m pip"
fi
echo "Installing requirements into venv..."
$PIP install --upgrade pip
$PIP install -r "$ROOT_DIR/requirements.txt"

echo "Dev setup complete. Activate venv with: source .venv/bin/activate and run tests via: python -m pytest -q -m \"not e2e\""
