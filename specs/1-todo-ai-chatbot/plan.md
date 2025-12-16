# Implementation Plan: Todo AI Chatbot

**Branch**: `1-todo-ai-chatbot` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-todo-ai-chatbot/spec.md`

## Summary

Build a production-ready AI-powered chatbot for managing todo tasks through natural language using a stateless MCP (Model Context Protocol) architecture. The system integrates OpenAI Agents SDK for natural language understanding with MCP tools for task operations, persisting all state to Neon PostgreSQL database. Frontend uses OpenAI ChatKit with Better Auth for authentication. Architecture enforces 100% statelessness at the server layer with conversation history loaded from database on every request.

**Technical Approach**: FastAPI backend with embedded MCP server, OpenAI Agents SDK for intent recognition and tool invocation, SQL Model ORM for async database operations, and JWT-based authentication. Rate limiting via Redis ensures production-grade resilience.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, OpenAI Agents SDK, Official MCP SDK (Python), SQLModel 0.0.14+, asyncpg, Alembic
**Storage**: Neon Serverless PostgreSQL (async connection pooling)
**Testing**: pytest with pytest-asyncio for async test support
**Target Platform**: Linux server (Docker-compatible) with Python 3.11+ runtime
**Project Type**: Web application (separate frontend/backend)
**Performance Goals**: <5s task creation, <3s task retrieval, <100ms p95 DB query latency, 10+ concurrent users
**Constraints**: 100% stateless server (no in-memory session storage), 10 req/min rate limit per user, OpenAI API token limits
**Scale/Scope**: MVP supporting 100-1000 users, ~10-100 tasks per user, ~50 messages per conversation

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: MCP-First Architecture ✅ **PASS**

- **Requirement**: All AI agent interactions through MCP tools
- **Implementation**: 5 MCP tools defined (add_task, list_tasks, complete_task, delete_task, update_task)
- **Verification**: Agent never accesses database directly; all operations via MCP protocol
- **Contract**: See `contracts/mcp-tools.json`

### Principle II: Stateless Server Design (NON-NEGOTIABLE) ✅ **PASS**

- **Requirement**: No in-memory conversation or session state
- **Implementation**:
  - Conversation history loaded from PostgreSQL on every request
  - Database session injected via FastAPI `Depends()`
  - Redis for distributed rate limiting (state external to app)
  - Server restart test in User Story 6 validates statelessness
- **Verification**: Multi-instance deployment possible without state sync

### Principle III: Test-First Development (NON-NEGOTIABLE) ✅ **PASS**

- **Requirement**: Write tests → Approve → Red → Green → Refactor
- **Implementation**:
  - Unit tests for MCP tools with mocked database
  - Integration tests for agent + MCP tool chains
  - Contract tests for API endpoints (request/response schemas)
  - Database model tests with SQLModel validation
- **Test Framework**: pytest + pytest-asyncio
- **Coverage Target**: >80% for critical paths (MCP tools, agent logic, API endpoints)

### Principle IV: Security First ✅ **PASS**

- **Requirement**: Production-grade security from day one
- **Implementation**:
  - Better Auth JWT token validation on all API endpoints
  - Row-level security: all database queries filtered by `user_id`
  - Environment variables for secrets (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
  - Input validation via Pydantic models
  - SQL injection prevention via SQLModel ORM (no raw queries)
  - CORS restricted to specific frontend origins
  - Rate limiting (10 req/min per user via Redis)
  - HTTPS enforced in production
- **Verification**: Security testing with multiple user accounts (cross-user access attempts must fail)

### Principle V: Database as Source of Truth ✅ **PASS**

- **Requirement**: All state persisted to PostgreSQL
- **Implementation**:
  - 3 tables: tasks, conversations, messages
  - Alembic migrations for schema versioning
  - Foreign key constraints enforced at DB level
  - `created_at` and `updated_at` timestamps on all mutable tables
  - Hard deletes for MVP (no soft delete)
- **Verification**: Server restart preserves all data (User Story 6)

### Principle VI: API Contract Clarity ✅ **PASS**

- **Requirement**: Explicit request/response schemas and error handling
- **Implementation**:
  - FastAPI Pydantic models for all API schemas
  - OpenAPI 3.1 spec auto-generated at `/docs`
  - HTTP status codes follow REST conventions (200/201/400/401/429/500)
  - Error responses include error_code + message + details
  - MCP tools return consistent JSON (see `contracts/mcp-tools.json`)
- **Contract Files**:
  - `contracts/chat-api.yaml` (OpenAPI 3.1)
  - `contracts/mcp-tools.json` (JSON Schema)

**Constitution Check Result**: ✅ **ALL GATES PASSED** - Ready for implementation

---

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-ai-chatbot/
├── spec.md                    # Feature specification (user stories, requirements)
├── plan.md                    # This file (implementation plan)
├── research.md                # Technology integration decisions (Phase 0)
├── data-model.md              # Database schema and SQLModel models (Phase 1)
├── quickstart.md              # Setup and deployment guide (Phase 1)
├── contracts/                 # API and MCP tool contracts (Phase 1)
│   ├── chat-api.yaml          # OpenAPI 3.1 spec for REST API
│   └── mcp-tools.json         # JSON Schema for MCP tools
├── checklists/                # Quality validation checklists
│   └── requirements.md        # Spec quality checklist (passed)
└── tasks.md                   # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment configuration (Pydantic Settings)
├── api/
│   └── chat.py                # Chat endpoint (/api/chat)
├── agents/
│   └── todo_agent.py          # OpenAI Agents SDK configuration
├── mcp/
│   ├── server.py              # Embedded MCP server setup
│   └── tools.py               # MCP tool implementations (5 tools)
├── db/
│   ├── models.py              # SQLModel models (Task, Conversation, Message)
│   └── session.py             # Async database session management
├── auth/
│   └── better_auth.py         # JWT token validation middleware
├── alembic/
│   ├── env.py                 # Alembic configuration
│   └── versions/              # Database migration scripts
│       └── 001_initial_schema.py
├── tests/
│   ├── conftest.py            # Pytest fixtures (test database, mocked services)
│   ├── unit/
│   │   ├── test_mcp_tools.py  # Unit tests for MCP tools (mocked DB)
│   │   ├── test_models.py     # SQLModel validation tests
│   │   └── test_auth.py       # Auth middleware tests
│   ├── integration/
│   │   ├── test_agent.py      # Agent + MCP tool integration tests
│   │   └── test_chat_api.py   # End-to-end API tests
│   └── contract/
│       └── test_api_contracts.py  # OpenAPI contract validation
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md                  # Backend-specific setup docs

frontend/
├── src/
│   ├── App.jsx                # Main React component with ChatKit
│   ├── components/
│   │   └── ChatInterface.jsx  # ChatKit wrapper
│   └── services/
│       └── api.js             # API client (axios)
├── public/
│   └── index.html
├── package.json               # NPM dependencies
├── .env.example               # Frontend environment variables
├── .env.local                 # Local development config (git-ignored)
└── README.md                  # Frontend-specific setup docs

.github/
└── workflows/
    ├── backend-ci.yml         # Backend CI/CD pipeline
    └── frontend-ci.yml        # Frontend CI/CD pipeline
```

