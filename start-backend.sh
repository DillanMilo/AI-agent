#!/bin/bash

echo "🚀 Starting AI Agent Backend..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Interactive API at: http://localhost:8000/redoc"
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
python api.py
