# Adding Skills to Todo AI Chatbot

This guide shows you how to extend your chatbot with new capabilities.

## Table of Contents
1. [MCP Tools (Chatbot Skills)](#mcp-tools-chatbot-skills)
2. [Custom Slash Commands](#custom-slash-commands)
3. [Examples](#examples)

---

## MCP Tools (Chatbot Skills)

MCP tools are functions your AI agent can call to perform actions. You currently have 5 tools.

### Step 1: Add Tool Function to `backend/mcp/tools.py`

**Example: Adding Task Priority Support**

```python
# ============================================================================
# Tool 6: set_task_priority
# ============================================================================

from typing import Literal

async def set_task_priority(
    db: AsyncSession,
    user_id: str,
    task_id: int,
    priority: Literal["low", "medium", "high", "urgent"] = "medium",
) -> dict:
    """
    Set the priority level for a task.

    MCP Tool Signature:
        Name: set_task_priority
        Parameters:
            - user_id (string, required): User identifier from JWT
            - task_id (integer, required): Task ID to update
            - priority (string, required): Priority level ("low", "medium", "high", "urgent")

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        task_id: ID of task to update
        priority: Priority level

    Returns:
        dict: Priority update result
        {
            "success": true,
            "task": {
                "id": 123,
                "title": "Buy groceries",
                "priority": "high",
                ...
            },
            "message": "Task priority set to high"
        }
    """
    try:
        # Fetch task with user_id filter (security)
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(
                f"Task {task_id} not found or does not belong to user {user_id}"
            )

        # Update priority
        task.priority = priority
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        logger.info(f"Task priority updated: id={task_id}, priority={priority}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            "message": f"Task priority set to {priority}",
        }

    except ValueError as e:
        logger.warning(f"Priority update failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to set priority for task {task_id}: {str(e)}")
        await db.rollback()
        raise
```

### Step 2: Add Database Field (if needed)

Edit `backend/db/models.py` to add the priority field:

```python
from sqlmodel import Field, SQLModel
from typing import Optional, Literal

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")  # NEW FIELD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Step 3: Register Tool in MCP Server

Edit `backend/mcp/server.py` to register your new tool:

```python
from backend.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    set_task_priority,  # NEW IMPORT
)

# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    # ... existing tools ...
    {
        "type": "function",
        "function": {
            "name": "set_task_priority",
            "description": "Set the priority level for a task (low, medium, high, urgent)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level for the task"
                    }
                },
                "required": ["task_id", "priority"]
            }
        }
    }
]

# Tool execution mapping
async def execute_tool(tool_name: str, arguments: dict, db: AsyncSession, user_id: str):
    """Execute the requested MCP tool"""

    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task,
        "set_task_priority": set_task_priority,  # NEW TOOL
    }

    # Rest of function...
```

### Step 4: Create Database Migration (Optional but Recommended)

```bash
# Create migration for priority field
cd backend
alembic revision --autogenerate -m "Add priority field to tasks"
alembic upgrade head
```

Or manually run SQL:

```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
```

### Step 5: Add Tests

Create tests in `backend/tests/test_mcp_tools.py`:

```python
@pytest.mark.asyncio
async def test_set_task_priority(db_session, test_user_id):
    """Test setting task priority"""

    # Create a task
    result = await add_task(
        db=db_session,
        user_id=test_user_id,
        title="Important task"
    )
    task_id = result["task"]["id"]

    # Set priority to high
    result = await set_task_priority(
        db=db_session,
        user_id=test_user_id,
        task_id=task_id,
        priority="high"
    )

    assert result["success"] is True
    assert result["task"]["priority"] == "high"
    assert result["message"] == "Task priority set to high"

@pytest.mark.asyncio
async def test_set_task_priority_invalid_task(db_session, test_user_id):
    """Test setting priority for non-existent task"""

    with pytest.raises(ValueError, match="not found"):
        await set_task_priority(
            db=db_session,
            user_id=test_user_id,
            task_id=99999,
            priority="high"
        )
```

### Step 6: Test Your New Skill

Start your app and try:

```
User: "Set task 1 to high priority"
Bot: "✅ Task priority set to high"

User: "Mark my grocery task as urgent"
Bot: "✅ Task priority set to urgent: Buy groceries"
```

---

## More MCP Tool Ideas

Here are skills you could add to your chatbot:

### 1. Task Tags/Labels

```python
async def add_task_tag(db, user_id, task_id, tag):
    """Add a tag/label to a task"""

