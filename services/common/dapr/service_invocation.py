"""Dapr Service Invocation wrapper for service-to-service calls"""
from typing import Any, Dict, Optional
from dapr.clients import DaprClient


class DaprServiceInvocation:
    """
    Wrapper for Dapr Service Invocation.

    Enables service-to-service communication without hardcoded URLs.
    Uses Dapr app-id for service discovery.

    Example:
        invoker = DaprServiceInvocation()
        response = await invoker.invoke_service(
            app_id="task-service",
            method_name="tasks",
            http_verb="POST",
            data={"title": "Buy groceries"}
        )
    """

    def __init__(self):
        """Initialize Dapr Service Invocation client"""
        self.client = DaprClient()

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        http_verb: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Invoke a method on another service via Dapr.

        Args:
            app_id: Target service's Dapr app-id (e.g., "task-service")
            method_name: HTTP endpoint path (e.g., "tasks" for /tasks)
            http_verb: HTTP method (GET, POST, PUT, DELETE)
            data: Request body data
            metadata: Optional metadata (headers, etc.)

        Returns:
            Response from invoked service

        Raises:
            Exception: If invocation fails

        Example:
            # Call task-service to create a task
            response = await invoke_service(
                app_id="task-service",
                method_name="tasks",
                http_verb="POST",
                data={"title": "Buy groceries", "user_id": "user_123"}
            )
        """
        response = self.client.invoke_method(
            app_id=app_id,
            method_name=method_name,
            data=data,
            http_verb=http_verb,
            metadata=metadata or {}
        )

        return response.data

    async def get(
        self,
        app_id: str,
        method_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Convenience method for GET requests.

        Args:
            app_id: Target service's Dapr app-id
            method_name: HTTP endpoint path
            metadata: Optional metadata

        Returns:
            Response data
        """
        return await self.invoke_service(
            app_id=app_id,
            method_name=method_name,
            http_verb="GET",
            metadata=metadata
        )

    async def post(
        self,
        app_id: str,
        method_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Convenience method for POST requests.

        Args:
            app_id: Target service's Dapr app-id
            method_name: HTTP endpoint path
            data: Request body
            metadata: Optional metadata

        Returns:
            Response data
        """
        return await self.invoke_service(
            app_id=app_id,
            method_name=method_name,
            http_verb="POST",
            data=data,
            metadata=metadata
        )

    async def put(
        self,
        app_id: str,
        method_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Convenience method for PUT requests.

        Args:
            app_id: Target service's Dapr app-id
            method_name: HTTP endpoint path
            data: Request body
            metadata: Optional metadata

        Returns:
            Response data
        """
        return await self.invoke_service(
            app_id=app_id,
            method_name=method_name,
            http_verb="PUT",
            data=data,
            metadata=metadata
        )

    async def delete(
        self,
        app_id: str,
        method_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Convenience method for DELETE requests.

        Args:
            app_id: Target service's Dapr app-id
            method_name: HTTP endpoint path
            metadata: Optional metadata

        Returns:
            Response data
        """
        return await self.invoke_service(
            app_id=app_id,
            method_name=method_name,
            http_verb="DELETE",
            metadata=metadata
        )

    def close(self):
        """Close Dapr client connection"""
        self.client.close()
