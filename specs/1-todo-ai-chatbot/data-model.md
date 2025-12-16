# Data Model: Todo AI Chatbot

**Feature**: 1-todo-ai-chatbot
**Date**: 2025-12-14
**ORM**: SQLModel (Pydantic + SQLAlchemy)
**Database**: Neon PostgreSQL (Serverless)

## Entity Relationship Diagram

```
User (from Better Auth - external)
  |
  | 1:N
  |
  ├─> Task
  |     - id (PK)
  |     - user_id (FK → User, indexed)
  |     - title
  |     - description
  |     - completed
  |     - created_at
  |     - updated_at
  |
  └─> Conversation
        - id (PK)
        - user_id (FK → User, indexed)
        - created_at
        - updated_at
        |
        | 1:N
        |
        └─> Message
              - id (PK)
              - conversation_id (FK → Conversation)
              - user_id (FK → User, for audit)
              - role (user | assistant)
              - content
              - created_at
```

## Database Models (SQLModel)

### Task Model

**Purpose**: Represents a todo item belonging to a user

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Todo task created and managed by users via natural language commands.

    Indexed fields: user_id (for efficient user-scoped queries)
    Constraints: user_id required, title required, completed defaults to False
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    title: str = Field(max_length=500, nullable=False, description="Task title (2-10 words typical)")
    description: Optional[str] = Field(default=None, max_length=2000, description="Optional task details")
    completed: bool = Field(default=False, nullable=False, description="Task completion status")
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
```

**Indexes**:
- `user_id` (B-tree index) - For filtering tasks by user
- Composite index `(user_id, completed)` - For filtering pending/completed tasks efficiently

**Constraints**:
- `user_id` NOT NULL - Every task must belong to a user
- `title` NOT NULL - Every task must have a title
- `completed` NOT NULL DEFAULT FALSE - Explicit completion status
- `title` max 500 chars - Prevent abuse
- `description` max 2000 chars - Reasonable limit

**State Transitions**:
```
[New Task] → created (completed=False)
[Complete Task] → completed=False → completed=True
[Update Task] → updates title/description, updated_at refreshed
[Delete Task] → hard delete (no soft delete for MVP)
```

---

### Conversation Model

**Purpose**: Represents a chat session between a user and the AI assistant

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Chat session containing a series of messages between user and AI.

    Indexed fields: user_id (for efficient user-scoped queries)
    Relationships: One conversation has many messages
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (not stored in DB, lazy-loaded)
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
```

**Indexes**:
- `user_id` (B-tree index) - For listing user's conversations

**Constraints**:
- `user_id` NOT NULL - Every conversation must belong to a user

**Lifecycle**:
- Created when first message sent with no conversation_id
- Updated timestamp refreshed on each new message
- Persists indefinitely (no automatic deletion for MVP)

---

### Message Model

**Purpose**: Represents a single message in a conversation (user or assistant)

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, Literal

class Message(SQLModel, table=True):
    """
    Individual message in a conversation thread.

    Indexed fields: conversation_id (for efficient conversation history queries)
    Relationships: Many messages belong to one conversation
    Role: 'user' for user input, 'assistant' for AI responses
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False, description="User ID (for audit trail)")
    role: Literal["user", "assistant"] = Field(nullable=False, description="Message sender role")
    content: str = Field(nullable=False, description="Message text content")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (not stored in DB, lazy-loaded)
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
```

**Indexes**:
- `conversation_id` (B-tree index) - For loading conversation history efficiently
- Composite index `(conversation_id, created_at)` - For ordering messages chronologically

**Constraints**:
- `conversation_id` NOT NULL, FOREIGN KEY → conversations.id
- `user_id` NOT NULL - Audit trail (which user this conversation belongs to)
- `role` NOT NULL, CHECK IN ('user', 'assistant')
- `content` NOT NULL - No empty messages
- Foreign key cascade: ON DELETE CASCADE (delete messages when conversation deleted)

**Query Patterns**:
```sql
-- Load last 50 messages for conversation (most common query)
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 50;

-- Count messages in conversation
SELECT COUNT(*) FROM messages WHERE conversation_id = ?;
```

---

## Database Migrations

### Migration Strategy

Use Alembic with SQLModel for schema versioning:

```python
# backend/alembic/versions/001_initial_schema.py
"""Initial schema: tasks, conversations, messages