async def remove_task_tag(db, user_id, task_id, tag):
    """Remove a tag from a task"""

async def list_tasks_by_tag(db, user_id, tag):
    """List all tasks with a specific tag"""
```

**Usage:**
- "Tag task 1 as #work"
- "Show me all #personal tasks"
- "Remove #urgent tag from task 3"

### 2. Due Dates

```python
async def set_task_due_date(db, user_id, task_id, due_date):
    """Set a due date for a task"""

async def list_overdue_tasks(db, user_id):
    """List all tasks past their due date"""

async def list_tasks_due_today(db, user_id):
    """List tasks due today"""
```

**Usage:**
- "Set task 1 due date to tomorrow"
- "Show me overdue tasks"
- "What's due today?"

### 3. Task Notes/Comments

```python
async def add_task_note(db, user_id, task_id, note):
    """Add a note/comment to a task"""

async def list_task_notes(db, user_id, task_id):
    """List all notes for a task"""
```

**Usage:**
- "Add note to task 1: Called the store, they close at 6pm"
- "Show notes for task 2"

### 4. Subtasks

```python
async def add_subtask(db, user_id, parent_task_id, title):
    """Add a subtask under a parent task"""

async def list_subtasks(db, user_id, parent_task_id):
    """List all subtasks for a task"""
```

**Usage:**
- "Add subtask to task 1: Buy milk"
- "Add subtask to task 1: Buy eggs"
- "Show subtasks for grocery shopping"

### 5. Task Statistics

```python
async def get_task_stats(db, user_id):
    """Get statistics about user's tasks"""
    # Returns: total tasks, completed count, pending count, completion rate

async def get_productivity_report(db, user_id, days=7):
    """Get productivity report for last N days"""
```

**Usage:**
- "Show my task statistics"
- "Give me a productivity report"

### 6. Task Search

```python
async def search_tasks(db, user_id, query):
    """Search tasks by keyword in title or description"""
```

**Usage:**
- "Search for tasks containing 'groceries'"
- "Find all tasks mentioning mom"

### 7. Task Reminders

```python
async def set_task_reminder(db, user_id, task_id, remind_at):
    """Set a reminder for a task"""

async def list_upcoming_reminders(db, user_id):
    """List reminders for today and tomorrow"""
```

**Usage:**
- "Remind me about task 1 at 3pm"
- "Show upcoming reminders"

### 8. Recurring Tasks

```python
async def create_recurring_task(db, user_id, title, frequency):
    """Create a task that repeats (daily, weekly, monthly)"""
```

**Usage:**
- "Create a daily task to exercise"
- "Add a weekly task to review goals"

### 9. Task Categories/Projects

```python
async def assign_task_to_project(db, user_id, task_id, project_name):
    """Assign a task to a project/category"""

async def list_projects(db, user_id):
    """List all projects with task counts"""
```

**Usage:**
- "Assign task 1 to Work project"
- "Show all my projects"
- "List tasks in Personal project"

### 10. Bulk Operations

```python
async def complete_all_tasks(db, user_id, filter_by=None):
    """Mark multiple tasks as complete"""

async def delete_completed_tasks(db, user_id):
    """Delete all completed tasks"""
```

**Usage:**
- "Complete all tasks tagged #today"
- "Delete all completed tasks"

---

## Custom Slash Commands

Slash commands are **development workflow automation** tools. They help you work faster on the project.

### Current Slash Commands

You already have these commands in `.claude/commands/`:

- `/sp.specify` - Create feature specification
- `/sp.plan` - Create implementation plan
- `/sp.tasks` - Generate task breakdown
- `/sp.implement` - Execute implementation
- `/sp.adr` - Create Architectural Decision Record
- `/sp.phr` - Create Prompt History Record
- `/sp.git.commit_pr` - Git workflow automation
- `/sp.analyze` - Analyze artifacts
- `/sp.clarify` - Ask clarification questions
- `/sp.checklist` - Generate custom checklist
- `/sp.constitution` - Manage project principles

### Creating a New Slash Command

**Example: `/test-all` - Run all tests with coverage**

Create `.claude/commands/test-all.md`:

```markdown
---
description: Run all tests with coverage report
---

## Test All Command

Run the complete test suite with coverage reporting.

