# Research: Todo AI Chatbot Technology Integration

**Feature**: 1-todo-ai-chatbot
**Date**: 2025-12-14
**Purpose**: Research and validate technology choices for production-ready MCP-based AI chatbot

## Research Questions

### Q1: How to integrate OpenAI Agents SDK with MCP Server?

**Decision**: Use OpenAI Agents SDK's tool calling API to invoke MCP tools via function definitions

**Rationale**:
- OpenAI Agents SDK expects tools to be defined as Python functions or callable objects
- MCP Server exposes tools via the MCP protocol (JSON-RPC)
- Integration approach: Create Python wrapper functions that call MCP server tools internally
- Agent sees clean function signatures; wrapper handles MCP protocol communication

**Implementation Strategy**:
```python
# Agent layer: Define tools as Python functions
async def add_task_tool(user_id: str, title: str, description: str | None = None):
    """Wrapper that calls MCP server add_task tool"""
    result = await mcp_client.call_tool("add_task", {
        "user_id": user_id,
        "title": title,
        "description": description
    })
    return result

# Register with OpenAI Agents SDK
agent = Agent(
    name="TodoAssistant",
    tools=[add_task_tool, list_tasks_tool, complete_task_tool, ...]
)
```

**Alternatives Considered**:
1. **Direct database access from agent** - Rejected: Violates Constitution Principle I (MCP-First)
2. **Agent calls FastAPI endpoints** - Rejected: Creates circular dependency (API → Agent → API)
3. **Skip MCP, use direct function calls** - Rejected: Loses MCP standardization and tooling benefits

**References**:
- OpenAI Agents SDK: Function calling documentation
- MCP SDK: Python client examples

---

### Q2: MCP Server Deployment Model - Embedded vs Standalone?

**Decision**: **Embedded MCP server** within FastAPI application (same process)

**Rationale**:
- Stateless requirement means MCP server has no persistent state anyway
- Embedding eliminates network overhead between FastAPI and MCP server
- Simpler deployment (single service vs two services)
- Easier local development and testing
- MCP tools still exposed via standard protocol for potential future external access

**Implementation Strategy**:
```python
# backend/main.py
from fastapi import FastAPI
from mcp.server import MCPServer
from mcp import tools as mcp_tools

app = FastAPI()
mcp_server = MCPServer()

# Register MCP tools
mcp_server.add_tool(mcp_tools.add_task)
mcp_server.add_tool(mcp_tools.list_tasks)
# ... other tools

# FastAPI endpoint uses MCP tools via internal calls
@app.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    # Agent invokes MCP tools directly (same process)
    result = await run_agent(user_id, request.message, mcp_server)
    return result
```

**Alternatives Considered**:
1. **Standalone MCP server (separate process/service)** - Rejected: Adds deployment complexity, network latency, no state to separate
2. **MCP over stdio** - Rejected: Designed for CLI tools, not web servers
3. **MCP over HTTP** - Possible future enhancement for external tool access

