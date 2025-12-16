<!--
Sync Impact Report:
- Version change: [template] → 1.0.0
- Initial ratification
- Principles defined: 6 core principles established
- Added sections: Technology Stack, Security Requirements, Development Workflow
- Templates requiring updates: ✅ All templates aligned with initial constitution
- Follow-up TODOs: None
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. MCP-First Architecture

All AI agent interactions with the application MUST go through Model Context Protocol (MCP) tools. Direct database access or API calls from the AI agent are prohibited.

**Rules:**
- Every task operation (create, read, update, delete) exposed as an MCP tool
- MCP tools are the single source of truth for AI capabilities
- Tools MUST be stateless and self-contained
- Tool parameters and returns follow strict schemas (documented in specs)
- No business logic in the AI agent layer—agents orchestrate tools only

**Rationale:** MCP provides a standardized, testable interface that decouples AI logic from application logic, enabling independent evolution and testing of both layers.

### II. Stateless Server Design (NON-NEGOTIABLE)

The FastAPI server MUST NOT hold any conversation or session state in memory. All state MUST be persisted to the database immediately.

**Rules:**
- Each API request is independent and self-contained
- Conversation history loaded from database on every request
- No in-memory caches for user sessions or conversation state
- Server restarts MUST NOT lose any user data or conversation context
- Horizontally scalable by design—any server instance handles any request

**Rationale:** Stateless architecture ensures scalability, resilience, and enables zero-downtime deployments. This is critical for production readiness.

### III. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written and approved before implementation begins. Red-Green-Refactor cycle strictly enforced.

**Rules:**
- Write tests → Get user approval → Confirm tests fail (Red) → Implement until pass (Green) → Refactor if needed
- MCP tools require unit tests with mocked database
- AI agent behavior requires integration tests with real tool calls
- API endpoints require request/response contract tests
- Database models require migration and constraint tests
- No PR merges without passing test suite

**Rationale:** AI agents can produce unpredictable behavior; comprehensive tests ensure reliability and catch regressions early. TDD enforces clear contracts before implementation.

### IV. Security First

User data, authentication, and secrets MUST be handled with production-grade security from day one.

**Rules:**
- All API endpoints require valid user authentication (Better Auth)
- Database queries MUST filter by `user_id` to prevent cross-user data leaks
- Environment variables for all secrets (database URLs, API keys)—never hardcoded
- Input validation on all API endpoints and MCP tool parameters
- SQL injection prevention via SQLModel ORM (no raw queries)
- HTTPS required for production deployments
- Secrets stored in `.env` and excluded from version control

**Rationale:** Security vulnerabilities in todo apps can expose sensitive user data. Building security in from the start is cheaper than retrofitting later.

### V. Database as Source of Truth

All application state—tasks, conversations, messages—MUST be persisted to Neon PostgreSQL. The database schema is the canonical data model.

**Rules:**
- No ephemeral state (in-memory structures, local files) for user data
- Database migrations tracked and versioned (Alembic or SQLModel migrations)
- All writes go through SQLModel ORM models
- Foreign key constraints enforced at database level
- Timestamps (`created_at`, `updated_at`) required on all mutable tables
- Soft deletes preferred over hard deletes where audit trail needed

**Rationale:** Database-driven architecture ensures data durability, enables multi-instance deployments, and provides audit trails for debugging.

### VI. API Contract Clarity

REST API endpoints MUST have explicit contracts with documented request/response schemas and error handling.

**Rules:**
- FastAPI Pydantic models for all request/response schemas
- HTTP status codes follow REST conventions (200/201/400/404/500)
- Error responses include machine-readable error codes and human-readable messages
- API versioning strategy defined before breaking changes (e.g., `/api/v1/`)
- OpenAPI documentation auto-generated and accessible at `/docs`
- Idempotency for state-changing operations where applicable

**Rationale:** Clear contracts enable frontend/backend teams to work independently, simplify testing, and reduce integration bugs.

## Technology Stack

**Mandated Technologies:**
- **Frontend:** OpenAI ChatKit (hosted with domain allowlist configuration)
- **Backend:** Python 3.11+ with FastAPI
- **AI Framework:** OpenAI Agents SDK
- **MCP Server:** Official MCP SDK (Python)
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** Better Auth
- **Testing:** pytest with pytest-asyncio

**Technology Constraints:**
- Python type hints required for all function signatures
- Async/await for all I/O operations (database, external APIs)
- Dependency injection for database sessions and MCP client
- Environment-based configuration (development, staging, production)

## Security Requirements

**Authentication & Authorization:**
- Better Auth integration for user identity
- JWT tokens for stateless authentication (if session-based, stored in database)
- Row-level security via `user_id` filters in all database queries
- No API endpoints accessible without valid authentication (except health checks)

**Data Protection:**
- Database connection strings stored in environment variables
- OpenAI API keys in environment variables, rotated regularly
- CORS configuration restricted to allowed frontend origins
- Rate limiting on chat endpoint to prevent abuse (e.g., 10 requests/minute per user)

**Compliance:**
- User data deletion capability (GDPR right to erasure)
- Audit logs for sensitive operations (account deletion, bulk task operations)

## Development Workflow

**Feature Development:**
1. **Specify:** Create feature spec in `specs/<feature-name>/spec.md`
2. **Plan:** Architecture and design decisions in `specs/<feature-name>/plan.md`
3. **Tasks:** Breakdown in `specs/<feature-name>/tasks.md` with acceptance criteria
4. **Red-Green-Refactor:** Write tests → Implement → Refactor
5. **Review:** Code review with constitution compliance check
6. **Deploy:** Merge to main triggers deployment pipeline

**Testing Gates:**
- All tests pass locally before pushing
- CI/CD pipeline runs full test suite on PRs
- Integration tests run against staging database before production deploy

**Code Review Requirements:**
- At least one approval required for merges
- Constitution compliance verified (principles I-VI)
- Test coverage maintained or improved
- No secrets or credentials in code

## Governance

**Constitution Authority:**
- This constitution supersedes all other development practices
- Non-negotiable principles (II, III) cannot be bypassed without formal amendment
- Amendments require rationale, impact analysis, and approval process

**Amendment Process:**
1. Propose change with rationale and impact assessment
2. Update constitution with semantic version bump (MAJOR for principle removal/redefinition, MINOR for additions, PATCH for clarifications)
3. Update dependent templates (spec, plan, tasks) to reflect changes
4. Document in `history/adr/` as an ADR
5. Communicate changes to all contributors

**Compliance Verification:**
- All PRs reviewed against constitution principles
- Automated checks where possible (linting, security scans, test coverage)
- Quarterly constitution review to ensure relevance

**Runtime Guidance:**
- See `CLAUDE.md` for AI assistant-specific development guidance
- See `README.md` for quickstart and setup instructions

**Version**: 1.0.0 | **Ratified**: 2025-12-14 | **Last Amended**: 2025-12-14
