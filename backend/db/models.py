"""
Database Models for Todo AI Chatbot

Architecture: SQLModel (Pydantic + SQLAlchemy) with async support
Schema: 3 tables - tasks, conversations, messages
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


# ============================================================================
# Task Model
# ============================================================================

class Task(SQLModel, table=True):
    """
    Todo task created and managed by users via natural language commands.

    Constitution Compliance:
    - Principle V: Database as Source of Truth
    - Principle IV: Security First (user_id filtering)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    title: str = Field(max_length=500, nullable=False, description="Task title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Optional task details")
    completed: bool = Field(default=False, nullable=False, description="Completion status")
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
    """Request model for creating a task"""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskUpdate(SQLModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskResponse(SQLModel):
    """Response model for task operations"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
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
