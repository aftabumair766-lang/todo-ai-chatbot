"""Dapr Pub/Sub wrapper for event-driven communication"""
import json
from typing import Any, Callable, Dict
from datetime import datetime
from uuid import uuid4
from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp
from cloudevents.http import CloudEvent


class DaprPubSub:
    """
    Wrapper for Dapr Pub/Sub operations with CloudEvents support.

    Publishes events in CloudEvents 1.0 format for standardization.
    """

    def __init__(self, pubsub_name: str = "pubsub"):
        """
        Initialize Dapr Pub/Sub client.

        Args:
            pubsub_name: Dapr pub/sub component name
        """
        self.pubsub_name = pubsub_name
        self.client = DaprClient()

    async def publish_event(
        self,
        topic: str,
        event_data: Dict[str, Any],
        event_type: str,
        source: str,
        metadata: Dict[str, str] = None
    ) -> None:
        """
        Publish event to Kafka topic via Dapr Pub/Sub.

        Wraps event data in CloudEvents 1.0 format:
        {
            "specversion": "1.0",
            "type": "task.created",
            "source": "task-service",
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "time": "2025-01-15T10:00:00Z",
            "datacontenttype": "application/json",
            "data": { ... }
        }

        Args:
            topic: Kafka topic name (e.g., "task.created")
            event_data: Event payload
            event_type: CloudEvent type (e.g., "task.created")
            source: Event source service (e.g., "task-service")
            metadata: Optional Dapr metadata

        Raises:
            Exception: If publish fails
        """
        # Build CloudEvent
        cloud_event = CloudEvent(
            attributes={
                "specversion": "1.0",
                "type": event_type,
                "source": source,
                "id": str(uuid4()),
                "time": datetime.utcnow().isoformat() + "Z",
                "datacontenttype": "application/json"
            },
            data=event_data
        )

        # Convert CloudEvent to dict
        event_dict = {
            "specversion": cloud_event["specversion"],
            "type": cloud_event["type"],
            "source": cloud_event["source"],
            "id": cloud_event["id"],
            "time": cloud_event["time"],
            "datacontenttype": cloud_event["datacontenttype"],
            "data": cloud_event.data
        }

        # Publish via Dapr
        self.client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name=topic,
            data=json.dumps(event_dict),
            data_content_type="application/cloudevents+json",
            metadata=metadata or {}
        )

    @staticmethod
    def subscribe(
        app: DaprApp,
        pubsub_name: str,
        topic: str,
        route: str = None
    ):
        """
        Decorator for subscribing to Dapr Pub/Sub topics.

        Usage:
            app = DaprApp(FastAPI())

            @DaprPubSub.subscribe(app, "pubsub", "task.created")
            async def handle_task_created(event_data: dict):
                # Process event
                pass

        Args:
            app: DaprApp instance
            pubsub_name: Pub/Sub component name
            topic: Topic to subscribe to
            route: Optional custom route (defaults to /events/{topic})

        Returns:
            Decorator function
        """
        route = route or f"/events/{topic}"

        def decorator(func: Callable):
            @app.subscribe(
                pubsub=pubsub_name,
                topic=topic,
                route=route
            )
            async def wrapper(event: dict):
                # Extract data from CloudEvent
                if "data" in event:
                    return await func(event["data"])
                return await func(event)

            return wrapper

        return decorator

    def close(self):
        """Close Dapr client connection"""
        self.client.close()
