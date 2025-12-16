"""
Todo AI Agent with OpenAI Agents SDK and MCP Tools Integration

Architecture: Stateless agent that orchestrates MCP tools for task management.
Constitution Compliance: Principle I (MCP-First), Principle II (Stateless)
"""

from typing import Any, Dict, List, Optional
import logging
from openai import AsyncOpenAI
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================================
# AGENT SYSTEM PROMPT (Enhanced for Beginner-Friendly UX)
# ============================================================================

AGENT_SYSTEM_PROMPT = """You are a friendly and helpful Todo Task Assistant that helps users manage their tasks through natural conversation.

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


# ============================================================================
# MCP TOOL WRAPPERS (Stateless - Call MCP Server)
# ============================================================================

async def add_task_tool(user_id: str, title: str, description: Optional[str] = None, db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Add a new task

    Validation: Empty title check happens here (agent-level validation)
    """
    # Input validation (beginner-friendly feature #4)
    if not title or not title.strip():
        return {
            "error": True,
            "message": "⚠️ Task title cannot be empty. Please provide a name for your task."
        }

    # Import here to avoid circular dependency
    from backend.mcp.tools import add_task as mcp_add_task

    try:
        result = await mcp_add_task(user_id=user_id, title=title.strip(), description=description, db=db)

        # Enhanced confirmation message (beginner-friendly feature #1)
        return {
            "success": True,
            "task_id": result["task"]["id"],
            "title": result["task"]["title"],
            "confirmation": f"✅ Task added: {result['task']['title']}"
        }
    except Exception as e:
        logger.error(f"Error in add_task_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to add task: {str(e)}"
        }


