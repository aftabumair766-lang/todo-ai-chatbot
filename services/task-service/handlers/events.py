"""Kafka event publishers for task-related events"""
from datetime import datetime
from uuid import UUID
from typing import Optional
import sys
import os

# Add common library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from dapr.pubsub import DaprPubSub

# Import event schemas
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.events import (
    TaskCreatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    RecurringTaskCreatedEvent,
    TASK_CREATED_TOPIC,
    TASK_COMPLETED_TOPIC,
    TASK_DELETED_TOPIC,
    RECURRING_TASK_CREATED_TOPIC
)


class TaskEventPublisher:
    """
    Publisher for task-related events to Kafka via Dapr Pub/Sub.

    All events are published in CloudEvents format.
    """

    def __init__(self, pubsub: DaprPubSub):
        """
        Initialize event publisher.

        Args:
            pubsub: Dapr Pub/Sub client
        """
        self.pubsub = pubsub

    async def publish_task_created(
        self,
        task_id: UUID,
        user_id: str,
        title: str,
        recurring_task_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        created_at: datetime = None
    ) -> None:
        """
        Publish task.created event to Kafka.

        Args:
            task_id: Task UUID
            user_id: User ID
            title: Task title
            recurring_task_id: Optional parent recurring task ID
            due_date: Optional due date
            created_at: Creation timestamp
        """
        if created_at is None:
            created_at = datetime.utcnow()

        event = TaskCreatedEvent(
            task_id=task_id,
            user_id=user_id,
            title=title,
            recurring_task_id=recurring_task_id,
            due_date=due_date,
            created_at=created_at
        )

        await self.pubsub.publish_event(
            topic=TASK_CREATED_TOPIC,
            event_data=event.dict(),
            event_type="task.created",
            source="task-service"
        )

        print(f"📤 Published task.created event: {task_id}")

    async def publish_task_completed(
        self,
        task_id: UUID,
        user_id: str,
        title: str,
        completed_at: datetime = None
    ) -> None:
        """
        Publish task.completed event to Kafka.

        Args:
            task_id: Task UUID
            user_id: User ID
            title: Task title
            completed_at: Completion timestamp
        """
        if completed_at is None:
            completed_at = datetime.utcnow()

        event = TaskCompletedEvent(
            task_id=task_id,
            user_id=user_id,
            title=title,
            completed_at=completed_at
        )

        await self.pubsub.publish_event(
            topic=TASK_COMPLETED_TOPIC,
            event_data=event.dict(),
            event_type="task.completed",
            source="task-service"
        )

        print(f"📤 Published task.completed event: {task_id}")

    async def publish_task_deleted(
        self,
        task_id: UUID,
        user_id: str,
        deleted_at: datetime = None
    ) -> None:
        """
        Publish task.deleted event to Kafka.

        Args:
            task_id: Task UUID
            user_id: User ID
            deleted_at: Deletion timestamp
        """
        if deleted_at is None:
            deleted_at = datetime.utcnow()

        event = TaskDeletedEvent(
            task_id=task_id,
            user_id=user_id,
            deleted_at=deleted_at
        )

        await self.pubsub.publish_event(
            topic=TASK_DELETED_TOPIC,
            event_data=event.dict(),
            event_type="task.deleted",
            source="task-service"
        )

        print(f"📤 Published task.deleted event: {task_id}")

    async def publish_recurring_task_created(
        self,
        recurring_task_id: UUID,
        user_id: str,
        title: str,
        recurrence_rule: str,
        timezone: str,
        next_generation_time: datetime,
        created_at: datetime = None
    ) -> None:
        """
        Publish recurring-task.created event to Kafka.

        Args:
            recurring_task_id: Recurring task UUID
            user_id: User ID
            title: Recurring task title
            recurrence_rule: Cron or RRULE expression
            timezone: Timezone for schedule
            next_generation_time: Next task instance generation time
            created_at: Creation timestamp
        """
        if created_at is None:
            created_at = datetime.utcnow()

        event = RecurringTaskCreatedEvent(
            recurring_task_id=recurring_task_id,
            user_id=user_id,
            title=title,
            recurrence_rule=recurrence_rule,
            timezone=timezone,
            next_generation_time=next_generation_time,
            created_at=created_at
        )

        await self.pubsub.publish_event(
            topic=RECURRING_TASK_CREATED_TOPIC,
            event_data=event.dict(),
            event_type="recurring-task.created",
            source="task-service"
        )

        print(f"📤 Published recurring-task.created event: {recurring_task_id}")


# Global event publisher (initialized in main.py)
_event_publisher: Optional[TaskEventPublisher] = None


def init_event_publisher(pubsub: DaprPubSub):
    """Initialize global event publisher"""
    global _event_publisher
    _event_publisher = TaskEventPublisher(pubsub)


def get_event_publisher() -> TaskEventPublisher:
    """Get global event publisher instance"""
    if not _event_publisher:
        raise RuntimeError("Event publisher not initialized")
    return _event_publisher
