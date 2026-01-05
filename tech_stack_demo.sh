#!/bin/bash
clear
echo "================================================"
echo "Todo AI Chatbot - Tech Stack"
echo "================================================"
sleep 2

echo ""
echo "🏗️  ARCHITECTURE:"
echo ""
echo "  Frontend:  Next.js (React Framework)"
echo "  Backend:   FastAPI (Python)"
echo "  ORM:       SQLModel"
echo "  Database:  Neon DB (PostgreSQL)"
sleep 3

echo ""
echo "📁 PROJECT STRUCTURE:"
tree -L 2 -I 'node_modules|venv|__pycache__|.next' 2>/dev/null || ls -la
sleep 3

echo ""
echo "🔧 BACKEND - FastAPI:"
head -30 backend/main.py
sleep 5

echo ""
echo "💾 DATABASE - SQLModel:"
head -30 backend/db/models.py
sleep 5

echo ""
echo "🌐 API ENDPOINTS:"
grep "@app\." backend/main.py | head -10
sleep 3

echo ""
echo "✅ TECH STACK COMPLETE"
echo "  • Next.js Frontend"
echo "  • FastAPI Backend"
echo "  • SQLModel ORM"
echo "  • Neon PostgreSQL"
sleep 2
