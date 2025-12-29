"""
MCP Tools for Task Management

5 tools implementing the Model Context Protocol for todo operations.
All tools enforce user_id filtering for security (Row-Level Security pattern).

Constitution Compliance:
- Principle I: MCP-First Architecture
- Principle IV: Security First (user_id in all queries)
- Principle V: Database as Source of Truth
- Principle III: Test-First Development (defensive error handling)
"""

import logging
from datetime import datetime
from typing import Optional, Literal, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from backend.db.models import Task, Tag, TaskTag

logger = logging.getLogger(__name__)


# ============================================================================
# Tool 1: add_task
# ============================================================================

async def add_task(
    db: AsyncSession,
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "medium",
    due_date: Optional[datetime] = None,
    reminder_time: Optional[datetime] = None,
    recurrence_type: Optional[str] = None,
    recurrence_interval: Optional[int] = None,
    recurrence_end_date: Optional[datetime] = None,
    tags: Optional[List[str]] = None,
) -> dict:
    """
    Create a new task for the user (Phase 5 Enhanced).

    MCP Tool Signature:
        Name: add_task
        Parameters:
            - user_id (string, required): User identifier from JWT
            - title (string, required): Task title (max 500 chars)
            - description (string, optional): Task details (max 2000 chars)
            - priority (string, optional): Priority level (low/medium/high/urgent)
            - due_date (datetime, optional): Task due date
            - reminder_time (datetime, optional): Reminder notification time
            - recurrence_type (string, optional): daily/weekly/monthly/yearly
            - recurrence_interval (int, optional): Repeat every X units
            - recurrence_end_date (datetime, optional): Stop recurrence after date
            - tags (list[string], optional): List of tag names

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        title: Task title
        description: Optional task description
        priority: Task priority (Phase 5)
        due_date: Task due date (Phase 5)
        reminder_time: Reminder time (Phase 5)
        recurrence_type: Recurrence pattern (Phase 5)
        recurrence_interval: Recurrence interval (Phase 5)
        recurrence_end_date: Recurrence end date (Phase 5)
        tags: List of tag names (Phase 5)

    Returns:
        dict: Task creation result with Phase 5 fields

    Raises:
        ValueError: If validation fails
        Exception: Database errors

    Constitution Compliance:
    - Principle IV: Security First (user_id filtering)
    - Principle V: Database as Source of Truth (immediate DB write)
    """
    # Input validation
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    if len(title) > 500:
        raise ValueError("Task title cannot exceed 500 characters")

    if description and len(description) > 2000:
        raise ValueError("Task description cannot exceed 2000 characters")

    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority and priority not in valid_priorities:
        raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

    # Validate recurrence
    valid_recurrence = ["daily", "weekly", "monthly", "yearly"]
    if recurrence_type and recurrence_type not in valid_recurrence:
        raise ValueError(f"Recurrence type must be one of: {', '.join(valid_recurrence)}")

    try:
        # Create task object with Phase 5 fields
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
            priority=priority or "medium",
            due_date=due_date,
            reminder_time=reminder_time,
            recurrence_type=recurrence_type,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
        )

        # Save to database
        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Handle tags if provided
        task_tags = []
        if tags:
            for tag_name in tags:
                # Find or create tag
                tag_query = select(Tag).where(
                    and_(Tag.user_id == user_id, Tag.name == tag_name.strip())
                )
                result = await db.execute(tag_query)
                tag = result.scalar_one_or_none()

                if not tag:
                    # Create new tag
                    tag = Tag(user_id=user_id, name=tag_name.strip())
                    db.add(tag)
                    await db.commit()
                    await db.refresh(tag)

                # Create task-tag association
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                db.add(task_tag)
                task_tags.append(tag_name.strip())

            await db.commit()

        logger.info(f"Task created: id={task.id}, user_id={user_id}, title={title[:50]}, priority={priority}, tags={task_tags}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "recurrence_type": task.recurrence_type,
                "recurrence_interval": task.recurrence_interval,
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "tags": task_tags if task_tags else [],
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            "message": "Task created successfully",
        }

    except Exception as e:
        logger.error(f"Failed to create task for user {user_id}: {str(e)}")
        await db.rollback()
        raise


# ============================================================================
# Tool 2: list_tasks
# ============================================================================

