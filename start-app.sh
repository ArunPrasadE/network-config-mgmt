#!/bin/bash
# ===========================================
# Network Config Management - Startup Script
# Works on macOS and WSL2
# ===========================================
# Usage:
#   ./start-app.sh           # start (build if needed)
#   ./start-app.sh --build   # force rebuild images

cd "$(dirname "$0")"

echo "=========================================="
echo " Network Config Management"
echo "=========================================="
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

docker compose up --build "$@"