**Structure Decision**: Web application with separate frontend/backend to support independent scaling and deployment. Backend uses Clean Architecture principles (API → Agents → MCP → Database layers) with clear separation of concerns. Frontend is thin client (presentational layer only).

---

## Complexity Tracking

> **Note**: No constitution violations. This section documents intentional complexity choices that align with project requirements.

| Design Choice | Justification | Alternatives Considered |
|---------------|---------------|------------------------|
| Embedded MCP Server (vs standalone) | Stateless requirement means MCP server has no state to separate; embedding eliminates network overhead and simplifies deployment | Standalone MCP server rejected: adds complexity without benefit for stateless architecture |
| OpenAI Agents SDK + MCP integration | Required by spec; MCP provides standardization, Agents SDK handles NLP | Custom NLP rejected: reinventing wheel; Direct DB access rejected: violates MCP-First principle |
| Redis for rate limiting | Distributed rate limiting required for multi-instance deployments | In-memory rate limiting rejected: violates stateless principle |
| Better Auth (external service) | JWT-based auth aligns with stateless principle; battle-tested solution | Custom auth rejected: security-critical, don't roll your own |

---

## Phase 0: Research & Technology Integration

**Status**: ✅ Completed

See [`research.md`](./research.md) for detailed analysis. Key decisions:

1. **OpenAI Agents SDK + MCP Integration**: Python wrapper functions call MCP tools; agent sees clean function signatures
2. **Embedded MCP Server**: Same process as FastAPI (no network overhead)
3. **Database Session Management**: FastAPI dependency injection with async SQLAlchemy sessions
4. **Conversation History Truncation**: Load last 50 messages (fits token budget)
5. **Better Auth Integration**: JWT middleware validates tokens, extracts user_id
6. **Rate Limiting**: slowapi + Redis for distributed rate limiting
7. **ChatKit Configuration**: Hosted with domain allowlist on Vercel/Netlify

---

## Phase 1: Design & Contracts

**Status**: ✅ Completed

### Data Model

See [`data-model.md`](./data-model.md) for full schema. Summary:

**Entities**:
- **Task**: id, user_id, title, description, completed, created_at, updated_at
- **Conversation**: id, user_id, created_at, updated_at
- **Message**: id, conversation_id, user_id, role, content, created_at

**Relationships**:
- User (external from Better Auth) → 1:N → Task
- User → 1:N → Conversation → 1:N → Message

**Indexes**:
- `tasks(user_id, completed)` - For filtering pending/completed tasks
- `messages(conversation_id, created_at)` - For loading conversation history

**Migrations**: Alembic with auto-generated migrations from SQLModel changes

### API Contracts

**Chat API** (`contracts/chat-api.yaml`):
- **POST /api/chat**: Send message, get AI response
  - Request: `{conversation_id?, message}`
  - Response: `{conversation_id, response, tool_calls[]}`
  - Auth: Bearer token (JWT from Better Auth)
  - Rate limit: 10 req/min per user

**MCP Tools** (`contracts/mcp-tools.json`):
1. `add_task(user_id, title, description?)` → `{task_id, status, title}`
2. `list_tasks(user_id, status)` → `Task[]`
3. `complete_task(user_id, task_id)` → `{task_id, status, title}`
4. `delete_task(user_id, task_id)` → `{task_id, status, title}`
5. `update_task(user_id, task_id, title?, description?)` → `{task_id, status, title}`

All tools validate user ownership and return structured JSON with error codes.

### Quickstart Guide

See [`quickstart.md`](./quickstart.md) for setup instructions. Covers:
- Local development setup (Python venv, npm install)
- Environment variable configuration
- Database migration commands
- Testing procedures
- Production deployment (Render, Vercel, Fly.io)
- Troubleshooting common issues

---

## Phase 2: Implementation Roadmap

**Note**: This plan document stops at Phase 1 (design). Implementation tasks will be generated by `/sp.tasks` command.

### High-Level Implementation Steps (for reference)

1. **Database & Models** (Priority: P1)
   - Create SQLModel models in `backend/db/models.py`
   - Setup async database session in `backend/db/session.py`
   - Create Alembic migration `001_initial_schema.py`
   - Test: Unit tests for model validation

2. **MCP Server & Tools** (Priority: P1)
   - Implement 5 MCP tools in `backend/mcp/tools.py`
   - Setup embedded MCP server in `backend/mcp/server.py`
   - Test: Unit tests with mocked database

3. **Agent Logic** (Priority: P1)
   - Configure OpenAI Agents SDK in `backend/agents/todo_agent.py`
   - Integrate MCP tools with agent
   - Test: Integration tests for agent + MCP tools

4. **Chat API** (Priority: P1)
   - Implement `/api/chat` endpoint in `backend/api/chat.py`
   - Add Better Auth middleware in `backend/auth/better_auth.py`
   - Add rate limiting with slowapi
   - Test: Contract tests for API endpoints

5. **Frontend ChatKit** (Priority: P2)
   - Setup React app with ChatKit component
   - Configure Better Auth integration
   - Test: Manual E2E testing

6. **README & Documentation** (Priority: P3)
   - Comprehensive README with setup instructions
   - API documentation (OpenAPI at `/docs`)
   - Deployment guides

### Critical Path

```
Database Models → MCP Tools → Agent Integration → Chat API → Frontend
     (Day 1)         (Day 2)        (Day 3)         (Day 4)     (Day 5)
```

**Assumptions**:
- Neon PostgreSQL database provisioned before Day 1
- OpenAI API key available
- Better Auth instance configured
- Redis instance available (Upstash or local)

---

## Architectural Decision Records (ADR) Candidates

📋 **Potential ADRs** (require user consent via `/sp.adr` command):

1. **ADR-001: Embedded MCP Server vs Standalone MCP Server**
   - Decision: Embed MCP server in FastAPI process
   - Rationale: Stateless architecture + no network overhead
   - Alternatives: Standalone server, MCP over HTTP

2. **ADR-002: Conversation History Truncation Strategy**
   - Decision: Load last 50 messages per conversation
   - Rationale: Fits token budget, recent messages most relevant
   - Alternatives: Load all (unbounded), summarize old messages

3. **ADR-003: Hard Delete vs Soft Delete for Tasks**
   - Decision: Hard delete for MVP
   - Rationale: Simplicity, no audit trail requirement for MVP
   - Alternatives: Soft delete with `deleted_at` column

