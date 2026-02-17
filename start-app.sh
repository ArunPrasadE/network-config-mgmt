#!/bin/bash
# ===========================================
# Network Config Management - Full App Startup
# ===========================================
# Starts Docker backend, frontend, and opens browser

cd "$(dirname "$0")"

echo "=========================================="
echo "Network Config Management - Starting..."
echo "=========================================="

# 1. Build/start Docker backend (idempotent for dev)
echo ""
echo "[1/4] Starting Docker backend..."
CONTAINER_NAME="netconfig-backend"
IMAGE_NAME="netconfig-backend:latest"

# Build image if missing (Dockerfile at root)
if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE_NAME"; then
    echo "      Building image from Dockerfile..."
    docker build -t "$IMAGE_NAME" .
    if [ $? -ne 0 ]; then
        echo "      ERROR: Build failed. Check Dockerfile syntax/logs."
        echo "      Tip: docker build -t test . && docker run --rm test"
        exit 1
    fi
    echo "      Image built successfully."
else
    echo "      Image exists, checking container..."
fi

# Stop/remove if exists but broken (dev restart)
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    docker rm -f "$CONTAINER_NAME"
fi

# Create/run fresh
echo "      Starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8000:8000 \
    -v "$(pwd):/app" \
    "$IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo "      Backend container created/started."
else
    echo "      ERROR: Run failed. Check: docker logs $CONTAINER_NAME"
    exit 1
fi

# 2. Wait for backend to be ready
echo ""
echo "[2/4] Waiting for backend API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/hosts > /dev/null 2>&1; then
        echo "      Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "      WARNING: Backend not responding yet, continuing anyway..."
    fi
    sleep 1
done

# 3. Start frontend
echo ""
echo "[3/4] Starting frontend..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "      Installing dependencies..."
    npm install
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!
cd ..

# 4. Wait a moment and open browser
echo ""
echo "[4/4] Opening browser..."
sleep 3

# Open browser (WSL2/Windows priority)
if command -v cmd.exe &> /dev/null; then
    cmd.exe /c start http://localhost:5173 2>/dev/null
elif command -v wslview &> /dev/null; then
    wslview http://localhost:5173
elif command -v open &> /dev/null; then
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
else
    echo "      Could not open browser automatically"
fi
echo "      Open manually: http://localhost:5173"

echo ""
echo "=========================================="
echo "App is running!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the frontend"

# Wait for frontend process
trap "kill $FRONTEND_PID 2>/dev/null; docker rm -f $CONTAINER_NAME 2>/dev/null; exit" INT TERM
wait $FRONTEND_PID
