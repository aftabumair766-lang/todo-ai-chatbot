"""CloudEvents schemas for task-related events"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TaskCreatedEvent(BaseModel):
    """
    Event published when a new task is created.
    Topic: task.created
    """
    task_id: UUID = Field(..., description="Unique task identifier")
    user_id: str = Field(..., description="User who created the task")
    title: str = Field(..., description="Task title")
    recurring_task_id: Optional[UUID] = Field(None, description="Parent recurring task if applicable")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "title": "Buy groceries",
                "recurring_task_id": None,
                "due_date": "2025-01-20T18:00:00Z",
                "created_at": "2025-01-15T10:00:00Z"
            }
        }


class TaskCompletedEvent(BaseModel):
    """
    Event published when a task is marked as completed.
    Topic: task.completed
    """
    task_id: UUID = Field(..., description="Unique task identifier")
    user_id: str = Field(..., description="User who completed the task")
    title: str = Field(..., description="Task title")
    completed_at: datetime = Field(..., description="Completion timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "title": "Buy groceries",
                "completed_at": "2025-01-20T17:30:00Z"
            }
        }


class TaskDeletedEvent(BaseModel):
    """
    Event published when a task is deleted.
    Topic: task.deleted
    """
    task_id: UUID = Field(..., description="Unique task identifier")
    user_id: str = Field(..., description="User who deleted the task")
    deleted_at: datetime = Field(..., description="Deletion timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "deleted_at": "2025-01-21T12:00:00Z"
            }
        }


class RecurringTaskCreatedEvent(BaseModel):
    """
    Event published when a new recurring task is created.
    Topic: recurring-task.created
    """
    recurring_task_id: UUID = Field(..., description="Unique recurring task identifier")
    user_id: str = Field(..., description="User who created the recurring task")
    title: str = Field(..., description="Recurring task title")
    recurrence_rule: str = Field(..., description="Cron or RRULE expression")
    timezone: str = Field(..., description="Timezone for schedule")
    next_generation_time: datetime = Field(..., description="Next task instance generation time")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "recurring_task_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "title": "Daily standup meeting",
                "recurrence_rule": "0 9 * * 1-5",
                "timezone": "America/New_York",
                "next_generation_time": "2025-01-15T09:00:00Z",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }


class ReminderTriggeredEvent(BaseModel):
    """
    Event published when a reminder is triggered.
    Topic: reminder.triggered
    """
    reminder_id: UUID = Field(..., description="Unique reminder identifier")
    task_id: UUID = Field(..., description="Associated task identifier")
    user_id: str = Field(..., description="User receiving the reminder")
    notification_channel: str = Field(..., description="Notification channel (email, sms, etc)")
    trigger_time: datetime = Field(..., description="Scheduled trigger time")
    notification_data: Optional[str] = Field(None, description="JSON metadata for notification")

    class Config:
        json_schema_extra = {
            "example": {
                "reminder_id": "750e8400-e29b-41d4-a716-446655440002",
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "notification_channel": "email",
                "trigger_time": "2025-01-15T08:45:00Z",
                "notification_data": "{\"email\": \"user@example.com\", \"subject\": \"Reminder: Buy groceries\"}"
            }
        }


class ReminderCanceledEvent(BaseModel):
    """
    Event published when a reminder is canceled.
    Topic: reminder.canceled
    """
    reminder_id: UUID = Field(..., description="Unique reminder identifier")
    task_id: UUID = Field(..., description="Associated task identifier")
    user_id: str = Field(..., description="User who canceled the reminder")
    canceled_at: datetime = Field(..., description="Cancellation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "reminder_id": "750e8400-e29b-41d4-a716-446655440002",
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "canceled_at": "2025-01-14T20:00:00Z"
            }
        }


# Topic name constants
TASK_CREATED_TOPIC = "task.created"
TASK_COMPLETED_TOPIC = "task.completed"
TASK_DELETED_TOPIC = "task.deleted"
RECURRING_TASK_CREATED_TOPIC = "recurring-task.created"
REMINDER_TRIGGERED_TOPIC = "reminder.triggered"
REMINDER_CANCELED_TOPIC = "reminder.canceled"
