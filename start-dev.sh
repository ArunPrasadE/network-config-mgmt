#!/bin/bash
# Start both backend and frontend for development

cd "$(dirname "$0")"

echo "=========================================="
echo "Network Config Management - Development"
echo "=========================================="
echo ""
echo "Starting services..."
echo ""

# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "Services Running:"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
