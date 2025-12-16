#!/bin/bash
# Quick Start Script for Todo AI Chatbot
# Works with or without Redis

echo "🚀 Starting Todo AI Chatbot..."
echo ""

# Set PYTHONPATH
export PYTHONPATH=/home/umair/todo-chatbot:$PYTHONPATH

# Check if OpenAI key is configured
if grep -q "sk-YOUR-KEY-HERE" backend/.env 2>/dev/null; then
    echo "⚠️  WARNING: OpenAI API key not configured!"
    echo "   Edit backend/.env and add your key from:"
    echo "   https://platform.openai.com/api-keys"
    echo ""
    echo "   Press Ctrl+C to stop, or Enter to continue anyway..."
    read
fi

# Start backend
echo "🐍 Starting Backend..."
cd backend
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"
echo "   📊 Logs: backend.log"
echo "   🔗 API: http://localhost:8000"
echo "   📚 Docs: http://localhost:8000/docs"
echo ""

cd ..

# Start frontend
echo "⚛️  Starting Frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
echo "   📊 Logs: frontend.log"
echo "   🔗 App: http://localhost:5173"
echo ""

cd ..

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Todo AI Chatbot is Running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Open: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "   Or run: pkill -f uvicorn && pkill -f vite"
echo ""
echo "💡 Press Ctrl+C when done"
echo ""

# Keep running
trap "echo ''; echo '🛑 Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Stopped'; exit 0" INT
wait
