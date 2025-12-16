"""
Tests for MCP Tools

Constitution Compliance: Principle III (Test-First Development)
"""

import pytest
from backend.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
)


# ============================================================================
# Test add_task
# ============================================================================

@pytest.mark.asyncio
async def test_add_task_success(test_db, mock_user_id):
    """Test successful task creation."""
    result = await add_task(
        db=test_db,
        user_id=mock_user_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
    )

    assert result["success"] is True
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["description"] == "Milk, eggs, bread"
    assert result["task"]["completed"] is False
    assert result["task"]["user_id"] == mock_user_id
    assert "id" in result["task"]


@pytest.mark.asyncio
async def test_add_task_without_description(test_db, mock_user_id):
    """Test task creation without description."""
    result = await add_task(
        db=test_db,
        user_id=mock_user_id,
        title="Simple task",
    )

    assert result["success"] is True
    assert result["task"]["title"] == "Simple task"
    assert result["task"]["description"] is None


@pytest.mark.asyncio
async def test_add_task_empty_title(test_db, mock_user_id):
    """Test that empty title is rejected."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await add_task(
            db=test_db,
            user_id=mock_user_id,
            title="",
        )


@pytest.mark.asyncio
async def test_add_task_title_too_long(test_db, mock_user_id):
    """Test that title longer than 500 chars is rejected."""
    long_title = "A" * 501

    with pytest.raises(ValueError, match="cannot exceed 500"):
        await add_task(
            db=test_db,
            user_id=mock_user_id,
            title=long_title,
        )


# ============================================================================
# Test list_tasks
# ============================================================================

@pytest.mark.asyncio
async def test_list_tasks_empty(test_db, mock_user_id):
    """Test listing tasks when user has none."""
    result = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="all",
    )

    assert result["success"] is True
    assert result["tasks"] == []
    assert result["count"] == 0


@pytest.mark.asyncio
async def test_list_tasks_all(test_db, sample_tasks, mock_user_id):
    """Test listing all tasks."""
    result = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="all",
    )

    assert result["success"] is True
    assert result["count"] == 3
    assert len(result["tasks"]) == 3


@pytest.mark.asyncio
async def test_list_tasks_pending_only(test_db, sample_tasks, mock_user_id):
    """Test listing only pending tasks."""
    result = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="pending",
    )

    assert result["success"] is True
    assert result["count"] == 2  # 2 pending tasks in sample_tasks
    assert all(not task["completed"] for task in result["tasks"])


@pytest.mark.asyncio
async def test_list_tasks_completed_only(test_db, sample_tasks, mock_user_id):
    """Test listing only completed tasks."""
    result = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="completed",
    )

    assert result["success"] is True
    assert result["count"] == 1  # 1 completed task in sample_tasks
    assert all(task["completed"] for task in result["tasks"])


@pytest.mark.asyncio
async def test_list_tasks_user_isolation(test_db, sample_tasks, mock_user_id):
    """Test that users only see their own tasks (Row-Level Security)."""
    # Create task for different user
    await add_task(
        db=test_db,
        user_id="different_user_123",
        title="Other user's task",
    )

    # Original user should only see their 3 tasks
    result = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="all",
    )

    assert result["count"] == 3


# ============================================================================
# Test complete_task
# ============================================================================

@pytest.mark.asyncio
async def test_complete_task_success(test_db, sample_tasks, mock_user_id):
    """Test marking task as completed."""
    task_id = sample_tasks[0].id  # First task (pending)

    result = await complete_task(
        db=test_db,
        user_id=mock_user_id,
        task_id=task_id,
    )

    assert result["success"] is True
    assert result["task"]["id"] == task_id
    assert result["task"]["completed"] is True


@pytest.mark.asyncio
async def test_complete_task_not_found(test_db, mock_user_id):
    """Test completing non-existent task."""
    with pytest.raises(ValueError, match="not found"):
        await complete_task(
            db=test_db,
            user_id=mock_user_id,
            task_id=99999,
        )


@pytest.mark.asyncio
async def test_complete_task_wrong_user(test_db, sample_tasks):
    """Test that user cannot complete another user's task."""
    task_id = sample_tasks[0].id

    with pytest.raises(ValueError, match="does not belong to user"):
        await complete_task(
            db=test_db,
            user_id="different_user_123",
            task_id=task_id,
        )


