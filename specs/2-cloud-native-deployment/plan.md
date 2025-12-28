# Implementation Plan: Cloud-Native Event-Driven Todo Chatbot

**Branch**: `2-cloud-native-deployment` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/2-cloud-native-deployment/spec.md`

## Summary

Transform the Phase I-IV monolithic serverless Todo AI Chatbot into a cloud-native, event-driven microservices architecture deployed on Kubernetes. The system uses Dapr runtime for infrastructure abstraction (state, pub/sub, secrets, service invocation), Kafka (Redpanda Cloud) for asynchronous event streaming, and supports deployment parity between local Minikube and cloud Kubernetes (DOKS/GKE/AKS). New features include recurring tasks via cron expressions and task reminders with scheduled notifications.

**Technical Approach**: Decompose FastAPI monolith into 4 microservices (API Gateway, Task Service, Scheduler Service, Notification Service) with Dapr sidecars, publish domain events to Kafka topics (task.created, recurring-task.created, reminder.triggered), migrate from direct PostgreSQL access to Dapr State Store API, deploy via Helm charts with environment-specific values, automate CI/CD with GitHub Actions, and monitor with Prometheus + Grafana.

---

## Technical Context

**Language/Version**: Python 3.11+ (all microservices)

**Primary Dependencies**:
- FastAPI 0.109+ (API framework)
- Dapr 1.13+ (runtime abstraction)
- dapr-ext-fastapi 1.13+ (FastAPI integration)
- SQLModel 0.0.14+ (ORM for database)
- confluent-kafka 2.3+ (Kafka client)
- croniter 2.0+ (cron expression parsing)
- APScheduler 3.10+ (scheduler service)
- prometheus-client 0.19+ (metrics)

**Storage**:
- Primary: Dapr State Store (PostgreSQL backend via Neon)
- Events: Redpanda Cloud (Kafka-compatible)
- Cache: Redis (for scheduler service)

**Testing**: pytest with pytest-asyncio, pytest-docker, pytest-kafka

**Target Platform**: Kubernetes 1.27+ (Minikube for local, DOKS/GKE/AKS for cloud)

**Project Type**: Microservices web application (4 services: API Gateway, Task Service, Scheduler Service, Notification Service)

**Performance Goals**:
- Task creation: <100ms event publish latency
- Event processing: <500ms consumer latency (p95)
- Kafka throughput: 1000 events/min sustained
- Kubernetes pod startup: <30s cold start
- Horizontal scaling: 10→100 concurrent users within 2min autoscale

**Constraints**:
- Deployment parity: Minikube behavior must match cloud (DOKS/GKE/AKS)
- No synchronous Kafka calls (event-driven only, async workflows)
- All infrastructure via Dapr abstractions (no direct PostgreSQL/Kafka clients in business logic)
- Zero-downtime deployments (rolling updates with health checks)
- Secrets never in code or images (Kubernetes Secrets + Dapr secret store)

**Scale/Scope**:
- Users: 1000-10,000 concurrent
- Tasks: 10-100 per user
- Recurring tasks: 5-20 per user
- Events: 10,000-100,000 per day
- Microservices: 4 deployable units
- Kubernetes pods: 8-12 (2-3 replicas per service)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: MCP-First Architecture ✅ **PASS**

- **Requirement**: All AI agent interactions through MCP tools
- **Implementation**: MCP tools remain from Phase I-IV, no changes required for Phase V infrastructure
- **Verification**: AI agent (OpenAI Agents SDK) continues using MCP tools (add_task, list_tasks, etc.) with Dapr as backend
- **Status**: ✅ Compliant - MCP layer unaffected by Dapr/Kafka migration (infrastructure abstraction is transparent)

### Principle II: Stateless Server Design (NON-NEGOTIABLE) ✅ **PASS**

- **Requirement**: No in-memory conversation or session state
- **Implementation**:
  - Dapr State Store replaces direct database access (state externalized)
  - Kubernetes horizontal pod autoscaler enables multi-instance deployment
  - Conversation history loaded from Dapr State Store on every request
  - No sticky sessions (any pod can handle any request)
- **Verification**: Pod restart test (kill pod, verify new pod handles next request without data loss)
- **Status**: ✅ Compliant - Dapr State Store enforces statelessness at infrastructure level

### Principle III: Test-First Development (NON-NEGOTIABLE) ✅ **PASS**

- **Requirement**: Tests written before implementation (Red-Green-Refactor)
- **Implementation**:
  - Unit tests for Dapr State Store API calls (mocked)
  - Integration tests for Kafka event publishing/consuming (pytest-kafka)
  - Contract tests for microservice APIs (OpenAPI validation)
  - End-to-end tests on Minikube (Helm deploy + smoke tests in CI)
- **Test Framework**: pytest + pytest-asyncio + pytest-docker (for Dapr/Kafka containers)
- **Coverage Target**: >80% for critical paths (event handlers, state operations, service invocation)
- **Status**: ✅ Compliant - TDD workflow enforced in tasks.md

### Principle IV: Security First ✅ **PASS**

- **Requirement**: Production-grade security from day one
- **Implementation**:
  - Better Auth JWT validation (unchanged from Phase I-IV)
  - Row-level security via user_id filtering in Dapr State Store keys
  - Kubernetes Secrets for all sensitive data (DATABASE_URL, KAFKA credentials, API keys)
  - Dapr secrets component for runtime secret access
  - Dapr mTLS for all inter-service communication (automatic)
  - Network Policies to restrict pod-to-pod traffic
  - RBAC for Kubernetes API access
  - Image scanning in CI/CD (Trivy for vulnerability detection)
- **Status**: ✅ Compliant - Dapr enhances security with automatic mTLS

### Principle V: Database as Source of Truth ✅ **PASS**

- **Requirement**: All state persisted to PostgreSQL
- **Implementation**:
  - Dapr State Store with PostgreSQL backend (Neon)
  - Event sourcing via Kafka (events retained 7 days)
  - Database migrations via Alembic
  - Dual-write pattern during migration (PostgreSQL + Dapr State Store)
  - Read replicas for complex queries (JOINs), Dapr State Store for CRUD
- **Status**: ✅ Compliant - PostgreSQL remains source of truth, accessed via Dapr abstraction

### Principle VI: API Contract Clarity ✅ **PASS**

- **Requirement**: Explicit REST API contracts with schemas
- **Implementation**:
  - FastAPI Pydantic models for all request/response (unchanged)
  - OpenAPI documentation at `/docs` (auto-generated)
  - Event schemas defined in JSON Schema (contracts/event-schemas.json)
  - Dapr service invocation uses typed payloads
  - CloudEvents standard for Kafka messages
- **Status**: ✅ Compliant - API contracts extended with event schemas

**Constitution Check Result**: ✅ **ALL GATES PASSED** - Ready for implementation

---

## Project Structure

### Documentation (this feature)

```text
specs/2-cloud-native-deployment/
├── spec.md                    # Feature specification (user stories, requirements)
├── plan.md                    # This file (implementation plan)
├── research.md                # Phase 0 research (Dapr, Kafka, Kubernetes patterns)
├── data-model.md              # Phase 1 data model (RecurringTask, Reminder, Events)
├── quickstart.md              # Phase 1 deployment guide (Minikube + Cloud)
├── contracts/                 # Phase 1 API and event contracts
│   ├── dapr-components.yaml   # Dapr component configurations
│   └── event-schemas.json     # Kafka event JSON schemas
├── checklists/                # Quality validation
│   └── requirements.md        # Spec quality checklist (passed)
└── tasks.md                   # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Microservices architecture (4 services)

