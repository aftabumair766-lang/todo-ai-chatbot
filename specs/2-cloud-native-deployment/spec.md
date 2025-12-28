# Feature Specification: Cloud-Native Event-Driven Todo Chatbot

**Feature Branch**: `2-cloud-native-deployment`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Build cloud-native event-driven todo chatbot with Kubernetes, Dapr, Kafka (Redpanda), including recurring tasks and reminders features. Decouple services via Dapr abstractions, use Kafka for async workflows, deploy to Minikube locally and DOKS/GKE/AKS in cloud with full CI/CD and monitoring."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Event-Driven Architecture on Kubernetes (Priority: P1)

As a DevOps engineer, I want to deploy the todo chatbot application on Kubernetes with Dapr runtime and Kafka event streaming so that the system can scale horizontally, recover from failures automatically, and process tasks asynchronously.

**Why this priority**: This is the foundational infrastructure requirement for Phase V. Without event-driven architecture on Kubernetes, none of the advanced features can be deployed in a production-grade, scalable manner. This story establishes the deployment model that all other features depend on.

**Independent Test**: Deploy all microservices to Minikube cluster with Dapr sidecars, create a task via API, verify Kafka event published to `task.created` topic, confirm consumer processes event and updates state via Dapr State Store. System continues operating after pod restart (stateless validation).

**Acceptance Scenarios**:

1. **Given** Minikube cluster with Dapr installed, **When** Helm charts deployed with `helm install todo-app`, **Then** all pods start successfully with Dapr sidecars, health checks pass, and API responds at `/health`
2. **Given** deployed system on Minikube, **When** user creates task via API, **Then** Kafka event published to `task.created` topic within 100ms, consumer receives event within 500ms, and task appears in database
3. **Given** deployed system on cloud Kubernetes (DOKS/GKE/AKS), **When** same operations performed as Minikube, **Then** identical behavior observed (deployment parity validated)
4. **Given** running pods, **When** pod killed (simulate failure), **Then** Kubernetes restarts pod within 30 seconds, Dapr sidecar reconnects, and system resumes processing without data loss
5. **Given** deployed system, **When** load balancer receives 100 concurrent requests, **Then** Kubernetes autoscaling triggers, new pods created, and all requests processed successfully

---

### User Story 2 - Create Recurring Tasks via Natural Language (Priority: P1)

As a user, I want to create recurring tasks by saying "Remind me to exercise every Monday" or "Pay bills on the 1st of every month" so that I don't have to manually create repetitive tasks each time.

**Why this priority**: Recurring tasks are a key differentiator for Phase V and represent high user value. This feature directly impacts user productivity and demonstrates the power of event-driven architecture (cron-like task generation via Kafka).

**Independent Test**: Send message "Add recurring task: team standup every weekday at 9am", verify recurring task created with cron expression `0 9 * * 1-5`, confirm Kafka event published to `recurring-task.created` topic, validate scheduler service generates individual task instances at correct times over 3 days.

**Acceptance Scenarios**:

1. **Given** authenticated user in chat, **When** user types "Remind me to exercise every Monday", **Then** chatbot creates recurring task with pattern "weekly on Monday", confirms with "I've set up a recurring reminder to exercise every Monday", and database stores recurrence rule
2. **Given** recurring task created, **When** scheduler service runs (cron-based or Kafka consumer), **Then** individual task instances generated for next 4 weeks, each published as `task.created` event to Kafka
3. **Given** user types "Pay bills on the 1st of every month", **When** AI agent parses intent, **Then** recurring task created with monthly pattern, task instances generated on 1st of each month starting next month
4. **Given** recurring task exists, **When** user completes one instance, **Then** only that instance marked complete, future instances remain pending, and Kafka event `task.completed` published for that instance only
5. **Given** user types "Stop my exercise reminder", **When** AI agent identifies recurring task by name, **Then** recurring task disabled (no new instances generated), existing instances remain, and confirmation message sent

---

### User Story 3 - Receive Task Reminders at Scheduled Times (Priority: P1)

As a user, I want to receive reminders 15 minutes before a task is due or at a specific time I set so that I'm notified proactively and can complete tasks on time.