async def list_tasks_tool(user_id: str, status: str = "all", db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: List tasks with enhanced formatting

    Enhanced: Adds emoji indicators (⏳/✅) and numbered list format
    """
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

        # Enhanced task list formatting (beginner-friendly features #2 and #3)
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

        # Format for agent response
        task_list_text = "\n".join([t["display"] for t in formatted_tasks])

        return {
            "success": True,
            "tasks": formatted_tasks,
            "count": len(formatted_tasks),
            "formatted_list": f"Your tasks:\n{task_list_text}"
        }
    except Exception as e:
        logger.error(f"Error in list_tasks_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to list tasks: {str(e)}"
        }


async def complete_task_tool(user_id: str, task_id: int, db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Mark task as complete

    Enhanced: Confirmation message with emoji
    """
    from backend.mcp.tools import complete_task as mcp_complete_task

    try:
        result = await mcp_complete_task(user_id=user_id, task_id=task_id, db=db)

        # Enhanced confirmation (beginner-friendly feature #1)
        return {
            "success": True,
            "task_id": result["task"]["id"],
            "title": result["task"]["title"],
            "confirmation": f"✅ Task completed: {result['task']['title']}"
        }
    except ValueError as e:
        # Task not found or already completed
        return {
            "error": True,
            "message": f"⚠️ {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error in complete_task_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to complete task: {str(e)}"
        }


async def delete_task_tool(user_id: str, task_id: int, db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Delete a task

    Enhanced: Confirmation message with emoji
    """
    from backend.mcp.tools import delete_task as mcp_delete_task

    try:
        result = await mcp_delete_task(user_id=user_id, task_id=task_id, db=db)

        # Enhanced confirmation (beginner-friendly feature #1)
        return {
            "success": True,
            "task_id": result["task"]["id"],
            "title": result["task"]["title"],
            "confirmation": f"🗑️ Task deleted: {result['task']['title']}"
        }
    except ValueError as e:
        # Task not found
        return {
            "error": True,
            "message": f"⚠️ {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error in delete_task_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to delete task: {str(e)}"
        }


async def update_task_tool(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    db=None
) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Update task title and/or description

    Enhanced: Confirmation message with emoji, validates at least one field provided
    """
    from backend.mcp.tools import update_task as mcp_update_task

    # Validation: at least one field required
    if not title and not description:
        return {
            "error": True,
            "message": "⚠️ Please provide at least a new title or description to update."
        }

    # Input validation for empty title
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

        # Enhanced confirmation (beginner-friendly feature #1)
        return {
            "success": True,
            "task_id": result["task"]["id"],
            "title": result["task"]["title"],
            "confirmation": f"✏️ Task updated: {result['task']['title']}"
        }
    except ValueError as e:
        # Task not found
        return {
            "error": True,
            "message": f"⚠️ {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error in update_task_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to update task: {str(e)}"
        }


# ============================================================================
# GREETING DETECTION (Beginner-Friendly Feature #5)
# ============================================================================

GREETING_KEYWORDS = [
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "howdy", "yo", "sup", "what's up", "whats up"
]

def is_greeting(message: str) -> bool:
    """Detect if message is a greeting (case-insensitive)"""
    message_lower = message.lower().strip()

    # Check for exact greeting keywords
    if message_lower in GREETING_KEYWORDS:
        return True

    # Check if message starts with greeting
    for greeting in GREETING_KEYWORDS:
        if message_lower.startswith(greeting):
            return True

    return False


def get_greeting_response() -> str:
    """Return friendly greeting response"""
    return (
        "👋 Hello! I'm your Todo Assistant. "
        "Ready to help you manage your tasks today! "
        "You can ask me to add, view, complete, update, or delete tasks."
    )


# ============================================================================
# AGENT RUNNER (OpenAI Agents SDK Integration)
# ============================================================================

async def run_todo_agent(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]],
    db
) -> Dict[str, Any]:
    """
    Run Todo Agent with OpenAI Agents SDK

    Args:
        user_id: Authenticated user ID
        message: User's latest message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        db: Database session (injected, stateless)

    Returns:
        {
            "response": str,  # Agent's response text
            "tool_calls": List[Dict],  # Tools invoked (for transparency)
        }

    Constitution Compliance:
        - Stateless: No in-memory conversation storage
        - MCP-First: All task operations via MCP tool wrappers
    """

    # Beginner-Friendly Feature #5: Greeting Detection
    if is_greeting(message):
        return {
            "response": get_greeting_response(),
            "tool_calls": []
        }

    # Build messages array for OpenAI
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT}
    ]

    # Add conversation history (last 50 messages for token budget)
    messages.extend(conversation_history[-50:])

    # Add current user message
    messages.append({"role": "user", "content": message})

    # Tool definitions for OpenAI function calling
    tools = [
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

    # Call OpenAI API (async)
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or gpt-4, gpt-3.5-turbo
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message_response = response.choices[0].message
        tool_calls_made = []

        # Handle tool calls (MCP tool invocations)
        if message_response.tool_calls:
            for tool_call in message_response.tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)  # Parse JSON args

                logger.info(f"Agent calling tool: {function_name} with args: {function_args}")

                # Invoke corresponding MCP tool wrapper
                if function_name == "add_task":
                    result = await add_task_tool(
                        user_id=user_id,
                        title=function_args.get("title"),
                        description=function_args.get("description"),
                        db=db
                    )
                elif function_name == "list_tasks":
                    result = await list_tasks_tool(
                        user_id=user_id,
                        status=function_args.get("status", "all"),
                        db=db
                    )
                elif function_name == "complete_task":
                    result = await complete_task_tool(
                        user_id=user_id,
                        task_id=function_args.get("task_id"),
                        db=db
                    )
                elif function_name == "delete_task":
                    result = await delete_task_tool(
                        user_id=user_id,
                        task_id=function_args.get("task_id"),
                        db=db
                    )
                elif function_name == "update_task":
                    result = await update_task_tool(
                        user_id=user_id,
                        task_id=function_args.get("task_id"),
                        title=function_args.get("title"),
                        description=function_args.get("description"),
                        db=db
                    )
                else:
                    result = {"error": True, "message": f"Unknown tool: {function_name}"}

                tool_calls_made.append({
                    "tool": function_name,
                    "arguments": function_args,
                    "result": result
                })

                # Add tool result back to messages for next agent turn
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            # Get final response from agent after tool calls
            second_response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages
            )
            final_response_text = second_response.choices[0].message.content
        else:
            # No tool calls, use direct response
            final_response_text = message_response.content

        return {
            "response": final_response_text,
            "tool_calls": tool_calls_made
        }

    except Exception as e:
        logger.error(f"Error in run_todo_agent: {e}")
        return {
            "response": f"⚠️ I encountered an error: {str(e)}. Please try again.",
            "tool_calls": []
        }
