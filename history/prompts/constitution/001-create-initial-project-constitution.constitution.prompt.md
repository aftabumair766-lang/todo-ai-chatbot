---
id: 001
title: Create initial project constitution
stage: constitution
date: 2025-12-14
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: Umair Aftab
command: /sp.constitution
labels: ["constitution", "setup", "principles", "mcp-architecture", "stateless-design"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (documentation artifact)
---

## Prompt

$ARGUMENTS

(User invoked /sp.constitution with no additional arguments)

## Response snapshot

Created Todo AI Chatbot Constitution v1.0.0 with 6 core principles:

**Core Principles Established:**
1. **MCP-First Architecture** - All AI interactions through Model Context Protocol tools
2. **Stateless Server Design (NON-NEGOTIABLE)** - No in-memory state; database is source of truth
3. **Test-First Development (NON-NEGOTIABLE)** - Red-Green-Refactor cycle strictly enforced
4. **Security First** - Authentication, input validation, secrets management from day one
5. **Database as Source of Truth** - All state persisted to Neon PostgreSQL
6. **API Contract Clarity** - Explicit schemas and error handling for all endpoints

**Additional Sections:**
- Technology Stack: Mandated Python 3.11+, FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Neon PostgreSQL, Better Auth
- Security Requirements: Authentication/authorization rules, data protection, GDPR compliance
- Development Workflow: Specify → Plan → Tasks → Red-Green-Refactor → Review → Deploy

**Governance:**
- Constitution version: 1.0.0
- Ratified: 2025-12-14
- Amendment process defined with semantic versioning
- Compliance verification required for all PRs

## Outcome

- ✅ Impact: Constitution establishes architectural foundation for entire Todo AI Chatbot project
- 🧪 Tests: N/A (documentation artifact, not code)
- 📁 Files: Created `.specify/memory/constitution.md` (179 lines)
- 🔁 Next prompts: `/sp.specify` to create feature specification for the chatbot
- 🧠 Reflection: Constitution principles (especially MCP-First and Stateless Server) directly align with the user's architectural requirements for the Todo AI Chatbot. These non-negotiable constraints will guide all implementation decisions.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (initial constitution)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution principles during `/sp.plan` phase to ensure architectural decisions comply
