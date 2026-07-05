#!/bin/bash
# LyricLab Setup Script
# Run: bash setup.sh
# After running, edit backend/app/secrets.py or set env vars with your API keys.

set -e
echo "=== LyricLab Setup ==="

# Backend deps
echo "[1] Installing backend dependencies..."
cd backend
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
pip install yt-dlp 2>/dev/null || pip3 install yt-dlp
cd ..

# Example secrets file
echo "[2] Creating secrets template..."
if [ ! -f "backend/app/secrets.py" ]; then
    cp backend/app/secrets.example.py backend/app/secrets.py
    echo "  Created backend/app/secrets.py - EDIT this file with your API keys"
fi

# .env template
echo "[3] Creating .env template..."
if [ ! -f ".env" ]; then
    cp backend/app/secrets.example.py .env 2>/dev/null || true
    echo "  Created .env for Docker - EDIT this file"
fi

# Frontend
echo "[4] Installing frontend dependencies..."
cd frontend && npm install 2>/dev/null || npm install --legacy-peer-deps
cd ..

# Directories
echo "[5] Creating data directories..."
mkdir -p data downloads output

echo ""
echo "=== Setup Complete ==="
echo "1. Edit backend/app/secrets.py with your API keys"
echo "2. Run: cd backend && uvicorn app.main:app --reload --port 8000"
echo "3. Run: cd frontend && npm run dev"
echo ""
echo "Or: docker-compose up -d"
