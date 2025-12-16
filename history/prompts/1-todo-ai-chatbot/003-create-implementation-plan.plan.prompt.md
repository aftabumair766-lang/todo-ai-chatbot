---
id: 003
title: Create Todo AI Chatbot implementation plan
stage: plan
date: 2025-12-14
surface: agent
model: claude-sonnet-4-5
feature: 1-todo-ai-chatbot
branch: 1-todo-ai-chatbot
user: Umair Aftab
command: /sp.plan
labels: ["plan", "architecture", "mcp-integration", "database-design", "api-contracts", "production-ready"]
links:
  spec: specs/1-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-todo-ai-chatbot/plan.md
  - specs/1-todo-ai-chatbot/research.md
  - specs/1-todo-ai-chatbot/data-model.md
  - specs/1-todo-ai-chatbot/quickstart.md
  - specs/1-todo-ai-chatbot/contracts/chat-api.yaml
  - specs/1-todo-ai-chatbot/contracts/mcp-tools.json
tests:
  - None (planning artifacts)
---

## Prompt

User invoked `/sp.plan` with no additional arguments (following `/sp.specify` completion).

**Context**: Specification complete with 31 functional requirements, 6 user stories (P1-P3 prioritized), 12 success criteria. Constitution v1.0.0 defines 6 core principles (MCP-First, Stateless Server, Test-First, Security First, Database as Source of Truth, API Contract Clarity).

**Requirement**: Create production-grade implementation plan following SDD workflow with Phase 0 (Research) and Phase 1 (Design & Contracts).

## Response snapshot

**Implementation Plan Created**: `specs/1-todo-ai-chatbot/plan.md`

### Phase 0: Research (Completed)

**File**: `research.md` (350+ lines)

**7 Research Questions Answered**:
1. **OpenAI Agents SDK + MCP Integration**: Use Python wrapper functions calling MCP tools; agent sees clean function signatures
2. **MCP Deployment Model**: Embedded MCP server within FastAPI (same process) - eliminates network overhead
3. **Database Session Management**: FastAPI dependency injection with async SQLAlchemy sessions
4. **Conversation History Truncation**: Load last 50 messages (fits token budget: ~7.5K-12.5K tokens)
5. **Better Auth Integration**: Middleware validates JWT tokens, extracts user_id from 'sub' claim
6. **Rate Limiting**: slowapi + Redis for distributed rate limiting (10 req/min per user)
7. **ChatKit Configuration**: Hosted with domain allowlist on Vercel/Netlify

**Technology Stack Locked**:
- FastAPI 0.109+, SQLModel 0.0.14+, asyncpg, Alembic, OpenAI Agents SDK, MCP SDK Python
- Neon PostgreSQL, Redis, Better Auth (JWT), OpenAI ChatKit (React)
- pytest + pytest-asyncio for testing

### Phase 1: Design & Contracts (Completed)

**Data Model** (`data-model.md`, 450+ lines):
- **3 Entities**: Task, Conversation, Message
- **Relationships**: User (external) → 1:N → Task/Conversation, Conversation → 1:N → Message
- **Indexes**: `tasks(user_id, completed)`, `messages(conversation_id, created_at)`
- **Migrations**: Alembic with SQLModel auto-generation
- **Validation Rules**: Pydantic validators for title (max 500), description (max 2000)

**API Contracts**:
1. **Chat API** (`contracts/chat-api.yaml`, OpenAPI 3.1, 280+ lines):
   - POST /api/chat: `{conversation_id?, message}` → `{conversation_id, response, tool_calls[]}`
   - Authentication: Bearer JWT (Better Auth)
   - Rate limiting: 10 req/min per user
   - Error codes: INVALID_REQUEST, UNAUTHORIZED, RATE_LIMIT_EXCEEDED, INTERNAL_ERROR

2. **MCP Tools** (`contracts/mcp-tools.json`, JSON Schema, 250+ lines):
   - 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
   - All tools validate user_id ownership
   - Structured input/output schemas with error codes
   - Stateless design enforced

**Quickstart Guide** (`quickstart.md`, 300+ lines):
- Local development setup (Python venv, npm install, environment variables)
- Database migration commands (Alembic)
- Testing procedures (pytest, cURL examples)
- Production deployment (Render, Vercel, Fly.io, Netlify)
- ChatKit domain allowlist configuration
- Troubleshooting (database, OpenAI, Redis, CORS issues)

**Implementation Plan** (`plan.md`, 550+ lines):
- Summary & technical context
- Constitution Check: ✅ All 6 principles validated
- Project structure (backend/, frontend/, specs/, tests/)
- Complexity tracking (4 design choices justified)
- Phase 0 & Phase 1 artifacts summary
- Phase 2 roadmap (5 implementation steps: Database → MCP → Agent → API → Frontend)
- ADR candidates (3 significant decisions identified)
- Risk mitigation (5 risks with probability/impact/mitigation)
- Performance targets & monitoring strategy
- Deployment architecture diagrams
- Security checklist (11 items)

### Constitution Compliance Validation

**Principle I (MCP-First)**: ✅ PASS
- 5 MCP tools defined with strict contracts
- Agent never accesses database directly
- Contracts in `mcp-tools.json`

**Principle II (Stateless Server)**: ✅ PASS
- Conversation history loaded from PostgreSQL on every request
- No in-memory session storage
- Redis for distributed rate limiting (external state)
- Server restart test (User Story 6)

**Principle III (Test-First)**: ✅ PASS
- Unit tests for MCP tools (mocked DB)
- Integration tests for agent + MCP chains
- Contract tests for API endpoints
- pytest + pytest-asyncio framework

**Principle IV (Security First)**: ✅ PASS
- Better Auth JWT validation on all endpoints
- Row-level security (all queries filter by user_id)
- Environment variables for secrets
- Input validation via Pydantic
- Rate limiting (10 req/min per user)

**Principle V (Database as Source of Truth)**: ✅ PASS
- 3 tables with foreign key constraints
- Alembic migrations
- Timestamps on all mutable tables
- Hard deletes for MVP

**Principle VI (API Contract Clarity)**: ✅ PASS
- FastAPI Pydantic models
- OpenAPI 3.1 spec at `/docs`
- Consistent error codes
- MCP tools return structured JSON

### Project Structure Established

```
backend/
  ├── main.py, config.py
  ├── api/chat.py
  ├── agents/todo_agent.py
  ├── mcp/server.py, tools.py
  ├── db/models.py, session.py
  ├── auth/better_auth.py
  ├── alembic/versions/
  └── tests/unit/, integration/, contract/

frontend/
  ├── src/App.jsx, components/, services/
  └── package.json, .env.example

specs/1-todo-ai-chatbot/
  ├── spec.md, plan.md, research.md, data-model.md, quickstart.md
  └── contracts/chat-api.yaml, mcp-tools.json
```

### Critical Path Identified

```
Day 1: Database Models + Migrations
Day 2: MCP Server + 5 Tools (unit tested)
Day 3: Agent Integration (OpenAI Agents SDK + MCP wrappers)
Day 4: Chat API + Auth + Rate Limiting
Day 5: Frontend ChatKit + E2E Testing
```

## Outcome

- ✅ Impact: Comprehensive production-grade implementation plan with complete architecture, contracts, and deployment strategy
- 🧪 Tests: Test strategy defined (unit, integration, contract tests) - implementation pending
- 📁 Files: Created plan.md (550 lines), research.md (350 lines), data-model.md (450 lines), quickstart.md (300 lines), chat-api.yaml (280 lines), mcp-tools.json (250 lines)
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown from implementation plan
- 🧠 Reflection: Plan successfully integrates all mandatory technologies (OpenAI Agents SDK, MCP SDK, FastAPI, SQLModel, Better Auth, ChatKit) while enforcing stateless architecture and security-first principles. All 6 Constitution principles validated. ADR candidates identified for embedded MCP server decision, conversation truncation strategy, and hard delete approach.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning phases completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - **PASS** (6/6 principles validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): During `/sp.tasks`, break down "Agent Integration" into granular subtasks (OpenAI SDK setup, MCP wrapper functions, tool registration, error handling) to ensure TDD approach is followed
