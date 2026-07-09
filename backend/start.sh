#!/usr/bin/env bash
# Start the VidMind FastAPI backend.
# Must be run from the project root (the folder that CONTAINS the backend/ directory).
# Usage:  bash backend/start.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [[ ! -f "$VENV_PYTHON" ]]; then
  echo "[VidMind] Virtual environment not found. Run:"
  echo "  bash backend/setup.sh"
  exit 1
fi

if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
  echo "[VidMind] WARNING: backend/.env not found."
  echo "  Copy backend/.env.example -> backend/.env and add your GROQ_API_KEY."
fi

echo "[VidMind] Starting server at http://localhost:8000 ..."
echo "[VidMind] API docs at http://localhost:8000/docs"

cd "$PROJECT_ROOT"
"$VENV_PYTHON" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload