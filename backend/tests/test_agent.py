"""
Tests for Todo Agent

Constitution Compliance: Principle III (Test-First Development)
"""

import pytest
from backend.agents.todo_agent import is_greeting, get_greeting_response


# ============================================================================
# Test Greeting Detection
# ============================================================================

def test_is_greeting_simple():
    """Test detection of simple greetings."""
    assert is_greeting("hi") is True
    assert is_greeting("hello") is True
    assert is_greeting("hey") is True
    assert is_greeting("Hello") is True  # Case insensitive
    assert is_greeting("HI") is True


def test_is_greeting_with_punctuation():
    """Test greetings with punctuation."""
    assert is_greeting("hi!") is True
    assert is_greeting("hello?") is True
    assert is_greeting("hey.") is True


def test_is_greeting_phrases():
    """Test greeting phrases."""
    assert is_greeting("good morning") is True
    assert is_greeting("good afternoon") is True
    assert is_greeting("good evening") is True
    assert is_greeting("what's up") is True
    assert is_greeting("whats up") is True


def test_is_greeting_informal():
    """Test informal greetings."""
    assert is_greeting("yo") is True
    assert is_greeting("sup") is True
    assert is_greeting("howdy") is True


def test_not_greeting():
    """Test that non-greetings are not detected."""
    assert is_greeting("add a task") is False
    assert is_greeting("show me my tasks") is False
    assert is_greeting("complete task 5") is False
    assert is_greeting("this is a longer message") is False


def test_get_greeting_response():
    """Test that greeting response is friendly and informative."""
    response = get_greeting_response()

    assert "👋" in response
    assert "Todo Assistant" in response
    assert "add" in response.lower()
    assert "view" in response.lower() or "see" in response.lower()


# ============================================================================
# Test Agent (with mocked OpenAI)
# Note: Full agent testing with OpenAI requires API key and mocking
# ============================================================================

# Placeholder for future agent integration tests
# These would mock the OpenAI API calls and test the agent flow

@pytest.mark.skip(reason="Requires OpenAI API mocking - implement in Phase 10")
@pytest.mark.asyncio
async def test_agent_add_task_flow(test_db, mock_user_id):
    """
    Test agent's ability to add a task via natural language.

    This test would:
    1. Mock OpenAI API response to call add_task tool
    2. Verify tool is executed with correct params
    3. Verify response contains confirmation message
    """
    pass


@pytest.mark.skip(reason="Requires OpenAI API mocking - implement in Phase 10")
@pytest.mark.asyncio
async def test_agent_list_tasks_flow(test_db, sample_tasks, mock_user_id):
    """
    Test agent's ability to list tasks via natural language.

    This test would:
    1. Mock OpenAI API response to call list_tasks tool
    2. Verify tasks are formatted with emoji
    3. Verify response is user-friendly
    """
    pass
