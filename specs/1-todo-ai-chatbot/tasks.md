# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/1-todo-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included per Constitution Principle III (Test-First Development - NON-NEGOTIABLE)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/` and `frontend/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure: backend/{main.py,config.py,api/,agents/,mcp/,db/,auth/,alembic/,tests/}
- [ ] T002 Create frontend project structure: frontend/{src/,public/,package.json}
- [ ] T003 [P] Initialize Python project with requirements.txt (FastAPI, SQLModel, asyncpg, alembic, openai-agents-sdk, mcp-sdk-python, slowapi, redis, pytest, pytest-asyncio, httpx)
- [ ] T004 [P] Initialize Node.js project with package.json (react, @openai/chatkit, axios)
- [ ] T005 [P] Create .env.example files for backend and frontend with all required environment variables
- [ ] T006 [P] Create .gitignore for Python (venv, __pycache__, .env, *.pyc) and Node.js (node_modules, .env.local, dist, build)
- [ ] T007 [P] Configure pytest in backend/pytest.ini with async support and test paths
- [ ] T008 [P] Setup mypy for type checking in backend/mypy.ini
- [ ] T009 [P] Setup ruff for linting in backend/pyproject.toml

**Checkpoint**: Project skeleton ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [ ] T010 Create SQLModel base models: Task, Conversation, Message in backend/db/models.py per data-model.md
- [ ] T011 Create async database session management in backend/db/session.py with get_db() dependency
- [ ] T012 Configure Alembic in backend/alembic/env.py for async SQLModel migrations
- [ ] T013 Create initial migration 001_initial_schema.py with tasks, conversations, messages tables and indexes

### Configuration & Environment

- [ ] T014 [P] Create backend/config.py with Pydantic Settings for DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, REDIS_URL, CORS_ORIGINS
- [ ] T015 [P] Setup structured logging configuration in backend/config.py with JSON format for production

### Authentication Foundation

- [ ] T016 Implement Better Auth JWT validation middleware in backend/auth/better_auth.py with get_current_user() dependency

### MCP Server Foundation

- [ ] T017 Setup embedded MCP server initialization in backend/mcp/server.py
- [ ] T018 [P] Implement add_task MCP tool in backend/mcp/tools.py per contracts/mcp-tools.json
- [ ] T019 [P] Implement list_tasks MCP tool in backend/mcp/tools.py per contracts/mcp-tools.json
- [ ] T020 [P] Implement complete_task MCP tool in backend/mcp/tools.py per contracts/mcp-tools.json
- [ ] T021 [P] Implement delete_task MCP tool in backend/mcp/tools.py per contracts/mcp-tools.json
- [ ] T022 [P] Implement update_task MCP tool in backend/mcp/tools.py per contracts/mcp-tools.json

### API Foundation

- [ ] T023 Create FastAPI app instance in backend/main.py with CORS middleware configuration
- [ ] T024 Add rate limiting with slowapi in backend/main.py (10 req/min per user_id)
- [ ] T025 Create Pydantic request/response models for chat endpoint in backend/api/chat.py (ChatRequest, ChatResponse, ToolCall, ErrorResponse)

### Test Infrastructure

- [ ] T026 [P] Create pytest conftest.py with async test database fixture and test client in backend/tests/conftest.py
- [ ] T027 [P] Create test utilities for mocking OpenAI Agents SDK and MCP server in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language commands like "Add a task to buy groceries"

**Independent Test**: Type "Add a task to call mom" in chat interface, verify task appears in database with correct user_id and title

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T028 [P] [US1] Unit test for add_task MCP tool with mocked database in backend/tests/unit/test_mcp_tools.py
- [ ] T029 [P] [US1] Unit test for Task model validation (title max 500 chars, description max 2000 chars) in backend/tests/unit/test_models.py
- [ ] T030 [P] [US1] Contract test for POST /api/chat with add task intent in backend/tests/contract/test_chat_api.py
- [ ] T031 [US1] Integration test for full agent → add_task → database flow in backend/tests/integration/test_agent_add_task.py

### Implementation for User Story 1

