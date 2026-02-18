#!/bin/bash
# ===========================================
# Network Config Management - Startup Script
# Works on macOS and WSL2
# ===========================================
# Usage:
#   ./start-app.sh           # start (pulls from ghcr.io if image missing)
#   ./start-app.sh --build   # force rebuild image locally (needs Docker Hub)

cd "$(dirname "$0")"

IMAGE="ghcr.io/arunprasade/netconfig:latest"

echo "=========================================="
echo " Network Config Management"
echo "=========================================="
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop"
echo "=========================================="
echo ""

# If image exists locally, start directly. Otherwise pull from ghcr.io.
if docker image inspect "$IMAGE" > /dev/null 2>&1; then
    echo "Image found locally. Starting..."
    echo ""
    docker compose up "$@"
else
    echo "Image not found locally. Pulling from ghcr.io..."
    echo ""
    docker compose pull
    docker compose up "$@"
fi