**Why this priority**: Reminders transform the chatbot from a passive task list to an active productivity assistant. This leverages event-driven architecture (Dapr bindings for notifications) and demonstrates asynchronous processing via Kafka. Critical for user engagement and MVP completeness.

**Independent Test**: Create task "Call mom" with reminder set for 2 minutes from now, wait 2 minutes, verify Kafka event `reminder.triggered` published at correct time, notification service receives event via Dapr binding, and notification sent to user (email/SMS/webhook).

**Acceptance Scenarios**:

1. **Given** user creates task "Meeting with Sarah at 3pm", **When** user adds "remind me 15 minutes before", **Then** system calculates reminder time (2:45pm), stores reminder in Dapr State Store, schedules Kafka event for 2:45pm
2. **Given** reminder time reached (2:45pm), **When** scheduler publishes `reminder.triggered` event to Kafka, **Then** notification service consumes event within 5 seconds, sends notification via Dapr output binding (email/webhook), and logs delivery status
3. **Given** user in chat interface, **When** reminder triggered, **Then** chatbot proactively sends message "Reminder: Meeting with Sarah in 15 minutes" without user prompt
4. **Given** user completes task before reminder time, **When** task marked complete, **Then** associated reminder canceled (Kafka event `reminder.canceled` published), no notification sent at scheduled time
5. **Given** notification service unavailable, **When** reminder event published to Kafka, **Then** event remains in Kafka topic (not lost), notification service processes event when it recovers (at-least-once delivery)

---

### User Story 4 - Dapr State Management for Stateless Services (Priority: P2)

As a developer, I want all services to use Dapr State Store API instead of direct database access so that services remain stateless, database can be swapped without code changes, and state is managed consistently across all microservices.

**Why this priority**: This enforces architectural principles (Dapr abstraction over direct infrastructure) and enables true statelessness. Required for production-grade deployment but not user-facing, hence P2. Foundational for scalability.

**Independent Test**: Create task via API, verify Dapr State Store API called (not direct PostgreSQL), inspect Dapr component configuration shows PostgreSQL as state backend, swap state backend to Redis in Dapr config without code changes, verify system continues working with Redis.

**Acceptance Scenarios**:

1. **Given** task service receives create request, **When** service saves task, **Then** Dapr State Store API invoked via HTTP POST to `http://localhost:3500/v1.0/state/statestore`, no direct PostgreSQL client used in code
2. **Given** Dapr component configured with PostgreSQL backend, **When** state saved via Dapr API, **Then** data persisted to PostgreSQL `dapr_state` table with key-value structure
3. **Given** Dapr component reconfigured to use Redis, **When** services restarted (no code changes), **Then** all state operations work identically, data stored in Redis instead of PostgreSQL
4. **Given** concurrent requests to update same task, **When** multiple services attempt state updates, **Then** Dapr handles optimistic concurrency control, prevents race conditions, and ensures consistency
5. **Given** state query for user tasks, **When** service queries Dapr State Store with filter `user_id=123`, **Then** Dapr returns all tasks for that user, row-level security enforced via state query metadata

---

### User Story 5 - Kafka Event-Driven Async Workflows (Priority: P2)

As a system architect, I want all cross-service communication to use Kafka events (via Dapr Pub/Sub) instead of synchronous HTTP calls so that services are decoupled, system resilient to failures, and workflows processable asynchronously.

**Why this priority**: Core architectural requirement for event-driven design. Enables scalability and resilience but doesn't directly deliver user features, hence P2. Critical for production operations.

**Independent Test**: Create task via API, monitor Kafka topic `task.created`, verify event published with full task payload (JSON), deploy separate consumer service, confirm consumer receives event and processes independently without blocking API response.

**Acceptance Scenarios**:

1. **Given** task created via API, **When** service publishes event via Dapr Pub/Sub API `POST /v1.0/publish/pubsub/task.created`, **Then** event appears in Redpanda Kafka topic `task.created` within 100ms, API returns success without waiting for consumers
2. **Given** event published to `task.created` topic, **When** multiple consumer services subscribed (analytics service, notification service), **Then** each consumer receives copy of event independently, processes at own pace, no coupling between consumers
3. **Given** consumer service down, **When** events published to Kafka, **Then** events remain in Kafka topic (retention 7 days), consumer processes backlog when it recovers, no events lost
4. **Given** task completion event `task.completed`, **When** event published to Kafka, **Then** downstream services (analytics, reminder cancellation) react asynchronously, no synchronous dependencies, workflow completes eventually
5. **Given** Kafka broker unavailable (network partition), **When** service attempts to publish event, **Then** Dapr retries with exponential backoff, publishes when Kafka recovers, or returns error after retry limit (failure handled gracefully)

---

### User Story 6 - CI/CD Pipeline with GitHub Actions (Priority: P2)

As a development team, I want automated CI/CD pipeline that tests, builds, and deploys to Kubernetes on every commit so that deployments are consistent, fast, and reduce manual errors.

**Why this priority**: Essential for production operations and team velocity but doesn't deliver user features directly, hence P2. Required before production deployment.

**Independent Test**: Push code to GitHub branch, verify GitHub Actions workflow triggers, runs tests, builds Docker images, pushes to registry, deploys to Minikube test cluster, runs smoke tests, and reports status within 10 minutes.

**Acceptance Scenarios**:

1. **Given** code pushed to `main` branch, **When** GitHub Actions workflow `ci-backend.yml` triggers, **Then** unit tests run, integration tests run, lint checks pass, Docker image built, and workflow succeeds within 8 minutes
2. **Given** Docker image built, **When** workflow tags image with commit SHA and `latest`, **Then** image pushed to Docker registry (Docker Hub or GitHub Container Registry), available for deployment
3. **Given** tests pass and image pushed, **When** deployment workflow `deploy-cloud.yml` triggers, **Then** Helm charts deployed to Kubernetes cluster (staging environment), health checks pass, and deployment marked successful
4. **Given** tests fail in CI pipeline, **When** workflow completes, **Then** GitHub Actions marks build as failed, prevents deployment, and notifies team via GitHub notifications
5. **Given** manual approval required for production, **When** engineer approves workflow step, **Then** deployment proceeds to production Kubernetes cluster (DOKS/GKE/AKS), zero-downtime rolling update performed

---

### User Story 7 - Observability with Prometheus and Grafana (Priority: P3)

As an SRE, I want Prometheus metrics and Grafana dashboards showing service health, Kafka lag, Dapr metrics, and business KPIs so that I can monitor system performance, detect issues proactively, and troubleshoot problems quickly.

**Why this priority**: Important for production operations but not blocking for initial deployment, hence P3. Can be added incrementally after core features validated.

**Independent Test**: Deploy Prometheus and Grafana to Kubernetes, verify Dapr metrics scraped automatically, create custom Grafana dashboard, confirm metrics visible (task creation rate, Kafka consumer lag, HTTP request latency), and alerts trigger when thresholds breached.

**Acceptance Scenarios**:

1. **Given** Prometheus deployed to Kubernetes, **When** Dapr sidecars running, **Then** Prometheus scrapes Dapr metrics endpoints automatically (configured via annotations), metrics available in Prometheus query interface
2. **Given** Grafana deployed, **When** Prometheus configured as data source, **Then** Grafana dashboards show real-time metrics: HTTP request rate, latency percentiles (p50/p95/p99), Kafka consumer lag, pod CPU/memory usage
3. **Given** task created via API, **When** observing Grafana dashboard, **Then** business metrics increment: `tasks_created_total` counter, `active_users` gauge, `task_completion_rate` histogram
4. **Given** alert rule configured for high Kafka lag (>1000 messages), **When** consumer falls behind, **Then** Prometheus AlertManager triggers alert, notification sent to on-call engineer via webhook/Slack
5. **Given** production incident, **When** SRE accesses Grafana, **Then** distributed trace ID visible in logs (Dapr tracing enabled), end-to-end request flow visualized across microservices via Zipkin/Jaeger integration

---

### Edge Cases

