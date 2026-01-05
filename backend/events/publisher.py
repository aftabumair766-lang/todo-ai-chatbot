"""
Event Publisher for Phase V - Event-Driven Architecture
Publishes task events to Kafka via Dapr Pub/Sub
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import contextmanager

try:
    from dapr.clients import DaprClient
    DAPR_AVAILABLE = True
except ImportError:
    DAPR_AVAILABLE = False
    logging.warning("Dapr SDK not installed. Event publishing disabled.")

logger = logging.getLogger(__name__)

# Dapr component and topic configuration
PUBSUB_NAME = "todo-pubsub"  # Must match kubernetes/dapr-components/pubsub-kafka.yaml
TASK_EVENTS_TOPIC = "task-events"
TAG_EVENTS_TOPIC = "tag-events"


class EventPublisher:
    """
    Publishes domain events to Kafka via Dapr Pub/Sub component.

    Events are published asynchronously and failures are logged but don't block operations.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize event publisher.

        Args:
            enabled: Whether event publishing is enabled (can be controlled via env var)
        """
        self.enabled = enabled and DAPR_AVAILABLE
        if not self.enabled:
            logger.info("Event publishing is disabled")

    @contextmanager
    def _get_client(self):
        """Context manager for Dapr client."""
        if not self.enabled:
            yield None
            return

        try:
            with DaprClient() as client:
                yield client
        except Exception as e:
            logger.error(f"Failed to create Dapr client: {e}")
            yield None

    def _publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Internal method to publish event to Dapr.

        Args:
            topic: Kafka topic name
            event_type: Event type identifier
            data: Event payload data
            metadata: Optional metadata for the event

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            return False

        event_payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data
        }

        try:
            with self._get_client() as client:
                if client is None:
                    return False

                client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=topic,
                    data=json.dumps(event_payload),
                    data_content_type="application/json",
                    publish_metadata=metadata or {}
                )

                logger.info(f"Published event: {event_type} to topic: {topic}")
                return True

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False

    # =========================================================================
    # Task Events
    # =========================================================================

    def publish_task_created(
        self,
        task_id: str,
        user_id: str,
        title: str,
        priority: Optional[str] = None,
        tags: Optional[list] = None,
        due_date: Optional[str] = None
    ) -> bool:
        """Publish task.created event."""
        return self._publish_event(
            topic=TASK_EVENTS_TOPIC,
            event_type="task.created",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "priority": priority,
                "tags": tags or [],
                "due_date": due_date
            }
        )

    def publish_task_updated(
        self,
        task_id: str,
        user_id: str,
        changes: Dict[str, Any]
    ) -> bool:
        """Publish task.updated event."""
        return self._publish_event(
            topic=TASK_EVENTS_TOPIC,
            event_type="task.updated",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "changes": changes
            }
        )

    def publish_task_completed(
        self,
        task_id: str,
        user_id: str,
        title: str
    ) -> bool:
        """Publish task.completed event."""
        return self._publish_event(
            topic=TASK_EVENTS_TOPIC,
            event_type="task.completed",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "completed_at": datetime.utcnow().isoformat() + "Z"
            }
        )

    def publish_task_deleted(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """Publish task.deleted event."""
        return self._publish_event(
            topic=TASK_EVENTS_TOPIC,
            event_type="task.deleted",
            data={
                "task_id": task_id,
                "user_id": user_id
            }
        )

    # =========================================================================
    # Tag Events
    # =========================================================================

    def publish_tag_created(
        self,
        tag_id: str,
        name: str,
        color: Optional[str] = None
    ) -> bool:
        """Publish tag.created event."""
        return self._publish_event(
            topic=TAG_EVENTS_TOPIC,
            event_type="tag.created",
            data={
                "tag_id": tag_id,
                "name": name,
                "color": color
            }
        )

    def publish_tag_deleted(
        self,
        tag_id: str,
        name: str
    ) -> bool:
        """Publish tag.deleted event."""
        return self._publish_event(
            topic=TAG_EVENTS_TOPIC,
            event_type="tag.deleted",
            data={
                "tag_id": tag_id,
                "name": name
            }
        )


# Global singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get or create the global event publisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        # Event publishing can be disabled via environment variable
        import os
        enabled = os.getenv("ENABLE_EVENT_PUBLISHING", "true").lower() == "true"
        _event_publisher = EventPublisher(enabled=enabled)
    return _event_publisher
