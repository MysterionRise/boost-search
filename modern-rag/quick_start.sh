#!/bin/bash

# Modern RAG Quick Start Script

echo "=== Modern RAG System - Quick Start ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    echo ""
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. Install Docker to run Qdrant locally."
    echo "   Or update QDRANT_HOST in .env to use a remote instance."
    echo ""
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Start Qdrant: docker-compose up qdrant -d"
echo "3. Run example: python examples/basic_usage.py"
echo "4. Or start API: uvicorn api.main:app --reload"
echo ""
echo "For more info, see README.md"
