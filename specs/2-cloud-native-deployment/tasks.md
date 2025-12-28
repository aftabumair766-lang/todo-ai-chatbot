# Tasks: Cloud-Native Event-Driven Todo Chatbot

**Input**: Design documents from `/specs/2-cloud-native-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5, US6, US7)
- Include exact file paths in descriptions

## Path Conventions

- **Microservices structure**: `services/{service-name}/` at repository root
- **Kubernetes manifests**: `kubernetes/dapr-components/`
- **Helm charts**: `helm/todo-app/`
- Paths follow plan.md structure

---

## Phase 1: Setup (Infrastructure Initialization)

**Purpose**: Project initialization and tooling setup

- [ ] T001 Create microservices project structure: services/{api-gateway,task-service,scheduler-service,notification-service}/{main.py,Dockerfile,requirements.txt}
- [ ] T002 Create Kubernetes manifest directories: kubernetes/dapr-components/, kubernetes/base/
- [ ] T003 Create Helm chart structure: helm/todo-app/{Chart.yaml,values.yaml,values-dev.yaml,values-prod.yaml,templates/}
- [ ] T004 [P] Create Python requirements.txt for all services with Dapr SDK, FastAPI, croniter, APScheduler, confluent-kafka
- [ ] T005 [P] Create Dockerfiles for all 4 services with Python 3.11 base image and multi-stage builds
- [ ] T006 [P] Create .dockerignore for Python services (exclude venv, __pycache__, .env, *.pyc)
- [ ] T007 [P] Create GitHub Actions workflow directory: .github/workflows/
- [ ] T008 [P] Setup pytest configuration for all services in services/{service}/pytest.ini
- [ ] T009 [P] Create Redpanda Cloud Kafka cluster and save connection details (manual step - document in quickstart.md)

**Checkpoint**: Project skeleton ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dapr Components & Kubernetes Foundation

- [ ] T010 Create Dapr State Store component manifest in kubernetes/dapr-components/statestore.yaml (PostgreSQL backend, connection string from secret)
- [ ] T011 Create Dapr Pub/Sub component manifest in kubernetes/dapr-components/pubsub.yaml (Kafka/Redpanda with SASL/SCRAM auth)
- [ ] T012 Create Dapr Secret Store component manifest in kubernetes/dapr-components/secretstore.yaml (Kubernetes secrets)
- [ ] T013 Create Dapr Email Binding component manifest in kubernetes/dapr-components/email-binding.yaml (SendGrid for notifications)
- [ ] T014 Create Dapr Cron Binding component manifest in kubernetes/dapr-components/cron-binding.yaml (scheduler every 1 minute)
- [ ] T015 [P] Create Kubernetes Secret template in kubernetes/base/secrets.yaml (placeholder for DATABASE_URL, KAFKA credentials, SENDGRID_API_KEY)
- [ ] T016 [P] Initialize Minikube cluster with 4 CPU / 8GB RAM and install Dapr runtime via `dapr init -k`

### Data Models (Shared Across Services)

- [ ] T017 Create RecurringTask model in services/task-service/models/recurring_task.py (SQLModel with recurrence_rule, next_generation_time, timezone)
- [ ] T018 Create TaskInstance model in services/task-service/models/task.py (extends Phase I-IV Task with recurring_task_id, instance_date, due_date)
- [ ] T019 Create Reminder model in services/scheduler-service/models/reminder.py (SQLModel with trigger_time, notification_channel, status)
- [ ] T020 [P] Create CloudEvents schemas in services/task-service/models/events.py (TaskCreated, TaskCompleted, RecurringTaskCreated, ReminderTriggered per contracts/event-schemas.json)

### Dapr Client Wrappers (Shared Library)

- [ ] T021 Create Dapr State Store wrapper in services/common/dapr/state.py (async methods: save_state, get_state, delete_state, query_state with key pattern `{entity}:{user_id}:{id}`)
- [ ] T022 Create Dapr Pub/Sub wrapper in services/common/dapr/pubsub.py (async methods: publish_event with CloudEvents envelope, subscribe decorator)
- [ ] T023 Create Dapr Service Invocation wrapper in services/common/dapr/service_invocation.py (async method: invoke_service with app-id and method-name)
- [ ] T024 [P] Create Dapr Bindings wrapper in services/common/dapr/bindings.py (async methods for email binding and cron binding)

### Helm Chart Foundation

- [ ] T025 Create Helm _helpers.tpl with common label templates in helm/todo-app/templates/_helpers.tpl
- [ ] T026 Create Helm deployment template for API Gateway in helm/todo-app/templates/api-gateway-deployment.yaml (Dapr annotations: enabled=true, app-id=api-gateway, port=8000)
- [ ] T027 Create Helm service template for API Gateway in helm/todo-app/templates/api-gateway-service.yaml (ClusterIP, port 8000)
- [ ] T028 [P] Create Helm templates for Task Service in helm/todo-app/templates/task-service-{deployment,service}.yaml (Dapr annotations: app-id=task-service)
- [ ] T029 [P] Create Helm templates for Scheduler Service in helm/todo-app/templates/scheduler-service-{deployment,service}.yaml (Dapr annotations: app-id=scheduler-service)
- [ ] T030 [P] Create Helm templates for Notification Service in helm/todo-app/templates/notification-service-{deployment,service}.yaml (Dapr annotations: app-id=notification-service)
- [ ] T031 Create Helm ConfigMap for Dapr components in helm/todo-app/templates/dapr-components-configmap.yaml (includes all 5 Dapr component YAMLs)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Deploy Event-Driven Architecture on Kubernetes (Priority: P1) 🎯 MVP

**Goal**: Deploy all microservices to Kubernetes with Dapr sidecars, Kafka event streaming, and stateless architecture

**Independent Test**: Deploy to Minikube with `helm install todo-app`, create task via API, verify Kafka event published to `task.created` topic, confirm consumer processes event via Dapr State Store, kill pod and verify system resumes without data loss

### Implementation for User Story 1

- [ ] T032 [US1] Create FastAPI app skeleton for API Gateway in services/api-gateway/main.py (health endpoint, CORS middleware, Dapr integration)
- [ ] T033 [US1] Implement Better Auth JWT validation middleware in services/api-gateway/middleware/auth.py (validate Bearer token, extract user_id)
- [ ] T034 [US1] Create FastAPI app skeleton for Task Service in services/task-service/main.py (health endpoint, Dapr State Store initialization)
- [ ] T035 [US1] Implement task CRUD endpoints in services/task-service/handlers/task_crud.py (create_task, get_task, list_tasks, update_task, delete_task using Dapr State Store API)
- [ ] T036 [US1] Implement Kafka event publisher for task.created in services/task-service/handlers/events.py (publish to Dapr Pub/Sub after task created)
- [ ] T037 [US1] Create FastAPI app skeleton for Scheduler Service in services/scheduler-service/main.py (health endpoint, APScheduler initialization, Dapr cron binding subscription)
- [ ] T038 [US1] Create FastAPI app skeleton for Notification Service in services/notification-service/main.py (health endpoint, Dapr Pub/Sub subscription to reminder.triggered)
- [ ] T039 [US1] Build Docker images for all 4 services with tags `{service-name}:v1`
- [ ] T040 [US1] Load Docker images into Minikube with `minikube image load {service-name}:v1`
- [ ] T041 [US1] Deploy Dapr components to Kubernetes with `kubectl apply -f kubernetes/dapr-components/`
- [ ] T042 [US1] Create Kubernetes Secret with credentials using `kubectl create secret generic dapr-secrets`
- [ ] T043 [US1] Deploy application with Helm: `helm install todo-app helm/todo-app --values helm/todo-app/values-dev.yaml`
- [ ] T044 [US1] Verify all pods running with Dapr sidecars (2 containers per pod: app + daprd)
- [ ] T045 [US1] Test API Gateway health endpoint via `kubectl port-forward svc/todo-api-gateway 8000:8000` and `curl localhost:8000/health`
- [ ] T046 [US1] Test task creation: POST to /api/chat, verify Kafka event in task.created topic via Dapr logs
- [ ] T047 [US1] Test pod restart: kill task-service pod, verify Kubernetes restarts within 30s, system continues functioning
- [ ] T048 [US1] Deploy to cloud Kubernetes (DOKS or GKE or AKS) with same Helm charts and values-prod.yaml, validate deployment parity

**Checkpoint**: User Story 1 complete - event-driven architecture deployed on Kubernetes, Dapr sidecars working, Kafka events flowing, stateless validation passed

---

## Phase 4: User Story 2 - Create Recurring Tasks via Natural Language (Priority: P1)

**Goal**: Users can create recurring tasks ("Remind me to exercise every Monday"), system generates task instances via scheduler

**Independent Test**: Send "Add recurring task: team standup every weekday at 9am", verify recurring task created with cron `0 9 * * 1-5`, scheduler generates task instances for next 3 days, each published to Kafka

### Implementation for User Story 2

- [ ] T049 [US2] Extend AI agent (OpenAI Agents SDK) to parse recurring task natural language in services/api-gateway/agents/recurring_task_parser.py (detect patterns: daily, weekly, monthly, convert to cron/RRULE)
- [ ] T050 [US2] Create recurring task CRUD endpoints in services/task-service/handlers/recurring_task_crud.py (create_recurring_task, get_recurring_task, list_recurring_tasks, disable_recurring_task)
- [ ] T051 [US2] Implement recurring task storage via Dapr State Store with key pattern `recurring-task:{user_id}:{id}`
- [ ] T052 [US2] Publish recurring-task.created event to Kafka after recurring task creation in services/task-service/handlers/events.py
- [ ] T053 [US2] Implement recurring task instance generator in services/scheduler-service/jobs/recurring_generator.py (cron job runs every 1 hour, loads recurring tasks, generates instances for next 7 days)
- [ ] T054 [US2] Use croniter library to calculate next occurrence times from cron expressions in services/scheduler-service/jobs/recurring_generator.py
- [ ] T055 [US2] Publish task.created events for generated instances to Kafka via Dapr Pub/Sub
- [ ] T056 [US2] Implement Kafka consumer in Task Service to persist generated task instances in services/task-service/consumers/task_instance_consumer.py
- [ ] T057 [US2] Add idempotency check to prevent duplicate task instances using `(recurring_task_id, instance_date)` unique constraint
- [ ] T058 [US2] Test recurring task creation: "Remind me to exercise every Monday", verify cron stored, instances generated, events published
- [ ] T059 [US2] Test recurring task disable: "Stop my exercise reminder", verify no new instances generated

**Checkpoint**: User Story 2 complete - recurring tasks working, scheduler generating instances, natural language parsing functional

---

## Phase 5: User Story 3 - Receive Task Reminders at Scheduled Times (Priority: P1)

**Goal**: Users receive notifications 15 minutes before tasks, leveraging event-driven architecture with Dapr bindings

**Independent Test**: Create task with reminder 2 minutes from now, wait 2 minutes, verify `reminder.triggered` event published, notification service sends email via SendGrid, user receives notification

### Implementation for User Story 3

- [ ] T060 [US3] Extend AI agent to parse reminder requests in services/api-gateway/agents/reminder_parser.py (detect "15 minutes before", "at 9am tomorrow", convert to absolute timestamp)
- [ ] T061 [US3] Create reminder CRUD endpoints in services/task-service/handlers/reminder_crud.py (create_reminder, get_reminder, cancel_reminder)
- [ ] T062 [US3] Implement reminder storage via Dapr State Store with key pattern `reminder:{user_id}:{id}`
- [ ] T063 [US3] Implement reminder checker job in services/scheduler-service/jobs/reminder_checker.py (runs every 1 minute via Dapr cron binding, queries Dapr State Store for due reminders)
- [ ] T064 [US3] Publish reminder.triggered events to Kafka for due reminders in services/scheduler-service/jobs/reminder_checker.py
- [ ] T065 [US3] Implement Kafka consumer for reminder.triggered in services/notification-service/consumers/reminder_consumer.py
- [ ] T066 [US3] Implement email notification sender in services/notification-service/senders/email.py (use Dapr email binding to SendGrid)
- [ ] T067 [US3] Implement webhook notification sender in services/notification-service/senders/webhook.py (HTTP POST to user-provided webhook URL)
- [ ] T068 [US3] Implement reminder cancellation when task completed in services/task-service/handlers/task_crud.py (publish reminder.canceled event)
- [ ] T069 [US3] Test reminder creation: Task "Call mom" with "remind me in 2 minutes", verify reminder scheduled
- [ ] T070 [US3] Test notification delivery: Wait 2 minutes, verify email sent via SendGrid, check Dapr binding logs
- [ ] T071 [US3] Test reminder cancellation: Complete task before reminder time, verify no notification sent

**Checkpoint**: User Story 3 complete - reminders working, notifications delivered via Dapr bindings, event-driven workflow validated

---

## Phase 6: User Story 4 - Dapr State Management for Stateless Services (Priority: P2)

**Goal**: All services use Dapr State Store API instead of direct database access, enabling database swaps without code changes

**Independent Test**: Verify Dapr State Store API called (not direct PostgreSQL), swap Dapr component backend from PostgreSQL to Redis, restart services, verify system continues working

### Implementation for User Story 4

- [ ] T072 [US4] Migrate existing Task CRUD from SQLModel to Dapr State Store API in services/task-service/handlers/task_crud.py
- [ ] T073 [US4] Implement Dapr State Store query API for listing user tasks with filter `user_id={id}` in services/common/dapr/state.py
- [ ] T074 [US4] Implement optimistic concurrency control using Dapr State Store ETags in services/common/dapr/state.py
- [ ] T075 [US4] Add Dapr State Store transaction support for atomic multi-entity updates in services/common/dapr/state.py
- [ ] T076 [US4] Test Dapr State Store backend swap: reconfigure statestore.yaml to use Redis, restart services, verify tasks still accessible
- [ ] T077 [US4] Verify no direct PostgreSQL client imports in service code (code audit)

**Checkpoint**: User Story 4 complete - Dapr State Store API fully adopted, database abstraction layer working, backend swappable

---

## Phase 7: User Story 5 - Kafka Event-Driven Async Workflows (Priority: P2)

**Goal**: All cross-service communication uses Kafka events via Dapr Pub/Sub, services decoupled and resilient

**Independent Test**: Create task, monitor Kafka topic, verify event published with CloudEvents envelope, deploy separate consumer, confirm independent processing without blocking API

### Implementation for User Story 5

- [ ] T078 [US5] Implement Dapr Pub/Sub subscription decorators for all Kafka topics in services/{service}/consumers/
- [ ] T079 [US5] Add idempotency tracking for Kafka consumers in services/common/dapr/idempotency.py (track processed event IDs in Dapr State Store with 7-day TTL)
- [ ] T080 [US5] Implement event schema validation using contracts/event-schemas.json in services/common/validation/event_validator.py
- [ ] T081 [US5] Add CloudEvents envelope wrapping for all published events in services/common/dapr/pubsub.py
- [ ] T082 [US5] Test Kafka broker failure: stop Redpanda, attempt event publish, verify Dapr retries with exponential backoff
- [ ] T083 [US5] Test consumer failure: stop consumer service, publish events, restart consumer, verify backlog processed
- [ ] T084 [US5] Test duplicate event handling: publish same event twice with same ID, verify consumer processes only once (idempotency)

**Checkpoint**: User Story 5 complete - event-driven workflows robust, Kafka consumers idempotent, services decoupled

---

## Phase 8: User Story 6 - CI/CD Pipeline with GitHub Actions (Priority: P2)

**Goal**: Automated pipeline tests, builds, and deploys to Kubernetes on every commit

**Independent Test**: Push code to GitHub, verify workflow triggers, tests run, Docker images built/pushed, deployment to Minikube succeeds, smoke tests pass within 10 minutes

### Implementation for User Story 6

- [ ] T085 [US6] Create GitHub Actions workflow for backend CI in .github/workflows/ci-backend.yml (matrix build for 4 services, run pytest, lint with ruff, type check with mypy)
- [ ] T086 [US6] Create GitHub Actions workflow for Docker build in .github/workflows/docker-build.yml (build all 4 service images, tag with commit SHA and latest, push to Docker Hub or GHCR)
- [ ] T087 [US6] Create GitHub Actions workflow for Minikube deployment in .github/workflows/deploy-minikube.yml (start Minikube, install Dapr, deploy Helm chart, run smoke tests)
- [ ] T088 [US6] Create GitHub Actions workflow for cloud deployment in .github/workflows/deploy-cloud.yml (deploy to DOKS/GKE/AKS with Helm, use --atomic flag for rollback on failure)
- [ ] T089 [US6] Configure GitHub Secrets for Docker registry credentials, Kubernetes kubeconfig, database URL, Kafka credentials
- [ ] T090 [US6] Implement smoke tests in tests/smoke/test_deployment.py (test /health endpoints, create task, verify Kafka event)
- [ ] T091 [US6] Add path-based workflow triggers to only build changed services in .github/workflows/ci-backend.yml
- [ ] T092 [US6] Test CI/CD pipeline: push code change, verify tests run, images built, Minikube deployment succeeds

**Checkpoint**: User Story 6 complete - CI/CD pipeline fully automated, deployments consistent and fast

---

## Phase 9: User Story 7 - Observability with Prometheus and Grafana (Priority: P3)

**Goal**: Prometheus metrics and Grafana dashboards for monitoring Dapr, Kafka, and business KPIs

**Independent Test**: Deploy Prometheus and Grafana, verify Dapr metrics scraped, create dashboard, confirm task creation rate visible, alert triggers when Kafka lag >1000

### Implementation for User Story 7

- [ ] T093 [US7] Install Prometheus Operator via Helm: `helm install monitoring prometheus-community/kube-prometheus-stack`
- [ ] T094 [US7] Create ServiceMonitor for Dapr metrics in kubernetes/monitoring/dapr-servicemonitor.yaml (scrape Dapr sidecar metrics endpoints)
- [ ] T095 [US7] Add custom business metrics to Task Service using prometheus-client in services/task-service/metrics.py (tasks_created_total, task_completion_rate)
- [ ] T096 [US7] Create Grafana dashboard JSON for Dapr metrics in kubernetes/monitoring/grafana-dapr-dashboard.json (import dashboard ID 14456)
- [ ] T097 [US7] Create custom Grafana dashboard for business KPIs in kubernetes/monitoring/grafana-todo-dashboard.json (tasks created, reminders sent, API latency)
- [ ] T098 [US7] Configure Prometheus AlertManager rules in kubernetes/monitoring/prometheus-alerts.yaml (high Kafka lag >1000, pod crash loop, high error rate >5%)
- [ ] T099 [US7] Test metrics collection: create tasks, observe Grafana dashboard updates in real-time
- [ ] T100 [US7] Test alerting: simulate high Kafka lag, verify Prometheus alert fires, notification sent

**Checkpoint**: User Story 7 complete - observability stack operational, metrics visible, alerts configured

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, documentation, and final validation

### Migration & Data Integrity

- [ ] T101 [P] Implement dual-write pattern in Task Service: write to both Dapr State Store and PostgreSQL in services/task-service/handlers/task_crud.py
- [ ] T102 [P] Create data consistency validator in scripts/validate_migration.py (compare Dapr State Store vs PostgreSQL for all tasks)
- [ ] T103 [P] Run migration for existing Phase I-IV tasks to Dapr State Store using scripts/migrate_to_dapr.py

### Security Hardening

- [ ] T104 [P] Create Kubernetes Network Policies in kubernetes/base/network-policies.yaml (restrict pod-to-pod traffic to necessary paths only)
- [ ] T105 [P] Verify Dapr mTLS enabled for all services via `dapr mtls --kubernetes`
- [ ] T106 [P] Run Trivy vulnerability scan on all Docker images in CI pipeline
- [ ] T107 [P] Audit all Dapr State Store keys for user_id prefix (row-level security check)

### Documentation

- [ ] T108 [P] Update README.md with Phase V deployment instructions (Minikube + cloud)
- [ ] T109 [P] Update CLAUDE.md with Phase V context (Dapr, Kafka, microservices architecture)
- [ ] T110 [P] Create runbook for common operations in docs/RUNBOOK.md (deployment, rollback, debugging Dapr sidecars, Kafka troubleshooting)

### Testing & Validation

- [ ] T111 Run full integration test suite: pytest services/*/tests/integration/ (end-to-end workflows)
- [ ] T112 [P] Run load testing with 100 concurrent users using k6 or locust
- [ ] T113 [P] Validate deployment parity: deploy to Minikube and cloud with same Helm charts, compare behavior

**Checkpoint**: Production-ready system with full documentation, security hardened, migration complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - US1, US2, US3 can run in parallel (P1 priority, independent features)
  - US4, US5, US6 can run in parallel after US1 (P2 priority, depend on deployed infrastructure)
  - US7 can run independently (P3 priority, observability layer)
- **Polish (Phase 10)**: Depends on all desired user stories complete

### User Story Dependencies

- **US1 (Deploy Kubernetes)**: No dependencies (foundational infrastructure)
- **US2 (Recurring Tasks)**: No dependencies (independent feature, can run parallel with US1 implementation)
- **US3 (Reminders)**: No dependencies (independent feature, can run parallel with US1/US2)
- **US4 (Dapr State Management)**: Depends on US1 (needs deployed infrastructure for testing)
- **US5 (Kafka Event-Driven)**: Depends on US1 (needs Kafka infrastructure deployed)
- **US6 (CI/CD)**: Depends on US1 (needs deployment target)
- **US7 (Observability)**: Independent (can deploy monitoring stack anytime)

### Parallel Execution Opportunities

**Within Foundational Phase** (Phase 2):
- T017-T020 (Data models) can run in parallel
- T021-T024 (Dapr wrappers) can run in parallel
- T026-T030 (Helm templates) can run in parallel

**User Story 1** (Phase 3):
- T032-T038 (Service skeletons) can run in parallel by different developers
- T039-T040 (Docker builds) sequential (build → load)

**User Stories 2, 3** (Phases 4-5):
- Can run fully in parallel (different features, no shared code)

**User Stories 4, 5, 6** (Phases 6-8):
- Can run in parallel after US1 infrastructure deployed

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - P1)

1. Complete **Phase 1: Setup** (Tasks T001-T009)
2. Complete **Phase 2: Foundational** (Tasks T010-T031) - **CRITICAL BLOCKER**
3. Complete **Phase 3: US1 - Deploy Kubernetes** (Tasks T032-T048)
4. Complete **Phase 4: US2 - Recurring Tasks** (Tasks T049-T059)
5. Complete **Phase 5: US3 - Reminders** (Tasks T060-T071)
6. **STOP and VALIDATE**: Test all 3 user stories independently
7. Deploy MVP to production with core features

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Ready for user story work
2. **MVP** (US1 + US2 + US3) → Test independently → Deploy (event-driven architecture + recurring tasks + reminders)
3. **Enhancement 1** (US4 - Dapr State Management) → Test independently → Deploy
4. **Enhancement 2** (US5 - Kafka Event-Driven) → Test independently → Deploy
5. **Enhancement 3** (US6 - CI/CD Pipeline) → Test independently → Deploy
6. **Enhancement 4** (US7 - Observability) → Test independently → Deploy
7. **Production Ready** (Phase 10) → Final polish → Production deployment

Each increment adds value without breaking previous stories.

### Parallel Team Strategy

With 4 developers after Foundational phase:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Kubernetes Deployment)
   - Developer B: User Story 2 (Recurring Tasks)
   - Developer C: User Story 3 (Reminders)
   - Developer D: User Story 7 (Observability - can start early)
3. **After US1 complete**:
   - Developer A: User Story 4 (Dapr State Management)
   - Developer B: User Story 5 (Kafka Event-Driven)
   - Developer C: User Story 6 (CI/CD Pipeline)
   - Developer D: Continue US7 or help others
4. **Stories complete independently** and integrate seamlessly

---

## Task Summary

**Total Tasks**: 113 tasks
- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 22 tasks (BLOCKING)
- **Phase 3 (US1 - Deploy Kubernetes, P1)**: 17 tasks (foundational infrastructure)
- **Phase 4 (US2 - Recurring Tasks, P1)**: 11 tasks (independent feature)
- **Phase 5 (US3 - Reminders, P1)**: 12 tasks (independent feature)
- **Phase 6 (US4 - Dapr State Management, P2)**: 6 tasks (architecture enhancement)
- **Phase 7 (US5 - Kafka Event-Driven, P2)**: 7 tasks (architecture enhancement)
- **Phase 8 (US6 - CI/CD Pipeline, P2)**: 8 tasks (automation)
- **Phase 9 (US7 - Observability, P3)**: 8 tasks (monitoring)
- **Phase 10 (Polish)**: 13 tasks (production readiness)

**Parallel Opportunities**: ~60% of tasks can run in parallel within their phases
**Independent Test Criteria**: Each user story has explicit independent test instructions
**MVP Scope**: Phases 1-5 (31 foundational + 40 MVP tasks = 71 tasks for core functionality)

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label (US1, US2, etc.) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All 7 user stories map to functional requirements (FR-001 through FR-047)
- Deployment parity validated through identical Helm charts for Minikube and cloud
- Event-driven architecture enforced through Kafka/Dapr Pub/Sub (no synchronous coupling)