# ============================================================================
# Test delete_task
# ============================================================================

@pytest.mark.asyncio
async def test_delete_task_success(test_db, sample_tasks, mock_user_id):
    """Test deleting a task."""
    task_id = sample_tasks[0].id

    result = await delete_task(
        db=test_db,
        user_id=mock_user_id,
        task_id=task_id,
    )

    assert result["success"] is True
    assert result["task_id"] == task_id

    # Verify task is deleted
    remaining_tasks = await list_tasks(
        db=test_db,
        user_id=mock_user_id,
        status="all",
    )
    assert remaining_tasks["count"] == 2


@pytest.mark.asyncio
async def test_delete_task_not_found(test_db, mock_user_id):
    """Test deleting non-existent task."""
    with pytest.raises(ValueError, match="not found"):
        await delete_task(
            db=test_db,
            user_id=mock_user_id,
            task_id=99999,
        )


@pytest.mark.asyncio
async def test_delete_task_wrong_user(test_db, sample_tasks):
    """Test that user cannot delete another user's task."""
    task_id = sample_tasks[0].id

    with pytest.raises(ValueError, match="does not belong to user"):
        await delete_task(
            db=test_db,
            user_id="different_user_123",
            task_id=task_id,
        )


# ============================================================================
# Test update_task
# ============================================================================

@pytest.mark.asyncio
async def test_update_task_title(test_db, sample_tasks, mock_user_id):
    """Test updating task title."""
    task_id = sample_tasks[0].id

    result = await update_task(
        db=test_db,
        user_id=mock_user_id,
        task_id=task_id,
        title="Updated title",
    )

    assert result["success"] is True
    assert result["task"]["title"] == "Updated title"


@pytest.mark.asyncio
async def test_update_task_description(test_db, sample_tasks, mock_user_id):
    """Test updating task description."""
    task_id = sample_tasks[0].id

    result = await update_task(
        db=test_db,
        user_id=mock_user_id,
        task_id=task_id,
        description="Updated description",
    )

    assert result["success"] is True
    assert result["task"]["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_task_both_fields(test_db, sample_tasks, mock_user_id):
    """Test updating both title and description."""
    task_id = sample_tasks[0].id

    result = await update_task(
        db=test_db,
        user_id=mock_user_id,
        task_id=task_id,
        title="New title",
        description="New description",
    )

    assert result["success"] is True
    assert result["task"]["title"] == "New title"
    assert result["task"]["description"] == "New description"


@pytest.mark.asyncio
async def test_update_task_no_fields(test_db, sample_tasks, mock_user_id):
    """Test that updating with no fields raises error."""
    task_id = sample_tasks[0].id

    with pytest.raises(ValueError, match="at least one field"):
        await update_task(
            db=test_db,
            user_id=mock_user_id,
            task_id=task_id,
        )


@pytest.mark.asyncio
async def test_update_task_empty_title(test_db, sample_tasks, mock_user_id):
    """Test that empty title is rejected."""
    task_id = sample_tasks[0].id

    with pytest.raises(ValueError, match="cannot be empty"):
        await update_task(
            db=test_db,
            user_id=mock_user_id,
            task_id=task_id,
            title="",
        )


@pytest.mark.asyncio
async def test_update_task_not_found(test_db, mock_user_id):
    """Test updating non-existent task."""
    with pytest.raises(ValueError, match="not found"):
        await update_task(
            db=test_db,
            user_id=mock_user_id,
            task_id=99999,
            title="New title",
        )


@pytest.mark.asyncio
async def test_update_task_wrong_user(test_db, sample_tasks):
    """Test that user cannot update another user's task."""
    task_id = sample_tasks[0].id

    with pytest.raises(ValueError, match="does not belong to user"):
        await update_task(
            db=test_db,
            user_id="different_user_123",
            task_id=task_id,
            title="Hacked title",
        )