**Trade-offs**:
- **Pro**: Simpler, faster, easier to deploy
- **Con**: Cannot scale MCP server independently (but it's stateless, so not needed)

---

### Q3: Database Session Management in Stateless Architecture

**Decision**: Use FastAPI dependency injection for database sessions with automatic cleanup

**Rationale**:
- FastAPI's `Depends()` ensures sessions are created per-request and closed automatically
- Async SQLAlchemy sessions for non-blocking I/O
- Connection pooling handled by SQLAlchemy engine
- Each MCP tool receives session as parameter (no global state)

**Implementation Strategy**:
```python
# backend/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# backend/mcp/tools.py
async def add_task(user_id: str, title: str, description: str | None, db: AsyncSession):
    """MCP tool receives database session as parameter"""
    task = Task(user_id=user_id, title=title, description=description)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"task_id": task.id, "status": "created", "title": task.title}

# backend/api/chat.py
@app.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Pass db session to agent/tools
    result = await run_agent(user_id, request.message, db)
    return result
```

**Alternatives Considered**:
1. **Global database connection** - Rejected: Not thread-safe, violates stateless principle
2. **Create new connection per tool call** - Rejected: Inefficient, connection pool exists for this
3. **Pass connection string to tools** - Rejected: Tools would manage their own sessions (error-prone)

---

### Q4: Conversation History Truncation Strategy

**Decision**: Load last 50 messages from database, sorted by created_at DESC

**Rationale**:
- OpenAI models have token limits (4K-128K depending on model)
- 50 messages ≈ 5,000-10,000 tokens (safe for most models with room for system prompt + tools)
- Recent messages most relevant for conversation context
- Database query is efficient with proper indexing on (conversation_id, created_at)

**Implementation Strategy**:
```python
# backend/api/chat.py
async def load_conversation_history(conversation_id: int, db: AsyncSession, limit: int = 50):
    """Load most recent N messages for conversation"""
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return list(reversed(messages))  # Return chronological order
```

**Alternatives Considered**:
1. **Load all messages** - Rejected: Unbounded growth, will exceed token limits
2. **Summarize old messages** - Possible future enhancement, adds complexity
3. **Sliding window (last N minutes)** - Rejected: Time-based less predictable than message count

**Token Budget Breakdown** (for GPT-4):
- System prompt: ~500 tokens
- Tool definitions (5 tools): ~1,000 tokens
- Conversation history (50 messages): ~5,000-10,000 tokens
- Response generation: ~1,000 tokens
- **Total**: ~7,500-12,500 tokens (well under 128K limit)

---

### Q5: Better Auth Integration Approach

**Decision**: Middleware-based authentication with user_id extracted from JWT token

**Rationale**:
- Better Auth provides JWT tokens after authentication
- FastAPI middleware validates token and injects user_id into request context
- All endpoints automatically protected
- user_id extracted once per request and passed to agent/MCP tools

**Implementation Strategy**:
```python
# backend/auth/better_auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Extract and validate user_id from Better Auth JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")  # Better Auth uses 'sub' claim for user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# backend/api/chat.py
@app.post("/api/chat")  # user_id from token, not URL
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Chat endpoint with automatic auth"""
    result = await run_agent(user_id, request.message, db)
    return result
```

**Alternatives Considered**:
1. **user_id in URL path** (/api/{user_id}/chat) - Rejected: User could spoof another user's ID
2. **Session-based auth** - Rejected: Violates stateless principle (sessions stored server-side)
3. **API key per user** - Rejected: Better Auth already provides JWT, redundant

**Security Note**: Original spec had `/api/{user_id}/chat` but this is a security vulnerability. User_id MUST come from authenticated JWT token, not user input.

---

### Q6: Rate Limiting Implementation

**Decision**: Use `slowapi` (FastAPI rate limiting library) with Redis backend

**Rationale**:
- slowapi integrates seamlessly with FastAPI
- Redis provides distributed rate limit counters (works across multiple server instances)
- Supports per-user rate limiting (10 req/min per user_id)
- Stateless at application level (rate limit state in Redis, not memory)

**Implementation Strategy**:
```python
# backend/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Use user_id as rate limit key (not IP)
def get_user_id_from_request(request: Request):
    # Extract from JWT token in Authorization header
    return request.state.user_id  # Set by auth middleware

limiter = Limiter(key_func=get_user_id_from_request, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# backend/api/chat.py
@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(...):
    ...
```

**Alternatives Considered**:
1. **In-memory rate limiting** - Rejected: Violates stateless principle, doesn't work with multiple instances
2. **Database-based rate limiting** - Rejected: Too slow, adds DB load
3. **No rate limiting** - Rejected: Violates spec requirement FR-024

**Infrastructure Requirement**: Redis instance needed for production deployment

---

### Q7: Frontend ChatKit Configuration

**Decision**: Use hosted ChatKit with domain allowlist configuration on Vercel/Netlify

**Rationale**:
- OpenAI ChatKit is a pre-built React component for chat interfaces
- Hosted option requires domain allowlist setup in OpenAI platform
- Vercel/Netlify provide free hosting with HTTPS and custom domains
- No backend rendering needed (static site with API calls)

**Implementation Strategy**:
```javascript
// frontend/src/App.jsx
import { ChatKit } from '@openai/chatkit';

function App() {
  return (
    <ChatKit
      apiEndpoint={process.env.REACT_APP_BACKEND_URL + '/api/chat'}
      authToken={getAuthToken()} // From Better Auth
      placeholder="Ask me to manage your tasks..."
      domainKey={process.env.REACT_APP_CHATKIT_DOMAIN_KEY}
    />
  );
}
```

**Setup Steps**:
1. Deploy frontend to Vercel (get production URL: https://todo-chatbot.vercel.app)
2. Add domain to OpenAI allowlist: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Get domain key from OpenAI
4. Set REACT_APP_CHATKIT_DOMAIN_KEY in Vercel environment variables

**Alternatives Considered**:
1. **Custom chat UI** - Rejected: Reinventing wheel, ChatKit is production-ready
2. **Self-hosted ChatKit** - Possible, but hosted is simpler for MVP

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | 0.109+ | Async support, OpenAPI docs, dependency injection |
| AI Agent | OpenAI Agents SDK | Latest | Required by spec, handles tool calling |
| MCP Server | Official MCP SDK (Python) | Latest | Required by spec, standard protocol |
| ORM | SQLModel | 0.0.14+ | Type-safe, async support, Pydantic integration |
| Database | Neon PostgreSQL | Serverless | Required by spec, auto-scaling |
| Auth | Better Auth | Latest | Required by spec, JWT-based |
| Frontend | OpenAI ChatKit (React) | Latest | Required by spec, pre-built chat UI |
| Rate Limiting | slowapi + Redis | Latest | Distributed rate limiting |
| Testing | pytest + pytest-asyncio | Latest | Async test support |
| Type Checking | mypy | Latest | Static type validation |
| Linting | ruff | Latest | Fast Python linter |

## Dependencies

### Python (backend/requirements.txt)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0  # PostgreSQL async driver
alembic==1.13.0  # Database migrations
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4
openai-agents-sdk  # (version TBD - check official release)
mcp-sdk-python  # (version TBD - check official release)
slowapi==0.1.9
redis==5.0.1
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0  # For testing API
```

### JavaScript (frontend/package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@openai/chatkit": "latest",
    "axios": "^1.6.0"
  }
}
```

## Infrastructure Requirements

1. **Neon PostgreSQL**:
   - Serverless PostgreSQL database
   - Connection string in environment variable: `DATABASE_URL`
   - Auto-scaling, no manual provisioning

2. **Redis** (for rate limiting):
   - Managed Redis instance (Upstash, Redis Cloud, or local for dev)
   - Connection string: `REDIS_URL`

3. **OpenAI API**:
   - API key: `OPENAI_API_KEY`
   - Sufficient quota for agent requests

4. **Better Auth**:
   - Configuration: `BETTER_AUTH_SECRET`, `BETTER_AUTH_ISSUER`

5. **Deployment**:
   - Backend: Render, Railway, or fly.io (Python + PostgreSQL + Redis support)
   - Frontend: Vercel or Netlify (static hosting)

## Open Questions / Risks

1. **OpenAI Agents SDK + MCP SDK compatibility**: Both are relatively new. Need to verify they work together as planned. **Mitigation**: Test integration early in implementation.

2. **MCP SDK Python maturity**: Official SDK may have limited documentation. **Mitigation**: Review SDK source code, join MCP community for support.

3. **ChatKit domain allowlist delays**: OpenAI approval may take time. **Mitigation**: Start with localhost testing, apply for domain allowlist early.

4. **Neon PostgreSQL cold starts**: Serverless databases may have cold start latency. **Mitigation**: Use connection pooling, consider keeping database warm with health checks.

## Next Steps

1. Create `data-model.md` with SQLModel schemas
2. Generate API contracts in `contracts/` directory
3. Create `quickstart.md` with setup instructions
4. Update agent context files
5. Proceed to `/sp.tasks` for actionable task breakdown