- **Recurring task edge cases**:
  - Ambiguous recurrence patterns (e.g., "remind me every other Thursday") → AI agent asks clarifying question or defaults to simplest interpretation (every Thursday)
  - Recurrence conflicts with timezone changes (DST) → System uses UTC internally, displays in user's timezone
  - User deletes recurring task with existing instances → Prompt for confirmation: "Delete all future instances or just the template?"

- **Reminder edge cases**:
  - Reminder time in the past (e.g., "remind me yesterday") → System returns error "Reminder time must be in the future"
  - Multiple reminders for same task → Support up to 3 reminders per task, error if exceeded
  - Notification service failure → Kafka retains event, service retries on recovery (at-least-once delivery)

- **Event-driven edge cases**:
  - Kafka broker down during event publish → Dapr retries with exponential backoff (5 attempts), returns error if exhausted, event not lost if published
  - Duplicate events (Kafka redelivery) → Consumers implement idempotency keys, duplicate events ignored
  - Event schema evolution → Use Avro schema registry or versioned JSON schemas, maintain backward compatibility

- **Kubernetes edge cases**:
  - Pod eviction under resource pressure → Kubernetes reschedules pod on another node, Dapr reconnects to state/pub-sub, no data loss
  - Node failure → Kubernetes detects unhealthy node, reschedules pods to healthy nodes within 5 minutes
  - Deployment rollout failure → Helm rollback triggered automatically or manually, previous version restored

- **Dapr component edge cases**:
  - State store unavailable (PostgreSQL down) → Dapr returns 500 error, service handles gracefully with retry logic
  - Pub/Sub component misconfigured → Dapr fails to start pod, Kubernetes readiness probe fails, deployment halted
  - Secrets component failure → Dapr cannot access secrets, pod startup fails, error logged for debugging

## Requirements *(mandatory)*

### Functional Requirements

#### Cloud-Native Infrastructure

- **FR-001**: System MUST deploy to Kubernetes (Minikube for local, DOKS/GKE/AKS for cloud) with identical configurations achieving deployment parity
- **FR-002**: System MUST use Dapr runtime with sidecars for all microservices providing state management, pub/sub, service invocation, and secrets management
- **FR-003**: System MUST use Redpanda Cloud (Kafka-compatible) for event streaming with at least 3 topics: `task.created`, `task.completed`, `reminder.triggered`
- **FR-004**: System MUST define Dapr components in YAML manifests for: pub/sub (Kafka), state store (PostgreSQL), secrets (Kubernetes Secrets), and bindings (output for notifications)
- **FR-005**: All services MUST use Dapr State Store API instead of direct database clients for state persistence
- **FR-006**: All inter-service communication MUST use Dapr Pub/Sub (Kafka events) for asynchronous workflows, no synchronous HTTP coupling between services
- **FR-007**: System MUST support both local Minikube deployment and cloud Kubernetes deployment (DOKS/GKE/AKS) with same Helm charts and environment-specific values files

#### Microservices Architecture

- **FR-008**: System MUST decompose into at least 4 microservices: API Gateway (user-facing), Task Service (CRUD), Scheduler Service (recurring tasks/reminders), Notification Service (alerts)
- **FR-009**: Each microservice MUST be independently deployable with its own Helm chart or as separate release in umbrella chart
- **FR-010**: Services MUST use Dapr service invocation for synchronous calls when necessary (e.g., API Gateway → Task Service) via `http://localhost:3500/v1.0/invoke/<service-id>/method/<method-name>`
- **FR-011**: Services MUST implement health check endpoints (`/health`, `/readiness`) for Kubernetes liveness and readiness probes

#### Recurring Tasks

- **FR-012**: System MUST support natural language recurring task creation with patterns: daily, weekly (specific days), monthly (specific date), yearly
- **FR-013**: System MUST parse natural language recurrence patterns using AI agent (OpenAI Agents SDK) and convert to cron expressions or recurrence rules (iCalendar RRULE format)
- **FR-014**: System MUST store recurring task template with recurrence rule in database and generate individual task instances via scheduler service
- **FR-015**: Scheduler Service MUST run periodically (every 1 hour) or event-driven (Dapr cron binding) to generate upcoming task instances (next 7 days) based on recurrence rules
- **FR-016**: Generated task instances MUST be published as `task.created` events to Kafka, consumed by Task Service, and persisted to database
- **FR-017**: Users MUST be able to view recurring task template separately from individual instances, edit template to update future instances, or disable template to stop generation