- [ ] T032 [US1] Configure OpenAI Agents SDK in backend/agents/todo_agent.py with add_task tool wrapper
- [ ] T033 [US1] Implement chat endpoint POST /api/chat in backend/api/chat.py with conversation creation logic (FR-016)
- [ ] T034 [US1] Implement conversation history loading (last 50 messages) in backend/api/chat.py (FR-005)
- [ ] T035 [US1] Implement message persistence (user and assistant) in backend/api/chat.py (FR-004)
- [ ] T036 [US1] Add error handling for add_task failures (task not found, validation errors) in backend/api/chat.py
- [ ] T037 [US1] Add logging for add_task operations with user_id and task_id in backend/api/chat.py

**Checkpoint**: User Story 1 complete - users can add tasks via natural language, conversation state persists to database

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Users can view their tasks by typing "Show me all my tasks" or "What's pending?"

**Independent Test**: Add 3 tasks to database, type "Show me all my tasks", verify chatbot lists all 3 correctly

### Tests for User Story 2 (TDD - Write First)

- [ ] T038 [P] [US2] Unit test for list_tasks MCP tool with status filters (all, pending, completed) in backend/tests/unit/test_mcp_tools.py
- [ ] T039 [P] [US2] Contract test for POST /api/chat with list tasks intent in backend/tests/contract/test_chat_api.py
- [ ] T040 [US2] Integration test for agent → list_tasks → formatting response in backend/tests/integration/test_agent_list_tasks.py

### Implementation for User Story 2

- [ ] T041 [US2] Add list_tasks tool wrapper to OpenAI Agents SDK configuration in backend/agents/todo_agent.py
- [ ] T042 [US2] Implement list_tasks intent recognition and response formatting in backend/agents/todo_agent.py
- [ ] T043 [US2] Add error handling for empty task lists (friendly message: "You don't have any tasks yet") in backend/agents/todo_agent.py
- [ ] T044 [US2] Add logging for list_tasks operations with user_id and filter status in backend/api/chat.py

**Checkpoint**: User Story 2 complete - users can view tasks filtered by status (all/pending/completed)

---

## Phase 5: User Story 6 - Resume Conversation After Server Restart (Priority: P1)

**Goal**: Conversation history persists across server restarts, validating stateless architecture

**Independent Test**: Start conversation, add tasks, restart backend server, send new message, verify chatbot remembers context

### Tests for User Story 6 (TDD - Write First)

- [ ] T045 [P] [US6] Unit test for conversation history loading from database in backend/tests/unit/test_chat_api.py
- [ ] T046 [P] [US6] Unit test for message persistence (user and assistant) in backend/tests/unit/test_chat_api.py
- [ ] T047 [US6] Integration test: create conversation → restart server (clear app state) → resume conversation in backend/tests/integration/test_stateless_architecture.py

### Implementation for User Story 6

- [ ] T048 [US6] Verify conversation history loading uses database (no in-memory caching) in backend/api/chat.py
- [ ] T049 [US6] Verify message persistence happens immediately after each chat request in backend/api/chat.py
- [ ] T050 [US6] Add integration test that simulates server restart and validates conversation continuity in backend/tests/integration/test_stateless_architecture.py

**Checkpoint**: User Story 6 complete - stateless architecture validated, conversations persist across restarts

---

## Phase 6: User Story 3 - Complete Task via Natural Language (Priority: P2)

**Goal**: Users can mark tasks complete by typing "Mark task 3 as complete" or "I finished buying groceries"

**Independent Test**: Create a task, type "Mark task [ID] as done", verify completed=true in database

### Tests for User Story 3 (TDD - Write First)

- [ ] T051 [P] [US3] Unit test for complete_task MCP tool with task ID validation in backend/tests/unit/test_mcp_tools.py
- [ ] T052 [P] [US3] Unit test for complete_task error cases (task not found, already completed) in backend/tests/unit/test_mcp_tools.py
- [ ] T053 [P] [US3] Contract test for POST /api/chat with complete task intent in backend/tests/contract/test_chat_api.py
- [ ] T054 [US3] Integration test for agent → complete_task by ID or title match in backend/tests/integration/test_agent_complete_task.py

### Implementation for User Story 3

- [ ] T055 [US3] Add complete_task tool wrapper to OpenAI Agents SDK configuration in backend/agents/todo_agent.py
- [ ] T056 [US3] Implement complete_task intent recognition (by ID or title match) in backend/agents/todo_agent.py
- [ ] T057 [US3] Add error handling for task not found and already completed cases in backend/agents/todo_agent.py
- [ ] T058 [US3] Add confirmation responses ("Task 3 'Call mom' is now complete") in backend/agents/todo_agent.py
- [ ] T059 [US3] Add logging for complete_task operations with task_id and user_id in backend/api/chat.py

