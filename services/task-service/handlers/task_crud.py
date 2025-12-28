"""Task CRUD handlers using Dapr State Store"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

# Import Dapr State Store wrapper
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from dapr.state import DaprStateStore


# Pydantic models for API
class TaskCreate(BaseModel):
    """Request model for creating a task"""
    title: str = Field(..., min_length=1, max_length=500)
    user_id: str = Field(..., description="User ID from JWT token")
    due_date: Optional[datetime] = None
    recurring_task_id: Optional[UUID] = None
    instance_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Response model for a task"""
    id: UUID
    user_id: str
    title: str
    completed: bool
    recurring_task_id: Optional[UUID] = None
    instance_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# Create router
router = APIRouter(prefix="/tasks", tags=["tasks"])


# Initialize state store (will be injected)
_state_store: Optional[DaprStateStore] = None


def init_router(state_store: DaprStateStore):
    """Initialize router with Dapr State Store"""
    global _state_store
    _state_store = state_store


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate) -> TaskResponse:
    """
    Create a new task and save to Dapr State Store.

    Args:
        task_data: Task creation data

    Returns:
        Created task

    Raises:
        HTTPException: If task creation fails
    """
    if not _state_store:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="State store not initialized"
        )

    # Generate task ID
    task_id = uuid4()

    # Create task data
    task = {
        "id": str(task_id),
        "user_id": task_data.user_id,
        "title": task_data.title,
        "completed": False,
        "recurring_task_id": str(task_data.recurring_task_id) if task_data.recurring_task_id else None,
        "instance_date": task_data.instance_date.isoformat() if task_data.instance_date else None,
        "due_date": task_data.due_date.isoformat() if task_data.due_date else None,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None
    }

    # Save to Dapr State Store
    await _state_store.save_state(
        entity="task",
        user_id=task_data.user_id,
        entity_id=str(task_id),
        data=task
    )

    # TODO: Publish task.created event (T036)

    return TaskResponse(**task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, user_id: str) -> TaskResponse:
    """
    Get a task by ID from Dapr State Store.

    Args:
        task_id: Task UUID
        user_id: User ID (from JWT token)

    Returns:
        Task data

    Raises:
        HTTPException: If task not found
    """
    if not _state_store:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="State store not initialized"
        )

    # Get from Dapr State Store
    task = await _state_store.get_state(
        entity="task",
        user_id=user_id,
        entity_id=str(task_id)
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse(**task)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(user_id: str, completed: Optional[bool] = None) -> List[TaskResponse]:
    """
    List all tasks for a user.

    Args:
        user_id: User ID (from JWT token)
        completed: Optional filter by completion status

    Returns:
        List of tasks

    Note: This is a simplified implementation. In production, use Dapr State Query API.
    """
    if not _state_store:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="State store not initialized"
        )

    # TODO: Implement proper Dapr State Query API
    # For now, return empty list (will be implemented in Phase 4)
    return []


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, user_id: str, update_data: TaskUpdate) -> TaskResponse:
    """
    Update a task in Dapr State Store.

    Args:
        task_id: Task UUID
        user_id: User ID (from JWT token)
        update_data: Task update data

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found
    """
    if not _state_store:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="State store not initialized"
        )

    # Get existing task
    task = await _state_store.get_state(
        entity="task",
        user_id=user_id,
        entity_id=str(task_id)
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Update fields
    if update_data.title is not None:
        task["title"] = update_data.title
    if update_data.completed is not None:
        task["completed"] = update_data.completed
        if update_data.completed and not task.get("completed_at"):
            task["completed_at"] = datetime.utcnow().isoformat()
            # TODO: Publish task.completed event (T036)
    if update_data.due_date is not None:
        task["due_date"] = update_data.due_date.isoformat()

    # Save updated task
    await _state_store.save_state(
        entity="task",
        user_id=user_id,
        entity_id=str(task_id),
        data=task
    )

    return TaskResponse(**task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, user_id: str):
    """
    Delete a task from Dapr State Store.

    Args:
        task_id: Task UUID
        user_id: User ID (from JWT token)

    Raises:
        HTTPException: If task not found
    """
    if not _state_store:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="State store not initialized"
        )

    # Check if task exists
    task = await _state_store.get_state(
        entity="task",
        user_id=user_id,
        entity_id=str(task_id)
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Delete from state store
    await _state_store.delete_state(
        entity="task",
        user_id=user_id,
        entity_id=str(task_id)
    )

    # TODO: Publish task.deleted event (T036)

    return None
