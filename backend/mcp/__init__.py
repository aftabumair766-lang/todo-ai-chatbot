"""
Model Context Protocol (MCP) Server for Todo AI Chatbot

Provides 5 MCP tools for task management:
1. add_task - Create a new task
2. list_tasks - List tasks with filtering
3. complete_task - Mark task as completed
4. delete_task - Delete a task
5. update_task - Update task details

Constitution Compliance:
- Principle I: MCP-First Architecture
- Principle IV: Security First (user_id filtering)
- Principle V: Database as Source of Truth
"""

from backend.mcp.server import create_mcp_server
from backend.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
)

__all__ = [
    "create_mcp_server",
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
]