services/
├── api-gateway/               # User-facing API (auth, routing, rate limiting)
│   ├── main.py
│   ├── routes/
│   │   └── chat.py            # Chat endpoint (proxies to task-service)
│   ├── middleware/
│   │   ├── auth.py            # Better Auth JWT validation
│   │   └── rate_limit.py      # Rate limiting (10 req/min per user)
│   ├── Dockerfile
│   └── requirements.txt
│
├── task-service/              # Core task CRUD + Dapr State Store
│   ├── main.py
│   ├── handlers/
│   │   ├── task_crud.py       # Create, read, update, delete tasks
│   │   ├── recurring_task.py  # Recurring task management
│   │   └── events.py          # Kafka event publishers
│   ├── dapr/
│   │   ├── state.py           # Dapr State Store API wrapper
│   │   └── pubsub.py          # Dapr Pub/Sub API wrapper
│   ├── models/
│   │   ├── task.py            # Task, RecurringTask SQLModel
│   │   └── events.py          # CloudEvents schemas
│   ├── Dockerfile
│   └── requirements.txt
│
├── scheduler-service/         # Cron jobs, reminder scheduling
│   ├── main.py
│   ├── jobs/
│   │   ├── recurring_generator.py  # Generate task instances from recurring templates
│   │   └── reminder_checker.py     # Check for due reminders every 1 min
│   ├── consumers/
│   │   └── task_events.py     # Kafka consumer for task.created (schedule reminders)
│   ├── dapr/
│   │   ├── state.py           # Dapr State Store for reminder metadata
│   │   ├── pubsub.py          # Publish reminder.triggered events
│   │   └── bindings.py        # Dapr cron binding
│   ├── Dockerfile
│   └── requirements.txt
│
└── notification-service/      # Email/SMS/webhook notifications
    ├── main.py
    ├── consumers/
    │   └── reminder_events.py  # Kafka consumer for reminder.triggered
    ├── senders/
    │   ├── email.py           # SendGrid integration via Dapr binding
    │   ├── sms.py             # Twilio integration
    │   └── webhook.py         # Generic webhook sender
    ├── dapr/
    │   └── bindings.py        # Dapr output bindings (email, SMS)
    ├── Dockerfile
    └── requirements.txt