**Checkpoint**: User Story 3 complete - users can complete tasks via natural language with error handling

---

## Phase 7: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can delete tasks by typing "Delete task 5" or "Remove the meeting task"

**Independent Test**: Create a task, type "Delete task [ID]", verify task removed from database

### Tests for User Story 4 (TDD - Write First)

- [ ] T060 [P] [US4] Unit test for delete_task MCP tool with ownership validation in backend/tests/unit/test_mcp_tools.py
- [ ] T061 [P] [US4] Unit test for delete_task error cases (task not found) in backend/tests/unit/test_mcp_tools.py
- [ ] T062 [P] [US4] Contract test for POST /api/chat with delete task intent in backend/tests/contract/test_chat_api.py
- [ ] T063 [US4] Integration test for agent → delete_task by ID or title match in backend/tests/integration/test_agent_delete_task.py

### Implementation for User Story 4

- [ ] T064 [US4] Add delete_task tool wrapper to OpenAI Agents SDK configuration in backend/agents/todo_agent.py
- [ ] T065 [US4] Implement delete_task intent recognition (by ID or title match) in backend/agents/todo_agent.py
- [ ] T066 [US4] Add clarification prompts when task is ambiguous ("Which task would you like to delete?") in backend/agents/todo_agent.py
- [ ] T067 [US4] Add confirmation responses ("I've deleted 'Old meeting' from your tasks") in backend/agents/todo_agent.py
- [ ] T068 [US4] Add logging for delete_task operations with task_id and user_id in backend/api/chat.py

**Checkpoint**: User Story 4 complete - users can delete tasks via natural language with clarifications

---

## Phase 8: User Story 5 - Update Task via Natural Language (Priority: P3)

**Goal**: Users can update tasks by typing "Change task 1 to 'Buy groceries and fruits'"

**Independent Test**: Create a task, type "Change task [ID] title to [new title]", verify database updated

### Tests for User Story 5 (TDD - Write First)

- [ ] T069 [P] [US5] Unit test for update_task MCP tool (title and description updates) in backend/tests/unit/test_mcp_tools.py
- [ ] T070 [P] [US5] Unit test for update_task validation (at least one of title/description required) in backend/tests/unit/test_mcp_tools.py
- [ ] T071 [P] [US5] Contract test for POST /api/chat with update task intent in backend/tests/contract/test_chat_api.py
- [ ] T072 [US5] Integration test for agent → update_task by ID in backend/tests/integration/test_agent_update_task.py

### Implementation for User Story 5

- [ ] T073 [US5] Add update_task tool wrapper to OpenAI Agents SDK configuration in backend/agents/todo_agent.py
- [ ] T074 [US5] Implement update_task intent recognition (title and/or description) in backend/agents/todo_agent.py
- [ ] T075 [US5] Add error handling for task not found and validation errors in backend/agents/todo_agent.py
- [ ] T076 [US5] Add confirmation responses ("I've updated task 1 to 'Buy groceries and fruits'") in backend/agents/todo_agent.py
- [ ] T077 [US5] Add logging for update_task operations with task_id and fields updated in backend/api/chat.py

**Checkpoint**: User Story 5 complete - users can update tasks via natural language

---

## Phase 9: Frontend ChatKit Integration

**Purpose**: Web interface for chat interaction

- [ ] T078 [P] Create React App component with OpenAI ChatKit integration in frontend/src/App.jsx
- [ ] T079 [P] Configure ChatKit with backend API endpoint and Better Auth token in frontend/src/App.jsx
- [ ] T080 [P] Add environment variable configuration for REACT_APP_BACKEND_URL, REACT_APP_BETTER_AUTH_URL, REACT_APP_CHATKIT_DOMAIN_KEY in frontend/.env.example
- [ ] T081 [P] Create API client service with axios for chat endpoint in frontend/src/services/api.js
- [ ] T082 [P] Add error handling for API failures (network errors, 401 unauthorized, 429 rate limit) in frontend/src/App.jsx
- [ ] T083 [P] Setup ChatKit domain allowlist on OpenAI platform and obtain domain key (manual step documented in quickstart.md)