**Action**: Run `/sp.adr <title>` if user wants to document these decisions formally.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API rate limits | Medium | High | Implement exponential backoff, user-friendly error messages, queue requests if needed |
| MCP SDK + Agents SDK incompatibility | Low | High | Test integration early (Day 2), have fallback plan (direct function calls) |
| Neon cold start latency | Medium | Medium | Use connection pooling, keep database warm with health checks |
| ChatKit domain allowlist delays | Low | Medium | Start with localhost testing, apply for domain early |
| Better Auth token expiration mid-conversation | High | Low | Implement token refresh in frontend, handle 401 gracefully |

---

## Performance Targets & Monitoring

### Performance Goals (from Spec)

- **Task Creation**: <5s (user sends message → confirmation received)
- **Task Retrieval**: <3s (user asks for tasks → list displayed)
- **Task Completion**: <3s (user marks complete → confirmation received)
- **Database Queries**: <100ms p95 latency
- **Concurrent Users**: 10+ without data corruption

### Monitoring Strategy

**Metrics to Track**:
- API response time (p50, p95, p99)
- Database query latency
- OpenAI API call duration
- Rate limit hit rate
- Error rate by endpoint
- Active conversation count

**Tools**:
- FastAPI built-in metrics (Prometheus integration)
- Database query logging (SQLAlchemy echo=True for dev)
- Structured logging (JSON format for production)
- Sentry for error tracking (optional)

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Backend (localhost:8000)
│   └── SQLite or local PostgreSQL
├── Frontend (localhost:3000)
├── Redis (localhost:6379)
└── Better Auth (external service)
```

### Production Environment

```
                    ┌─────────────────┐
                    │   Vercel/Netlify│
                    │   (Frontend)    │
                    └────────┬────────┘
                             │ HTTPS
                             ▼
                    ┌─────────────────┐
                    │  Render/Fly.io  │
                    │  (FastAPI)      │
                    └────┬────────┬───┘
                         │        │
           ┌─────────────┘        └──────────────┐
           ▼                                     ▼
  ┌─────────────────┐                  ┌─────────────────┐
  │ Neon PostgreSQL │                  │  Redis (Upstash)│
  │  (Database)     │                  │  (Rate Limit)   │
  └─────────────────┘                  └─────────────────┘
           ▲
           │
  ┌────────┴────────┐
  │  Better Auth    │
  │  (External)     │
  └─────────────────┘
```

**Infrastructure Requirements**:
- Backend: 512MB RAM, 1 vCPU (sufficient for 100-1000 users)
- Database: Neon Serverless (auto-scales)
- Redis: Upstash Serverless (for rate limiting)
- Frontend: Serverless static hosting

---

## Security Checklist

- [ ] **Environment Variables**: All secrets in `.env` (never hardcoded)
- [ ] **JWT Validation**: Every API endpoint validates Bearer token
- [ ] **Row-Level Security**: All queries filter by `user_id`
- [ ] **Input Validation**: Pydantic models validate all inputs
- [ ] **SQL Injection**: SQLModel ORM prevents raw queries
- [ ] **CORS**: Restricted to specific frontend domains (not `*`)
- [ ] **Rate Limiting**: 10 req/min per user enforced
- [ ] **HTTPS**: Enforced in production (Vercel/Netlify/Render auto-provide)
- [ ] **Secrets Management**: `.env` in `.gitignore`, `.env.example` documented
- [ ] **Error Messages**: No stack traces exposed to users
- [ ] **Audit Trail**: `user_id` logged in all database writes

---

## Next Steps

1. **Run `/sp.tasks`**: Generate actionable task breakdown from this plan
2. **Review Tasks**: Prioritize tasks and assign to development sprints
3. **Setup Infrastructure**: Provision Neon PostgreSQL, Redis, Better Auth
4. **Begin Implementation**: Follow Task list with TDD approach (Red-Green-Refactor)
5. **Continuous Testing**: Run tests after each task completion
6. **Deploy to Staging**: Test with real users before production
7. **Production Deployment**: Follow deployment guide in quickstart.md

---

**Plan Status**: ✅ Phase 0 & Phase 1 Complete | Ready for `/sp.tasks` command

**Planning Artifacts**:
- ✅ research.md (7 research questions answered)
- ✅ data-model.md (3 tables, relationships, migrations)
- ✅ contracts/chat-api.yaml (OpenAPI 3.1 spec)
- ✅ contracts/mcp-tools.json (5 MCP tools with schemas)
- ✅ quickstart.md (setup and deployment guide)
- ⏭️ tasks.md (awaiting `/sp.tasks` command)

**Constitution Compliance**: ✅ All 6 principles validated (see Constitution Check section)
