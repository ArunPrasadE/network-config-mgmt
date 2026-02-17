#!/bin/bash
# Start the FastAPI backend server

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Start the server
echo "Starting FastAPI backend on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
