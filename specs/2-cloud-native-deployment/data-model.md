# Data Model: Cloud-Native Event-Driven Todo Chatbot

**Feature**: 2-cloud-native-deployment
**Created**: 2025-12-27
**Status**: Phase 1 Complete

## Overview

This document extends the Phase I-IV data model with new entities for recurring tasks, reminders, and event sourcing. The model supports event-driven architecture with Kafka and Dapr State Store abstraction.

---

## New Entities (Phase V)

### RecurringTask

Represents a task template that generates task instances on a schedule.

**Storage**: Dapr State Store (PostgreSQL backend) with key pattern `recurring-task:{user_id}:{id}`

**Attributes**:
- `id` (UUID, primary key): Unique identifier for recurring task template
- `user_id` (string, indexed): Owner user ID from Better Auth
- `title` (string, max 500 chars): Task title template
- `description` (string, max 2000 chars, nullable): Task description template
- `recurrence_rule` (string): Cron expression or iCalen

dar RRULE format (e.g., `0 9 * * 1-5` for weekdays at 9am)
- `timezone` (string, default UTC): User timezone for recurrence calculation
- `active` (boolean, default true): Whether to generate new instances
- `next_generation_time` (timestamp): Next time to generate task instance
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Relationships**:
- One-to-Many with TaskInstance (a recurring task generates many task instances)
- Belongs-to User (via user_id)

**Validation Rules**:
- `recurrence_rule` must be valid cron or RRULE format
- `next_generation_time` must be in the future when active=true
- Cannot delete if active instances exist (soft delete only)

**State Transitions**:
- Created → Active (default)
- Active → Paused (user pauses recurring task)
- Paused → Active (user resumes)
- Active → Deleted (soft delete, sets active=false)

---

### TaskInstance

Extends existing Task entity to support both one-time and recurring tasks.

**Storage**: Dapr State Store (PostgreSQL backend) with key pattern `task:{user_id}:{id}`

**Attributes** (extends Phase I-IV Task):
- `id` (UUID, primary key): Unique identifier
- `user_id` (string, indexed): Owner user ID
- `recurring_task_id` (UUID, nullable, foreign key): Reference to RecurringTask if generated
- `title` (string, max 500 chars)
- `description` (string, max 2000 chars, nullable)
- `due_date` (timestamp, nullable): When task is due (used for reminder calculation)
- `completed` (boolean, default false)
- `completed_at` (timestamp, nullable): When task was completed
- `instance_date` (date, nullable): For recurring tasks, the date this instance represents (e.g., "2025-12-27" for "Weekly standup")
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Relationships**:
- Belongs-to User (via user_id)
- Belongs-to RecurringTask (via recurring_task_id, nullable)
- One-to-Many with Reminder

**Indexes**:
- `(user_id, completed)` - For listing pending/completed tasks
- `(user_id, due_date)` - For reminder scheduling
- `(recurring_task_id, instance_date)` - For preventing duplicate recurring instances

**Validation Rules**:
- If `recurring_task_id` is not null, `instance_date` must not be null
- Cannot have duplicate `(recurring_task_id, instance_date)` combinations
- `completed_at` must be after `created_at`

---

### Reminder

Represents a scheduled notification for a task.

**Storage**: Dapr State Store (PostgreSQL backend) with key pattern `reminder:{user_id}:{id}`

**Attributes**:
- `id` (UUID, primary key): Unique identifier
- `task_id` (UUID, foreign key): Task to remind about
- `user_id` (string, indexed): Owner user ID
- `trigger_time` (timestamp): Absolute time when reminder fires
- `notification_channel` (enum): email | sms | chat | webhook
- `notification_metadata` (JSON): Channel-specific data (email address, phone number, webhook URL)
- `status` (enum): pending | triggered | canceled | failed
- `triggered_at` (timestamp, nullable): When notification was sent
- `error_message` (string, nullable): If status=failed, error details
- `created_at` (timestamp)

**Relationships**:
- Belongs-to TaskInstance (via task_id)
- Belongs-to User (via user_id)

**Indexes**:
- `(user_id, status, trigger_time)` - For scheduler to find pending reminders
- `(task_id)` - For finding reminders when task completed (to cancel)

**Validation Rules**:
- `trigger_time` must be in the future when created
- If `status` = triggered, `triggered_at` must not be null
- Cannot update `status` from `triggered` to `pending` (no rollbacks)

**State Transitions**:
- pending → triggered (scheduler sends notification)
- pending → canceled (task completed before reminder)
- pending → failed (notification service error)
- failed → pending (retry after transient error)

---

## Event Entities (Kafka Messages)

### DomainEvent

CloudEvents envelope for all domain events published to Kafka.

