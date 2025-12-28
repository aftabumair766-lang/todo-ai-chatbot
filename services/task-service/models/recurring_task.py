"""RecurringTask model for Phase V"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class RecurringTask(SQLModel, table=True):
    """
    Recurring task definition for creating task instances on a schedule.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner's user ID
        title: Task title (max 500 chars)
        recurrence_rule: Cron expression or RRULE format
        timezone: Timezone for schedule (default UTC)
        active: Whether this recurring task is enabled
        next_generation_time: Next time to generate a task instance
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "recurring_tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    recurrence_rule: str = Field(nullable=False)  # Cron or RRULE format
    timezone: str = Field(default="UTC", nullable=False)
    active: bool = Field(default=True, nullable=False)
    next_generation_time: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "title": "Daily standup meeting",
                "recurrence_rule": "0 9 * * 1-5",  # Weekdays at 9 AM
                "timezone": "America/New_York",
                "active": True,
                "next_generation_time": "2025-01-15T09:00:00Z",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