async def list_tasks(
    db: AsyncSession,
    user_id: str,
    status: Literal["all", "pending", "completed"] = "all",
) -> dict:
    """
    List tasks for the user with optional status filtering.

    MCP Tool Signature:
        Name: list_tasks
        Parameters:
            - user_id (string, required): User identifier from JWT
            - status (string, optional): Filter by status ("all", "pending", "completed")

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        status: Filter option - "all", "pending", or "completed"

    Returns:
        dict: Task list result
        {
            "success": true,
            "tasks": [
                {
                    "id": 123,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": false,
                    "created_at": "2025-12-14T10:30:00Z",
                    "updated_at": "2025-12-14T10:30:00Z"
                },
                ...
            ],
            "count": 5,
            "filter": "pending"
        }

    Constitution Compliance:
    - Principle IV: Security First (ALWAYS filter by user_id)
    - Principle V: Database as Source of Truth (fetch fresh data)
    """
    try:
        # Build base query with user_id filter (Row-Level Security)
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        # "all" means no additional filter

        # Order by created_at descending (newest first)
        query = query.order_by(Task.created_at.desc())

        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()

        # Format response
        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]

        logger.info(f"Listed {len(task_list)} tasks for user {user_id} (filter={status})")

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list),
            "filter": status,
        }

    except Exception as e:
        logger.error(f"Failed to list tasks for user {user_id}: {str(e)}")
        raise


# ============================================================================
# Tool 3: complete_task
# ============================================================================

async def complete_task(
    db: AsyncSession,
    user_id: str,
    task_id: int,
) -> dict:
    """
    Mark a task as completed.

    MCP Tool Signature:
        Name: complete_task
        Parameters:
            - user_id (string, required): User identifier from JWT
            - task_id (integer, required): Task ID to complete

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        task_id: ID of task to mark as completed

    Returns:
        dict: Completion result
        {
            "success": true,
            "task": {
                "id": 123,
                "title": "Buy groceries",
                "completed": true,
                ...
            },
            "message": "Task marked as completed"
        }

    Raises:
        ValueError: If task not found or doesn't belong to user

    Constitution Compliance:
    - Principle IV: Security First (verify user_id ownership)
    - Principle V: Database as Source of Truth (update persisted)
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

        # Update completion status
        task.completed = True
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        logger.info(f"Task completed: id={task_id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            "message": "Task marked as completed",
        }

    except ValueError as e:
        logger.warning(f"Task completion failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to complete task {task_id} for user {user_id}: {str(e)}")
        await db.rollback()
        raise


# ============================================================================
# Tool 4: delete_task
# ============================================================================

async def delete_task(
    db: AsyncSession,
    user_id: str,
    task_id: int,
) -> dict:
    """
    Delete a task permanently.

    MCP Tool Signature:
        Name: delete_task
        Parameters:
            - user_id (string, required): User identifier from JWT
            - task_id (integer, required): Task ID to delete

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        task_id: ID of task to delete

    Returns:
        dict: Deletion result
        {
            "success": true,
            "task_id": 123,
            "message": "Task deleted successfully"
        }

    Raises:
        ValueError: If task not found or doesn't belong to user

    Constitution Compliance:
    - Principle IV: Security First (verify user_id ownership)
    - Principle V: Database as Source of Truth (immediate deletion)
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

        # Save task info before deleting
        task_info = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        # Delete task
        await db.delete(task)
        await db.commit()

        logger.info(f"Task deleted: id={task_id}, user_id={user_id}")

        return {
            "success": True,
            "task": task_info,
            "message": "Task deleted successfully",
        }

    except ValueError as e:
        logger.warning(f"Task deletion failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id} for user {user_id}: {str(e)}")
        await db.rollback()
        raise


# ============================================================================
# Tool 5: update_task
# ============================================================================

async def update_task(
    db: AsyncSession,
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update task title and/or description.

    MCP Tool Signature:
        Name: update_task
        Parameters:
            - user_id (string, required): User identifier from JWT
            - task_id (integer, required): Task ID to update
            - title (string, optional): New task title
            - description (string, optional): New task description

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        task_id: ID of task to update
        title: Optional new title
        description: Optional new description

    Returns:
        dict: Update result
        {
            "success": true,
            "task": {
                "id": 123,
                "title": "Updated title",
                "description": "Updated description",
                ...
            },
            "message": "Task updated successfully"
        }

    Raises:
        ValueError: If task not found, doesn't belong to user, or validation fails

    Constitution Compliance:
    - Principle IV: Security First (verify user_id ownership)
    - Principle V: Database as Source of Truth (update persisted)
    """
    # Validate at least one field is being updated
    if title is None and description is None:
        raise ValueError("Must provide at least one field to update (title or description)")

    # Validate field lengths
    if title is not None:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > 500:
            raise ValueError("Task title cannot exceed 500 characters")

    if description is not None and len(description) > 2000:
        raise ValueError("Task description cannot exceed 2000 characters")

    try:
        # Fetch task with user_id filter (security)
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(
                f"Task {task_id} not found or does not belong to user {user_id}"
            )

        # Update fields
        if title is not None:
            task.title = title.strip()

        if description is not None:
            task.description = description.strip() if description.strip() else None

        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        logger.info(f"Task updated: id={task_id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            "message": "Task updated successfully",
        }

    except ValueError as e:
        logger.warning(f"Task update failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id} for user {user_id}: {str(e)}")
        await db.rollback()
        raise