**Checkpoint**: Frontend ready for E2E testing with backend

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, documentation, and final validation

### Database & Migrations

- [ ] T084 [P] Run Alembic upgrade head to create database tables on Neon PostgreSQL
- [ ] T085 [P] Create database indexes for performance: tasks(user_id, completed), messages(conversation_id, created_at)
- [ ] T086 [P] Add PostgreSQL triggers for auto-updating updated_at timestamps on tasks and conversations tables

### Security Hardening

- [ ] T087 [P] Verify all database queries filter by user_id (row-level security audit) in backend/mcp/tools.py
- [ ] T088 [P] Verify JWT token validation on all API endpoints in backend/auth/better_auth.py
- [ ] T089 [P] Verify CORS configuration restricts origins to specific frontend domains in backend/main.py
- [ ] T090 [P] Verify no secrets in code (audit for hardcoded API keys, passwords) across all files

### Error Handling & Logging

- [ ] T091 [P] Add global exception handler for FastAPI to return user-friendly errors (no stack traces) in backend/main.py
- [ ] T092 [P] Add structured logging for all MCP tool calls with user_id, tool name, and status in backend/mcp/tools.py
- [ ] T093 [P] Add OpenAI API error handling with exponential backoff retry in backend/agents/todo_agent.py

### Testing & Validation

- [ ] T094 Run full test suite: pytest backend/tests/ with coverage report (target >80%)
- [ ] T095 [P] Add E2E test: Full user flow through frontend → backend → database in backend/tests/integration/test_e2e_chat_flow.py
- [ ] T096 [P] Run security test: Attempt cross-user data access with different user_ids in backend/tests/integration/test_security.py
- [ ] T097 Run quickstart.md validation: Follow local setup steps and verify all commands work

### Documentation

- [ ] T098 [P] Create comprehensive README.md in repository root with setup, deployment, and architecture overview
- [ ] T099 [P] Create backend/README.md with API documentation, environment variables, and development guide
- [ ] T100 [P] Create frontend/README.md with setup, configuration, and ChatKit domain allowlist instructions
- [ ] T101 [P] Verify OpenAPI documentation is accessible at http://localhost:8000/docs after server start

### Deployment Preparation

- [ ] T102 [P] Create Dockerfile for backend with Python 3.11+ and all dependencies
- [ ] T103 [P] Create docker-compose.yml for local development with backend, PostgreSQL, and Redis
- [ ] T104 [P] Document production deployment steps (Render/Fly.io for backend, Vercel/Netlify for frontend) in README.md
- [ ] T105 [P] Create CI/CD workflow .github/workflows/backend-ci.yml for running tests on PR

**Checkpoint**: Production-ready system with full documentation and deployment guides

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Frontend (Phase 9)**: Can start after Phase 2, parallelize with user story work
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Add Task**: No dependencies on other stories (can start after Foundational)
- **User Story 2 (P1) - View Tasks**: No dependencies on other stories (can start after Foundational, but typically done after US1 for testing convenience)
- **User Story 6 (P1) - Stateless**: No dependencies on other stories (validates architecture, can be done anytime after Foundational)
- **User Story 3 (P2) - Complete Task**: No dependencies on other stories (requires tasks to exist, but test can create them)
- **User Story 4 (P2) - Delete Task**: No dependencies on other stories (requires tasks to exist, but test can create them)
- **User Story 5 (P3) - Update Task**: No dependencies on other stories (requires tasks to exist, but test can create them)

### Within Each User Story (TDD Workflow)

1. **Write Tests FIRST** (all tests marked [P] within a story can run in parallel)
2. **Verify Tests FAIL** (Red phase)
3. **Implement Features** (some tasks sequential due to dependencies)
4. **Verify Tests PASS** (Green phase)
5. **Refactor** (if needed)
6. **Story Complete** → Move to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: Tasks T003, T004, T005, T006, T007, T008, T009 can run in parallel
- **Foundational (Phase 2)**:
  - Database tasks (T010-T013) are sequential
  - Config tasks (T014, T015) can run in parallel with database
  - Auth task (T016) independent, can run in parallel
  - MCP tools (T018-T022) can run in parallel (different tools, same file - needs coordination)
  - API tasks (T023-T025) can run in parallel with MCP tools
  - Test infrastructure (T026-T027) can run in parallel with other tasks
