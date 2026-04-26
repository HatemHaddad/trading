#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load env
source "$SCRIPT_DIR/.env"

# Start API
source "$SCRIPT_DIR/venv/bin/activate"
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "API started (PID $API_PID) on http://localhost:8000"

# Serve built frontend
cd "$SCRIPT_DIR/web"
npx serve dist --listen 3000 &
WEB_PID=$!
echo "Web app started (PID $WEB_PID) on http://localhost:3000"

echo ""
echo "Press Ctrl+C to stop both servers."
wait