kubernetes/
├── dapr-components/           # Dapr component manifests
│   ├── statestore.yaml        # PostgreSQL state store
│   ├── pubsub.yaml            # Kafka (Redpanda) pub/sub
│   ├── secretstore.yaml       # Kubernetes secrets
│   ├── email-binding.yaml     # SendGrid binding
│   └── cron-binding.yaml      # Scheduler cron binding
│
└── base/                      # Base Kubernetes manifests (if not using Helm)
    ├── api-gateway.yaml
    ├── task-service.yaml
    ├── scheduler-service.yaml
    └── notification-service.yaml

helm/
├── todo-app/                  # Umbrella Helm chart
│   ├── Chart.yaml
│   ├── values.yaml            # Default values
│   ├── values-dev.yaml        # Minikube overrides
│   ├── values-prod.yaml       # Cloud overrides
│   ├── templates/
│   │   ├── _helpers.tpl       # Common templates
│   │   ├── api-gateway.yaml   # Deployment + Service
│   │   ├── task-service.yaml
│   │   ├── scheduler-service.yaml
│   │   ├── notification-service.yaml
│   │   ├── dapr-components.yaml  # Dapr components from configmap
│   │   └── secrets.yaml       # Placeholder (created separately)
│   └── charts/                # Subcharts (if using dependencies)
│
└── common/                    # Shared Helm library chart
    ├── Chart.yaml
    └── templates/
        ├── _deployment.tpl    # Reusable deployment template
        └── _service.tpl       # Reusable service template

.github/
└── workflows/
    ├── ci-backend.yml         # Build + test all services
    ├── ci-integration.yml     # Integration tests with Dapr/Kafka
    ├── deploy-minikube.yml    # Deploy to Minikube for testing
    └── deploy-cloud.yml       # Deploy to DOKS/GKE/AKS

backend/                       # Phase I-IV code (legacy, will migrate)
├── main.py                    # Monolithic FastAPI app (to be decomposed)
├── api/
├── agents/
├── mcp/
├── db/
└── auth/

tests/
├── unit/
│   ├── test_dapr_state.py     # Dapr State Store API tests
│   ├── test_kafka_events.py   # Kafka event publishing tests
│   └── test_services.py       # Service logic tests
├── integration/
│   ├── test_event_flow.py     # End-to-end event workflows
│   ├── test_dapr_sidecar.py   # Dapr integration tests
│   └── test_minikube.py       # Kubernetes deployment tests
└── contract/
    ├── test_api_contracts.py  # OpenAPI contract validation
    └── test_event_schemas.py  # Event schema validation
