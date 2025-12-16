#!/bin/bash
# Start Todo AI Chatbot (Development Mode)

set -e

echo "🤖 Starting Todo AI Chatbot..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env not found${NC}"
    echo "📝 Please copy backend/.env.example to backend/.env and configure"
    exit 1
fi

# Start Redis
echo -e "${BLUE}🔴 Checking Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not running${NC}"
    echo "Start Redis with: redis-server"
    exit 1
fi
echo -e "${GREEN}✅ Redis is running${NC}"
echo ""

# Backend
echo -e "${BLUE}🐍 Starting Backend...${NC}"
cd backend

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Start backend in background
uvicorn backend.main:app --reload --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

cd ..

# Frontend
echo -e "${BLUE}⚛️  Starting Frontend...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   App: http://localhost:5173"
echo ""

cd ..

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Todo AI Chatbot is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Open in browser: http://localhost:5173"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo ""

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm .backend.pid .frontend.pid 2>/dev/null; echo '✅ Stopped'; exit 0" INT

# Keep script running
wait
