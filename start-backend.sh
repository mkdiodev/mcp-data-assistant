#!/bin/bash
# ============================================
# MCP Data Assistant - Backend Startup Script
# ============================================

echo "🚀 Starting MCP Data Assistant Backend..."
echo "==========================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found!"
    echo "   Copy backend/.env.example to backend/.env and configure it."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start FastAPI server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000