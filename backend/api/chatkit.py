"""
ChatKit Session Management API

Endpoints for creating and managing ChatKit sessions.
OpenAI ChatKit integration for Todo AI Chatbot.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from backend.config import get_settings
from backend.auth.better_auth import get_current_user

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatKitSessionResponse(BaseModel):
    """ChatKit session creation response"""
    client_secret: str
    session_id: str


# ============================================================================
# ChatKit Session Endpoint
# ============================================================================

@router.post("/chatkit/session", response_model=ChatKitSessionResponse)
async def create_chatkit_session(
    user_id: str = Depends(get_current_user)
):
    """
    Create a new ChatKit session.

    This endpoint creates a ChatKit session using OpenAI's beta API
    and returns the client secret for the frontend to use.

    Args:
        user_id: Authenticated user ID from JWT token

    Returns:
        ChatKitSessionResponse: Session credentials

    Raises:
        HTTPException: If session creation fails
    """
    try:
        logger.info(f"Creating ChatKit session for user: {user_id}")

        # Check if workflow ID is configured
        if not settings.CHATKIT_WORKFLOW_ID:
            raise HTTPException(
                status_code=500,
                detail="ChatKit workflow not configured. Please set CHATKIT_WORKFLOW_ID in .env file. See docs/CHATKIT_SETUP.md for instructions."
            )

        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Create ChatKit session
        # Using the workflow ID configured in OpenAI platform
        session = await client.beta.chatkit.sessions.create(
            user=user_id,
            workflow={"id": settings.CHATKIT_WORKFLOW_ID}
        )

        logger.info(f"ChatKit session created: {session.id}")

        return ChatKitSessionResponse(
            client_secret=session.client_secret,
            session_id=session.id
        )

    except Exception as e:
        logger.error(f"Failed to create ChatKit session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ChatKit session: {str(e)}"
        )
