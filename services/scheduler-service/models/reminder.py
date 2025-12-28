"""Reminder model for task notifications"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class NotificationChannel(str, Enum):
    """Supported notification channels"""
    EMAIL = "email"
    SMS = "sms"
    CHAT = "chat"
    WEBHOOK = "webhook"


class ReminderStatus(str, Enum):
    """Reminder lifecycle states"""
    PENDING = "pending"      # Waiting to be triggered
    TRIGGERED = "triggered"  # Notification sent
    CANCELED = "canceled"    # User canceled before trigger
    FAILED = "failed"        # Notification failed to send


class Reminder(SQLModel, table=True):
    """
    Reminder for task notifications.

    Attributes:
        id: Unique identifier (UUID)
        task_id: Associated task ID
        user_id: Owner's user ID
        trigger_time: When to send the notification
        notification_channel: Delivery method (email, sms, chat, webhook)
        status: Current reminder status
        notification_data: JSON metadata for the notification
        created_at: Creation timestamp
        triggered_at: When notification was sent (nullable)
        error_message: Error details if failed (nullable)
    """
    __tablename__ = "reminders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(index=True, nullable=False)
    trigger_time: datetime = Field(index=True, nullable=False)
    notification_channel: NotificationChannel = Field(default=NotificationChannel.EMAIL, nullable=False)
    status: ReminderStatus = Field(default=ReminderStatus.PENDING, nullable=False)
    notification_data: Optional[str] = Field(default=None, nullable=True)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    triggered_at: Optional[datetime] = Field(default=None, nullable=True)
    error_message: Optional[str] = Field(default=None, nullable=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440002",
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "trigger_time": "2025-01-15T08:45:00Z",
                "notification_channel": "email",
                "status": "pending",
                "notification_data": "{\"email\": \"user@example.com\", \"subject\": \"Reminder: Daily standup\"}",
                "created_at": "2025-01-14T12:00:00Z",
                "triggered_at": None,
                "error_message": None
            }
        }