#### Task Reminders

- **FR-018**: System MUST support adding reminders to tasks with relative time (e.g., "15 minutes before", "1 hour before") or absolute time (e.g., "at 9am tomorrow")
- **FR-019**: System MUST calculate absolute reminder time from relative expressions using task due date/time or user-specified time
- **FR-020**: Reminder Service MUST schedule reminder events by storing reminder metadata in Dapr State Store with trigger time
- **FR-021**: Scheduler Service MUST check for due reminders every 1 minute, publish `reminder.triggered` events to Kafka for reminders whose time has arrived
- **FR-022**: Notification Service MUST consume `reminder.triggered` events and send notifications via Dapr output binding (email, SMS, webhook, or in-app chat message)
- **FR-023**: System MUST cancel reminder if task completed before reminder time, publishing `reminder.canceled` event to Kafka
- **FR-024**: Users MUST be able to snooze reminders (reschedule for later) or dismiss reminders via chat commands

#### Event-Driven Workflows

- **FR-025**: System MUST publish domain events to Kafka topics for all state changes: `task.created`, `task.updated`, `task.completed`, `task.deleted`, `recurring-task.created`, `reminder.triggered`, `reminder.canceled`
- **FR-026**: Event schemas MUST be defined in JSON Schema or Avro format with versioning for schema evolution
- **FR-027**: Services MUST publish events via Dapr Pub/Sub API (`POST /v1.0/publish/<pubsub-name>/<topic>`) with CloudEvents format (standard event envelope)
- **FR-028**: Services MUST subscribe to Kafka topics via Dapr Pub/Sub subscriptions defined in YAML or programmatically via SDK
- **FR-029**: Event consumers MUST implement idempotency to handle duplicate events (Kafka at-least-once delivery semantics)
- **FR-030**: Kafka topics MUST have retention of at least 7 days to support event replay and consumer recovery after downtime

#### CI/CD Pipeline

- **FR-031**: System MUST have GitHub Actions workflows for: backend CI (test, lint, build), frontend CI (test, build), Minikube deployment, cloud deployment
- **FR-032**: Backend CI workflow MUST run unit tests, integration tests, type checks (mypy), linting (ruff), build Docker image, push to registry on success
- **FR-033**: Deployment workflows MUST deploy Helm charts to Kubernetes, wait for rollout completion, run smoke tests, report status
- **FR-034**: Production deployment MUST require manual approval step in GitHub Actions workflow before deploying to cloud Kubernetes cluster
- **FR-035**: CI/CD pipeline MUST build multi-architecture Docker images (amd64, arm64) for compatibility with different cloud providers

#### Observability & Monitoring

- **FR-036**: System MUST expose Prometheus metrics from all services via Dapr metrics endpoint (`/metrics`) and custom business metrics
- **FR-037**: System MUST deploy Prometheus operator to Kubernetes with ServiceMonitor resources for automatic metric scraping
- **FR-038**: System MUST deploy Grafana with pre-configured dashboards showing: service health, Kafka consumer lag, Dapr metrics, HTTP request latency, business KPIs (tasks created, completion rate)
- **FR-039**: System MUST configure Prometheus AlertManager with alert rules for critical conditions: high Kafka lag (>1000 messages), pod crashes, high error rate (>5%)
- **FR-040**: All services MUST use structured logging in JSON format with correlation IDs for distributed tracing
- **FR-041**: System MUST integrate Dapr tracing with Zipkin or Jaeger for end-to-end request tracing across microservices

#### Security & Compliance

