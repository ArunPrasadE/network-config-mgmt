#!/bin/bash
# ===========================================
# Build and push Docker image to ghcr.io
# Run this on a machine with Docker Hub access (e.g. WSL2)
# ===========================================
# Prerequisites:
#   echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u ArunPrasadE --password-stdin

cd "$(dirname "$0")"

echo "Building image..."
docker compose build

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed. Docker Hub access required for base images."
    exit 1
fi

echo ""
echo "Pushing to ghcr.io..."
docker compose push

if [ $? -eq 0 ]; then
    echo ""
    echo "Done. Image pushed to:"
    echo "  ghcr.io/arunprasade/netconfig:latest"
    echo ""
    echo "On your Mac, pull with: docker compose pull"
else
    echo ""
    echo "ERROR: Push failed. Check ghcr.io authentication:"
    echo '  echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u ArunPrasadE --password-stdin'
    exit 1
fi
