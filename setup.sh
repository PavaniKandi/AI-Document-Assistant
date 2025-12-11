#!/bin/bash

echo "🚀 Document Q&A Application - Quick Setup"
echo "=========================================="
echo ""

# Check if Ollama is running
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running!"
    echo "Please start Ollama with: ollama serve"
    echo "Or download from https://ollama.ai"
    exit 1
fi
echo "✅ Ollama is running"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "✅ Backend ready"
echo ""

# Frontend setup
cd ../frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install > /dev/null 2>&1

echo "✅ Frontend ready"
echo ""

echo "=========================================="
echo "Setup complete! Now run:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo "=========================================="
