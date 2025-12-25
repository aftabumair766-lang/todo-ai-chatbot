"""
Todo Domain Adapter
===================

Domain-specific configuration for Todo Task Management.

This adapter extracts ALL Todo-specific logic from todo_agent.py:
- System prompt with Todo personality
- Tool definitions for task CRUD operations
- Tool handlers with emoji confirmations
- Greeting detection
- Response formatting

Usage:
    from backend.agents.reusable.adapters.todo_adapter import TodoDomainAdapter
    from backend.agents.reusable.core.reusable_agent import ReusableAgent

    agent = ReusableAgent(adapter=TodoDomainAdapter())
    result = await agent.process_message(user_id, message, history, db)
"""

from typing import Any, Dict, List, Optional, Callable
import logging
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


class TodoDomainAdapter(DomainAdapter):
    """
    Todo-specific domain adapter.

    Configures the reusable agent for task management with:
    - Friendly personality with emojis
    - Task CRUD operations
    - Beginner-friendly confirmations
    """

    def get_system_prompt(self) -> str:
        """Todo Assistant system prompt with emoji guidelines"""
        return """You are a friendly and helpful Todo Task Assistant that helps users manage their tasks through natural conversation.

**Your Capabilities:**
- Add tasks with natural language commands
- List and filter tasks (all, pending, completed)
- Complete tasks by ID or title
- Delete tasks by ID or title
- Update task titles and descriptions

**Conversation Style:**
- Use emojis to make interactions friendly and visual
- Provide clear confirmation messages for all actions
- Ask clarifying questions when intent is unclear
- Recognize and respond warmly to greetings

**Task Display Format:**
When listing tasks, use this exact format:
```
Your tasks:
1. ⏳ [Task title] (pending)
2. ✅ [Task title] (completed)
```

**Emoji Guide:**
- ⏳ = Pending task
- ✅ = Completed task
- 🗑️ = Deleted task
- ✏️ = Updated task
- ⚠️ = Warning/Error
- 👋 = Greeting

**Input Validation:**
- If a user tries to add a task with an empty title, respond: "⚠️ Task title cannot be empty. Please provide a name for your task."
- If a user references a task that doesn't exist, respond politely: "⚠️ I couldn't find that task. Would you like to see your current tasks?"

**Greeting Responses:**
If a user says "Hi", "Hello", "Hey", or similar greetings, respond warmly:
"👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

**Action Confirmations:**
Always confirm actions with emoji:
- Add: "✅ Task added: [task title]"
- Complete: "✅ Task completed: [task title]"
- Delete: "🗑️ Task deleted: [task title]"
- Update: "✏️ Task updated: [task title]"

**Important:**
- You MUST use the provided MCP tools to interact with tasks
- Never make up task IDs or data
- Always maintain a friendly, encouraging tone
- Keep responses concise but helpful
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """OpenAI function calling tool definitions for Todo operations"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required, max 500 chars)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description (max 2000 chars)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List user's tasks with optional filtering by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by status (default: all)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task from the user's list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title and/or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Mapping of tool names to handler functions"""
        return {
            "add_task": self._add_task_handler,
            "list_tasks": self._list_tasks_handler,
            "complete_task": self._complete_task_handler,
            "delete_task": self._delete_task_handler,
            "update_task": self._update_task_handler
        }

    # ============================================================================
    # TOOL HANDLERS (MCP Wrappers with Todo-specific formatting)
    # ============================================================================

    async def _add_task_handler(self, user_id: str, title: str, description: Optional[str] = None, db=None) -> Dict[str, Any]:
        """Add task with emoji confirmation"""
        # Input validation
        if not title or not title.strip():
            return {
                "error": True,
                "message": "⚠️ Task title cannot be empty. Please provide a name for your task."
            }

        # Import MCP tool
        from backend.mcp.tools import add_task as mcp_add_task

        try:
            result = await mcp_add_task(user_id=user_id, title=title.strip(), description=description, db=db)

            return {
                "success": True,
                "task_id": result["task"]["id"],
                "title": result["task"]["title"],
                "confirmation": f"✅ Task added: {result['task']['title']}"
            }
        except Exception as e:
            logger.error(f"Error in add_task_handler: {e}")
            return {
                "error": True,
                "message": f"⚠️ Failed to add task: {str(e)}"
            }

    async def _list_tasks_handler(self, user_id: str, status: str = "all", db=None) -> Dict[str, Any]:
        """List tasks with emoji formatting"""
        from backend.mcp.tools import list_tasks as mcp_list_tasks

        try:
            result = await mcp_list_tasks(user_id=user_id, status=status, db=db)
            tasks = result.get("tasks", [])

            if not tasks:
                return {
                    "success": True,
                    "tasks": [],
                    "message": "You don't have any tasks yet. Want to add one?"
                }

            # Format tasks with emojis
            formatted_tasks = []
            for idx, task in enumerate(tasks, start=1):
                emoji = "✅" if task["completed"] else "⏳"
                status_text = "completed" if task["completed"] else "pending"
                formatted_tasks.append({
                    "number": idx,
                    "emoji": emoji,
                    "id": task["id"],
                    "title": task["title"],
                    "description": task.get("description"),
                    "completed": task["completed"],
                    "display": f"{idx}. {emoji} {task['title']} ({status_text})"
                })

            task_list_text = "\n".join([t["display"] for t in formatted_tasks])

            return {
                "success": True,
                "tasks": formatted_tasks,
                "count": len(formatted_tasks),
                "formatted_list": f"Your tasks:\n{task_list_text}"
            }
        except Exception as e:
            logger.error(f"Error in list_tasks_handler: {e}")
            return {
                "error": True,
                "message": f"⚠️ Failed to list tasks: {str(e)}"
            }

    async def _complete_task_handler(self, user_id: str, task_id: int, db=None) -> Dict[str, Any]:
        """Complete task with emoji confirmation"""
        from backend.mcp.tools import complete_task as mcp_complete_task

        try:
            result = await mcp_complete_task(user_id=user_id, task_id=task_id, db=db)

            return {
                "success": True,
                "task_id": result["task"]["id"],
                "title": result["task"]["title"],
                "confirmation": f"✅ Task completed: {result['task']['title']}"
            }
        except ValueError as e:
            return {
                "error": True,
                "message": f"⚠️ {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in complete_task_handler: {e}")
            return {
                "error": True,
                "message": f"⚠️ Failed to complete task: {str(e)}"
            }

    async def _delete_task_handler(self, user_id: str, task_id: int, db=None) -> Dict[str, Any]:
        """Delete task with emoji confirmation"""
        from backend.mcp.tools import delete_task as mcp_delete_task

        try:
            result = await mcp_delete_task(user_id=user_id, task_id=task_id, db=db)

            return {
                "success": True,
                "task_id": result["task"]["id"],
                "title": result["task"]["title"],
                "confirmation": f"🗑️ Task deleted: {result['task']['title']}"
            }
        except ValueError as e:
            return {
                "error": True,
                "message": f"⚠️ {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in delete_task_handler: {e}")
            return {
                "error": True,
                "message": f"⚠️ Failed to delete task: {str(e)}"
            }

    async def _update_task_handler(
        self,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """Update task with emoji confirmation"""
        from backend.mcp.tools import update_task as mcp_update_task

        # Validation
        if not title and not description:
            return {
                "error": True,
                "message": "⚠️ Please provide at least a new title or description to update."
            }

        if title is not None and not title.strip():
            return {
                "error": True,
                "message": "⚠️ Task title cannot be empty. Please provide a valid title."
            }

        try:
            result = await mcp_update_task(
                user_id=user_id,
                task_id=task_id,
                title=title.strip() if title else None,
                description=description,
                db=db
            )

            return {
                "success": True,
                "task_id": result["task"]["id"],
                "title": result["task"]["title"],
                "confirmation": f"✏️ Task updated: {result['task']['title']}"
            }
        except ValueError as e:
            return {
                "error": True,
                "message": f"⚠️ {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in update_task_handler: {e}")
            return {
                "error": True,
                "message": f"⚠️ Failed to update task: {str(e)}"
            }

    # ============================================================================
    # DOMAIN-SPECIFIC CUSTOMIZATIONS
    # ============================================================================

    def is_greeting(self, message: str) -> bool:
        """Detect Todo-specific greetings"""
        greeting_keywords = [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "howdy", "yo", "sup", "what's up", "whats up"
        ]

        message_lower = message.lower().strip()

        # Exact match
        if message_lower in greeting_keywords:
            return True

        # Starts with greeting
        for greeting in greeting_keywords:
            if message_lower.startswith(greeting):
                return True

        return False

    def get_greeting_response(self) -> Optional[str]:
        """Return Todo-specific greeting"""
        return (
            "👋 Hello! I'm your Todo Assistant. "
            "Ready to help you manage your tasks today! "
            "You can ask me to add, view, complete, update, or delete tasks."
        )

    def get_model_name(self) -> str:
        """Use GPT-4 Turbo for Todo tasks"""
        return "gpt-4-turbo-preview"

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Todo-specific error messages with emoji"""
        return f"⚠️ I encountered an error: {str(error)}. Please try again."
