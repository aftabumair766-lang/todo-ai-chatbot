# 🤖 Todo AI Chatbot

A production-ready AI-powered todo chatbot with natural language processing, built with OpenAI GPT-4, FastAPI, and React.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![OpenAI GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://platform.openai.com/)

## ✨ Features

- **Natural Language Understanding**: Manage tasks using plain English
- **5 Task Operations**: Add, view, complete, update, and delete tasks
- **Beginner-Friendly UX**:
  - ✅ Emoji confirmations for all actions
  - ⏳/✅ Task status indicators
  - 📋 Neat numbered task lists
  - ⚠️ Input validation with helpful errors
  - 👋 Friendly greeting responses
- **Production Architecture**:
  - 100% Stateless design (no in-memory sessions)
  - JWT authentication with Better Auth
  - Rate limiting (10 req/min)
  - Row-level security (user_id filtering)
  - Async PostgreSQL with connection pooling
- **MCP-First Architecture**: All operations via Model Context Protocol tools
- **Full Type Safety**: Python type hints + TypeScript frontend
- **Comprehensive Testing**: Unit, integration, and end-to-end tests

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Reusable Agent](#-reusable-agent)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or Neon Serverless)
- Redis 6+ (for rate limiting)
- OpenAI API key

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/todo-chatbot.git
cd todo-chatbot

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Initialize database
alembic upgrade head

# 5. Start backend
uvicorn backend.main:app --reload

# 6. Setup frontend (new terminal)
cd ../frontend
npm install
npm run dev

# 7. Open browser
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
```

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│              http://localhost:5173                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     ↓
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)               │
│  ┌───────────────────────────────────────────────────┐  │
│  │         JWT Auth Middleware                       │  │
│  │         (Better Auth)                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Rate Limiter (Redis)                      │  │
│  │         10 requests/minute                        │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Chat Endpoint                             │  │
│  │         POST /api/chat                            │  │
│  └───────────────────┬─────────────────────────────────┘
│                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │      OpenAI Agent (GPT-4 Turbo)                  │   │
│  │   - Natural language understanding               │   │
│  │   - Function calling orchestration               │   │
│  │   - Greeting detection                           │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │         MCP Server (Embedded)                    │   │
│  │   5 Tools:                                       │   │
│  │   - add_task                                     │   │
│  │   - list_tasks                                   │   │
│  │   - complete_task                                │   │
│  │   - delete_task                                  │   │
│  │   - update_task                                  │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │     SQLModel ORM (Async)                         │   │
│  └──────────────────┬───────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
    ┌───────▼────────┐ ┌─────▼──────┐
    │   PostgreSQL   │ │   Redis    │
    │   (Neon)       │ │            │
    └────────────────┘ └────────────┘
```

### Request Flow (Stateless)

```
1. User sends message: "Add a task to buy groceries"
2. Frontend → Backend: POST /api/chat with JWT token
3. Auth middleware validates JWT, extracts user_id
4. Rate limiter checks request quota
5. Chat endpoint loads conversation history from DB
6. Agent receives message + history
7. Agent calls OpenAI GPT-4 with function calling
8. GPT-4 decides to call add_task tool
9. MCP tool executes: INSERT INTO tasks ...
10. Tool returns confirmation: "✅ Task added: Buy groceries"
11. Agent formats final response
12. Backend saves user + assistant messages to DB
13. Backend returns response to frontend
14. Frontend displays message in chat

NO in-memory state • ALL data in database • Fully stateless
```

---

## 📁 Project Structure

```
todo-chatbot/
├── backend/                    # Python FastAPI backend
│   ├── agents/                 # AI agent implementations
│   │   ├── base_agent.py      # Generic reusable agent ⭐
│   │   └── todo_agent.py      # Todo-specific agent
│   ├── api/                    # API routes
│   │   └── chat.py            # Chat endpoint
│   ├── auth/                   # Authentication
│   │   └── better_auth.py     # JWT middleware
│   ├── db/                     # Database
│   │   ├── models.py          # SQLModel schemas
│   │   └── session.py         # Async session management
│   ├── mcp/                    # MCP Server
│   │   ├── server.py          # MCP server implementation
│   │   └── tools.py           # 5 MCP tools
│   ├── tests/                  # Test suite
│   │   ├── test_mcp_tools.py  # MCP tool tests (25 tests)
│   │   ├── test_agent.py      # Agent tests
│   │   ├── test_chat.py       # API tests
│   │   └── test_user_stories.py # E2E user story tests
│   ├── alembic/                # Database migrations
│   ├── config.py               # Pydantic settings
│   ├── main.py                 # FastAPI app
│   └── requirements.txt
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── App.css            # Styles
│   │   └── main.tsx           # Entry point
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/                       # Documentation
│   ├── QUICK_START_REUSABLE_AGENT.md
│   ├── AGENT_REUSABILITY_GUIDE.md
│   └── AGENT_USAGE_EXAMPLES.md
├── scripts/
│   └── package_agent.sh       # Agent packaging script
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 💻 Installation

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlmodel, openai; print('✅ All dependencies installed')"
```

### Frontend Setup

```bash
cd frontend
npm install

# Verify installation
npm run build
```

---

## ⚙️ Configuration

### Environment Variables

Create `backend/.env`:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/tododb

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxx

# Better Auth (JWT)
BETTER_AUTH_SECRET=your-32-character-secret-key-here
BETTER_AUTH_ISSUER=https://auth.yourdomain.com

# Redis (Rate Limiting)
REDIS_URL=redis://localhost:6379/0

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_PER_MINUTE=10
```

### Database Setup (Neon PostgreSQL)

```bash
# 1. Create Neon project at https://neon.tech
# 2. Get connection string
# 3. Run migrations
cd backend
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: tasks, conversations, messages
```

### Redis Setup

```bash
# Option 1: Local Redis
brew install redis  # macOS
sudo apt install redis  # Ubuntu
redis-server

# Option 2: Redis Cloud
# Sign up at https://redis.com/try-free/
# Use connection string in REDIS_URL
```

---

## 🔧 Development

### Start Backend

```bash
cd backend
source venv/bin/activate

# Development mode (auto-reload)
uvicorn backend.main:app --reload --port 8000

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Start Frontend

```bash
cd frontend
npm run dev

# Build for production
npm run build
npm run preview
```

### Code Quality

```bash
# Backend
cd backend
ruff check .        # Linting
mypy .              # Type checking
pytest              # Run tests

# Frontend
cd frontend
npm run lint        # ESLint
npm run format      # Prettier
```

---

## 🧪 Testing

### Run All Tests

```bash
cd backend
pytest -v

# With coverage
pytest --cov=. --cov-report=html

# Specific test files
pytest tests/test_mcp_tools.py -v
pytest tests/test_user_stories.py -v
```

### Test Results

```
✅ 25 MCP tool tests (CRUD operations, validation, security)
✅ 10 Agent tests (greeting detection, tool execution)
✅ 15 API tests (authentication, endpoints, error handling)
✅ 6 User story tests (E2E scenarios)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
56 tests passed
```

---

## 🚀 Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

### Quick Deploy (Docker)

```bash
# Coming soon: docker-compose up
```

### Deploy to Cloud

- **Backend**: Railway, Fly.io, AWS ECS
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: Neon (Serverless PostgreSQL)
- **Redis**: Upstash, Redis Cloud

---

## 📚 API Documentation

### Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### POST /api/chat
```json
// Request
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123  // Optional
}

// Response
{
  "conversation_id": 123,
  "message": "✅ Task added: Buy groceries",
  "user_message": "Add a task to buy groceries"
}
```

#### GET /health
```json
{
  "status": "healthy",
  "service": "todo-ai-chatbot",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 🔄 Reusable Agent

The agent is **100% reusable** for any domain!

**Use in other projects:**

```python
from backend.agents.base_agent import BaseAgent

# Define your tools (e-commerce, calendar, support, etc.)
agent = BaseAgent(
    api_key="sk-...",
    tools=[...],  # Your tools
    tool_handlers={...}  # Your handlers
)

# Use it!
result = await agent.process_message(
    user_message="Your message",
    user_id="user_123",
    conversation_history=[],
    db=db
)
```

**See full guide**: [docs/AGENT_REUSABILITY_GUIDE.md](docs/AGENT_REUSABILITY_GUIDE.md)

**Examples**: E-commerce, Calendar, Support, Healthcare agents in [docs/AGENT_USAGE_EXAMPLES.md](docs/AGENT_USAGE_EXAMPLES.md)

---

## 🐛 Troubleshooting

### Common Issues

**Database connection error:**
```bash
# Verify connection string
psql $DATABASE_URL -c "SELECT 1"

# Check migrations
alembic current
alembic upgrade head
```

**OpenAI API errors:**
```bash
# Verify API key
python -c "from openai import OpenAI; OpenAI(api_key='sk-...').models.list()"

# Check quota
# https://platform.openai.com/account/usage
```

**Redis connection error:**
```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# Test connection
redis-cli -u $REDIS_URL ping
```

**Frontend CORS errors:**
```python
# backend/config.py
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# Restart backend after changes
```

---

## 📖 Documentation

- [Quick Start Guide](docs/QUICK_START_REUSABLE_AGENT.md)
- [Agent Reusability Guide](docs/AGENT_REUSABILITY_GUIDE.md)
- [Usage Examples](docs/AGENT_USAGE_EXAMPLES.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) *(coming soon)*
- [API Reference](http://localhost:8000/docs)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 and function calling
- FastAPI for the amazing Python web framework
- Neon for serverless PostgreSQL
- Better Auth for JWT authentication

---

## 📧 Support

- GitHub Issues: https://github.com/yourusername/todo-chatbot/issues
- Documentation: [docs/](docs/)
- Email: your.email@example.com

---

**Built with ❤️ using OpenAI GPT-4, FastAPI, and React**

🎉 **Your agent is production-ready and reusable for ANY domain!**
