"""
Chat API Endpoint

Handles natural language conversations for task management.
Constitution Compliance: All 6 principles enforced.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.auth import get_current_user
from backend.db.session import get_db
from backend.db.models import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models (Request/Response)
# ============================================================================

class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    Constitution Compliance:
    - Principle VI: API Contract Clarity (explicit request schema)
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message in natural language",
        examples=["Add a task to buy groceries", "Show me all my tasks"],
    )
    conversation_id: Optional[int] = Field(
        None,
        description="Conversation ID to continue existing chat (optional for new conversation)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": 123,
            }
        }


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.

    Constitution Compliance:
    - Principle VI: API Contract Clarity (explicit response schema)
    """

    conversation_id: int = Field(
        ..., description="Conversation ID for this chat session"
    )
    message: str = Field(..., description="AI assistant response")
    user_message: str = Field(..., description="Echo of user's message")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 123,
                "message": "✅ Task created: Buy groceries",
                "user_message": "Add a task to buy groceries",
            }
        }


# ============================================================================
# Chat Endpoint
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Natural language chat endpoint for task management.

    This is a PLACEHOLDER implementation for Phase 2.
    Full OpenAI Agents SDK integration will be implemented in Phase 3 (User Story 1).

    Request Flow (Stateless):
    1. Authenticate user via JWT (user_id extracted)
    2. Load or create conversation from DB
    3. Fetch conversation history (last 50 messages)
    4. Save user message to DB
    5. [TODO Phase 3] Run OpenAI Agent with MCP tools
    6. Save assistant response to DB
    7. Return response

    Args:
        request: Chat request with user message and optional conversation_id
        user_id: Authenticated user ID from JWT (via dependency)
        db: Async database session (via dependency)

    Returns:
        ChatResponse: Assistant response with conversation_id

    Raises:
        HTTPException 401: If authentication fails
        HTTPException 404: If conversation not found or doesn't belong to user
        HTTPException 500: If processing fails

    Constitution Compliance:
    - Principle II: Stateless (no in-memory state, all from DB)
    - Principle IV: Security First (user_id filtering, JWT auth)
    - Principle V: Database as Source of Truth (history from DB)
    - Principle VI: API Contract Clarity (typed request/response)

    Rate Limiting:
    - 10 requests per minute per IP (configured in main.py)
    """
    try:
        # Step 1: Load or create conversation
        conversation = await _get_or_create_conversation(
            db, user_id, request.conversation_id
        )

        # Step 2: Fetch conversation history (last 50 messages)
        history = await _get_conversation_history(db, conversation.id, limit=50)

        # Step 3: Save user message to database
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message,
        )
        db.add(user_message)
        await db.commit()

        logger.info(
            f"User message saved: conversation_id={conversation.id}, user_id={user_id}"
        )

        # Step 4: Process with OpenAI Agent
        from backend.agents.todo_agent import run_todo_agent

        # Convert history to agent format
        conversation_messages = [
            {"role": msg.role, "content": msg.content} for msg in history
        ]

        # Run agent
        agent_result = await run_todo_agent(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_messages,
            db=db,
        )

        assistant_response = agent_result["response"]

        logger.info(
            f"Agent executed: {len(agent_result.get('tool_calls', []))} tool calls"
        )

        # Step 5: Save assistant response to database
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=assistant_response,
        )
        db.add(assistant_message)
        await db.commit()

        logger.info(
            f"Assistant message saved: conversation_id={conversation.id}, user_id={user_id}"
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_response,
            user_message=request.message,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (auth errors, not found, etc.)
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message",
        )


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_or_create_conversation(
    db: AsyncSession, user_id: str, conversation_id: Optional[int]
) -> Conversation:
    """
    Get existing conversation or create new one.

    Args:
        db: Async database session
        user_id: Authenticated user ID
        conversation_id: Optional conversation ID

    Returns:
        Conversation: Existing or newly created conversation

    Raises:
        HTTPException 404: If conversation not found or doesn't belong to user

    Constitution Compliance:
    - Principle IV: Security First (verify user_id ownership)
    - Principle V: Database as Source of Truth
    """
    if conversation_id is not None:
        # Load existing conversation
        query = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or does not belong to user",
            )

        logger.debug(f"Loaded existing conversation: {conversation_id}")
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        logger.info(f"Created new conversation: {conversation.id} for user {user_id}")
        return conversation


async def _get_conversation_history(
    db: AsyncSession, conversation_id: int, limit: int = 50
) -> list[Message]:
    """
    Fetch conversation history (last N messages).

    Args:
        db: Async database session
        conversation_id: Conversation ID
        limit: Maximum number of messages to fetch

    Returns:
        list[Message]: List of messages ordered by created_at

    Constitution Compliance:
    - Principle II: Stateless (history loaded from DB each request)
    - Principle V: Database as Source of Truth
    """
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest to newest)
    messages_chronological = list(reversed(messages))

    logger.debug(
        f"Loaded {len(messages_chronological)} messages for conversation {conversation_id}"
    )
    return messages_chronological


