"""TaskInstance model extending Phase I-IV Task"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class TaskInstance(SQLModel, table=True):
    """
    Task instance - extends original Task model with recurring task support.

    This model represents individual task instances that may be generated
    from recurring tasks or created as standalone tasks.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner's user ID
        title: Task title (max 500 chars)
        completed: Whether task is completed
        recurring_task_id: Parent recurring task ID (nullable)
        instance_date: Date for this instance (nullable)
        due_date: Due date/time for this task (nullable)
        created_at: Creation timestamp
        completed_at: Completion timestamp (nullable)
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    completed: bool = Field(default=False, nullable=False)

    # Phase V additions for recurring tasks
    recurring_task_id: Optional[UUID] = Field(default=None, foreign_key="recurring_tasks.id", nullable=True)
    instance_date: Optional[datetime] = Field(default=None, nullable=True)
    due_date: Optional[datetime] = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "title": "Daily standup meeting - Jan 15",
                "completed": False,
                "recurring_task_id": "550e8400-e29b-41d4-a716-446655440000",
                "instance_date": "2025-01-15T00:00:00Z",
                "due_date": "2025-01-15T09:00:00Z",
                "created_at": "2025-01-15T00:00:00Z",
                "completed_at": None
            }
        }