- **FR-042**: All secrets (API keys, database passwords, Kafka credentials) MUST be stored in Kubernetes Secrets and accessed via Dapr secrets component
- **FR-043**: Services MUST NOT hardcode secrets in code or container images, all secrets injected at runtime via environment variables from Dapr
- **FR-044**: Inter-service communication MUST use mTLS encryption provided by Dapr service mesh capabilities
- **FR-045**: Kubernetes Network Policies MUST restrict traffic between services to only necessary communication paths
- **FR-046**: All API endpoints MUST continue to validate JWT tokens from Better Auth for user authentication
- **FR-047**: Kafka topics MUST use SASL/SCRAM authentication for Redpanda Cloud connection

### Key Entities

- **RecurringTask**: Recurring task template
  - Attributes: id, user_id, title, description, recurrence_rule (cron or RRULE format), active (boolean), next_generation_time, created_at, updated_at
  - Relationships: Belongs to User, generates many Task instances

- **TaskInstance**: Individual occurrence of a recurring task
  - Attributes: id, recurring_task_id (nullable for one-time tasks), user_id, title, description, due_date, completed, created_at, updated_at
  - Relationships: Optionally belongs to RecurringTask, belongs to User

- **Reminder**: Scheduled reminder for a task
  - Attributes: id, task_id, user_id, trigger_time (absolute timestamp), notification_channel (email, SMS, chat), status (pending, triggered, canceled), created_at
  - Relationships: Belongs to TaskInstance, belongs to User

- **Event** (Kafka messages): Domain events
  - Attributes: event_id (UUID), event_type (task.created, etc.), aggregate_id (task_id), user_id, timestamp, payload (JSON with event-specific data), schema_version
  - CloudEvents envelope: specversion, type, source, id, datacontenttype, data

- **DaprComponent**: Dapr component configuration
  - Types: pubsub (Kafka), statestore (PostgreSQL), secretstore (Kubernetes), binding.output (notification), binding.cron (scheduler)
  - Configuration: name, type, version, metadata (connection strings, authentication)

- **KubernetesPod**: Containerized service instance
  - Attributes: name, namespace, image, replicas, resource limits/requests, Dapr annotations (enabled, app-id, port)
  - Relationships: Belongs to Deployment, has Dapr sidecar

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Infrastructure & Deployment

- **SC-001**: System deploys successfully to Minikube (local) within 5 minutes from `helm install` command with all pods healthy and ready
- **SC-002**: System deploys successfully to cloud Kubernetes (DOKS/GKE/AKS) within 10 minutes with identical behavior to Minikube (deployment parity validated)
- **SC-003**: System survives pod failures with zero data loss - killing any pod results in Kubernetes restart within 30 seconds and automatic recovery without manual intervention
- **SC-004**: System scales horizontally - increasing load from 10 to 100 concurrent users triggers Kubernetes autoscaling, new pods created within 2 minutes, all requests handled successfully
- **SC-005**: Dapr components initialize successfully for all services - 100% of pods have Dapr sidecars in ready state, state store connections verified, pub/sub subscriptions active

#### Event-Driven Architecture

- **SC-006**: Task creation publishes Kafka event within 100ms - creating task via API results in `task.created` event appearing in Kafka topic before API response returns
- **SC-007**: Event consumers process events within 500ms average - time from event published to consumer processing complete is under 500ms for 95% of events
- **SC-008**: System handles 1000 events per minute without Kafka lag exceeding 100 messages - sustained load of 1000 events/min results in consumer lag staying below 100 messages
- **SC-009**: Events survive service failures - when consumer service crashes, events remain in Kafka, consumer processes backlog when restarted with zero event loss
- **SC-010**: Duplicate events handled correctly - sending same event twice (simulating Kafka redelivery) results in idempotent processing, no duplicate database records

#### Recurring Tasks & Reminders

- **SC-011**: Users create recurring tasks via natural language in under 10 seconds - typing "remind me to exercise every Monday" results in recurring task creation and confirmation within 10 seconds
- **SC-012**: Scheduler generates task instances correctly - recurring task with weekly pattern generates exactly 4 task instances over 28-day period, each published as Kafka event
- **SC-013**: Reminders trigger at correct time with 1-minute precision - setting reminder for "15 minutes before" results in notification delivered within 1 minute of calculated time
- **SC-014**: Notification delivery succeeds for 95% of reminders - 95% of `reminder.triggered` events result in successful notification delivery (email/SMS/webhook)
- **SC-015**: Completed tasks cancel future reminders - completing task before reminder time results in `reminder.canceled` event published, no notification sent