### Steps:

1. Navigate to backend directory
2. Activate virtual environment
3. Run pytest with coverage
4. Display results

### Execution:

```bash
cd /home/umair/todo-chatbot/backend
source venv/bin/activate
pytest -v --cov=. --cov-report=term-missing --cov-report=html
echo "Coverage report generated at backend/htmlcov/index.html"
```

### Expected Output:

- All tests passing (56/56)
- Coverage percentage
- HTML coverage report location
```

**Usage:**
```
/test-all
```

### More Slash Command Ideas

**1. `/deploy-check` - Pre-deployment verification**

```markdown
---
description: Verify project is ready for deployment
---

## Deployment Check

Runs all pre-deployment checks:

1. Run all tests
2. Check for .env in git
3. Verify .gitignore
4. Check for TODO/FIXME comments
5. Run type checking
6. Check requirements.txt is up to date

```bash
# Run checks...
```
```

**2. `/db-migrate` - Run database migrations**

```markdown
---
description: Create and apply database migrations
---

## Database Migration

1. Generate migration from model changes
2. Review migration
3. Apply to database

```bash
cd backend
alembic revision --autogenerate -m "$ARGUMENTS"
alembic upgrade head
```
```

**3. `/add-tool` - Scaffold new MCP tool**

```markdown
---
description: Create boilerplate for new MCP tool
---

## Add New MCP Tool

Creates a new tool template in backend/mcp/tools.py

Provide tool name as argument: /add-tool set_task_priority
```

---

## Complete Example: Adding "Task Priority" Feature

Let's implement a complete new skill from start to finish:

### 1. Update Database Model

File: `backend/db/models.py`

```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    priority: str = Field(default="medium")  # Add this line
```

### 2. Add MCP Tool

File: `backend/mcp/tools.py`

```python
async def set_task_priority(
    db: AsyncSession,
    user_id: str,
    task_id: int,
    priority: Literal["low", "medium", "high", "urgent"] = "medium",
) -> dict:
    """Set task priority level"""

    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise ValueError(f"Task {task_id} not found")

    task.priority = priority
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
        },
        "message": f"Task priority set to {priority}"
    }
```

### 3. Register Tool

File: `backend/mcp/server.py`

```python
TOOL_DEFINITIONS = [
    # ... existing tools ...
    {
        "type": "function",
        "function": {
            "name": "set_task_priority",
            "description": "Set priority level for a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"]
                    }
                },
                "required": ["task_id", "priority"]
            }
        }
    }
]
```

### 4. Update Frontend (Optional)

File: `frontend/src/App.tsx`

Add priority badge display in task list:

```typescript
const getPriorityColor = (priority: string) => {
  switch(priority) {
    case 'urgent': return '🔴';
    case 'high': return '🟠';
    case 'medium': return '🟡';
    case 'low': return '🟢';
    default: return '';
  }
};

// In your task display:
<div className="task-priority">
  {getPriorityColor(task.priority)} {task.priority}
</div>
```

### 5. Run Database Migration

```bash
cd /home/umair/todo-chatbot/backend

# Option 1: SQL Migration
psql $DATABASE_URL -c "ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';"

# Option 2: Using Alembic
alembic revision --autogenerate -m "Add priority to tasks"
alembic upgrade head
```

### 6. Test It

```bash
cd backend
pytest tests/test_mcp_tools.py -v -k priority
```

### 7. Try It Out

Start the app and test:

```
User: "Add a task to buy groceries"
Bot: "✅ Task added: Buy groceries"

User: "Set task 1 to high priority"
Bot: "✅ Task priority set to high"

User: "Show my tasks"
Bot: "📋 Your tasks:
     1. 🟠 Buy groceries (high priority)"
```

---

## Summary

**Two Types of Skills:**

1. **MCP Tools** - Chatbot capabilities (add_task, set_priority, etc.)
   - Add to `backend/mcp/tools.py`
   - Register in `backend/mcp/server.py`
   - Update database model if needed
   - Add tests

2. **Slash Commands** - Development automation (/test-all, /deploy-check)
   - Create markdown file in `.claude/commands/`
   - Add description and bash commands
   - Use during development

**Next Steps:**

Choose a skill to add:
- Task priorities (shown above)
- Due dates
- Tags/labels
- Subtasks
- Search functionality
- Statistics/reports

Would you like me to help implement any specific skill?