Revision ID: 001
Revises:
Create Date: 2025-12-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_user_id_completed', 'tasks', ['user_id', 'completed'])

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role_valid')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('tasks')
```

### Updated_at Trigger (PostgreSQL)

Auto-update `updated_at` timestamp on row modification:

```sql
-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for conversations table
CREATE TRIGGER update_conversations_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## Validation Rules

### Task Validation

```python
from pydantic import validator

class TaskCreate(SQLModel):
    """Validation model for task creation"""
    user_id: str
    title: str
    description: Optional[str] = None

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task title cannot be empty')
        if len(v) > 500:
            raise ValueError('Task title cannot exceed 500 characters')
        return v.strip()

    @validator('description')
    def description_length(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Task description cannot exceed 2000 characters')
        return v.strip() if v else None
```

### Message Validation

```python
class MessageCreate(SQLModel):
    """Validation model for message creation"""
    conversation_id: int
    user_id: str
    role: Literal["user", "assistant"]
    content: str

    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

    @validator('role')
    def role_valid(cls, v):
        if v not in ["user", "assistant"]:
            raise ValueError('Role must be "user" or "assistant"')
        return v
```

---

## Query Optimization

### Common Query Patterns

1. **List user's pending tasks** (most frequent):
```python
tasks = await db.execute(
    select(Task)
    .where(Task.user_id == user_id, Task.completed == False)
    .order_by(Task.created_at.desc())
)
```
**Index used**: `ix_tasks_user_id_completed`

2. **Load conversation history** (most frequent):
```python
messages = await db.execute(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(50)
)
```
**Index used**: `ix_messages_conversation_created`

3. **Find user's conversations**:
```python
conversations = await db.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
)
```
**Index used**: `ix_conversations_user_id`

### Performance Targets

- Task queries: < 50ms p95
- Conversation history load: < 100ms p95 (50 messages)
- Message insert: < 20ms p95
- Task create/update/delete: < 30ms p95

---

## Data Retention & Cleanup

**MVP Strategy**: No automatic cleanup (infinite retention)

**Future Considerations**:
- Archive conversations older than 90 days to cold storage
- Soft delete tasks with audit trail
- GDPR compliance: User data deletion on request

---

## Test Data Fixtures

### Sample Test Data

```python
# Test user
test_user_id = "auth0|test-user-123"

# Test tasks
test_tasks = [
    Task(id=1, user_id=test_user_id, title="Buy groceries", description="Milk, eggs", completed=False),
    Task(id=2, user_id=test_user_id, title="Call mom", description=None, completed=True),
    Task(id=3, user_id=test_user_id, title="Pay bills", description="Electricity and water", completed=False),
]

# Test conversation
test_conversation = Conversation(id=100, user_id=test_user_id)

# Test messages
test_messages = [
    Message(id=1, conversation_id=100, user_id=test_user_id, role="user", content="Add a task to buy groceries"),
    Message(id=2, conversation_id=100, user_id=test_user_id, role="assistant", content="I've added 'Buy groceries' to your tasks"),
    Message(id=3, conversation_id=100, user_id=test_user_id, role="user", content="Show me all my tasks"),
]
```

---

## Security Considerations

1. **Row-Level Security**: All queries MUST filter by `user_id` to prevent cross-user data access
2. **SQL Injection**: Use parameterized queries via SQLModel (no raw SQL)
3. **Audit Trail**: `user_id` stored in messages for accountability
4. **Foreign Keys**: Enforce referential integrity at database level
5. **Input Validation**: Pydantic validators prevent invalid data persistence

---

## Next Steps

1. Generate API contracts (`contracts/` directory)
2. Create quickstart guide for database setup
3. Implement SQLModel models in `backend/db/models.py`
4. Create Alembic migration scripts
5. Write unit tests for model validation
