"""
Database Models for Todo AI Chatbot

Architecture: SQLModel (Pydantic + SQLAlchemy) with async support
Schema: 4 tables - users, tasks, conversations, messages
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


# ============================================================================
# User Model (Better Auth)
# ============================================================================

class User(SQLModel, table=True):
    """
    User model for Better Auth authentication.

    Constitution Compliance:
    - Principle IV: Security First (passwords hashed, never stored in plaintext)
    - Principle V: Database as Source of Truth
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False, max_length=255, description="User email (unique)")
    username: str = Field(unique=True, index=True, nullable=False, max_length=100, description="Username (unique)")
    hashed_password: str = Field(nullable=False, description="Bcrypt hashed password")
    is_active: bool = Field(default=True, nullable=False, description="Account active status")
    is_verified: bool = Field(default=False, nullable=False, description="Email verification status")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-12-25T00:00:00Z",
                "updated_at": "2025-12-25T00:00:00Z"
            }
        }


# ============================================================================
# Task Model
# ============================================================================

class Task(SQLModel, table=True):
    """
    Todo task created and managed by users via natural language commands.

    Constitution Compliance:
    - Principle V: Database as Source of Truth
    - Principle IV: Security First (user_id filtering)

    Phase 5 Features:
    - Recurring tasks (daily, weekly, monthly)
    - Due dates & reminders
    - Priority levels (low, medium, high, urgent)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    title: str = Field(max_length=500, nullable=False, description="Task title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Optional task details")
    completed: bool = Field(default=False, nullable=False, description="Completion status")

    # Phase 5: Priority feature
    priority: str = Field(default="medium", nullable=False, description="Priority: low, medium, high, urgent")

    # Phase 5: Due dates & reminders
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    reminder_time: Optional[datetime] = Field(default=None, description="Reminder notification time")
    reminder_sent: bool = Field(default=False, nullable=False, description="Whether reminder was sent")

    # Phase 5: Recurring tasks
    recurrence_type: Optional[str] = Field(default=None, description="Recurrence: daily, weekly, monthly, yearly")
    recurrence_interval: Optional[int] = Field(default=None, description="Repeat every X days/weeks/months")
    recurrence_end_date: Optional[datetime] = Field(default=None, description="Stop recurrence after this date")
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", description="Original recurring task ID")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "auth0|507f1f77bcf86cd799439011",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread from Whole Foods",
                "completed": False,
                "created_at": "2025-12-14T10:30:00Z",
                "updated_at": "2025-12-14T10:30:00Z"
            }
        }


# ============================================================================
# Tag Model (Phase 5)
# ============================================================================

class Tag(SQLModel, table=True):
    """
    Tags for organizing tasks (Phase 5 feature).

    Constitution Compliance:
    - Principle V: Database as Source of Truth
    - Principle IV: Security First (user_id filtering)
    """
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    name: str = Field(max_length=50, nullable=False, description="Tag name")
    color: Optional[str] = Field(default=None, max_length=7, description="Tag color (hex code)")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "auth0|507f1f77bcf86cd799439011",
                "name": "work",
                "color": "#FF5733",
                "created_at": "2025-12-30T10:00:00Z"
            }
        }


# ============================================================================
# TaskTag Association (Phase 5)
# ============================================================================

class TaskTag(SQLModel, table=True):
    """
    Many-to-many relationship between tasks and tags (Phase 5 feature).
    """
    __tablename__ = "task_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True, nullable=False)
    tag_id: int = Field(foreign_key="tags.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_id": 123,
                "tag_id": 5,
                "created_at": "2025-12-30T10:00:00Z"
            }
        }


# ============================================================================
# Conversation Model
# ============================================================================

class Conversation(SQLModel, table=True):
    """
    Chat session containing a series of messages between user and AI.

    Constitution Compliance:
    - Principle II: Stateless Server Design (conversation loaded from DB each request)
    - Principle V: Database as Source of Truth
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (lazy-loaded, not stored in DB)
    messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "user_id": "auth0|507f1f77bcf86cd799439011",
                "created_at": "2025-12-14T10:00:00Z",
                "updated_at": "2025-12-14T10:45:00Z"
            }
        }


