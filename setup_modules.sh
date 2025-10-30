#!/usr/bin/env bash
set -euo pipefail

# setup_modules.sh
# Creates (or reuses) venv in project root and installs required packages.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
PYTHON_CMD="${PYTHON_CMD:-python3}"
PKGS=(tld fuzzywuzzy requests argparse  )

echo "Setting up venv and required modules at: $VENV_DIR"

# Ensure python3 exists
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "Error: $PYTHON_CMD not found. Install Python 3." >&2
  exit 1
fi

# Create venv if missing
if [[ -d "$VENV_DIR" ]]; then
  echo "Virtualenv '$VENV_DIR' already exists — reusing."
else
  echo "Creating virtualenv..."
  "$PYTHON_CMD" -m venv "$VENV_DIR"
fi

PY_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

# Bootstrap pip if missing
if [[ ! -x "$PIP_BIN" ]]; then
  echo "Bootstrapping pip inside venv..."
  "$PY_BIN" -m ensurepip --upgrade || true
fi

echo "Upgrading pip, setuptools and wheel..."
"$PIP_BIN" install --upgrade pip setuptools wheel

echo "Installing packages: ${PKGS[*]} ..."
"$PIP_BIN" install "${PKGS[@]}"

echo "Setup complete."
echo "To run the scanner with venv python: $PY_BIN ./XSS/xss1.py --url <target>"
echo "You do NOT need to 'source' venv in scripts that call $PY_BIN directly."

