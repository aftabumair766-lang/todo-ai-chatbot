"""
MCP Server Implementation

Embedded MCP server that runs in the same process as FastAPI.
Registers 5 task management tools and handles tool execution requests.

Constitution Compliance:
- Principle I: MCP-First Architecture (embedded server pattern)
- Principle II: Stateless (no server-side state, tools use DB)
"""

import logging
from typing import Any, Callable, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from backend.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    create_tag,
    list_tags,
    delete_tag,
)

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Embedded Model Context Protocol server.

    Manages tool registration and execution for the OpenAI Agents SDK.
    Runs in the same process as FastAPI (no separate server needed).

    Constitution Compliance:
    - Principle I: MCP-First Architecture
    - Principle II: Stateless Design (no state in server, all in DB)
    """

    def __init__(self) -> None:
        """Initialize MCP server with tool registry."""
        self.tools: Dict[str, Callable] = {}
        self._register_tools()
        logger.info("MCP Server initialized with 8 tools (Phase 5 Enhanced)")

    def _register_tools(self) -> None:
        """
        Register all MCP tools with their schemas.

        Tools Registered (Phase 5 Enhanced):
        1. add_task - Create a new task (with priority, due dates, tags, recurrence)
        2. list_tasks - List tasks with filtering (priority, tags, search, sort)
        3. complete_task - Mark task as completed
        4. delete_task - Delete a task
        5. update_task - Update task details (all Phase 5 fields)
        6. create_tag - Create a new tag
        7. list_tags - List all user tags
        8. delete_tag - Delete a tag
        """
        self.tools = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task,
            "create_tag": create_tag,
            "list_tags": list_tags,
            "delete_tag": delete_tag,
        }

    def get_tool_schemas(self) -> list[dict]:
        """
        Get JSON schemas for all registered tools.

        Used by OpenAI Agents SDK to understand available functions.

        Returns:
            list[dict]: Tool schemas in OpenAI function calling format

        Format matches OpenAI function calling specification:
        https://platform.openai.com/docs/guides/function-calling
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task with Phase 5 features (priority, due dates, reminders, recurring tasks, tags). Use this when the user wants to add, create, or make a new task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "title": {
                                "type": "string",
                                "description": "Task title (max 500 characters)",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description or details (max 2000 characters)",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Task priority level (default: medium)",
                                "default": "medium",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Task due date in ISO format (e.g., 2025-12-31T23:59:59)",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "Reminder notification time in ISO format",
                            },
                            "recurrence_type": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "yearly"],
                                "description": "Recurrence pattern for repeating tasks",
                            },
                            "recurrence_interval": {
                                "type": "integer",
                                "description": "Repeat every X days/weeks/months (requires recurrence_type)",
                            },
                            "recurrence_end_date": {
                                "type": "string",
                                "description": "Stop recurring after this date in ISO format",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tag names to organize the task (auto-creates tags if needed)",
                            },
                        },
                        "required": ["user_id", "title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List tasks with Phase 5 filtering (status, priority, tags, search) and sorting. Use this when the user wants to see, view, list, search, or filter their tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by completion status (default: all)",
                                "default": "all",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Filter tasks by priority level",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter tasks by tag names (returns tasks with any of these tags)",
                            },
                            "search": {
                                "type": "string",
                                "description": "Search tasks by title or description (case-insensitive)",
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": ["created_at", "updated_at", "due_date", "priority", "title"],
                                "description": "Sort tasks by field (default: created_at)",
                                "default": "created_at",
                            },
                            "sort_order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Sort order: ascending or descending (default: desc)",
                                "default": "desc",
                            },
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed. Use this when the user wants to complete, finish, or mark a task as done.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to mark as completed",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently delete a task. Use this when the user wants to delete, remove, or cancel a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to delete",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update any task field including Phase 5 features (title, description, priority, due dates, tags, etc.). Use this when the user wants to edit, modify, or update a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to update",
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional, max 500 characters)",
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional, max 2000 characters)",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "New priority level",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date in ISO format",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "New reminder time in ISO format",
                            },
                            "recurrence_type": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "yearly"],
                                "description": "New recurrence pattern",
                            },
                            "recurrence_interval": {
                                "type": "integer",
                                "description": "New recurrence interval",
                            },
                            "recurrence_end_date": {
                                "type": "string",
                                "description": "New recurrence end date in ISO format",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New list of tags (replaces all existing tags)",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_tag",
                    "description": "Create a new tag for organizing tasks. Use this when the user wants to create or add a tag.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "name": {
                                "type": "string",
                                "description": "Tag name (max 50 characters)",
                            },
                            "color": {
                                "type": "string",
                                "description": "Optional hex color code (e.g., #FF5733)",
                            },
                        },
                        "required": ["user_id", "name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tags",
                    "description": "List all tags for the user with usage counts. Use this when the user wants to see or list their tags.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_tag",
                    "description": "Delete a tag (removes it from all tasks). Use this when the user wants to delete or remove a tag.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier from JWT authentication",
                            },
                            "tag_id": {
                                "type": "integer",
                                "description": "ID of the tag to delete",
                            },
                        },
                        "required": ["user_id", "tag_id"],
                    },
                },
            },
        ]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        db: AsyncSession,
    ) -> dict:
        """
        Execute a registered MCP tool.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments (includes user_id and tool-specific params)
            db: Async database session for tool execution

        Returns:
            dict: Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: Tool execution errors

        Constitution Compliance:
        - Principle II: Stateless (no state stored, DB session per request)
        - Principle IV: Security First (user_id validated in tools)
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")

        tool_func = self.tools[tool_name]

        try:
            logger.debug(f"Executing tool: {tool_name} with args: {arguments}")
            result = await tool_func(db=db, **arguments)
            logger.info(f"Tool executed successfully: {tool_name}")
            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}, error: {str(e)}")
            raise


# Global MCP server instance (singleton pattern)
_mcp_server: MCPServer | None = None


def create_mcp_server() -> MCPServer:
    """
    Create or retrieve the singleton MCP server instance.

    Returns:
        MCPServer: Global MCP server instance

    Constitution Compliance:
    - Principle I: MCP-First Architecture (single embedded server)
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server


def get_mcp_server() -> MCPServer:
    """
    Get the global MCP server instance.

    Returns:
        MCPServer: Global MCP server instance

    Raises:
        RuntimeError: If server not initialized
    """
    if _mcp_server is None:
        raise RuntimeError("MCP server not initialized. Call create_mcp_server() first.")
    return _mcp_server