# ============================================================================
# Message Model
# ============================================================================

class Message(SQLModel, table=True):
    """
    Individual message in a conversation thread.

    Constitution Compliance:
    - Principle II: Stateless Server Design (history loaded from DB)
    - Principle IV: Security First (user_id for audit trail)
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False, description="User ID (audit trail)")
    role: str = Field(nullable=False, description="Message sender role: 'user' or 'assistant'")
    content: str = Field(nullable=False, description="Message text content")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (lazy-loaded, not stored in DB)
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 456,
                "conversation_id": 123,
                "user_id": "auth0|507f1f77bcf86cd799439011",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2025-12-14T10:30:00Z"
            }
        }


# ============================================================================
# Pydantic Models for API (Request/Response)
# ============================================================================

class TaskCreate(SQLModel):
    """Request model for creating a task (Phase 5 enhanced)"""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default="medium", description="low, medium, high, urgent")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    reminder_time: Optional[datetime] = Field(default=None, description="Reminder time")
    recurrence_type: Optional[str] = Field(default=None, description="daily, weekly, monthly, yearly")
    recurrence_interval: Optional[int] = Field(default=None, description="Repeat every X units")
    recurrence_end_date: Optional[datetime] = Field(default=None, description="Stop recurrence after")
    tags: Optional[List[str]] = Field(default=None, description="List of tag names")


class TaskUpdate(SQLModel):
    """Request model for updating a task (Phase 5 enhanced)"""
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default=None, description="low, medium, high, urgent")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    reminder_time: Optional[datetime] = Field(default=None, description="Reminder time")
    recurrence_type: Optional[str] = Field(default=None, description="daily, weekly, monthly, yearly")
    recurrence_interval: Optional[int] = Field(default=None, description="Repeat every X units")
    recurrence_end_date: Optional[datetime] = Field(default=None, description="Stop recurrence after")
    tags: Optional[List[str]] = Field(default=None, description="List of tag names")


class TaskResponse(SQLModel):
    """Response model for task operations (Phase 5 enhanced)"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    due_date: Optional[datetime]
    reminder_time: Optional[datetime]
    reminder_sent: bool
    recurrence_type: Optional[str]
    recurrence_interval: Optional[int]
    recurrence_end_date: Optional[datetime]
    parent_task_id: Optional[int]
    tags: Optional[List[str]] = Field(default=None, description="List of tag names")
    created_at: datetime
    updated_at: datetime


class MessageCreate(SQLModel):
    """Request model for creating a message"""
    conversation_id: Optional[int] = None
    role: str  # Should be 'user' or 'assistant'
    content: str = Field(min_length=1)


class MessageResponse(SQLModel):
    """Response model for messages"""
    id: int
    conversation_id: int
    user_id: str
    role: str
    content: str
    created_at: datetime


# ============================================================================
# Tag Models (Phase 5)
# ============================================================================

class TagCreate(SQLModel):
    """Request model for creating a tag"""
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7, description="Hex color code")


class TagResponse(SQLModel):
    """Response model for tag operations"""
    id: int
    user_id: str
    name: str
    color: Optional[str]
    created_at: datetime


# ============================================================================
# Auth Models (Request/Response)
# ============================================================================

class UserRegister(SQLModel):
    """Request model for user registration"""
    email: str = Field(min_length=3, max_length=255, description="Valid email address")
    username: str = Field(min_length=3, max_length=100, description="Username (3-100 chars)")
    password: str = Field(min_length=8, max_length=72, description="Password (8-72 chars, bcrypt limit)")


class UserLogin(SQLModel):
    """Request model for user login"""
    email: str = Field(description="Email address")
    password: str = Field(description="Password")


class UserResponse(SQLModel):
    """Response model for user data (no password)"""
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(SQLModel):
    """Response model for authentication tokens"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(description="Authenticated user data")
