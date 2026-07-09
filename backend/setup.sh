#!/usr/bin/env bash
# Run once from the project root to create the backend venv and install deps.
# Usage:  bash backend/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "[VidMind] Creating virtual environment at $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

echo "[VidMind] Installing dependencies ..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet

echo ""
echo "[VidMind] Setup complete."
echo "  1. Copy backend/.env.example  ->  backend/.env"
echo "  2. Fill in your GROQ_API_KEY  (https://console.groq.com)"
echo "  3. Run:  bash backend/start.sh"