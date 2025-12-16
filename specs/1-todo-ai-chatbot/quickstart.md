# Quickstart Guide: Todo AI Chatbot

**Feature**: 1-todo-ai-chatbot
**Last Updated**: 2025-12-14
**Target Audience**: Developers setting up local development or production deployment

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher (for frontend)
- **PostgreSQL**: Access to Neon Serverless PostgreSQL (or local PostgreSQL for development)
- **Redis**: For rate limiting (Upstash, Redis Cloud, or local)
- **OpenAI API Key**: For AI agent functionality
- **Better Auth**: Configured instance with JWT tokens

---

## Quick Start (Local Development)

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/your-org/todo-chatbot.git
cd todo-chatbot

# Checkout feature branch
git checkout 1-todo-ai-chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `backend/.env`:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@ep-example-123.us-east-2.aws.neon.tech/tododb?sslmode=require

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Better Auth
BETTER_AUTH_SECRET=your-jwt-secret-key-min-32-chars
BETTER_AUTH_ISSUER=https://auth.yourdomain.com

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379/0  # Or Upstash URL for production

# App Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173  # Frontend URLs
```

### 4. Database Setup

```bash
# Run migrations to create tables
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: tasks, conversations, messages
```

### 5. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Server runs at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 6. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_BETTER_AUTH_URL=https://auth.yourdomain.com
REACT_APP_CHATKIT_DOMAIN_KEY=  # Leave empty for localhost (no domain allowlist needed)
```

### 7. Start Frontend

```bash
npm run dev

# Frontend runs at: http://localhost:3000 (or http://localhost:5173 for Vite)
```

---

## Testing the Application

### Manual Testing

1. **Obtain JWT Token**: Authenticate via Better Auth frontend to get JWT token
2. **Open Frontend**: Navigate to http://localhost:3000
3. **Test Natural Language Commands**:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"
   - "Delete task 2"
   - "Change task 3 to 'Buy groceries and fruits'"

### API Testing with cURL

```bash
# Get JWT token (replace with your Better Auth endpoint)
TOKEN=$(curl -X POST https://auth.yourdomain.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "✅ I've added 'Buy groceries' to your tasks.",
#   "tool_calls": [...]
# }
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_mcp_tools.py -v

# Run integration tests only
pytest tests/integration/ -v
```

---

## Production Deployment

### Backend Deployment (Render / Railway / Fly.io)

#### Option 1: Render

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
4. Add environment variables (DATABASE_URL, OPENAI_API_KEY, etc.)
5. Deploy

#### Option 2: Fly.io

```bash
cd backend

# Install fly CLI
curl -L https://fly.io/install.sh | sh

# Login and create app
fly auth login
fly launch

# Set secrets
fly secrets set DATABASE_URL="postgresql+asyncpg://..." \
  OPENAI_API_KEY="sk-..." \
  BETTER_AUTH_SECRET="..." \
  REDIS_URL="redis://..."

# Deploy
fly deploy
```

### Frontend Deployment (Vercel / Netlify)

#### Option 1: Vercel

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - REACT_APP_BACKEND_URL
# - REACT_APP_BETTER_AUTH_URL
# - REACT_APP_CHATKIT_DOMAIN_KEY (get from OpenAI after domain allowlist approval)
```

#### Option 2: Netlify

```bash
cd frontend

# Install Netlify CLI
npm install -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod

# Set environment variables in Netlify dashboard
```

### OpenAI ChatKit Domain Allowlist Setup

1. Deploy frontend to get production URL (e.g., https://todo-chatbot.vercel.app)
2. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Click "Add domain"
4. Enter your frontend URL (without trailing slash)
5. Copy the domain key provided
6. Set `REACT_APP_CHATKIT_DOMAIN_KEY` in Vercel/Netlify environment variables
7. Redeploy frontend

---

## Database Migrations

### Create New Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to tasks"

# Edit generated migration in alembic/versions/
# Verify upgrade() and downgrade() functions

# Apply migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Check current revision
alembic current
```

---

## Troubleshooting

### Database Connection Issues

**Problem**: `asyncpg.exceptions.InvalidCatalogNameError: database "tododb" does not exist`

**Solution**:
```bash
# Create database in Neon dashboard or via SQL
psql $DATABASE_URL -c "CREATE DATABASE tododb;"
```

### OpenAI API Rate Limits

**Problem**: `openai.error.RateLimitError: Rate limit reached`

**Solution**:
- Check OpenAI dashboard for quota limits
- Upgrade to higher tier if needed
- Implement exponential backoff in code (already included)

### Redis Connection Issues

**Problem**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
```bash
# For local development, start Redis:
redis-server

# For production, verify REDIS_URL is correct
# Test connection:
redis-cli -u $REDIS_URL ping
# Should return: PONG
```

### Better Auth Token Validation Fails

**Problem**: `401 Unauthorized: Invalid token`

**Solution**:
- Verify BETTER_AUTH_SECRET matches your Better Auth instance
- Check token expiration (Better Auth tokens expire after 1 hour by default)
- Ensure `sub` claim in JWT contains user_id

### CORS Errors in Browser

**Problem**: `Access to fetch at 'http://localhost:8000/api/chat' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:
- Add frontend URL to CORS_ORIGINS in backend .env
- Restart backend server after changing .env
- For production, set specific domains (not `*`)

---

## Next Steps

1. Read `specs/1-todo-ai-chatbot/plan.md` for architecture details
2. Review `specs/1-todo-ai-chatbot/tasks.md` for implementation tasks
3. Explore API docs at http://localhost:8000/docs
4. Join development: see CONTRIBUTING.md

---

## Support

- **Documentation**: See `specs/1-todo-ai-chatbot/` directory
- **API Reference**: http://localhost:8000/docs (OpenAPI/Swagger)
- **Issues**: GitHub Issues
- **Community**: Discord/Slack (if applicable)