- **User Story Tests**: All tests within a story marked [P] can run in parallel
- **User Stories**: Once Foundational completes, all 6 user stories can start in parallel by different developers
- **Frontend (Phase 9)**: All tasks (T078-T083) can run in parallel (different files)
- **Polish (Phase 10)**: Most tasks marked [P] can run in parallel (different concerns)

---

## Parallel Example: Foundational Phase (Phase 2)

```bash
# These tasks can run simultaneously by different developers:

Task T014: "Create backend/config.py with Pydantic Settings"
Task T016: "Implement JWT validation in backend/auth/better_auth.py"
Task T018: "Implement add_task MCP tool in backend/mcp/tools.py"
Task T019: "Implement list_tasks MCP tool in backend/mcp/tools.py"
Task T026: "Create pytest conftest.py in backend/tests/conftest.py"

# While these must run sequentially:
T010 → T011 → T012 → T013 (database setup chain)
```

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T028: "Unit test for add_task MCP tool in backend/tests/unit/test_mcp_tools.py"
Task T029: "Unit test for Task model validation in backend/tests/unit/test_models.py"
Task T030: "Contract test for POST /api/chat in backend/tests/contract/test_chat_api.py"

# After tests fail, implementation tasks have some parallelism:
Task T036: "Add error handling in backend/api/chat.py" (can run in parallel with logging)
Task T037: "Add logging in backend/api/chat.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 6 Only - P1)

1. Complete **Phase 1: Setup** (Tasks T001-T009)
2. Complete **Phase 2: Foundational** (Tasks T010-T027) - **CRITICAL BLOCKER**
3. Complete **Phase 3: User Story 1 - Add Task** (Tasks T028-T037)
4. Complete **Phase 4: User Story 2 - View Tasks** (Tasks T038-T044)
5. Complete **Phase 5: User Story 6 - Stateless** (Tasks T045-T050)
6. **STOP and VALIDATE**: Test all 3 user stories independently
7. Deploy/demo MVP with core functionality

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Ready for user story work
2. **MVP** (US1 + US2 + US6) → Test independently → Deploy (core value!)
3. **Enhancement 1** (US3 - Complete Task) → Test independently → Deploy
4. **Enhancement 2** (US4 - Delete Task) → Test independently → Deploy
5. **Enhancement 3** (US5 - Update Task) → Test independently → Deploy
6. **Frontend** (Phase 9) → Integrate with backend → Deploy
7. **Production Ready** (Phase 10) → Final polish → Production deployment

Each increment adds value without breaking previous stories.

### Parallel Team Strategy

With 3 developers after Foundational phase:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Add Task) + US6 (Stateless)
   - Developer B: User Story 2 (View Tasks)
   - Developer C: User Story 3 (Complete Task)
3. **Stories complete independently** and integrate seamlessly

---

## Task Summary

**Total Tasks**: 105 tasks
- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 18 tasks (BLOCKING)
- **Phase 3 (US1 - Add Task, P1)**: 10 tasks (4 tests + 6 implementation)
- **Phase 4 (US2 - View Tasks, P1)**: 7 tasks (3 tests + 4 implementation)
- **Phase 5 (US6 - Stateless, P1)**: 6 tasks (3 tests + 3 implementation)
- **Phase 6 (US3 - Complete Task, P2)**: 9 tasks (4 tests + 5 implementation)
- **Phase 7 (US4 - Delete Task, P2)**: 9 tasks (4 tests + 5 implementation)
- **Phase 8 (US5 - Update Task, P3)**: 9 tasks (4 tests + 5 implementation)
- **Phase 9 (Frontend)**: 6 tasks
- **Phase 10 (Polish)**: 22 tasks

**Parallel Opportunities**: ~60% of tasks can run in parallel within their phases
**Independent Test Criteria**: Each user story has explicit independent test instructions
**MVP Scope**: Phases 1-5 (27 foundational + 23 MVP tasks = 50 tasks for core functionality)

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label (US1, US2, etc.) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD CRITICAL**: Verify tests FAIL before implementing (Red phase)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution Principle III enforced: Test-First Development
- All 6 user stories map to functional requirements (FR-001 through FR-031)
