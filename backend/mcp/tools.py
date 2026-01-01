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
from sqlalchemy import select, or_, and_, delete
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
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
) -> dict:
    """
    List tasks for the user with Phase 5 filtering, search, and sorting.

    MCP Tool Signature:
        Name: list_tasks
        Parameters:
            - user_id (string, required): User identifier from JWT
            - status (string, optional): Filter by status ("all", "pending", "completed")
            - priority (string, optional): Filter by priority (low/medium/high/urgent)
            - tags (list[string], optional): Filter by tag names
            - search (string, optional): Search in title and description
            - sort_by (string, optional): Sort field (created_at/due_date/priority/title)
            - sort_order (string, optional): Sort order (asc/desc)

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        status: Filter option - "all", "pending", or "completed"
        priority: Filter by priority level (Phase 5)
        tags: Filter by tags (Phase 5)
        search: Search query (Phase 5)
        sort_by: Sort field (Phase 5)
        sort_order: Sort direction (Phase 5)

    Returns:
        dict: Task list result with Phase 5 fields

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

        # Phase 5: Priority filter
        if priority:
            query = query.where(Task.priority == priority)

        # Phase 5: Search in title and description
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )

        # Phase 5: Tag filter
        if tags:
            # Join with task_tags and tags tables
            query = query.join(TaskTag, Task.id == TaskTag.task_id)
            query = query.join(Tag, TaskTag.tag_id == Tag.id)
            query = query.where(Tag.name.in_(tags))

        # Phase 5: Sorting
        if sort_by == "due_date":
            sort_column = Task.due_date
        elif sort_by == "priority":
            # Custom priority order: urgent > high > medium > low
            priority_order = {
                "urgent": 0,
                "high": 1,
                "medium": 2,
                "low": 3
            }
            sort_column = Task.priority
        elif sort_by == "title":
            sort_column = Task.title
        else:
            sort_column = Task.created_at

        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()

        # Get tags for each task
        task_list = []
        for task in tasks:
            # Fetch tags for this task
            tags_query = select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
            tags_result = await db.execute(tags_query)
            task_tags = [tag.name for tag in tags_result.scalars().all()]

            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "recurrence_type": task.recurrence_type,
                "tags": task_tags,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            })

        logger.info(f"Listed {len(task_list)} tasks for user {user_id} (status={status}, priority={priority}, search={search})")

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

        # Fetch tags for response
        tags_query = (
            select(Tag.name)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == task.id)
        )
        tags_result = await db.execute(tags_query)
        task_tags = [row[0] for row in tags_result.all()]

        logger.info(f"Task completed: id={task_id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "reminder_sent": task.reminder_sent,
                "recurrence_type": task.recurrence_type,
                "recurrence_interval": task.recurrence_interval,
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "parent_task_id": task.parent_task_id,
                "tags": task_tags,
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

        # Fetch tags before deleting (they'll be gone after deletion)
        tags_query = (
            select(Tag.name)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == task.id)
        )
        tags_result = await db.execute(tags_query)
        task_tags = [row[0] for row in tags_result.all()]

        # Save task info before deleting (with Phase 5 fields)
        task_info = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
            "reminder_sent": task.reminder_sent,
            "recurrence_type": task.recurrence_type,
            "recurrence_interval": task.recurrence_interval,
            "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
            "parent_task_id": task.parent_task_id,
            "tags": task_tags,
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
    priority: Optional[str] = None,
    due_date: Optional[datetime] = None,
    reminder_time: Optional[datetime] = None,
    recurrence_type: Optional[str] = None,
    recurrence_interval: Optional[int] = None,
    recurrence_end_date: Optional[datetime] = None,
    tags: Optional[List[str]] = None,
) -> dict:
    """
    Update task fields (Phase 5 Enhanced).

    MCP Tool Signature:
        Name: update_task
        Parameters:
            - user_id (string, required): User identifier from JWT
            - task_id (integer, required): Task ID to update
            - title (string, optional): New task title
            - description (string, optional): New task description
            - priority (string, optional): New priority (low/medium/high/urgent)
            - due_date (datetime, optional): New due date
            - reminder_time (datetime, optional): New reminder time
            - recurrence_type (string, optional): New recurrence type
            - recurrence_interval (int, optional): New recurrence interval
            - recurrence_end_date (datetime, optional): New recurrence end date
            - tags (list[string], optional): New tags list

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        task_id: ID of task to update
        All other args: Optional update fields

    Returns:
        dict: Update result with Phase 5 fields

    Raises:
        ValueError: If validation fails

    Constitution Compliance:
    - Principle IV: Security First (verify user_id ownership)
    - Principle V: Database as Source of Truth (update persisted)
    """
    # Validate at least one field is being updated
    if all(v is None for v in [title, description, priority, due_date, reminder_time, recurrence_type, recurrence_interval, recurrence_end_date, tags]):
        raise ValueError("Must provide at least one field to update")

    # Validate field lengths
    if title is not None:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > 500:
            raise ValueError("Task title cannot exceed 500 characters")

    if description is not None and len(description) > 2000:
        raise ValueError("Task description cannot exceed 2000 characters")

    # Validate priority
    if priority is not None:
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

    # Validate recurrence
    if recurrence_type is not None:
        valid_recurrence = ["daily", "weekly", "monthly", "yearly"]
        if recurrence_type not in valid_recurrence:
            raise ValueError(f"Recurrence type must be one of: {', '.join(valid_recurrence)}")

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

        # Update Phase 5 fields
        if priority is not None:
            task.priority = priority

        if due_date is not None:
            task.due_date = due_date

        if reminder_time is not None:
            task.reminder_time = reminder_time

        if recurrence_type is not None:
            task.recurrence_type = recurrence_type

        if recurrence_interval is not None:
            task.recurrence_interval = recurrence_interval

        if recurrence_end_date is not None:
            task.recurrence_end_date = recurrence_end_date

        # Handle tag updates if provided
        if tags is not None:
            # Delete existing task-tag associations
            delete_query = delete(TaskTag).where(TaskTag.task_id == task_id)
            await db.execute(delete_query)

            # Add new tags
            for tag_name in tags:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue

                # Find or create tag
                tag_query = select(Tag).where(and_(Tag.user_id == user_id, Tag.name == tag_name))
                tag_result = await db.execute(tag_query)
                tag = tag_result.scalar_one_or_none()

                if not tag:
                    tag = Tag(user_id=user_id, name=tag_name)
                    db.add(tag)
                    await db.flush()  # Get the tag ID

                # Create task-tag association
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                db.add(task_tag)

        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        # Fetch tags for response
        tags_query = (
            select(Tag.name)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == task.id)
        )
        tags_result = await db.execute(tags_query)
        task_tags = [row[0] for row in tags_result.all()]

        logger.info(f"Task updated: id={task_id}, user_id={user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "reminder_sent": task.reminder_sent,
                "recurrence_type": task.recurrence_type,
                "recurrence_interval": task.recurrence_interval,
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "parent_task_id": task.parent_task_id,
                "tags": task_tags,
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


# ============================================================================
# Tag Management Functions (Phase 5)
# ============================================================================

async def create_tag(
    db: AsyncSession,
    user_id: str,
    name: str,
    color: Optional[str] = None,
) -> dict:
    """
    Create a new tag for organizing tasks.

    MCP Tool Signature:
        Name: create_tag
        Parameters:
            - user_id (string, required): User identifier from JWT
            - name (string, required): Tag name (max 50 chars)
            - color (string, optional): Hex color code (e.g., #FF5733)

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        name: Tag name
        color: Optional hex color code

    Returns:
        dict: Created tag information

    Raises:
        ValueError: If tag already exists or validation fails

    Constitution Compliance:
    - Principle IV: Security First (user_id filtering)
    - Principle V: Database as Source of Truth
    """
    # Validate tag name
    if not name or not name.strip():
        raise ValueError("Tag name cannot be empty")

    if len(name) > 50:
        raise ValueError("Tag name cannot exceed 50 characters")

    # Validate color if provided
    if color:
        if not color.startswith("#") or len(color) != 7:
            raise ValueError("Color must be a hex code (e.g., #FF5733)")

    try:
        # Check if tag already exists for this user
        query = select(Tag).where(and_(Tag.user_id == user_id, Tag.name == name.strip()))
        result = await db.execute(query)
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            raise ValueError(f"Tag '{name.strip()}' already exists")

        # Create new tag
        tag = Tag(
            user_id=user_id,
            name=name.strip(),
            color=color,
        )

        db.add(tag)
        await db.commit()
        await db.refresh(tag)

        logger.info(f"Tag created: id={tag.id}, name={tag.name}, user_id={user_id}")

        return {
            "success": True,
            "tag": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
            },
            "message": "Tag created successfully",
        }

    except ValueError as e:
        logger.warning(f"Tag creation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to create tag for user {user_id}: {str(e)}")
        await db.rollback()
        raise


async def list_tags(
    db: AsyncSession,
    user_id: str,
) -> dict:
    """
    List all tags for a user.

    MCP Tool Signature:
        Name: list_tags
        Parameters:
            - user_id (string, required): User identifier from JWT

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT

    Returns:
        dict: List of user's tags with usage counts

    Constitution Compliance:
    - Principle IV: Security First (user_id filtering)
    - Principle V: Database as Source of Truth
    """
    try:
        # Fetch all tags for user
        query = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
        result = await db.execute(query)
        tags = result.scalars().all()

        # Get usage count for each tag
        tags_with_count = []
        for tag in tags:
            count_query = select(TaskTag).where(TaskTag.tag_id == tag.id)
            count_result = await db.execute(count_query)
            usage_count = len(count_result.scalars().all())

            tags_with_count.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "usage_count": usage_count,
                "created_at": tag.created_at.isoformat(),
            })

        logger.info(f"Listed {len(tags_with_count)} tags for user {user_id}")

        return {
            "success": True,
            "tags": tags_with_count,
            "count": len(tags_with_count),
        }

    except Exception as e:
        logger.error(f"Failed to list tags for user {user_id}: {str(e)}")
        raise


async def delete_tag(
    db: AsyncSession,
    user_id: str,
    tag_id: int,
) -> dict:
    """
    Delete a tag (removes it from all tasks).

    MCP Tool Signature:
        Name: delete_tag
        Parameters:
            - user_id (string, required): User identifier from JWT
            - tag_id (integer, required): Tag ID to delete

    Args:
        db: Async database session
        user_id: User ID from Better Auth JWT
        tag_id: ID of tag to delete

    Returns:
        dict: Deletion result

    Raises:
        ValueError: If tag not found or doesn't belong to user

    Constitution Compliance:
    - Principle IV: Security First (user_id filtering)
    - Principle V: Database as Source of Truth
    """
    try:
        # Fetch tag with user_id filter (security)
        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            raise ValueError(
                f"Tag {tag_id} not found or does not belong to user {user_id}"
            )

        # Save tag info before deleting
        tag_info = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat(),
        }

        # Delete tag (cascade will remove task_tags associations)
        await db.delete(tag)
        await db.commit()

        logger.info(f"Tag deleted: id={tag_id}, name={tag.name}, user_id={user_id}")

        return {
            "success": True,
            "tag": tag_info,
            "message": "Tag deleted successfully",
        }

    except ValueError as e:
        logger.warning(f"Tag deletion failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to delete tag {tag_id} for user {user_id}: {str(e)}")
        await db.rollback()
        raise
