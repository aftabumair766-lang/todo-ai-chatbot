---
id: 002
title: Create Phase V Implementation Plan
stage: plan
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 2-cloud-native-deployment
branch: 2-cloud-native-deployment
user: umair
command: /sp.plan
labels: ["phase-v", "implementation-plan", "kubernetes", "dapr", "kafka", "microservices", "architecture"]
links:
  spec: specs/2-cloud-native-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/2-cloud-native-deployment/plan.md
  - specs/2-cloud-native-deployment/research.md
  - specs/2-cloud-native-deployment/data-model.md
  - specs/2-cloud-native-deployment/quickstart.md
  - specs/2-cloud-native-deployment/contracts/dapr-components.yaml
  - specs/2-cloud-native-deployment/contracts/event-schemas.json
tests:
  - Constitution Check passed (all 6 principles validated)
  - Guardian Agent Phase V compliance verified
  - Research completed for 7 technology integration patterns
  - Data model designed with 3 new entities + 8 event types
  - Contracts defined for Dapr components and Kafka events
---

## Prompt

User input for /sp.plan command: (no additional arguments, using specification from /sp.specify)

Context: Create implementation plan for Phase V cloud-native deployment based on the specification created in specs/2-cloud-native-deployment/spec.md. The plan must address:
- Microservices decomposition (4 services: API Gateway, Task Service, Scheduler Service, Notification Service)
- Dapr runtime integration (state, pub/sub, secrets, service invocation, bindings)
- Kafka (Redpanda Cloud) event-driven architecture
- Kubernetes deployment (Minikube + cloud parity)
- Helm charts for deployment automation
- CI/CD with GitHub Actions
- Prometheus + Grafana monitoring
- Advanced features (recurring tasks, reminders)
- Migration from Phase I-IV monolithic serverless to cloud-native microservices

Guardian Agent requirements enforced:
1. Event-driven architecture (no synchronous Kafka coupling)
2. Dapr abstractions over direct infrastructure
3. Deployment parity (Minikube = Cloud)
4. All Phase V components addressed
5. Test-first development approach
6. Constitution compliance

## Response snapshot

**Phase 0: Research & Technology Integration** ✅ Complete

Generated comprehensive research document covering 7 key integration patterns:
1. Dapr + FastAPI Integration (dapr-ext-fastapi SDK, sidecar pattern, mTLS)
2. Dapr + Kafka Pub/Sub (CloudEvents format, idempotency, at-least-once delivery)
3. Microservices Decomposition (4 services based on DDD bounded contexts)
4. Kubernetes + Dapr Deployment (annotations, component manifests, secrets management)
5. Helm Charts Strategy (umbrella chart with common templates, env-specific values)
6. GitHub Actions CI/CD (monorepo, matrix builds, Minikube testing, atomic deployments)
7. Prometheus + Grafana Monitoring (Dapr dashboards, custom business metrics, AlertManager)

**Phase 1: Design & Contracts** ✅ Complete

**Data Model** (data-model.md):
- 3 new entities: RecurringTask (cron templates), TaskInstance (extends Task with recurring support), Reminder (scheduled notifications)
- 8 Kafka event types with CloudEvents envelope
- Dapr State Store key patterns: `{entity}:{user_id}:{id}`
- Migration strategy: Dual-write → Dapr-first read → Full Dapr (6 weeks)

**Contracts** (contracts/ directory):
- Dapr components YAML: statestore (PostgreSQL), pubsub (Kafka/Redpanda), secretstore (Kubernetes), email-binding (SendGrid), cron-binding (scheduler)
- Event schemas JSON: TaskCreated, TaskCompleted, RecurringTaskCreated, ReminderTriggered, ReminderCanceled (all with JSON Schema validation)

**Quickstart Guide** (quickstart.md):
- Minikube deployment (Dapr init, Docker build, Helm install, port-forward)
- Cloud deployment (DOKS/GKE/AKS with doctl/gcloud/az CLI)
- Monitoring setup (kube-prometheus-stack, Grafana dashboards)
- CI/CD configuration (GitHub Secrets, workflow triggers)
- Troubleshooting guide (common issues: ImagePullBackOff, Dapr injection, Kafka connection)

**Implementation Plan** (plan.md):
- **Technical Context**: Python 3.11+, Dapr 1.13+, Kafka/Redpanda, Kubernetes 1.27+, Helm 3+
- **Constitution Check**: All 6 principles validated ✅
  - MCP-First: ✅ MCP layer unchanged (transparent Dapr backend)
  - Stateless: ✅ Dapr State Store enforces statelessness
  - Test-First: ✅ TDD with pytest + pytest-docker/kafka
  - Security First: ✅ mTLS, Kubernetes Secrets, network policies
  - Database as Truth: ✅ PostgreSQL via Dapr abstraction
  - API Contracts: ✅ OpenAPI + CloudEvents schemas
- **Project Structure**: 4 microservices (services/ directory), Helm charts (helm/todo-app/), Kubernetes manifests (kubernetes/dapr-components/), GitHub workflows (.github/workflows/)
- **Implementation Phases**: 7 phases over 8 weeks (Infrastructure → Microservices → Features → Helm → CI/CD → Monitoring → Migration)
- **ADR Candidates**: 5 decisions requiring documentation (microservices decomposition, Dapr vs Istio, Kafka vs RabbitMQ, Helm umbrella chart, dual-write migration)
- **Risk Mitigation**: 10 risks with probability/impact/mitigation (Dapr learning curve, event ordering, resource exhaustion, deployment parity drift, etc.)

## Outcome

- ✅ Impact: Complete Phase V implementation plan created with architecture, design artifacts, and deployment guides. Addresses 100% of Guardian Agent Phase V requirements (event-driven architecture, Dapr abstractions, Kafka async workflows, deployment parity, advanced features, CI/CD, monitoring).
- 🧪 Tests: Constitution Check passed (6/6 principles). All quality gates cleared for proceeding to implementation tasks.
- 📁 Files: Created plan.md (comprehensive roadmap), research.md (technology integration), data-model.md (entities + events), quickstart.md (deployment guide), contracts/dapr-components.yaml (5 Dapr components), contracts/event-schemas.json (5 event schemas)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task breakdown with test-first development approach, dependency ordering, and parallel execution opportunities
- 🧠 Reflection: Planning phase successfully balances technical depth (Dapr/Kafka/Kubernetes details) with actionable guidance (quickstart, troubleshooting). Microservices decomposition based on DDD provides clear boundaries. Dual-write migration pattern ensures zero-downtime transition. Deployment parity requirement (Minikube = Cloud) enforced via Helm charts with environment-specific values.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning phase completed successfully with all Phase 1 artifacts generated.
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 6 principles validated)
  - Guardian Agent Phase V Compliance: PASS (event-driven architecture ✅, Dapr abstractions ✅, Kafka async ✅, deployment parity ✅, advanced features ✅, CI/CD ✅, monitoring ✅)
  - Research Completeness: PASS (7/7 technology integrations researched with implementation details)
  - Design Artifacts: PASS (data model, contracts, quickstart all complete)
- Prompt variant (if applicable): N/A - Standard /sp.plan workflow
- Next experiment (smallest change to try): For future planning, consider adding architecture diagrams directly in plan.md (currently text-based descriptions). Explore Mermaid or PlantUML in markdown for visual architecture representation. For Phase V, current text descriptions with ASCII art are sufficient given complexity.
