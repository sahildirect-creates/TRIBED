#!/bin/bash

echo "🚀 Starting TRIBED Platform..."

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB first."
    echo "   Run: sudo systemctl start mongod"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}Step 1: Setting up Backend...${NC}"

# Backend setup
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Set environment variables
export MONGODB_URL="mongodb://localhost:27017"
export SECRET_KEY="tribed-secret-key-dev-mode"

echo ""
echo -e "${BLUE}Step 2: Running Content Scraper (first-time setup)...${NC}"

# Check if content DB exists
if [ ! -f "../ml-engine/content_db.json" ]; then
    echo "Scraping initial content..."
    cd ../scrapers
    python scraper.py
    cd ../backend
else
    echo "Content DB already exists, skipping scraper..."
fi

echo ""
echo -e "${BLUE}Step 3: Starting Backend Server...${NC}"

# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../frontend

echo ""
echo -e "${BLUE}Step 4: Setting up Frontend...${NC}"

# Frontend setup
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Starting Frontend Server..."
echo ""
echo -e "${GREEN}🎉 TRIBED is running!${NC}"
echo -e "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "   Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
