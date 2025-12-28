# Phase V Research: Cloud-Native Microservices with Dapr, Kafka, and Kubernetes

**Academic Assignment - Phase V: Production-Ready Cloud-Native Deployment**

This research document provides comprehensive integration patterns for deploying a cloud-native microservices architecture using Dapr, Kafka (Redpanda), Kubernetes, Helm, and observability tools.

---

## Table of Contents

1. [Dapr + FastAPI Integration](#1-dapr--fastapi-integration)
2. [Dapr + Kafka (Redpanda) Pub/Sub](#2-dapr--kafka-redpanda-pubsub)
3. [Microservices Decomposition Strategy](#3-microservices-decomposition-strategy)
4. [Kubernetes + Dapr Deployment](#4-kubernetes--dapr-deployment)
5. [Helm Charts for Dapr-enabled Microservices](#5-helm-charts-for-dapr-enabled-microservices)
6. [GitHub Actions CI/CD for Kubernetes](#6-github-actions-cicd-for-kubernetes)
7. [Prometheus + Grafana for Dapr Monitoring](#7-prometheus--grafana-for-dapr-monitoring)
8. [References](#references)

---

## 1. Dapr + FastAPI Integration

### Decision

**Adopt Dapr sidecar pattern with FastAPI using the official `dapr-ext-fastapi` Python SDK extension.**

### Rationale

- **Abstraction of Infrastructure Concerns**: Dapr sidecars handle service discovery, mTLS encryption, retries, and observability without application code changes
- **Polyglot Support**: Enables seamless communication between Python FastAPI services and other language services (e.g., .NET, Go)
- **Built-in mTLS**: Automatic mutual TLS for all service-to-service calls with certificate rotation (24-hour validity by default)
- **Production-Ready**: Used at scale by companies like CNCF members, with active community support

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Dapr Sidecar** | Platform-agnostic, mTLS, retries, observability | Additional sidecar container overhead | **✅ Chosen** |
| **Direct HTTP Calls** | Simple, no extra dependencies | Manual service discovery, no mTLS, manual retries | ❌ Not scalable |
| **Service Mesh (Istio)** | Advanced traffic management, security | Complex setup, steep learning curve | ❌ Overkill for this use case |

### Implementation Details

#### Installation

```bash
# Install Dapr Python SDK with FastAPI extension
pip install dapr dapr-ext-fastapi

# Requirements.txt
dapr==1.13.0
dapr-ext-fastapi==1.13.0
fastapi==0.109.0
uvicorn==0.27.0
```

#### FastAPI Service with Dapr Integration

```python
# backend/main.py - FastAPI with Dapr
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient

app = FastAPI(title="Todo Task Service")
dapr_app = DaprApp(app)

# Service-to-service invocation using Dapr
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    # Direct database access (will migrate to Dapr State Store)
    async with db_session() as session:
        task = await session.get(Task, task_id)
        return task

# Invoke another service via Dapr sidecar
@app.post("/tasks/{task_id}/notify")
async def notify_task_created(task_id: int):
    with DaprClient() as client:
        # Dapr handles service discovery, retries, mTLS
        response = client.invoke_method(
            app_id="notification-service",
            method_name="send-notification",
            data={"task_id": task_id, "event": "task.created"},
            http_verb="POST"
        )
        return {"status": "notified", "response": response.text()}
```

#### Converting SQLModel to Dapr State Store

**Current Approach (Direct PostgreSQL)**:
```python
# Current: Direct database access
async with db_session() as session:
    task = Task(title="Buy groceries", user_id=user_id)
    session.add(task)
    await session.commit()
```

**Dapr State Store Approach**:
```python
from dapr.clients import DaprClient

# Using Dapr State Store API
with DaprClient() as client:
    # Save state (Dapr handles PostgreSQL connection)
    client.save_state(
        store_name="statestore",
        key=f"task-{task_id}",
        value={
            "title": "Buy groceries",
            "user_id": user_id,
            "status": "pending"
        },
        state_metadata={"contentType": "application/json"}
    )

    # Retrieve state
    state = client.get_state(store_name="statestore", key=f"task-{task_id}")
    task_data = state.json()
```

**Migration Strategy**:
1. **Phase 1**: Keep SQLModel for complex queries, use Dapr for service invocation only
2. **Phase 2**: Migrate simple CRUD operations to Dapr State Store
3. **Phase 3**: Use SQLModel for reporting/analytics, Dapr State Store for transactional data

### Dapr Configuration for FastAPI

```yaml
# dapr-config.yaml - Dapr configuration
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
  metric:
    enabled: true
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

### References

- [Dapr Python SDK integration with FastAPI](https://docs.dapr.io/developing-applications/sdks/python/python-sdk-extensions/python-fastapi/)
- [Dapr sidecar overview](https://docs.dapr.io/concepts/dapr-services/sidecar/)
- [Service invocation overview](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/service-invocation-overview/)

### Risks/Tradeoffs

- **Additional Latency**: Sidecar introduces ~1-2ms latency per request (acceptable for most use cases)
- **Resource Overhead**: Each pod requires additional sidecar container (~50-100MB memory)
- **Learning Curve**: Team needs to understand Dapr concepts (components, building blocks)
- **State Store Limitations**: Dapr State Store doesn't support complex SQL queries (keep SQLModel for analytics)

---

## 2. Dapr + Kafka (Redpanda) Pub/Sub

### Decision

**Use Dapr Pub/Sub component with Redpanda (Kafka-compatible) for asynchronous event-driven communication.**

### Rationale

- **CloudEvents Standard**: Dapr automatically wraps messages in CloudEvents format (industry standard)
- **At-Least-Once Delivery**: Built-in retries and dead-letter topics for reliability
- **Technology Agnostic**: Switch from Redpanda to RabbitMQ/Azure Service Bus without code changes
- **Built-in Observability**: Automatic tracing and metrics for pub/sub operations

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Dapr Pub/Sub** | CloudEvents, portability, observability | Abstraction overhead | **✅ Chosen** |
| **Direct Kafka Client** | Full Kafka control, optimized performance | Vendor lock-in, manual CloudEvents | ❌ Not portable |
| **Celery + Redis** | Familiar Python tool, simple | Not event-driven, lacks CloudEvents | ❌ Not cloud-native |

### Implementation Details

#### Dapr Kafka/Redpanda Component Configuration

```yaml
# components/kafka-pubsub.yaml - Dapr Kafka Pub/Sub Component
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Redpanda Cloud connection (Kafka-compatible)
    - name: brokers
      value: "redpanda-cluster.cloud.redpanda.com:9092"
    - name: consumerGroup
      value: "todo-task-service"
    - name: clientId
      value: "todo-task-service"
    - name: authType
      value: "certificate"  # Or "password" for SASL
    - name: consumeRetryInterval
      value: "200ms"
    - name: maxMessageBytes
      value: "1048576"  # 1MB
    # CloudEvents configuration (default is enabled)
    - name: cloudEventType
      value: "com.todo.task.v1"
```

#### Publishing Events (FastAPI Producer)

```python
# backend/services/task_service.py
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI

app = FastAPI()
dapr_app = DaprApp(app)

@app.post("/tasks")
async def create_task(task: TaskCreate):
    # 1. Save task to database
    async with db_session() as session:
        new_task = Task(**task.dict())
        session.add(new_task)
        await session.commit()

    # 2. Publish event via Dapr (automatically wrapped in CloudEvents)
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="task-events",
            topic_name="task.created",
            data={
                "task_id": new_task.id,
                "user_id": new_task.user_id,
                "title": new_task.title,
                "timestamp": datetime.utcnow().isoformat()
            },
            data_content_type="application/json"
        )

    return {"status": "created", "task_id": new_task.id}
```

#### Subscribing to Events (Declarative YAML)

```yaml
# components/subscription.yaml - Declarative subscription
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-created-subscription
spec:
  pubsubname: task-events
  topic: task.created
  routes:
    default: /events/task-created
  scopes:
  - notification-service
  deadLetterTopic: task.created.dlq
  bulkSubscribe:
    enabled: true
    maxMessagesCount: 100
    maxAwaitDurationMs: 1000
```

#### Consuming Events (FastAPI Subscriber)

```python
# notification-service/main.py
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from cloudevents.sdk.event import v1

app = FastAPI()
dapr_app = DaprApp(app)

# Subscribe to topic using decorator
@dapr_app.subscribe(pubsub_name="task-events", topic="task.created")
async def on_task_created(event: v1.Event):
    """
    Handle task.created events
    CloudEvents envelope automatically unwrapped by Dapr
    """
    task_data = event.data
    task_id = task_data["task_id"]

    # Idempotency check (critical for at-least-once delivery)
    if await is_already_processed(task_id, event.id):
        print(f"Event {event.id} already processed, skipping")
        return {"status": "duplicate"}

    # Process event
    await send_notification(
        user_id=task_data["user_id"],
        message=f"Task created: {task_data['title']}"
    )

    # Store event ID to prevent duplicate processing
    await mark_as_processed(task_id, event.id)

    return {"status": "success"}

# Idempotency helper (using Redis or database)
async def is_already_processed(task_id: int, event_id: str) -> bool:
    with DaprClient() as client:
        state = client.get_state(
            store_name="statestore",
            key=f"event-{event_id}"
        )
        return state.data is not None

async def mark_as_processed(task_id: int, event_id: str):
    with DaprClient() as client:
        client.save_state(
            store_name="statestore",
            key=f"event-{event_id}",
            value={"processed_at": datetime.utcnow().isoformat(), "task_id": task_id}
        )
```

#### CloudEvents Format

Dapr automatically wraps your data in CloudEvents:

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.v1",
  "source": "task-service",
  "id": "A234-1234-1234",
  "time": "2025-01-15T12:34:56Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries",
    "timestamp": "2025-01-15T12:34:56Z"
  }
}
```

### Idempotency Handling Strategy

**Problem**: At-least-once delivery means consumers may receive duplicate messages.

**Solution**: Implement idempotency using event IDs:

```python
# Pattern 1: Event ID tracking (recommended)
@dapr_app.subscribe(pubsub_name="task-events", topic="task.completed")
async def on_task_completed(event: v1.Event):
    event_id = event.id  # CloudEvents unique ID

    # Check if already processed
    if await event_store.exists(event_id):
        return {"status": "duplicate"}

    # Process event
    await update_analytics(event.data)

    # Mark as processed
    await event_store.save(event_id, timestamp=datetime.utcnow())

# Pattern 2: Inbox pattern (for critical operations)
async def inbox_pattern_handler(event: v1.Event):
    async with db.transaction():
        # 1. Insert into inbox table (unique constraint on event_id)
        try:
            await db.execute(
                "INSERT INTO event_inbox (event_id, payload, status) VALUES ($1, $2, 'pending')",
                event.id, event.data
            )
        except UniqueViolation:
            return {"status": "duplicate"}

        # 2. Process event
        await process_event(event.data)

        # 3. Mark as completed
        await db.execute(
            "UPDATE event_inbox SET status='completed' WHERE event_id=$1",
            event.id
        )
```

### References

- [Dapr Pub/Sub with CloudEvents](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-cloudevents/)
- [Apache Kafka component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [At-least-once delivery with Dapr](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-overview/)

### Risks/Tradeoffs

- **At-Least-Once Only**: No exactly-once delivery (must implement idempotency in application)
- **CloudEvents Overhead**: Additional metadata increases message size (~200 bytes)
- **Redpanda Compatibility**: While Kafka-compatible, some advanced Kafka features may not work
- **Consumer Group Management**: Must carefully design consumer groups to avoid duplicate processing

---

## 3. Microservices Decomposition Strategy

### Decision

**Decompose monolithic FastAPI app into 4 microservices based on Domain-Driven Design (DDD) bounded contexts.**

### Rationale

- **Single Responsibility**: Each service handles one business domain
- **Independent Deployment**: Services can be updated without affecting others
- **Technology Freedom**: Each service can use optimal tech stack (Python, Go, etc.)
- **Fault Isolation**: Failures in one service don't cascade to others

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **DDD Bounded Contexts** | Clear boundaries, scalable | Requires careful design | **✅ Chosen** |
| **By Technical Layer** | Simple to understand | High coupling, hard to scale | ❌ Poor separation |
| **By CRUD Operations** | Easy to implement | Violates SRP, not domain-driven | ❌ Not maintainable |

### Proposed Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Service                     │
│  - Authentication (JWT validation)                          │
│  - Rate limiting (10 req/min per user)                      │
│  - Request routing to backend services                      │
│  - CORS handling                                            │
│  Technology: FastAPI + Dapr service invocation              │
└────────────────────┬────────────────────────────────────────┘
                     │ (Dapr service invocation)
        ┌────────────┼────────────┬───────────────┐
        │            │            │               │
┌───────▼────┐ ┌────▼─────┐ ┌────▼──────┐ ┌─────▼─────────┐
│   Task     │ │Scheduler │ │Notification│ │  Analytics    │
│  Service   │ │ Service  │ │  Service   │ │   Service     │
│            │ │          │ │            │ │               │
│ - CRUD ops │ │- Cron    │ │- Email/SMS │ │- Reporting    │
│ - Business │ │  jobs    │ │- Push notif│ │- Metrics      │
│   rules    │ │- Remind  │ │- Webhooks  │ │- Dashboards   │
│            │ │  users   │ │            │ │               │
│ FastAPI    │ │FastAPI   │ │ FastAPI/Go │ │  Python/Go    │
└────┬───────┘ └────┬─────┘ └────┬───────┘ └───────┬───────┘
     │              │              │                 │
     │ (State)      │ (State)      │                 │ (Read-only)
     ▼              ▼              ▼                 ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐    ┌──────────────┐
│Tasks DB     │ │Scheduler │ │   -      │    │Analytics DB  │
│(PostgreSQL) │ │DB (Redis)│ │(Stateless│    │(PostgreSQL)  │
└─────────────┘ └──────────┘ └──────────┘    └──────────────┘
     │                                              ▲
     │         ┌────────────────────────┐           │
     └────────►│  Kafka Event Bus       │───────────┘
               │  (Redpanda)            │
               │  - task.created        │
               │  - task.completed      │
               │  - task.deleted        │
               └────────────────────────┘
```

### Domain Boundaries

#### 1. API Gateway Service

**Bounded Context**: External interface and cross-cutting concerns

**Responsibilities**:
- JWT authentication (validate Better Auth tokens)
- Rate limiting (Redis-backed)
- Request routing (Dapr service invocation)
- CORS configuration

**Database**: None (stateless)

**Example Code**:
```python
# api-gateway/main.py
from fastapi import FastAPI, Depends
from dapr.clients import DaprClient

app = FastAPI()

@app.post("/api/tasks")
async def create_task_proxy(task: TaskCreate, user=Depends(get_current_user)):
    # Route to Task Service via Dapr
    with DaprClient() as client:
        response = client.invoke_method(
            app_id="task-service",
            method_name="tasks",
            data=task.dict(),
            http_verb="POST",
            metadata={"user_id": user.id}
        )
        return response.json()
```

#### 2. Task Service

**Bounded Context**: Core task management domain

**Responsibilities**:
- CRUD operations for tasks
- Business rules (validation, constraints)
- Task state transitions
- Publishing domain events

**Database**: PostgreSQL (tasks table with user_id, title, status, etc.)

**Example Code**:
```python
# task-service/main.py
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@app.post("/tasks")
async def create_task(task: TaskCreate):
    # 1. Validate and save
    async with db_session() as session:
        new_task = Task(**task.dict())
        session.add(new_task)
        await session.commit()

    # 2. Publish event
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="task-events",
            topic_name="task.created",
            data={"task_id": new_task.id, "user_id": new_task.user_id}
        )

    return new_task
```

#### 3. Scheduler Service

**Bounded Context**: Time-based operations and reminders

**Responsibilities**:
- Cron job scheduling
- Reminder notifications (check due dates)
- Recurring task creation

**Database**: Redis (lightweight, cron job metadata)

**Example Code**:
```python
# scheduler-service/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dapr.clients import DaprClient

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=5)
async def check_due_tasks():
    # 1. Query Task Service for due tasks
    with DaprClient() as client:
        tasks = client.invoke_method(
            app_id="task-service",
            method_name="tasks/due",
            http_verb="GET"
        ).json()

    # 2. Publish reminder events
    for task in tasks:
        client.publish_event(
            pubsub_name="task-events",
            topic_name="task.reminder",
            data={"task_id": task["id"]}
        )

scheduler.start()
```

#### 4. Notification Service

**Bounded Context**: User communication

**Responsibilities**:
- Send email/SMS notifications
- Push notifications
- Webhook integrations

**Database**: None (stateless, consumes events)

**Example Code**:
```python
# notification-service/main.py
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub_name="task-events", topic="task.created")
async def notify_task_created(event: v1.Event):
    task_id = event.data["task_id"]
    user_id = event.data["user_id"]

    # Send notification (email, SMS, push, etc.)
    await send_email(
        to=get_user_email(user_id),
        subject="Task Created",
        body=f"Your task #{task_id} was created"
    )

    return {"status": "notified"}
```

### Database Strategy: Database per Service vs Shared Database

**Decision**: **Database per Service** (with exceptions)

| Service | Database Strategy | Rationale |
|---------|------------------|-----------|
| **Task Service** | **Dedicated PostgreSQL** | Core domain, needs transactional integrity |
| **Scheduler Service** | **Redis** | Lightweight, cron metadata only |
| **Notification Service** | **None (Stateless)** | Event-driven, no persistent state |
| **Analytics Service** | **Shared Read-Replica** | Read-only, aggregates from Task Service DB |

**Tradeoffs**:

| Aspect | Database per Service | Shared Database |
|--------|---------------------|-----------------|
| **Autonomy** | ✅ High (independent schema changes) | ❌ Low (coordination required) |
| **Transactions** | ❌ Complex (distributed transactions) | ✅ Simple (ACID guarantees) |
| **Scalability** | ✅ Scale independently | ❌ Single bottleneck |
| **Data Consistency** | ❌ Eventual consistency | ✅ Immediate consistency |
| **Operational Overhead** | ❌ High (multiple DBs to manage) | ✅ Low (one DB) |

**For Todo App**: Use **Database per Service** for Task/Scheduler, **Shared Read-Replica** for Analytics (acceptable tradeoff).

### Shared Code Strategy

**Problem**: Avoid duplicating common code (e.g., auth middleware, Pydantic models)

**Solution**: Create shared Python package

```python
# shared-lib/setup.py
from setuptools import setup

setup(
    name="todo-shared",
    version="1.0.0",
    packages=["todo_shared"],
    install_requires=["pydantic", "fastapi"]
)

# shared-lib/todo_shared/models.py
from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str | None = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: str

# Install in each service
# pip install -e ../shared-lib
```

### References

- [FastAPI Microservice Patterns: Domain Driven Design](https://python.plainenglish.io/fastapi-microservice-patterns-domain-driven-design-e99f6f475691)
- [Decompose by subdomain pattern](https://microservices.io/patterns/decomposition/decompose-by-subdomain.html)
- [Database per service pattern](https://microservices.io/patterns/data/database-per-service.html)
- [Identify microservice boundaries - Azure Architecture](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries)

### Risks/Tradeoffs

- **Distributed Transactions**: No ACID across services (use Saga pattern or accept eventual consistency)
- **Network Latency**: Multiple service calls slower than monolith (mitigate with caching)
- **Operational Complexity**: More services to deploy, monitor, and debug
- **Data Duplication**: Some data duplicated across services (acceptable for performance)

---

## 4. Kubernetes + Dapr Deployment

### Decision

**Deploy Dapr-enabled microservices on Kubernetes using Dapr annotations and Helm charts.**

### Rationale

- **Kubernetes-Native**: Dapr designed for Kubernetes with first-class support
- **Automatic Sidecar Injection**: Dapr operator injects sidecars based on annotations
- **Component Scoping**: Dapr components can be scoped to specific namespaces/apps
- **Production Best Practices**: Dapr provides guidelines for resource limits, security

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Dapr on Kubernetes** | Native integration, auto sidecar injection | Requires Kubernetes knowledge | **✅ Chosen** |
| **Dapr Self-Hosted** | Simple local dev, no K8s needed | Not production-ready | ❌ Dev only |
| **No Dapr (Plain K8s)** | Full control, no abstraction | Manual mTLS, service discovery | ❌ Too manual |

### Implementation Details

#### Initialize Dapr on Kubernetes

```bash
# Install Dapr on Kubernetes cluster
dapr init -k

# Verify installation
dapr status -k

# Output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
#   dapr-dashboard         dapr-system  True     Running  1         1.13.0   5m
#   dapr-sentry            dapr-system  True     Running  1         1.13.0   5m
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.13.0   5m
#   dapr-operator          dapr-system  True     Running  1         1.13.0   5m
#   dapr-placement-server  dapr-system  True     Running  1         1.13.0   5m

# For development, include Redis and Zipkin
dapr init -k --dev
```

#### Dapr-Enabled Kubernetes Deployment

```yaml
# k8s/task-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-service
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: task-service
  template:
    metadata:
      labels:
        app: task-service
      annotations:
        # Dapr annotations (required)
        dapr.io/enabled: "true"                    # Enable Dapr sidecar
        dapr.io/app-id: "task-service"             # Unique app ID for service invocation
        dapr.io/app-port: "8000"                   # Port your app listens on
        dapr.io/config: "dapr-config"              # Dapr configuration

        # Optional Dapr annotations
        dapr.io/log-level: "info"                  # Dapr sidecar log level
        dapr.io/enable-profiling: "false"          # Profiling endpoint
        dapr.io/enable-metrics: "true"             # Prometheus metrics
        dapr.io/metrics-port: "9090"               # Metrics port
        dapr.io/enable-debug: "false"              # Debug mode
        dapr.io/sidecar-cpu-limit: "1000m"         # CPU limit for sidecar
        dapr.io/sidecar-memory-limit: "512Mi"      # Memory limit for sidecar
        dapr.io/sidecar-cpu-request: "100m"        # CPU request
        dapr.io/sidecar-memory-request: "256Mi"    # Memory request
    spec:
      containers:
      - name: task-service
        image: todo-task-service:v1.0.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: task-service-secrets
              key: database-url
        - name: DAPR_HTTP_PORT
          value: "3500"  # Dapr sidecar HTTP port
        - name: DAPR_GRPC_PORT
          value: "50001"  # Dapr sidecar gRPC port
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### Dapr Components (State Store + Pub/Sub)

```yaml
# k8s/components/statestore.yaml - PostgreSQL State Store
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v2
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connection-string
  - name: timeout
    value: "20"
  - name: tablePrefix
    value: "dapr_"
scopes:
- task-service  # Only task-service can access this component
---
# k8s/components/pubsub.yaml - Kafka Pub/Sub
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-cluster:9092"
  - name: consumerGroup
    value: "todo-services"
  - name: authType
    secretKeyRef:
      name: kafka-secret
      key: auth-type
scopes:
- task-service
- notification-service
- scheduler-service
```

#### Secrets and ConfigMaps

**Best Practices**:
1. **Use Kubernetes Secrets for sensitive data** (API keys, passwords, certificates)
2. **Use ConfigMaps for non-sensitive config** (feature flags, API endpoints)
3. **Leverage Dapr Secret Store** for automatic secret management

```yaml
# k8s/secrets.yaml - Kubernetes Secret
apiVersion: v1
kind: Secret
metadata:
  name: task-service-secrets
  namespace: todo-app
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BuZW9uLnRlY2gvdG9kb2Ri  # base64 encoded
  openai-api-key: c2stcHJvai14eHh4eHh4  # base64 encoded
---
# k8s/configmap.yaml - ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: task-service-config
  namespace: todo-app
data:
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
  RATE_LIMIT_PER_MINUTE: "10"
```

**Using ConfigMaps and Secrets in Deployment**:

```yaml
spec:
  containers:
  - name: task-service
    envFrom:
    - configMapRef:
        name: task-service-config  # Load all ConfigMap keys as env vars
    - secretRef:
        name: task-service-secrets  # Load all Secret keys as env vars
```

**Dapr Secret Store Integration**:

```yaml
# components/secretstore.yaml - Kubernetes Secret Store
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secretstore
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

```python
# Access secrets via Dapr
from dapr.clients import DaprClient

with DaprClient() as client:
    secret = client.get_secret(
        store_name="kubernetes-secretstore",
        key="database-url",
        secret_name="task-service-secrets"
    )
    DATABASE_URL = secret.secret["database-url"]
```

### Component Organization Strategy

**Decision**: Single file for all components in development, per-component files in production.

**Development** (single file for simplicity):
```yaml
# components/components.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
```

**Production** (organized by type):
```
k8s/
├── components/
│   ├── statestore.yaml
│   ├── pubsub-kafka.yaml
│   ├── secretstore.yaml
│   └── configuration.yaml
├── deployments/
│   ├── task-service.yaml
│   ├── notification-service.yaml
│   └── scheduler-service.yaml
└── base/
    ├── namespace.yaml
    ├── configmaps.yaml
    └── secrets.yaml
```

### References

- [Deploy Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/)
- [Dapr Kubernetes annotations](https://docs.dapr.io/reference/arguments-annotations-overview/)
- [Kubernetes secrets in Dapr](https://docs.dapr.io/reference/components-reference/supported-secret-stores/kubernetes-secret-store/)
- [Production guidelines](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-production/)

### Risks/Tradeoffs

- **Resource Overhead**: Each sidecar adds ~50-100MB memory per pod
- **Component Configuration Complexity**: YAML proliferation (mitigate with Helm)
- **RBAC Requirements**: Dapr needs cluster-level permissions for sidecar injection
- **mTLS Certificate Management**: Requires Dapr Sentry service (default 1-year root cert)

---

## 5. Helm Charts for Dapr-enabled Microservices

### Decision

**Use umbrella chart pattern with shared common templates for DRY microservices deployment.**

### Rationale

- **Reusability**: Common chart reduces duplication across services
- **Environment Management**: Single values file per environment (dev, staging, prod)
- **Atomic Deployments**: Deploy entire system with `helm install umbrella-chart`
- **Version Control**: Helm chart versions track deployment history

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Umbrella Chart** | Single deployment, shared config | Complex initial setup | **✅ Chosen** |
| **Separate Charts** | Simple, independent services | Duplicate templates, hard to manage | ❌ Not DRY |
| **Kustomize** | YAML overlays, no templating | Less flexible, no versioning | ❌ Limited reuse |

### Implementation Details

#### Directory Structure

```
helm/
├── todo-umbrella/              # Umbrella chart (parent)
│   ├── Chart.yaml
│   ├── values.yaml             # Global values
│   ├── values-dev.yaml         # Dev environment overrides
│   ├── values-prod.yaml        # Production overrides
│   └── charts/                 # Subcharts
│       ├── task-service/
│       ├── notification-service/
│       └── scheduler-service/
│
└── common/                     # Shared templates
    ├── Chart.yaml
    ├── templates/
    │   ├── _deployment.yaml    # Reusable deployment template
    │   ├── _service.yaml       # Reusable service template
    │   ├── _configmap.yaml     # Reusable ConfigMap template
    │   └── _helpers.tpl        # Helper functions
    └── values.yaml
```

#### Umbrella Chart Configuration

```yaml
# helm/todo-umbrella/Chart.yaml
apiVersion: v2
name: todo-umbrella
description: Complete Todo AI Chatbot microservices stack
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: task-service
    version: 1.0.0
    repository: file://../charts/task-service
    condition: task-service.enabled

  - name: notification-service
    version: 1.0.0
    repository: file://../charts/notification-service
    condition: notification-service.enabled

  - name: scheduler-service
    version: 1.0.0
    repository: file://../charts/scheduler-service
    condition: scheduler-service.enabled

  - name: common
    version: 1.0.0
    repository: file://../common
```

```yaml
# helm/todo-umbrella/values.yaml - Global values
global:
  namespace: todo-app
  environment: production

  # Dapr configuration
  dapr:
    enabled: true
    logLevel: info
    metricsEnabled: true
    mtlsEnabled: true

  # Image registry
  imageRegistry: ghcr.io/yourusername
  imagePullPolicy: IfNotPresent

  # Database
  database:
    host: neon.tech
    port: 5432
    name: tododb

  # Kafka/Redpanda
  kafka:
    brokers: redpanda-cluster:9092
    consumerGroup: todo-services

# Service-specific overrides
task-service:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-task-service
    tag: v1.0.0
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  dapr:
    appId: task-service
    appPort: 8000

notification-service:
  enabled: true
  replicaCount: 1
  image:
    repository: todo-notification-service
    tag: v1.0.0
  resources:
    requests:
      cpu: 50m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  dapr:
    appId: notification-service
    appPort: 8001

scheduler-service:
  enabled: true
  replicaCount: 1
  image:
    repository: todo-scheduler-service
    tag: v1.0.0
```

#### Common Chart Templates

```yaml
# helm/common/templates/_deployment.yaml
{{- define "common.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.name }}
  namespace: {{ .Values.global.namespace }}
  labels:
    app: {{ .Values.name }}
    version: {{ .Values.image.tag }}
spec:
  replicas: {{ .Values.replicaCount | default 1 }}
  selector:
    matchLabels:
      app: {{ .Values.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.name }}
      annotations:
        {{- if .Values.global.dapr.enabled }}
        dapr.io/enabled: "true"
        dapr.io/app-id: {{ .Values.dapr.appId }}
        dapr.io/app-port: {{ .Values.dapr.appPort | quote }}
        dapr.io/config: "dapr-config"
        dapr.io/log-level: {{ .Values.global.dapr.logLevel }}
        dapr.io/enable-metrics: {{ .Values.global.dapr.metricsEnabled | quote }}
        dapr.io/sidecar-cpu-limit: {{ .Values.dapr.sidecarResources.limits.cpu | default "500m" }}
        dapr.io/sidecar-memory-limit: {{ .Values.dapr.sidecarResources.limits.memory | default "256Mi" }}
        {{- end }}
    spec:
      containers:
      - name: {{ .Values.name }}
        image: "{{ .Values.global.imageRegistry }}/{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.global.imagePullPolicy }}
        ports:
        - containerPort: {{ .Values.dapr.appPort }}
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ .Values.name }}-secrets
              key: database-url
        - name: ENVIRONMENT
          value: {{ .Values.global.environment }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: /health
            port: {{ .Values.dapr.appPort }}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: {{ .Values.dapr.appPort }}
          initialDelaySeconds: 10
          periodSeconds: 5
{{- end }}
```

#### Service-Specific Chart (Using Common Template)

```yaml
# helm/charts/task-service/Chart.yaml
apiVersion: v2
name: task-service
version: 1.0.0
dependencies:
  - name: common
    version: 1.0.0
    repository: file://../../common
```

```yaml
# helm/charts/task-service/templates/deployment.yaml
{{- include "common.deployment" . }}
```

```yaml
# helm/charts/task-service/values.yaml
name: task-service
replicaCount: 2

image:
  repository: todo-task-service
  tag: v1.0.0

dapr:
  appId: task-service
  appPort: 8000

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

#### Environment-Specific Values

```yaml
# helm/todo-umbrella/values-dev.yaml - Development overrides
global:
  environment: development
  imageRegistry: localhost:5000  # Local registry
  dapr:
    logLevel: debug
    mtlsEnabled: false  # Disable mTLS for easier debugging

task-service:
  replicaCount: 1  # Single replica for dev
  resources:
    requests:
      cpu: 50m
      memory: 128Mi
```

```yaml
# helm/todo-umbrella/values-prod.yaml - Production overrides
global:
  environment: production
  imageRegistry: ghcr.io/yourusername
  dapr:
    logLevel: info
    mtlsEnabled: true

task-service:
  replicaCount: 3  # High availability
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
```

#### Deployment Commands

```bash
# Build dependencies
helm dependency update helm/todo-umbrella

# Install to Minikube (development)
helm install todo-app helm/todo-umbrella \
  -f helm/todo-umbrella/values-dev.yaml \
  -n todo-app \
  --create-namespace

# Install to production cluster
helm install todo-app helm/todo-umbrella \
  -f helm/todo-umbrella/values-prod.yaml \
  -n todo-app \
  --create-namespace

# Upgrade deployment
helm upgrade todo-app helm/todo-umbrella \
  -f helm/todo-umbrella/values-prod.yaml \
  -n todo-app

# Rollback to previous version
helm rollback todo-app 1 -n todo-app

# Uninstall
helm uninstall todo-app -n todo-app
```

#### Service Startup Order with Init Containers

**Problem**: Services may start before their dependencies (e.g., Task Service before PostgreSQL)

**Solution**: Use init containers with wait-for scripts

```yaml
# helm/common/templates/_deployment.yaml (extended)
spec:
  initContainers:
  {{- if .Values.waitFor }}
  - name: wait-for-dependencies
    image: busybox:1.35
    command: ['sh', '-c']
    args:
    - |
      {{- range .Values.waitFor }}
      echo "Waiting for {{ .host }}:{{ .port }}..."
      until nc -z {{ .host }} {{ .port }}; do
        echo "Waiting for {{ .host }}:{{ .port }}..."
        sleep 2
      done
      echo "{{ .host }}:{{ .port }} is available"
      {{- end }}
  {{- end }}
  containers:
  - name: {{ .Values.name }}
    # ... rest of spec
```

```yaml
# helm/charts/task-service/values.yaml
waitFor:
  - host: postgres.database.svc.cluster.local
    port: 5432
  - host: redpanda.messaging.svc.cluster.local
    port: 9092
```

### References

- [DRY Helm Charts for Microservices](https://medium.com/faun/dry-helm-charts-for-micro-services-db3a1d6ecb80)
- [Refactoring with Umbrella Pattern in Helm](https://medium.com/@fdsh/refactoring-with-umbrella-pattern-in-helm-515997a91c89)
- [Helm Chart Development Tips](https://helm.sh/docs/howto/charts_tips_and_tricks/)

### Risks/Tradeoffs

- **Initial Complexity**: Common chart requires upfront investment in template design
- **Abstraction Overhead**: Too much abstraction makes debugging harder
- **Dependency Management**: Must carefully version and update chart dependencies
- **Init Container Limitations**: Wait-for pattern only checks network connectivity, not service readiness

---

## 6. GitHub Actions CI/CD for Kubernetes

### Decision

**Implement multi-service monorepo CI/CD with path-based triggers, matrix builds, and Minikube testing.**

### Rationale

- **Efficient Builds**: Only build/deploy services that changed (path-based triggers)
- **Parallel Execution**: Matrix builds for multiple services simultaneously
- **Pre-Production Testing**: Minikube integration tests before production deployment
- **Single Source of Truth**: Monorepo with separate pipelines per service

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Monorepo with Path Triggers** | Efficient, single repo | Complex workflow logic | **✅ Chosen** |
| **Multi-Repo (Repo per Service)** | Simple per-service CI/CD | Coordination overhead, code duplication | ❌ Too fragmented |
| **Single Pipeline for All** | Simple, one workflow | Slow, builds everything on any change | ❌ Inefficient |

### Implementation Details

#### Workflow Structure

```
.github/
└── workflows/
    ├── build-and-test.yml          # Build Docker images, run tests
    ├── deploy-minikube.yml         # Deploy to Minikube for integration tests
    ├── deploy-production.yml       # Deploy to production cluster (DOKS/GKE)
    └── pr-validation.yml           # PR checks (lint, test, build)
```

#### Build and Test Workflow (Multi-Service)

```yaml
# .github/workflows/build-and-test.yml
name: Build and Test Microservices

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/services/**'
      - '.github/workflows/build-and-test.yml'
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository_owner }}/todo

jobs:
  # Detect which services changed
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      task-service: ${{ steps.changes.outputs.task-service }}
      notification-service: ${{ steps.changes.outputs.notification-service }}
      scheduler-service: ${{ steps.changes.outputs.scheduler-service }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            task-service:
              - 'backend/services/task-service/**'
            notification-service:
              - 'backend/services/notification-service/**'
            scheduler-service:
              - 'backend/services/scheduler-service/**'

  # Build changed services
  build:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - name: task-service
            changed: ${{ needs.detect-changes.outputs.task-service }}
          - name: notification-service
            changed: ${{ needs.detect-changes.outputs.notification-service }}
          - name: scheduler-service
            changed: ${{ needs.detect-changes.outputs.scheduler-service }}

    # Only run if service changed
    if: matrix.service.changed == 'true'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service.name }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend/services/${{ matrix.service.name }}
          file: ./backend/services/${{ matrix.service.name }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run unit tests
        run: |
          docker run --rm \
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service.name }}:${{ github.sha }} \
            pytest tests/ -v
```

#### Deploy to Minikube (Integration Testing)

```yaml
# .github/workflows/deploy-minikube.yml
name: Deploy to Minikube (Integration Tests)

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-on-minikube:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Start Minikube
        uses: medyagh/setup-minikube@latest
        with:
          cpus: 2
          memory: 4096
          kubernetes-version: v1.28.0

      - name: Initialize Dapr on Minikube
        run: |
          # Install Dapr CLI
          wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

          # Initialize Dapr on Kubernetes
          dapr init -k --wait --timeout 600

          # Verify Dapr installation
          dapr status -k

      - name: Build Docker images in Minikube
        run: |
          # Use Minikube's Docker daemon
          eval $(minikube docker-env)

          # Build images
          docker build -t todo-task-service:test ./backend/services/task-service
          docker build -t todo-notification-service:test ./backend/services/notification-service
          docker build -t todo-scheduler-service:test ./backend/services/scheduler-service

      - name: Create Kubernetes secrets
        run: |
          kubectl create namespace todo-app || true

          kubectl create secret generic task-service-secrets \
            --from-literal=database-url=${{ secrets.DATABASE_URL }} \
            --from-literal=openai-api-key=${{ secrets.OPENAI_API_KEY }} \
            -n todo-app \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy Dapr components
        run: |
          kubectl apply -f k8s/components/ -n todo-app

      - name: Deploy services with Helm
        run: |
          # Install Helm
          curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

          # Deploy umbrella chart
          helm install todo-app ./helm/todo-umbrella \
            -f ./helm/todo-umbrella/values-dev.yaml \
            -n todo-app \
            --set task-service.image.tag=test \
            --set notification-service.image.tag=test \
            --set scheduler-service.image.tag=test \
            --wait \
            --timeout 5m

      - name: Run integration tests
        run: |
          # Wait for pods to be ready
          kubectl wait --for=condition=ready pod -l app=task-service -n todo-app --timeout=300s

          # Port-forward to task service
          kubectl port-forward svc/task-service 8000:8000 -n todo-app &
          sleep 5

          # Run integration tests
          pytest integration-tests/ -v --url http://localhost:8000

      - name: Show logs on failure
        if: failure()
        run: |
          echo "=== Task Service Logs ==="
          kubectl logs -l app=task-service -n todo-app --tail=100

          echo "=== Dapr Sidecar Logs ==="
          kubectl logs -l app=task-service -c daprd -n todo-app --tail=100

          echo "=== Pod Status ==="
          kubectl get pods -n todo-app

      - name: Cleanup
        if: always()
        run: |
          helm uninstall todo-app -n todo-app || true
          kubectl delete namespace todo-app || true
```

#### Deploy to Production (Cloud Kubernetes)

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags:
      - 'v*.*.*'

env:
  REGISTRY: ghcr.io
  CLUSTER_NAME: todo-production
  CLUSTER_REGION: nyc1  # DigitalOcean example

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires approval

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install doctl (DigitalOcean CLI)
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Set up kubectl
        run: |
          doctl kubernetes cluster kubeconfig save ${{ env.CLUSTER_NAME }}
          kubectl cluster-info

      - name: Install Helm
        run: |
          curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

      - name: Deploy with Helm
        run: |
          helm upgrade --install todo-app ./helm/todo-umbrella \
            -f ./helm/todo-umbrella/values-prod.yaml \
            -n todo-app \
            --create-namespace \
            --set task-service.image.tag=${{ github.sha }} \
            --set notification-service.image.tag=${{ github.sha }} \
            --set scheduler-service.image.tag=${{ github.sha }} \
            --wait \
            --timeout 10m \
            --atomic  # Rollback on failure

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/task-service -n todo-app
          kubectl rollout status deployment/notification-service -n todo-app
          kubectl rollout status deployment/scheduler-service -n todo-app

      - name: Run smoke tests
        run: |
          # Get LoadBalancer IP
          TASK_SERVICE_IP=$(kubectl get svc task-service -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

          # Health check
          curl -f http://$TASK_SERVICE_IP/health || exit 1

          # Basic functionality test
          curl -f -X POST http://$TASK_SERVICE_IP/tasks \
            -H "Content-Type: application/json" \
            -d '{"title": "Smoke test task"}' || exit 1

      - name: Rollback on failure
        if: failure()
        run: |
          helm rollback todo-app -n todo-app
```

#### PR Validation Workflow

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff mypy

      - name: Lint with Ruff
        run: ruff check backend/

      - name: Type check with mypy
        run: mypy backend/ --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: pytest backend/tests/ --cov=backend --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Helm Upgrade Strategies

**Rolling Update (Default)**:
```bash
helm upgrade todo-app ./helm/todo-umbrella \
  --wait \
  --timeout 10m
```

**Atomic Deployment (Rollback on Failure)**:
```bash
helm upgrade todo-app ./helm/todo-umbrella \
  --atomic \
  --timeout 10m
```

**Blue-Green Deployment (Manual)**:
```bash
# Deploy to green environment
helm install todo-app-green ./helm/todo-umbrella \
  -n todo-app-green \
  --create-namespace

# Test green environment
kubectl port-forward svc/task-service -n todo-app-green 8001:8000

# Switch traffic (update Ingress or LoadBalancer)
kubectl apply -f k8s/ingress-green.yaml

# Delete blue environment
helm uninstall todo-app -n todo-app
```

### References

- [GitHub Actions Kubernetes Deployment](https://spacelift.io/blog/github-actions-kubernetes)
- [Deploying with Helm and GitHub Actions](https://medium.com/swlh/deploying-to-kubernetes-with-helm-and-github-actions-14825e6df1f2)
- [Monorepo CI/CD with GitHub Actions](https://blog.logrocket.com/creating-separate-monorepo-ci-cd-pipelines-github-actions/)
- [Setup Minikube in GitHub Actions](https://minikube.sigs.k8s.io/docs/tutorials/setup_minikube_in_github_actions/)

### Risks/Tradeoffs

- **GitHub Actions Limitations**: 6-hour timeout, 20 concurrent jobs (free tier)
- **Secret Management**: Must securely store KUBECONFIG, API keys in GitHub Secrets
- **Minikube Resource Constraints**: GitHub runners have limited CPU/memory (2-core, 7GB RAM)
- **Cost**: Cloud Kubernetes clusters incur charges (Minikube is free for local testing)

---

## 7. Prometheus + Grafana for Dapr Monitoring

### Decision

**Deploy Prometheus Operator with ServiceMonitor for automatic Dapr metrics scraping, pre-built Grafana dashboards, and AlertManager for critical alerts.**

### Rationale

- **Auto-Discovery**: ServiceMonitor automatically discovers Dapr sidecars and scrapes metrics
- **Pre-Built Dashboards**: Dapr community provides Grafana dashboard templates
- **Unified Observability**: Single platform for metrics, alerts, and visualization
- **CloudEvents Tracing**: Dapr integrates with Zipkin/Jaeger for distributed tracing

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Prometheus + Grafana** | Industry standard, rich ecosystem | Setup complexity | **✅ Chosen** |
| **DataDog/New Relic** | Managed, easy setup | Expensive, vendor lock-in | ❌ Too costly |
| **Loki + Grafana** | Logs + metrics in one place | Not optimized for metrics | ❌ Use for logs only |

### Implementation Details

#### Install Prometheus Operator with Helm

```bash
# Add Prometheus community Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + AlertManager)
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin123 \
  --wait
```

#### ServiceMonitor for Dapr Metrics

```yaml
# k8s/monitoring/dapr-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr-metrics
  namespace: monitoring
  labels:
    app: dapr
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: dapr
  namespaceSelector:
    matchNames:
      - dapr-system
      - todo-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
---
# ServiceMonitor for FastAPI services
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-services-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      monitoring: "true"
  namespaceSelector:
    matchNames:
      - todo-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

#### Expose Metrics from FastAPI Services

```python
# backend/services/task-service/main.py
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Instrument FastAPI with Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="fastapi_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app)

# Custom metrics
task_created_counter = Counter(
    'tasks_created_total',
    'Total number of tasks created',
    ['user_id']
)

task_completion_time = Histogram(
    'task_completion_seconds',
    'Time to complete a task',
    ['status']
)

active_tasks_gauge = Gauge(
    'active_tasks',
    'Number of active tasks',
    ['user_id']
)

@app.post("/tasks")
async def create_task(task: TaskCreate, user_id: str):
    # Increment custom counter
    task_created_counter.labels(user_id=user_id).inc()

    # Update active tasks gauge
    active_tasks_gauge.labels(user_id=user_id).inc()

    # ... task creation logic

    return {"status": "created"}

# Expose metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

#### Service Configuration for Metrics

```yaml
# k8s/task-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: task-service
  namespace: todo-app
  labels:
    app: task-service
    monitoring: "true"  # Label for ServiceMonitor selector
spec:
  selector:
    app: task-service
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: metrics  # Prometheus metrics port
    port: 9090
    targetPort: 9090
```

#### Grafana Dashboards

**Import Pre-Built Dapr Dashboard**:

```bash
# Access Grafana
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring

# Login: admin / admin123
# Navigate to Dashboards -> Import -> Upload JSON file
```

**Dapr System Dashboard JSON** (community dashboard):
- Dashboard ID: `14456` (Grafana.com)
- Metrics: HTTP request rate, latency, gRPC metrics, actor invocations, pub/sub metrics

**Custom Task Service Dashboard**:

```json
{
  "dashboard": {
    "title": "Todo Task Service Metrics",
    "panels": [
      {
        "title": "Tasks Created (per minute)",
        "targets": [
          {
            "expr": "rate(tasks_created_total[1m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Tasks by User",
        "targets": [
          {
            "expr": "active_tasks"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Task Completion Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(task_completion_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "HTTP Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{app=\"task-service\"}[1m])"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

#### AlertManager Rules

```yaml
# k8s/monitoring/prometheus-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-alerts
  namespace: monitoring
spec:
  groups:
  - name: task-service-alerts
    interval: 30s
    rules:
    # High error rate
    - alert: HighErrorRate
      expr: |
        rate(http_requests_total{status=~"5..", app="task-service"}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate on Task Service"
        description: "Task Service is experiencing {{ $value }} 5xx errors per second"

    # Pod down
    - alert: PodDown
      expr: |
        up{app="task-service"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Task Service pod is down"
        description: "Task Service pod {{ $labels.pod }} is down"

    # High memory usage
    - alert: HighMemoryUsage
      expr: |
        container_memory_usage_bytes{pod=~"task-service.*"} / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage on Task Service"
        description: "Task Service pod {{ $labels.pod }} is using {{ $value | humanizePercentage }} memory"

  - name: kafka-alerts
    interval: 30s
    rules:
    # Kafka consumer lag
    - alert: KafkaConsumerLag
      expr: |
        kafka_consumergroup_lag > 100
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Kafka consumer lag is high"
        description: "Consumer group {{ $labels.consumergroup }} has lag of {{ $value }} messages"

    # Kafka broker down
    - alert: KafkaBrokerDown
      expr: |
        up{job="kafka"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Kafka broker is down"
        description: "Kafka broker {{ $labels.instance }} is down"

  - name: dapr-alerts
    interval: 30s
    rules:
    # Dapr sidecar down
    - alert: DaprSidecarDown
      expr: |
        up{job="dapr-system"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Dapr sidecar is down"
        description: "Dapr sidecar on pod {{ $labels.pod }} is down"

    # High Dapr service invocation latency
    - alert: HighDaprInvocationLatency
      expr: |
        histogram_quantile(0.95, rate(dapr_http_server_request_duration_seconds_bucket[5m])) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High Dapr service invocation latency"
        description: "Dapr p95 latency is {{ $value }}s"
```

#### AlertManager Configuration

```yaml
# k8s/monitoring/alertmanager-config.yaml
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-monitoring-kube-prometheus-alertmanager
  namespace: monitoring
type: Opaque
stringData:
  alertmanager.yaml: |
    global:
      resolve_timeout: 5m

    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'slack-notifications'
      routes:
      - match:
          severity: critical
        receiver: 'pagerduty'
      - match:
          severity: warning
        receiver: 'slack-notifications'

    receivers:
    - name: 'slack-notifications'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

    - name: 'pagerduty'
      pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

### Kafka Monitoring with Prometheus

```yaml
# k8s/monitoring/kafka-exporter.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-exporter
  template:
    metadata:
      labels:
        app: kafka-exporter
    spec:
      containers:
      - name: kafka-exporter
        image: danielqsj/kafka-exporter:latest
        args:
        - --kafka.server=redpanda-cluster:9092
        ports:
        - containerPort: 9308
          name: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: kafka-exporter
  namespace: monitoring
  labels:
    app: kafka-exporter
spec:
  ports:
  - name: metrics
    port: 9308
    targetPort: 9308
  selector:
    app: kafka-exporter
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kafka-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: kafka-exporter
  endpoints:
  - port: metrics
    interval: 30s
```

### References

- [Dapr Prometheus monitoring](https://docs.dapr.io/operations/observability/metrics/prometheus/)
- [Dapr Grafana dashboards](https://docs.dapr.io/operations/observability/metrics/grafana/)
- [Prometheus AlertManager rules](https://samber.github.io/awesome-prometheus-alerts/rules.html)
- [Kafka monitoring with Prometheus](https://www.lydtechconsulting.com/blog-monitoring-demo-pt3.html)

### Risks/Tradeoffs

- **Metrics Storage**: Prometheus disk usage grows over time (configure retention: `--storage.tsdb.retention.time=30d`)
- **High Cardinality**: Too many labels on metrics can overwhelm Prometheus (limit user_id labels)
- **Alert Fatigue**: Too many alerts reduce effectiveness (tune thresholds carefully)
- **Grafana Performance**: Large dashboards can be slow (limit time ranges, use aggregation)

---

## References

### Dapr Resources
- [Dapr Python SDK integration with FastAPI](https://docs.dapr.io/developing-applications/sdks/python/python-sdk-extensions/python-fastapi/)
- [Dapr Pub/Sub with CloudEvents](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-cloudevents/)
- [Dapr State Store PostgreSQL](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql-v2/)
- [Dapr mTLS security](https://docs.dapr.io/operations/security/mtls/)
- [Dapr Kubernetes deployment](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/)

### Microservices Architecture
- [FastAPI Microservice Patterns: Domain Driven Design](https://python.plainenglish.io/fastapi-microservice-patterns-domain-driven-design-e99f6f475691)
- [Decompose by subdomain pattern](https://microservices.io/patterns/decomposition/decompose-by-subdomain.html)
- [Database per service vs shared database](https://microservices.io/patterns/data/database-per-service.html)
- [Identify microservice boundaries - Azure](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries)

### Kubernetes & Helm
- [Helm umbrella chart pattern](https://medium.com/@fdsh/refactoring-with-umbrella-pattern-in-helm-515997a91c89)
- [DRY Helm Charts for Microservices](https://medium.com/faun/dry-helm-charts-for-micro-services-db3a1d6ecb80)
- [Kubernetes deployment strategies](https://spacelift.io/blog/kubernetes-deployment-strategies)
- [Helm chart development tips](https://helm.sh/docs/howto/charts_tips_and_tricks/)

### CI/CD
- [GitHub Actions Kubernetes deployment](https://spacelift.io/blog/github-actions-kubernetes)
- [Deploying with Helm and GitHub Actions](https://medium.com/swlh/deploying-to-kubernetes-with-helm-and-github-actions-14825e6df1f2)
- [Monorepo CI/CD pipelines](https://blog.logrocket.com/creating-separate-monorepo-ci-cd-pipelines-github-actions/)
- [Setup Minikube in GitHub Actions](https://minikube.sigs.k8s.io/docs/tutorials/setup_minikube_in_github_actions/)

### Observability
- [Dapr Prometheus monitoring](https://docs.dapr.io/operations/observability/metrics/prometheus/)
- [Dapr Grafana dashboards](https://docs.dapr.io/operations/observability/metrics/grafana/)
- [Prometheus AlertManager rules](https://samber.github.io/awesome-prometheus-alerts/rules.html)
- [Kafka monitoring with Prometheus](https://www.lydtechconsulting.com/blog-monitoring-demo-pt3.html)
- [FastAPI Prometheus integration](https://github.com/trallnag/prometheus-fastapi-instrumentator)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-27
**Author**: Research Team
**Status**: Ready for Implementation Planning
