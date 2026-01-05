#!/bin/bash

# Quick Start Script for Soil Analysis API
# This script helps you get the API running locally in seconds

set -e

echo "🌱 Soil Analysis API - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 detected: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created (you can edit it to add your Roboflow API key)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Starting the API server..."
echo "=================================="
echo ""
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py
