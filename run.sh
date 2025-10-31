#!/bin/bash

# Server Control Panel - Startup Script

echo "========================================="
echo "  Server Control Panel"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================="
echo "  Starting server..."
echo "========================================="
echo ""

# Run the FastAPI app with Uvicorn
cd backend
uvicorn app:app --host 0.0.0.0 --port 5001 --reload
