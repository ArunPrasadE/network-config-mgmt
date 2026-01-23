#!/bin/bash
# ===========================================
# Network Config Management - Full App Startup
# ===========================================
# Starts Docker backend, frontend, and opens browser

cd "$(dirname "$0")"

echo "=========================================="
echo "Network Config Management - Starting..."
echo "=========================================="

# 1. Start Docker container (backend)
echo ""
echo "[1/4] Starting Docker container..."
if docker ps | grep -q netconfig-backend; then
    echo "      Container already running"
else
    docker start netconfig-backend
    if [ $? -eq 0 ]; then
        echo "      Container started successfully"
    else
        echo "      ERROR: Failed to start container"
        echo "      Make sure Docker Desktop is running"
        exit 1
    fi
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

# Open browser (works on WSL)
if command -v wslview &> /dev/null; then
    wslview http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
elif command -v cmd.exe &> /dev/null; then
    cmd.exe /c start http://localhost:5173
else
    echo "      Could not open browser automatically"
    echo "      Please open http://localhost:5173 manually"
fi

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
trap "kill $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait $FRONTEND_PID
