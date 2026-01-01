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
- Set task priority levels (low, medium, high, urgent)
- Set due dates and reminder times for tasks
- Create and manage colorful tags for organization
- List and filter tasks (all, pending, completed)
- Search tasks by keywords
- Filter tasks by priority level or tags
- Sort tasks by any field (priority, due date, created date, etc.)
- Complete tasks by ID or title
- Delete tasks by ID or title
- Update task titles, descriptions, priority, tags, and due dates

**Conversation Style:**
- Use emojis to make interactions friendly and visual
- Provide clear confirmation messages for all actions
- Ask clarifying questions when intent is unclear
- Recognize and respond warmly to greetings

**Task Display Format:**
When listing tasks, use this format:
```
Your tasks:
1. 🔴 [URGENT] Task title (pending) 🏷️ work, urgent
2. 🟠 [HIGH] Task title - Due: 2024-01-15 (pending) 🏷️ personal
3. ✅ [MEDIUM] Task title (completed)
```

**Emoji Guide:**
- 🔴 = Urgent priority
- 🟠 = High priority
- 🟡 = Medium priority
- 🟢 = Low priority
- ⏳ = Pending task
- ✅ = Completed task
- 🗑️ = Deleted task
- ✏️ = Updated task
- 🏷️ = Tags
- 📅 = Due date
- ⚠️ = Warning/Error
- 👋 = Greeting

**Input Validation:**
- If a user tries to add a task with an empty title, respond: "⚠️ Task title cannot be empty. Please provide a name for your task."
- If a user references a task that doesn't exist, respond politely: "⚠️ I couldn't find that task. Would you like to see your current tasks?"

**Greeting Responses:**
If a user says "Hi", "Hello", "Hey", or similar greetings, respond warmly:
"👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks. I can also help you organize with tags and priorities!"

**Action Confirmations:**
Always confirm actions with emoji:
- Add: "✅ Task added: [task title] with [priority] priority"
- Complete: "✅ Task completed: [task title]"
- Delete: "🗑️ Task deleted: [task title]"
- Update: "✏️ Task updated: [task title]"
- Create Tag: "🏷️ Tag created: [tag name] ([color])"

