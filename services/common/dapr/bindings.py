"""Dapr Bindings wrapper for external integrations"""
from typing import Any, Callable, Dict, Optional
from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp


class DaprBindings:
    """
    Wrapper for Dapr Bindings (input and output).

    Supports:
    - Output binding: Send email via SendGrid
    - Input binding: Receive cron triggers
    """

    def __init__(self):
        """Initialize Dapr Bindings client"""
        self.client = DaprClient()

    async def invoke_binding(
        self,
        binding_name: str,
        operation: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Invoke an output binding.

        Args:
            binding_name: Dapr binding component name (e.g., "email-binding")
            operation: Binding operation (e.g., "create")
            data: Binding data
            metadata: Optional metadata

        Returns:
            Response from binding

        Raises:
            Exception: If binding invocation fails
        """
        response = self.client.invoke_binding(
            binding_name=binding_name,
            operation=operation,
            data=data or {},
            metadata=metadata or {}
        )

        return response.data

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> None:
        """
        Send email via SendGrid binding.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Optional sender email (uses default from binding)
            from_name: Optional sender name (uses default from binding)

        Raises:
            Exception: If email send fails

        Example:
            await bindings.send_email(
                to_email="user@example.com",
                subject="Task Reminder",
                body="Don't forget: Buy groceries"
            )
        """
        metadata = {
            "emailTo": to_email,
            "subject": subject
        }

        if from_email:
            metadata["emailFrom"] = from_email
        if from_name:
            metadata["emailFromName"] = from_name

        await self.invoke_binding(
            binding_name="email-binding",
            operation="create",
            data={"body": body},
            metadata=metadata
        )

    @staticmethod
    def subscribe_to_binding(
        app: DaprApp,
        binding_name: str,
        route: str = None
    ):
        """
        Decorator for subscribing to input bindings (e.g., cron).

        Usage:
            app = DaprApp(FastAPI())

            @DaprBindings.subscribe_to_binding(app, "cron-binding")
            async def handle_cron_trigger(data: dict):
                # Process cron event
                pass

        Args:
            app: DaprApp instance
            binding_name: Binding component name
            route: Optional custom route (defaults to /bindings/{binding_name})

        Returns:
            Decorator function
        """
        route = route or f"/bindings/{binding_name}"

        def decorator(func: Callable):
            @app.binding(binding_name, route=route)
            async def wrapper(request: Dict[str, Any]):
                return await func(request)

            return wrapper

        return decorator

    def close(self):
        """Close Dapr client connection"""
        self.client.close()
