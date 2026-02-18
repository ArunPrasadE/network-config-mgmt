#!/bin/bash
# Starts both backend (FastAPI) and frontend (Vite) inside a single container.
# Backend runs in background; frontend runs in foreground.
# Ctrl+C stops everything.

# Trap SIGTERM/SIGINT so both processes get cleaned up
trap 'kill $(jobs -p) 2>/dev/null; exit 0' SIGTERM SIGINT

echo "Installing frontend dependencies..."
cd /app/frontend && npm install

echo "Starting backend (FastAPI) on :8000..."
cd /app && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &

echo "Starting frontend (Vite) on :5173..."
cd /app/frontend && npm run dev -- --host 0.0.0.0