```

**Structure Decision**: Microservices architecture with domain-driven design. Each service is independently deployable with its own Dockerfile, Helm chart templates, and Dapr configuration. Services communicate via Dapr Pub/Sub (Kafka) for async workflows and Dapr service invocation for sync calls. Umbrella Helm chart deploys all services together with shared configuration.

---

## Complexity Tracking

> **No Constitution Violations - This section documents intentional complexity choices**

| Design Choice | Why Needed | Simpler Alternative Rejected Because |
|---------------|------------|-------------------------------------|
| 4 Microservices (vs monolith) | Domain boundaries clear (API, Tasks, Scheduler, Notifications), independent scaling, fault isolation | Monolith rejected: Cannot scale scheduler independently of API, scheduler failures crash entire app |
| Dapr + Kafka (vs direct PostgreSQL + HTTP) | Infrastructure abstraction (swap PostgreSQL for Redis without code changes), event-driven decoupling, polyglot support | Direct access rejected: Tight coupling to PostgreSQL, no async workflows, hard to scale |
| Umbrella Helm chart (vs separate charts) | Atomic deployments (all services versioned together), shared configuration (DRY), simplified rollback | Separate charts rejected: Version skew between services, duplicate values, complex dependency management |
| Dual-write pattern during migration | Zero-downtime migration from PostgreSQL to Dapr State Store, rollback safety | Big bang migration rejected: High risk, no rollback path, potential data loss |
| CloudEvents for Kafka messages | Standardized event envelope, interoperability, tooling support (tracing, debugging) | Custom JSON rejected: Reinventing wheel, no standardization, harder debugging |

---

## Phase 0: Research & Technology Integration

**Status**: ✅ Completed

See [`research.md`](./research.md) for detailed analysis. Key decisions:

1. **Dapr + FastAPI Integration**: Use `dapr-ext-fastapi` SDK with sidecar pattern for mTLS, retries, and observability
2. **Dapr State Store Migration**: Dual-write pattern (PostgreSQL + Dapr) → Dapr-first read → Full Dapr (6-week migration)
3. **Kafka (Redpanda) Pub/Sub**: Dapr Pub/Sub component with CloudEvents format, at-least-once delivery with idempotency (event ID tracking)
4. **Microservices Boundaries**: 4 services based on DDD (API Gateway, Task Service, Scheduler Service, Notification Service)
5. **Kubernetes + Dapr Deployment**: Dapr annotations on Deployments, automatic sidecar injection, per-service component scoping
6. **Helm Chart Strategy**: Umbrella chart with common templates for DRY, environment-specific values files (dev, prod)
7. **CI/CD with GitHub Actions**: Monorepo with path-based triggers, matrix builds, Minikube for pre-production testing, Helm atomic upgrades
8. **Monitoring**: Prometheus Operator + Grafana dashboards (Dapr metrics + custom business metrics), AlertManager rules

---

## Phase 1: Design & Contracts

**Status**: ✅ Completed

### Data Model

See [`data-model.md`](./data-model.md) for full schema. Summary:

**New Entities**:
- **RecurringTask**: Template with recurrence_rule (cron/RRULE), next_generation_time, active flag
- **TaskInstance**: Extends Task with recurring_task_id, instance_date, due_date
- **Reminder**: trigger_time, notification_channel, status (pending/triggered/canceled)
- **DomainEvent**: CloudEvents envelope for Kafka messages

**Kafka Topics**: 8 topics (task.created, task.completed, task.deleted, task.updated, recurring-task.created, recurring-task.updated, reminder.triggered, reminder.canceled)

**Storage Pattern**: Dapr State Store (PostgreSQL backend) with key pattern `{entity}:{user_id}:{id}`

**Migration**: Dual-write → Dapr-first read → Full Dapr (6 weeks)

### API Contracts

**Dapr Components** (`contracts/dapr-components.yaml`):
- State Store: PostgreSQL with connection string from Kubernetes Secret
- Pub/Sub: Kafka (Redpanda Cloud) with SASL/SCRAM auth
- Secret Store: Kubernetes secrets
- Email Binding: SendGrid for notifications
- Cron Binding: Every 1 minute for scheduler

**Event Schemas** (`contracts/event-schemas.json`):
- TaskCreated: task_id, user_id, title, description, due_date, recurring_task_id, instance_date
- TaskCompleted: task_id, user_id, title, completed_at
- RecurringTaskCreated: recurring_task_id, recurrence_rule, next_generation_time
- ReminderTriggered: reminder_id, task_id, notification_channel, trigger_time
- ReminderCanceled: reminder_id, task_id, reason (task_completed/task_deleted/user_canceled)

### Quickstart Guide

See [`quickstart.md`](./quickstart.md) for step-by-step deployment instructions covering:
- Minikube local deployment (Dapr init, Docker build, Helm install)
- Cloud deployment (DOKS, GKE, AKS with kubectl, doctl, gcloud, az CLI)
- Monitoring setup (Prometheus + Grafana with kube-prometheus-stack)
- CI/CD configuration (GitHub Actions secrets and workflows)
- Troubleshooting guide (common issues and solutions)

---

## Phase 2: Implementation Roadmap

**Note**: This plan document stops at Phase 1 (design). Implementation tasks will be generated by `/sp.tasks` command.

### High-Level Implementation Phases

#### Phase 2.1: Infrastructure Foundation (Week 1)
- Setup Redpanda Cloud Kafka cluster
- Create Dapr component manifests for all services
- Initialize Minikube with Dapr (`dapr init -k`)
- Create Kubernetes Secrets for credentials
- Deploy Dapr components and verify

#### Phase 2.2: Microservices Decomposition (Week 2-3)
- Extract API Gateway from monolithic backend
- Create Task Service with Dapr State Store integration
- Implement Kafka event publishers (task.created, task.completed)
- Build Scheduler Service with APScheduler + Dapr cron binding
- Develop Notification Service with Dapr email binding
- Test service-to-service communication via Dapr

#### Phase 2.3: Advanced Features (Week 4)
- Implement recurring task creation (parse cron/RRULE from natural language)
- Build recurring task instance generator (scheduler job)
- Add reminder scheduling logic (calculate trigger times)
- Implement reminder notification delivery (Kafka consumer → SendGrid)
- Test end-to-end workflows (recurring task → instances → reminders → notifications)

#### Phase 2.4: Helm Charts & Deployment (Week 5)
- Create Helm umbrella chart with all 4 services
- Template Dapr annotations and component configurations
- Build environment-specific values files (dev, prod)
- Test Minikube deployment with Helm
- Deploy to cloud Kubernetes (DOKS/GKE/AKS)
- Validate deployment parity (Minikube behavior matches cloud)

#### Phase 2.5: CI/CD Pipeline (Week 6)
- Create GitHub Actions workflows (build, test, deploy)
- Setup Docker registry (Docker Hub or GHCR)
- Implement matrix builds for all services
- Add Minikube integration tests in CI
- Configure cloud deployment with Helm atomic upgrades
- Test full CI/CD flow (commit → build → test → deploy)

#### Phase 2.6: Observability & Monitoring (Week 7)
- Deploy Prometheus Operator with ServiceMonitor
- Install Grafana and import Dapr dashboards
- Create custom dashboards for business metrics
- Configure Prometheus AlertManager rules
- Setup distributed tracing (Dapr → Zipkin)
- Test alerting (trigger Kafka lag alert)

#### Phase 2.7: Migration & Production Readiness (Week 8)
- Implement dual-write pattern (PostgreSQL + Dapr State Store)
- Migrate existing Phase I-IV data to Dapr State Store
- Switch to Dapr-first read pattern with PostgreSQL fallback
- Monitor cache hit rate (target >95%)
- Full cutover to Dapr State Store
- Production deployment with zero downtime

---

## Architectural Decision Records (ADR) Candidates

📋 **Potential ADRs** (require user consent via `/sp.adr` command):

1. **ADR-001: Microservices Decomposition Strategy**
   - Decision: 4 services based on DDD bounded contexts
   - Rationale: Clear domain boundaries, independent scaling, fault isolation
   - Alternatives: Monolith (rejected: cannot scale independently), 2 services (rejected: scheduler + notifications still coupled)

2. **ADR-002: Dapr vs Istio Service Mesh**
   - Decision: Dapr for application-level abstractions
   - Rationale: Simpler learning curve, state + pub/sub + bindings in one framework, polyglot support
   - Alternatives: Istio (rejected: overkill for this use case, no state/pub/sub abstractions)

3. **ADR-003: Kafka vs RabbitMQ for Event Streaming**
   - Decision: Kafka (Redpanda Cloud) for event sourcing
   - Rationale: Event retention (7 days), replay capability, higher throughput, industry standard
   - Alternatives: RabbitMQ (rejected: no event replay, lower throughput)

4. **ADR-004: Helm Umbrella Chart vs Separate Charts**
   - Decision: Umbrella chart with common templates
   - Rationale: Atomic deployments, shared configuration (DRY), simplified versioning
   - Alternatives: Separate charts (rejected: version skew risk, duplicate values)

5. **ADR-005: Dual-Write Migration Pattern**
   - Decision: Gradual migration with dual-write safety net
   - Rationale: Zero downtime, rollback capability, data integrity validation
   - Alternatives: Big bang migration (rejected: high risk, no rollback)

**Action**: Run `/sp.adr <title>` if user wants to document these decisions formally.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dapr learning curve delays development | Medium | High | Hands-on workshop (1 day), pair programming, official quickstarts, allocate 20% buffer time |
| Kafka message ordering issues | Medium | Medium | Use partitioning by user_id (guarantees ordering per user), document ordering semantics in code comments |
| Minikube resource exhaustion | High | Low | Allocate 4 CPU / 8GB RAM minimum, use resource limits/requests in Helm charts, monitor with kubectl top |
| Deployment parity drift (Minikube ≠ cloud) | Medium | High | CI tests on both Minikube and cloud, same Helm charts + values overrides only, quarterly parity audits |
| Event duplication causing duplicate database writes | High | Medium | Implement idempotency (event ID tracking in Dapr State Store), write integration tests for duplicate events |
| Helm upgrade rollback failures | Low | High | Use `--atomic` flag (auto-rollback on failure), test rollback in staging, keep last 3 release histories |
| Prometheus storage fills disk | Medium | Low | Configure 15-day retention, use remote storage (Thanos) if needed, alert at 80% disk usage |
| Network policies break service communication | Medium | Medium | Start with permissive policies, incrementally tighten, test after each change, document all allowed paths |
| GitHub Actions runner quota exhaustion | Low | Medium | Use self-hosted runners for high-frequency builds, optimize workflows (cache layers, parallel jobs) |
| PostgreSQL → Dapr State Store migration data loss | Low | Critical | Dual-write pattern with validation, automated data consistency checks, 30-day PostgreSQL backup retention |

---

## Performance Targets & Monitoring

### Performance Goals (from Spec)

- **Task Creation**: <100ms event publish latency (API → Kafka)
- **Event Processing**: <500ms consumer latency (p95) (Kafka → Consumer → DB)
- **Kafka Throughput**: 1000 events/min sustained (no lag >100 messages)
- **Pod Startup**: <30s cold start (image pull + Dapr sidecar init)
- **Horizontal Scaling**: 10→100 concurrent users within 2min autoscale

### Monitoring Strategy

**Metrics to Track**:
- Dapr metrics: HTTP/gRPC latency, pub/sub throughput, state operation duration
- Kafka metrics: Consumer lag, message rate, partition distribution
- Business metrics: Tasks created/hour, reminders sent/hour, task completion rate
- Kubernetes metrics: Pod CPU/memory usage, pod restart count, node capacity

**Dashboards**:
- Dapr System Dashboard (Grafana ID 14456)
- Dapr Sidecar Dashboard (Grafana ID 19837)
- Custom Todo Service Dashboard (tasks created, reminders sent, API latency)

**Alerts**:
- Kafka consumer lag >1000 messages
- Pod crash loop (>3 restarts in 5min)
- High memory usage (>80% pod limit)
- High error rate (>5% 5xx responses)
- Dapr sidecar failures

---

## Deployment Architecture

### Development Environment (Minikube)

```
Developer Machine (4 CPU, 8GB RAM)
├── Minikube Cluster
│   ├── Dapr Control Plane (3 pods)
│   ├── API Gateway (1 pod + Dapr sidecar)
│   ├── Task Service (1 pod + Dapr sidecar)
│   ├── Scheduler Service (1 pod + Dapr sidecar)
│   ├── Notification Service (1 pod + Dapr sidecar)
│   ├── Dapr Components (ConfigMaps)
│   └── Secrets (Kubernetes Secrets)
├── External Services
│   ├── Redpanda Cloud (Kafka)
│   ├── Neon PostgreSQL
│   └── SendGrid (Email)
└── Docker Registry (local or Docker Hub)
```

### Production Environment (Cloud Kubernetes)

```
                      ┌─────────────────┐
                      │  Load Balancer  │
                      │  (Cloud Provider│
                      └────────┬────────┘
                               │ HTTPS
                               ▼
                  ┌────────────────────────┐
                  │   API Gateway Service  │
                  │   (2-3 replicas)       │
                  │   + Dapr Sidecars      │
                  └───┬─────────────┬──────┘
                      │             │
        ┌─────────────┴─────┐      │ Dapr Service
        │ Dapr Pub/Sub      │      │ Invocation
        │ (Kafka Events)    │      ▼
        └────┬──────────────┘  ┌──────────────────┐
             │                 │  Task Service    │
             │                 │  (2-3 replicas)  │
             │                 │  + Dapr Sidecars │
             │                 └─────┬────────────┘
             │                       │
             │ Kafka                 │ Dapr State Store
             │ Events                ▼
             ▼                 ┌──────────────────┐
   ┌──────────────────┐        │  PostgreSQL      │
   │  Scheduler       │        │  (Neon Serverless│
   │  Service         │        └──────────────────┘
   │  (1 replica)     │
   │  + Dapr Sidecar  │
   └────┬─────────────┘
        │ Kafka reminder.triggered
        ▼
   ┌──────────────────┐
   │  Notification    │
   │  Service         │
   │  (2-3 replicas)  │
   │  + Dapr Sidecars │
   └────┬─────────────┘
        │ Dapr Email Binding
        ▼
   ┌──────────────────┐
   │  SendGrid        │
   │  (Email Provider)│
   └──────────────────┘

Monitoring Stack:
┌──────────────────┐
│  Prometheus      │
│  (metrics)       │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│  Grafana         │
│  (dashboards)    │
└──────────────────┘
```

**Infrastructure Requirements**:
- Kubernetes nodes: 3 nodes, 2 vCPU / 4GB RAM each (minimum)
- Dapr control plane: 3 pods (operator, sidecar-injector, sentry)
- Application pods: 8-12 total (2-3 replicas per service + sidecars)
- Storage: Persistent volumes for Prometheus (20GB), Grafana (5GB)

---

## Security Checklist

- [x] **Environment Variables**: All secrets in Kubernetes Secrets (never hardcoded)
- [x] **JWT Validation**: API Gateway validates Bearer tokens from Better Auth
- [x] **Row-Level Security**: Dapr State Store keys include user_id partition
- [x] **Dapr mTLS**: Automatic mutual TLS for all service-to-service calls (enabled by default)
- [x] **Network Policies**: Restrict pod-to-pod traffic to necessary paths only
- [x] **RBAC**: Kubernetes role-based access control for service accounts
- [x] **Image Scanning**: Trivy scan in CI/CD (fail on high/critical CVEs)
- [x] **Secrets Management**: Dapr secrets component for runtime access
- [x] **HTTPS**: Enforced via cloud load balancer (cert-manager for TLS certs)
- [x] **Audit Trail**: user_id logged in all events and state operations

---

## Next Steps

1. **Run `/sp.tasks`**: Generate actionable task breakdown from this plan
2. **Review Tasks**: Prioritize by user story (P1 → P2 → P3)
3. **Setup Infrastructure**: Provision Redpanda Cloud, configure Kubernetes cluster
4. **Begin Implementation**: Follow TDD approach (Write tests → Red → Green → Refactor)
5. **Incremental Deployment**: Deploy each microservice independently, validate, then move to next
6. **Monitor Metrics**: Setup Grafana dashboards early for visibility
7. **Production Deployment**: Follow quickstart.md deployment guide for cloud

---

**Plan Status**: ✅ Phase 0 & Phase 1 Complete | Ready for `/sp.tasks` command

**Planning Artifacts**:
- ✅ research.md (7 research questions answered with implementation details)
- ✅ data-model.md (3 new entities + 8 event types + migration strategy)
- ✅ contracts/dapr-components.yaml (5 Dapr components configured)
- ✅ contracts/event-schemas.json (5 event schemas with JSON Schema)
- ✅ quickstart.md (Minikube + cloud deployment guide)
- ⏭️ tasks.md (awaiting `/sp.tasks` command)

**Constitution Compliance**: ✅ All 6 principles validated (see Constitution Check section)

**Guardian Agent Compliance**: ✅ All Phase V requirements addressed (event-driven architecture, Dapr abstractions, Kafka async workflows, deployment parity, advanced features, CI/CD, monitoring)
