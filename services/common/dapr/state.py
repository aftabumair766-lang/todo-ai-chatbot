"""Dapr State Store wrapper for stateless microservices"""
import json
from typing import Any, Dict, List, Optional
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem, StateOptions


class DaprStateStore:
    """
    Wrapper for Dapr State Store operations.

    Provides async methods for CRUD operations with key pattern:
    {entity}:{user_id}:{id}

    Example keys:
        - task:user_123:650e8400-e29b-41d4-a716-446655440001
        - recurring-task:user_123:550e8400-e29b-41d4-a716-446655440000
        - reminder:user_123:750e8400-e29b-41d4-a716-446655440002
    """

    def __init__(self, store_name: str = "statestore"):
        """
        Initialize Dapr State Store client.

        Args:
            store_name: Dapr state store component name
        """
        self.store_name = store_name
        self.client = DaprClient()

    def _build_key(self, entity: str, user_id: str, entity_id: str) -> str:
        """
        Build state store key following pattern: {entity}:{user_id}:{id}

        Args:
            entity: Entity type (task, recurring-task, reminder)
            user_id: User identifier
            entity_id: Entity identifier

        Returns:
            Formatted key string
        """
        return f"{entity}:{user_id}:{entity_id}"

    async def save_state(
        self,
        entity: str,
        user_id: str,
        entity_id: str,
        data: Dict[str, Any],
        etag: Optional[str] = None
    ) -> None:
        """
        Save state to Dapr State Store.

        Args:
            entity: Entity type (task, recurring-task, reminder)
            user_id: User identifier
            entity_id: Entity identifier
            data: Data to store (will be JSON serialized)
            etag: Optional ETag for optimistic concurrency

        Raises:
            Exception: If save operation fails
        """
        key = self._build_key(entity, user_id, entity_id)
        value = json.dumps(data)

        state_metadata = {}
        if etag:
            state_metadata["etag"] = etag

        self.client.save_state(
            store_name=self.store_name,
            key=key,
            value=value,
            metadata=state_metadata
        )

    async def get_state(
        self,
        entity: str,
        user_id: str,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get state from Dapr State Store.

        Args:
            entity: Entity type (task, recurring-task, reminder)
            user_id: User identifier
            entity_id: Entity identifier

        Returns:
            Deserialized data or None if not found
        """
        key = self._build_key(entity, user_id, entity_id)
        response = self.client.get_state(
            store_name=self.store_name,
            key=key
        )

        if not response.data:
            return None

        return json.loads(response.data)

    async def delete_state(
        self,
        entity: str,
        user_id: str,
        entity_id: str,
        etag: Optional[str] = None
    ) -> None:
        """
        Delete state from Dapr State Store.

        Args:
            entity: Entity type (task, recurring-task, reminder)
            user_id: User identifier
            entity_id: Entity identifier
            etag: Optional ETag for optimistic concurrency

        Raises:
            Exception: If delete operation fails
        """
        key = self._build_key(entity, user_id, entity_id)

        state_metadata = {}
        if etag:
            state_metadata["etag"] = etag

        self.client.delete_state(
            store_name=self.store_name,
            key=key,
            metadata=state_metadata
        )

    async def query_state(
        self,
        entity: str,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query state store for entities belonging to a user.

        Note: This is a simplified implementation. For production,
        use Dapr State Query API with proper filtering.

        Args:
            entity: Entity type (task, recurring-task, reminder)
            user_id: User identifier
            filters: Optional additional filters

        Returns:
            List of matching entities
        """
        # TODO: Implement proper Dapr State Query API
        # For now, this is a placeholder that would need
        # the actual query implementation based on:
        # https://docs.dapr.io/developing-applications/building-blocks/state-management/howto-state-query-api/

        # Placeholder for query logic
        query = {
            "filter": {
                "EQ": {"key": f"{entity}:{user_id}:"}
            }
        }

        # Return empty list - implement actual query in production
        return []

    def close(self):
        """Close Dapr client connection"""
        self.client.close()