#### CI/CD & Automation

- **SC-016**: CI pipeline completes within 10 minutes - pushing code to GitHub triggers workflow that runs tests, builds image, and pushes to registry within 10 minutes
- **SC-017**: Deployments complete with zero downtime - Helm upgrade performs rolling update, old pods remain serving traffic until new pods ready, zero dropped requests
- **SC-018**: Failed deployments rollback automatically - if health checks fail after deployment, Kubernetes rollback triggers within 5 minutes, previous version restored
- **SC-019**: 100% of commits have passing CI before merge - GitHub branch protection requires CI success, prevents merging broken code

#### Observability & Monitoring

- **SC-020**: Prometheus collects metrics from all services - 100% of deployed pods have metrics scraped successfully, metrics visible in Prometheus UI
- **SC-021**: Grafana dashboards show real-time data - business metrics (tasks created, reminders sent) update within 15 seconds of actual events
- **SC-022**: Alerts trigger within 2 minutes of threshold breach - when Kafka lag exceeds 1000 messages, Prometheus alert fires within 2 minutes, notification sent to on-call
- **SC-023**: Distributed traces span all microservices - creating task via API generates trace ID, visible in Zipkin/Jaeger showing request flow through API Gateway → Task Service → Kafka → Consumer
- **SC-024**: Logs searchable and correlated - all logs in JSON format, searchable by trace ID, error logs include full context for debugging

#### Security & Reliability

- **SC-025**: Zero secrets exposed in code or images - scanning Docker images and GitHub repo shows no hardcoded API keys, passwords, or tokens
- **SC-026**: All inter-service communication encrypted - network traffic between services uses mTLS (Dapr service mesh enabled), verified via traffic inspection
- **SC-027**: System maintains 99.9% uptime over 30-day period - less than 43 minutes downtime per month in production environment
- **SC-028**: Backup and disaster recovery tested - simulating database failure results in recovery from backup within 1 hour, data loss limited to last 5 minutes

## Assumptions

- **Assumption 1**: Phase I-IV implementation (basic todo chatbot with MCP + OpenAI Agents SDK) is complete and working
- **Assumption 2**: Redpanda Cloud account provisioned with Kafka cluster accessible via SASL/SCRAM authentication
- **Assumption 3**: Kubernetes cluster available (Minikube for local, DOKS/GKE/AKS for cloud) with sufficient resources: 4 CPU cores, 8GB RAM minimum
- **Assumption 4**: Dapr CLI installed locally for Minikube setup (`dapr init -k` command available)
- **Assumption 5**: Docker registry available (Docker Hub, GitHub Container Registry, or cloud provider registry) for storing images
- **Assumption 6**: GitHub Actions enabled for repository with sufficient runner minutes
- **Assumption 7**: Prometheus and Grafana deployable via Helm charts (kube-prometheus-stack or similar)
- **Assumption 8**: DNS and load balancer configuration handled by cloud provider for production deployments
- **Assumption 9**: SSL/TLS certificates managed via cert-manager or cloud provider for HTTPS ingress
- **Assumption 10**: Notification channels (email/SMS providers) configured with API keys for reminder delivery
- **Assumption 11**: Development team familiar with Kubernetes, Helm, and Dapr concepts
- **Assumption 12**: Natural language parsing for recurrence patterns handled by OpenAI Agents SDK (no custom NLP required)

## Out of Scope

- Multi-tenant isolation (single organization deployment assumed)
- Custom Kafka schema registry (using JSON Schema in code, not Confluent Schema Registry)
- Advanced Dapr features: actors, workflows, distributed lock
- Service mesh beyond Dapr (Istio, Linkerd not required)
- Custom Kubernetes operators
- Multi-region or multi-cloud deployment (single region assumed)
- Cost optimization and FinOps analysis
- Performance testing and load testing automation
- Blue-green or canary deployment strategies (rolling updates only)
- Backup automation (manual backup procedures acceptable for MVP)
- Log aggregation platform (ELK, Loki - logs accessible via kubectl only)
- APM tools (New Relic, Datadog - Prometheus/Grafana only)
- Chaos engineering and fault injection testing
- Compliance certifications (SOC2, HIPAA, etc.)
- Mobile app or desktop client (web interface only)
- Real-time collaborative editing of tasks
- Task attachments or file uploads
- Integration with external calendars (Google Calendar, Outlook)
- Voice input for task creation
- AI-powered task prioritization or suggestions