**Kafka Topics**:
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`
- `recurring-task.created`
- `recurring-task.updated`
- `reminder.triggered`
- `reminder.canceled`

**CloudEvents Schema** (standard):
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "task-service",
  "id": "uuid-v4",
  "time": "2025-12-27T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "uuid",
    "user_id": "string",
    "title": "string",
    "completed": false,
    "created_at": "timestamp"
  }
}
```

**Event Payload Schemas** (data field):

#### task.created
```json
{
  "task_id": "uuid",
  "user_id": "string",
  "title": "string",
  "description": "string | null",
  "due_date": "timestamp | null",
  "recurring_task_id": "uuid | null",
  "instance_date": "date | null",
  "created_at": "timestamp"
}
```

#### task.completed
```json
{
  "task_id": "uuid",
  "user_id": "string",
  "title": "string",
  "completed_at": "timestamp"
}
```

#### recurring-task.created
```json
{
  "recurring_task_id": "uuid",
  "user_id": "string",
  "title": "string",
  "recurrence_rule": "string",
  "timezone": "string",
  "next_generation_time": "timestamp"
}
```

#### reminder.triggered
```json
{
  "reminder_id": "uuid",
  "task_id": "uuid",
  "user_id": "string",
  "task_title": "string",
  "notification_channel": "email | sms | chat",
  "trigger_time": "timestamp"
}
```

**Idempotency**:
- All events include `id` (UUID) for deduplication
- Consumers track processed event IDs in Dapr State Store (key: `processed-events:{consumer-name}:{event-id}`, TTL: 7 days)

---

## Existing Entities (Phase I-IV) - No Changes

### User

**Note**: Managed by Better Auth, not stored in application database.

**Attributes**:
- `user_id` (string): Unique identifier from Better Auth JWT

---

### Conversation

**Storage**: Dapr State Store (PostgreSQL backend)

**Attributes**:
- `id` (UUID, primary key)
- `user_id` (string, indexed)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**No changes required for Phase V.**

---

### Message

**Storage**: Dapr State Store (PostgreSQL backend)

**Attributes**:
- `id` (UUID, primary key)
- `conversation_id` (UUID, foreign key)
- `user_id` (string, indexed)
- `role` (enum: user | assistant)
- `content` (text)
- `created_at` (timestamp)

**No changes required for Phase V.**

---

## Migration Strategy

### From Direct PostgreSQL to Dapr State Store

**Phase 1: Dual-Write Pattern**
1. Keep existing SQLModel code functional
2. Add Dapr State Store writes alongside database writes
3. Verify data consistency between both stores
4. Monitor for 1 week in staging

**Phase 2: Dapr-First Read Pattern**
1. Read from Dapr State Store
2. Fallback to PostgreSQL if not found (cache miss)
3. Backfill missing data to Dapr
4. Monitor cache hit rate (target: >95%)

**Phase 3: Full Migration**
1. Stop database writes (Dapr only)
2. PostgreSQL becomes read-only backup
3. Keep PostgreSQL for 30 days for rollback safety
4. Decommission PostgreSQL direct access

**Migration Timeline**: 6 weeks total

---

## Dapr State Store Keys

**Key Naming Convention**: `{entity}:{partition-key}:{id}`

Examples:
- `task:user-123:task-uuid-456`
- `recurring-task:user-123:recurring-uuid-789`
- `reminder:user-123:reminder-uuid-abc`
- `conversation:user-123:conv-uuid-def`
- `processed-events:scheduler-service:event-uuid-xyz`

**Benefits**:
- Partition by user_id for scalability
- Human-readable for debugging
- Supports Dapr query API with prefix filters

---

## Database Schema (PostgreSQL Backend for Dapr)

**Note**: Dapr State Store uses key-value storage. PostgreSQL backend stores JSON documents.

**Dapr State Table** (auto-created by Dapr):
```sql
CREATE TABLE dapr_state (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  etag TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_dapr_state_key_prefix ON dapr_state (key text_pattern_ops);
```

**Application Schema** (for complex queries, keep existing tables):
- `tasks` table (read-replica of Dapr state, updated via Kafka consumers)
- `recurring_tasks` table
- `reminders` table
- `conversations` table (no changes)
- `messages` table (no changes)

**Rationale**: Use Dapr for writes (abstraction), keep PostgreSQL for complex JOINs and reporting queries.

---

## Summary

**New Entities**: 3 (RecurringTask, TaskInstance extension, Reminder)
**Event Types**: 8 Kafka topics
**Storage Pattern**: Dapr State Store with PostgreSQL backend + read replicas for queries
**Migration**: Dual-write → Dapr-first read → Full migration (6 weeks)
**Idempotency**: Event ID tracking in Dapr State Store with 7-day TTL
