#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d .venv ]; then
  echo "📦 Creating local virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip >/dev/null 2>&1 || true
python -m pip install -e .

echo "✅ vflask is installed and ready."

vflask --help