## Dependencies

- **External Service**: Redpanda Cloud (Kafka cluster) with connection credentials and SASL/SCRAM authentication
- **Infrastructure**: Kubernetes cluster (Minikube for local, DOKS/GKE/AKS for cloud) with kubectl access
- **Runtime**: Dapr runtime installed on Kubernetes cluster (`dapr init -k` completed)
- **Container Registry**: Docker registry (Docker Hub, GHCR, or cloud provider) with push access
- **CI/CD**: GitHub Actions with access to repository and Docker registry credentials
- **Database**: Neon PostgreSQL (from Phase I-IV) continues as state backend
- **Monitoring**: Prometheus and Grafana Helm charts (kube-prometheus-stack recommended)
- **Secrets Management**: Kubernetes Secrets or external secrets manager (AWS Secrets Manager, Azure Key Vault)
- **Notification Provider**: Email service (SendGrid, AWS SES) or SMS service (Twilio) with API keys
- **Phase I-IV**: All Phase I-IV components (FastAPI backend, OpenAI Agents SDK, MCP tools, Better Auth) must be functional

## Risks

- **Risk 1**: Dapr learning curve steep for team → Mitigation: Hands-on Dapr workshop, use official quickstarts, pair programming
- **Risk 2**: Redpanda Cloud costs exceed budget → Mitigation: Monitor usage, set alerts, consider self-hosted Kafka on Kubernetes if needed
- **Risk 3**: Kubernetes resource constraints on Minikube → Mitigation: Allocate 4 CPU / 8GB RAM minimum, use resource limits/requests
- **Risk 4**: Event-driven complexity introduces debugging challenges → Mitigation: Comprehensive logging, distributed tracing, event replay tools
- **Risk 5**: Kafka message ordering issues for task updates → Mitigation: Use partitioning by user_id, document ordering guarantees
- **Risk 6**: CI/CD pipeline failures block deployments → Mitigation: Fail-fast tests, parallel jobs, deployment rollback automation
- **Risk 7**: Dapr component misconfiguration prevents pod startup → Mitigation: Validate Dapr components in CI, use Dapr dashboard for debugging
- **Risk 8**: Network policies too restrictive, break service communication → Mitigation: Start permissive, incrementally tighten, test thoroughly
- **Risk 9**: Prometheus storage fills disk → Mitigation: Configure retention (15 days), use remote storage (Thanos) if needed
- **Risk 10**: Migration from Phase I-IV monolith to microservices requires significant refactoring → Mitigation: Incremental migration, strangler fig pattern, maintain backward compatibility

## Quality Requirements

**Production-Grade Standards** (per Constitution Principle III and Phase V requirements):

- Zero runtime errors in deployed services
- No TODOs or placeholders in production code
- Full type hints (Python typing) for all functions
- Clear comments explaining Dapr, Kafka, and event-driven logic
- Defensive error handling with circuit breakers for external services
- 100% reproducible deployments (Helm charts, Dockerfiles, CI/CD workflows)
- Comprehensive tests: unit (mocked Dapr/Kafka), integration (real Dapr/Kafka), end-to-end (deployed to Kubernetes)
- Structured logging with correlation IDs across all services
- All Kubernetes manifests pass `kubectl apply --dry-run=server --validate=true`
- All Dapr components validated with `dapr components` command
- All Helm charts validated with `helm lint` passing with zero warnings
- All Docker images scanned for vulnerabilities (Trivy or similar) with zero high/critical CVEs
- README.md and CLAUDE.md updated with Phase V setup instructions
- Runbook documentation for common operational tasks (deployment, rollback, debugging)
