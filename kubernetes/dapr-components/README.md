# Dapr Components - Phase V

## What This Does

This directory contains Dapr component configurations for event-driven architecture.

## Components

### 1. pubsub-kafka.yaml
**Purpose:** Kafka pub/sub for event publishing
**Provider:** Redpanda Cloud (FREE tier)
**Topics:**
- `task-events` - Task CRUD operations
- `tag-events` - Tag operations
- `reminder-events` - Reminder notifications

## Setup Instructions

### Step 1: Get Redpanda Credentials
1. Sign up at https://redpanda.com/try-redpanda
2. Create FREE serverless cluster
3. Create topic: `task-events`
4. Note credentials from Overview tab

### Step 2: Configure Component
```bash
# Copy template
cp pubsub-kafka.yaml.template pubsub-kafka.yaml

# Edit with your credentials
nano pubsub-kafka.yaml

# Replace:
# - YOUR_BOOTSTRAP_SERVER (e.g., abc123.redpanda.com:9092)
# - YOUR_SASL_USERNAME
# - YOUR_SASL_PASSWORD
```

### Step 3: Apply to Kubernetes
```bash
# Apply component
kubectl apply -f pubsub-kafka.yaml

# Verify
kubectl get components -n todo-app

# Check Dapr logs
kubectl logs -n dapr-system -l app=dapr-operator
```

## Testing

### Publish Test Event
```bash
# Exec into a pod
kubectl exec -it -n todo-app deployment/todo-backend -- /bin/bash

# Inside pod, test Dapr
curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "message": "Hello from Dapr!"}'
```

### Subscribe to Events
```bash
# In backend code (backend/api/chat.py)
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name='todo-pubsub',
        topic_name='task-events',
        data=json.dumps({'action': 'created', 'task_id': task.id})
    )
```

## Troubleshooting

### Component Not Working
```bash
# Check component status
kubectl describe component todo-pubsub -n todo-app

# Check Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd

# Verify Redpanda connectivity
telnet YOUR_BOOTSTRAP_SERVER 9092
```

### Events Not Publishing
1. Verify credentials are correct
2. Check topic exists in Redpanda
3. Ensure Dapr sidecar is injected
4. Check application logs

## Event Schema

### Task Events
```json
{
  "event_type": "task.created",
  "timestamp": "2025-01-02T10:30:00Z",
  "data": {
    "task_id": "123",
    "user_id": "user-456",
    "title": "New task",
    "priority": "high",
    "tags": ["work", "urgent"]
  }
}
```

## Security Notes

- ⚠️ Never commit `pubsub-kafka.yaml` with real credentials
- ✅ The template file is safe to commit
- ✅ Add `pubsub-kafka.yaml` to .gitignore
- ✅ Use Kubernetes secrets for production

## Phase V Requirements Met

✅ Event-driven architecture
✅ Pub/Sub messaging
✅ Cloud-native messaging (Kafka)
✅ Microservices communication
✅ Scalable event handling
