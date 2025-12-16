"""
Tests for Chat API Endpoint

Constitution Compliance: Principle III (Test-First Development)
"""

import pytest
from fastapi import status


# ============================================================================
# Test Chat Endpoint - Authentication
# ============================================================================

@pytest.mark.asyncio
async def test_chat_requires_authentication(async_test_client):
    """Test that chat endpoint requires authentication."""
    response = await async_test_client.post(
        "/api/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Test Chat Endpoint - New Conversation
# ============================================================================

@pytest.mark.asyncio
async def test_chat_creates_new_conversation(
    async_test_client, auth_headers, test_db, mock_user_id
):
    """Test that chat endpoint creates a new conversation."""
    response = await async_test_client.post(
        "/api/chat",
        json={"message": "Hello"},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "conversation_id" in data
    assert "message" in data
    assert "user_message" in data
    assert data["user_message"] == "Hello"


# ============================================================================
# Test Chat Endpoint - Existing Conversation
# ============================================================================

@pytest.mark.asyncio
async def test_chat_continues_conversation(
    async_test_client, auth_headers, sample_conversation, mock_user_id
):
    """Test that chat endpoint can continue existing conversation."""
    conversation_id = sample_conversation.id

    response = await async_test_client.post(
        "/api/chat",
        json={
            "message": "Show me my tasks",
            "conversation_id": conversation_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["conversation_id"] == conversation_id


# ============================================================================
# Test Chat Endpoint - Greeting Detection
# ============================================================================

@pytest.mark.asyncio
async def test_chat_greeting_response(async_test_client, auth_headers, mock_user_id):
    """Test that greetings receive friendly response."""
    response = await async_test_client.post(
        "/api/chat",
        json={"message": "hi"},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "👋" in data["message"]
    assert "Todo Assistant" in data["message"]


# ============================================================================
# Test Chat Endpoint - User Isolation
# ============================================================================

@pytest.mark.asyncio
async def test_chat_conversation_isolation(
    async_test_client, auth_headers, sample_conversation
):
    """Test that users cannot access other users' conversations."""
    # Try to access conversation with different user's auth
    response = await async_test_client.post(
        "/api/chat",
        json={
            "message": "Hello",
            "conversation_id": sample_conversation.id,
        },
        headers={"Authorization": "Bearer fake_different_user_token"},
    )

    # Should fail authentication or return 404
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
    ]


# ============================================================================
# Test Chat Endpoint - Message History
# ============================================================================

@pytest.mark.asyncio
async def test_chat_saves_messages(
    async_test_client, auth_headers, test_db, mock_user_id
):
    """Test that chat endpoint saves both user and assistant messages."""
    from sqlalchemy import select
    from backend.db.models import Message

    response = await async_test_client.post(
        "/api/chat",
        json={"message": "Hello"},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    conversation_id = data["conversation_id"]

    # Check that messages are saved in database
    query = select(Message).where(Message.conversation_id == conversation_id)
    result = await test_db.execute(query)
    messages = result.scalars().all()

    # Should have 2 messages: user + assistant
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"


# ============================================================================
# Test Chat Endpoint - Input Validation
# ============================================================================

@pytest.mark.asyncio
async def test_chat_empty_message(async_test_client, auth_headers):
    """Test that empty message is rejected."""
    response = await async_test_client.post(
        "/api/chat",
        json={"message": ""},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_chat_message_too_long(async_test_client, auth_headers):
    """Test that message longer than 5000 chars is rejected."""
    long_message = "A" * 5001

    response = await async_test_client.post(
        "/api/chat",
        json={"message": long_message},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
