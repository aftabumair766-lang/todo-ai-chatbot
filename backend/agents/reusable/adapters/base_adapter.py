"""
Base Domain Adapter Interface
==============================

Defines the contract for domain-specific adapters that configure the reusable agent.

Any domain (Todo, CRM, E-commerce, Support, etc.) implements this interface to:
- Define system personality and instructions
- Configure tool definitions and handlers
- Customize response formatting
- Handle greetings and special cases
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional, Any


class DomainAdapter(ABC):
    """
    Abstract base class for domain-specific agent configuration.

    Implement this interface to create agents for different domains:
    - TodoDomainAdapter (task management)
    - CRMDomainAdapter (customer relationships)
    - EcommerceDomainAdapter (product catalog, orders)
    - SupportDomainAdapter (ticket management)
    """

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt that defines agent personality and behavior.

        Examples:
        - Todo: "You are a friendly Todo Task Assistant..."
        - CRM: "You are a professional CRM assistant managing customer relationships..."
        - Support: "You are a helpful customer support agent..."

        Returns:
            str: Full system prompt with instructions, formatting rules, and examples
        """
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return OpenAI function calling tool definitions.

        Returns:
            List of tool definitions in OpenAI format:
            [{
                "type": "function",
                "function": {
                    "name": "tool_name",
                    "description": "What the tool does",
                    "parameters": {"type": "object", "properties": {...}}
                }
            }]
        """
        pass

    @abstractmethod
    def get_tool_handlers(self) -> Dict[str, Callable]:
        """
        Return mapping of tool names to handler functions.

        Returns:
            Dict mapping tool names to async functions:
            {
                "add_task": add_task_handler,
                "list_tasks": list_tasks_handler,
                ...
            }
        """
        pass

    def is_greeting(self, message: str) -> bool:
        """
        Check if message is a greeting (optional, domain-specific).

        Args:
            message: User's input message

        Returns:
            bool: True if message is a greeting
        """
        common_greetings = ["hi", "hello", "hey", "greetings", "good morning",
                          "good afternoon", "good evening"]
        return message.lower().strip() in common_greetings

    def get_greeting_response(self) -> Optional[str]:
        """
        Return a domain-specific greeting response (optional).

        Returns:
            str: Greeting message, or None to use default agent behavior
        """
        return None

    def format_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Apply domain-specific formatting to agent responses (optional).

        Override this to add emojis, structure, or custom formatting.

        Args:
            response: Raw agent response
            context: Optional context (tool results, user info, etc.)

        Returns:
            str: Formatted response
        """
        return response

    def get_model_name(self) -> str:
        """
        Return preferred OpenAI model for this domain (optional).

        Returns:
            str: Model name (default: "gpt-4-turbo-preview")
        """
        return "gpt-4-turbo-preview"

    def validate_tool_input(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Validate tool arguments before execution (optional).

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments from OpenAI

        Returns:
            str: Error message if invalid, None if valid
        """
        return None

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate domain-specific error messages (optional).

        Args:
            error: The exception that occurred
            context: Optional context (tool name, user input, etc.)

        Returns:
            str: User-friendly error message
        """
        return f"I encountered an error: {str(error)}. Please try again."