**Important:**
- You MUST use the provided MCP tools to interact with tasks and tags
- Never make up task IDs or data
- Always maintain a friendly, encouraging tone
- Keep responses concise but helpful
- When users mention priorities, use: urgent, high, medium, or low
- Tags are automatically created when adding/updating tasks
"""


# ============================================================================
# MCP TOOL WRAPPERS (Stateless - Call MCP Server)
# ============================================================================

async def add_task_tool(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "medium",
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    tags: Optional[List[str]] = None,
    db=None
) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Add a new task with Phase 5 features

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
    from datetime import datetime

    try:
        # Parse date strings if provided
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                pass

        reminder_datetime = None
        if reminder_time:
            try:
                reminder_datetime = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
            except:
                pass

        result = await mcp_add_task(
            user_id=user_id,
            title=title.strip(),
            description=description,
            priority=priority,
            due_date=due_datetime,
            reminder_time=reminder_datetime,
            tags=tags,
            db=db
        )

        # Enhanced confirmation message with Phase 5 features
        task = result["task"]
        priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
        confirmation = f"✅ Task added: {priority_emoji} {task['title']}"

        if task.get("tags"):
            confirmation += f" 🏷️ {', '.join(task['tags'])}"

        if task.get("due_date"):
            confirmation += f" 📅 Due: {task['due_date'][:10]}"

        return {
            "success": True,
            "task_id": task["id"],
            "title": task["title"],
            "priority": task.get("priority"),
            "tags": task.get("tags", []),
            "due_date": task.get("due_date"),
            "confirmation": confirmation
        }
    except Exception as e:
        logger.error(f"Error in add_task_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to add task: {str(e)}"
        }


async def list_tasks_tool(
    user_id: str,
    status: str = "all",
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db=None
) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: List tasks with enhanced formatting and Phase 5 filtering

    Enhanced: Adds emoji indicators, priority levels, tags, search, and sorting
    """
    from backend.mcp.tools import list_tasks as mcp_list_tasks

    try:
        result = await mcp_list_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            tags=tags,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )
        tasks = result.get("tasks", [])

        if not tasks:
            return {
                "success": True,
                "tasks": [],
                "message": "You don't have any tasks yet. Want to add one?"
            }

        # Enhanced task list formatting with Phase 5 features
        formatted_tasks = []
        for idx, task in enumerate(tasks, start=1):
            # Priority emoji
            priority_emoji = {
                "urgent": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(task.get("priority", "medium"), "🟡")

            # Status emoji
            status_emoji = "✅" if task["completed"] else "⏳"
            status_text = "completed" if task["completed"] else "pending"

            # Build display string
            display = f"{idx}. {priority_emoji} [{task.get('priority', 'medium').upper()}] {task['title']} ({status_text})"

            # Add tags if present
            if task.get("tags"):
                display += f" 🏷️ {', '.join(task['tags'])}"

            # Add due date if present
            if task.get("due_date"):
                display += f" 📅 Due: {task['due_date'][:10]}"

            formatted_tasks.append({
                "number": idx,
                "emoji": status_emoji,
                "priority_emoji": priority_emoji,
                "id": task["id"],
                "title": task["title"],
                "description": task.get("description"),
                "priority": task.get("priority"),
                "tags": task.get("tags", []),
                "due_date": task.get("due_date"),
                "completed": task["completed"],
                "display": display
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
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    tags: Optional[List[str]] = None,
    db=None
) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Update task with Phase 5 features

    Enhanced: Supports updating priority, tags, due dates, and more
    """
    from backend.mcp.tools import update_task as mcp_update_task
    from datetime import datetime

    # Validation: at least one field required
    if not any([title, description, priority, due_date, reminder_time, tags]):
        return {
            "error": True,
            "message": "⚠️ Please provide at least one field to update."
        }

    # Input validation for empty title
    if title is not None and not title.strip():
        return {
            "error": True,
            "message": "⚠️ Task title cannot be empty. Please provide a valid title."
        }

    try:
        # Parse date strings if provided
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                pass

        reminder_datetime = None
        if reminder_time:
            try:
                reminder_datetime = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
            except:
                pass

        result = await mcp_update_task(
            user_id=user_id,
            task_id=task_id,
            title=title.strip() if title else None,
            description=description,
            priority=priority,
            due_date=due_datetime,
            reminder_time=reminder_datetime,
            tags=tags,
            db=db
        )

        # Enhanced confirmation with Phase 5 features
        task = result["task"]
        priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
        confirmation = f"✏️ Task updated: {priority_emoji} {task['title']}"

        if task.get("tags"):
            confirmation += f" 🏷️ {', '.join(task['tags'])}"

        return {
            "success": True,
            "task_id": task["id"],
            "title": task["title"],
            "priority": task.get("priority"),
            "tags": task.get("tags", []),
            "confirmation": confirmation
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


async def create_tag_tool(
    user_id: str,
    name: str,
    color: Optional[str] = None,
    db=None
) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Create a new tag with optional color

    Phase 5 Feature: Tag management
    """
    from backend.mcp.tools import create_tag as mcp_create_tag

    # Validate tag name
    if not name or not name.strip():
        return {
            "error": True,
            "message": "⚠️ Tag name cannot be empty."
        }

    try:
        result = await mcp_create_tag(
            user_id=user_id,
            name=name.strip(),
            color=color,
            db=db
        )

        tag = result["tag"]
        confirmation = f"🏷️ Tag created: {tag['name']}"
        if tag.get("color"):
            confirmation += f" ({tag['color']})"

        return {
            "success": True,
            "tag_id": tag["id"],
            "name": tag["name"],
            "color": tag.get("color"),
            "confirmation": confirmation
        }
    except ValueError as e:
        # Tag already exists or invalid color
        return {
            "error": True,
            "message": f"⚠️ {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error in create_tag_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to create tag: {str(e)}"
        }


async def list_tags_tool(user_id: str, db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: List all tags with usage statistics

    Phase 5 Feature: Tag analytics
    """
    from backend.mcp.tools import list_tags as mcp_list_tags

    try:
        result = await mcp_list_tags(user_id=user_id, db=db)
        tags = result.get("tags", [])

        if not tags:
            return {
                "success": True,
                "tags": [],
                "message": "You don't have any tags yet. Tags are automatically created when you add or update tasks!"
            }

        # Format tag list
        formatted_tags = []
        for idx, tag in enumerate(tags, start=1):
            usage = tag.get("usage_count", 0)
            color = tag.get("color", "")
            display = f"{idx}. 🏷️ {tag['name']}"
            if color:
                display += f" ({color})"
            display += f" - {usage} task{'s' if usage != 1 else ''}"

            formatted_tags.append({
                "number": idx,
                "id": tag["id"],
                "name": tag["name"],
                "color": color,
                "usage_count": usage,
                "display": display
            })

        tag_list_text = "\n".join([t["display"] for t in formatted_tags])

        return {
            "success": True,
            "tags": formatted_tags,
            "count": len(formatted_tags),
            "formatted_list": f"Your tags:\n{tag_list_text}"
        }
    except Exception as e:
        logger.error(f"Error in list_tags_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to list tags: {str(e)}"
        }


async def delete_tag_tool(user_id: str, tag_id: int, db=None) -> Dict[str, Any]:
    """
    MCP Tool Wrapper: Delete a tag

    Phase 5 Feature: Tag management
    """
    from backend.mcp.tools import delete_tag as mcp_delete_tag

    try:
        result = await mcp_delete_tag(user_id=user_id, tag_id=tag_id, db=db)

        return {
            "success": True,
            "tag_id": result["tag"]["id"],
            "name": result["tag"]["name"],
            "confirmation": f"🗑️ Tag deleted: {result['tag']['name']}"
        }
    except ValueError as e:
        # Tag not found
        return {
            "error": True,
            "message": f"⚠️ {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error in delete_tag_tool: {e}")
        return {
            "error": True,
            "message": f"⚠️ Failed to delete tag: {str(e)}"
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
                "description": "Add a new task to the user's todo list with priority, tags, and due dates",
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
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level (default: medium). Use 'urgent' for critical tasks, 'high' for important tasks, 'medium' for normal tasks, 'low' for tasks that can wait."
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (e.g., '2024-12-31T17:00:00'). Can be parsed from natural language like 'tomorrow', 'next week', etc."
                        },
                        "reminder_time": {
                            "type": "string",
                            "description": "Reminder time in ISO format (e.g., '2024-12-31T09:00:00')"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tag names to organize the task (e.g., ['work', 'urgent', 'personal']). Tags are automatically created if they don't exist."
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
                "description": "List user's tasks with advanced filtering, search, and sorting capabilities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by completion status (default: all)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Filter tasks by priority level (e.g., show only urgent tasks)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter tasks that have ALL of these tags (e.g., ['work', 'urgent'])"
                        },
                        "search": {
                            "type": "string",
                            "description": "Search tasks by keyword in title or description (case-insensitive)"
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["created_at", "updated_at", "due_date", "priority", "title"],
                            "description": "Field to sort by (default: created_at)"
                        },
                        "sort_order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort order: 'asc' for ascending, 'desc' for descending (default: desc)"
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
                "description": "Update a task's title, description, priority, tags, or due dates",
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
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "New priority level (optional)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in ISO format (optional)"
                        },
                        "reminder_time": {
                            "type": "string",
                            "description": "New reminder time in ISO format (optional)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New list of tags (replaces existing tags, optional). Tags are automatically created if they don't exist."
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_tag",
                "description": "Create a new tag with an optional color for organizing tasks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Tag name (required, e.g., 'work', 'personal', 'urgent')"
                        },
                        "color": {
                            "type": "string",
                            "description": "Hex color code for the tag (optional, e.g., '#FF5733', '#00FF00')"
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tags",
                "description": "List all user's tags with usage statistics (how many tasks use each tag)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_tag",
                "description": "Delete a tag (removes tag from all tasks that use it)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tag_id": {
                            "type": "integer",
                            "description": "ID of the tag to delete"
                        }
                    },
                    "required": ["tag_id"]
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
                        priority=function_args.get("priority", "medium"),
                        due_date=function_args.get("due_date"),
                        reminder_time=function_args.get("reminder_time"),
                        tags=function_args.get("tags"),
                        db=db
                    )
                elif function_name == "list_tasks":
                    result = await list_tasks_tool(
                        user_id=user_id,
                        status=function_args.get("status", "all"),
                        priority=function_args.get("priority"),
                        tags=function_args.get("tags"),
                        search=function_args.get("search"),
                        sort_by=function_args.get("sort_by", "created_at"),
                        sort_order=function_args.get("sort_order", "desc"),
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
                        priority=function_args.get("priority"),
                        due_date=function_args.get("due_date"),
                        reminder_time=function_args.get("reminder_time"),
                        tags=function_args.get("tags"),
                        db=db
                    )
                elif function_name == "create_tag":
                    result = await create_tag_tool(
                        user_id=user_id,
                        name=function_args.get("name"),
                        color=function_args.get("color"),
                        db=db
                    )
                elif function_name == "list_tags":
                    result = await list_tags_tool(
                        user_id=user_id,
                        db=db
                    )
                elif function_name == "delete_tag":
                    result = await delete_tag_tool(
                        user_id=user_id,
                        tag_id=function_args.get("tag_id"),
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
