"""
Pytest Configuration and Fixtures

Provides reusable test fixtures for database, API, and authentication testing.
Constitution Compliance: Principle III (Test-First Development - NON-NEGOTIABLE)
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from httpx import AsyncClient
from backend.main import app
from backend.db.session import get_db
from backend.db.models import Task, Conversation, Message
from backend.config import get_settings

# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Get settings
settings = get_settings()


# ============================================================================
# Event Loop Fixture (Required for async tests)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.

    Scope: session (shared across all tests)
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Create test database engine.

    Scope: function (new engine per test)
    Uses in-memory SQLite for fast, isolated tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.

    Scope: function (new session per test)
    Provides clean database state for each test.

    Constitution Compliance:
    - Principle II: Stateless (fresh DB per test)
    - Principle III: Test-First Development (isolated tests)
    """
    AsyncSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_client(test_db: AsyncSession):
    """
    Create FastAPI test client with test database.

    Scope: function (new client per test)
    Overrides database dependency with test database.
    """

    # Override get_db dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_test_client(test_db: AsyncSession):
    """
    Create async FastAPI test client.

    Scope: function (new client per test)
    Use this for testing async endpoints.
    """

    # Override get_db dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def mock_user_id() -> str:
    """
    Mock user ID for testing.

    Returns:
        str: Test user ID
    """
    return "test_user_12345"


@pytest.fixture
def mock_jwt_token(mock_user_id: str) -> str:
    """
    Generate mock JWT token for testing.

    Args:
        mock_user_id: Test user ID

    Returns:
        str: Mock JWT token

    Note: This is a placeholder. In real tests, generate valid JWT
    using the same secret and algorithm as production.
    """
    from jose import jwt

    payload = {
        "sub": mock_user_id,
        "iss": settings.BETTER_AUTH_ISSUER,
        "exp": 9999999999,  # Far future expiration
        "iat": 1000000000,
    }

    token = jwt.encode(
        payload, settings.BETTER_AUTH_SECRET, algorithm="HS256"
    )

    return token


@pytest.fixture
def auth_headers(mock_jwt_token: str) -> dict:
    """
    Create authentication headers for API requests.

    Args:
        mock_jwt_token: Mock JWT token

    Returns:
        dict: Authorization headers
    """
    return {"Authorization": f"Bearer {mock_jwt_token}"}


# ============================================================================
# Data Fixtures (Pre-populated Test Data)
# ============================================================================

@pytest_asyncio.fixture
async def sample_tasks(test_db: AsyncSession, mock_user_id: str) -> list[Task]:
    """
    Create sample tasks for testing.

    Args:
        test_db: Test database session
        mock_user_id: Test user ID

    Returns:
        list[Task]: List of sample tasks

    Constitution Compliance:
    - Principle III: Test-First Development (test data fixtures)
    """
    tasks = [
        Task(
            user_id=mock_user_id,
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,
        ),
        Task(
            user_id=mock_user_id,
            title="Write tests",
            description="Unit and integration tests",
            completed=True,
        ),
        Task(
            user_id=mock_user_id,
            title="Deploy to production",
            description=None,
            completed=False,
        ),
    ]

    for task in tasks:
        test_db.add(task)

    await test_db.commit()

    for task in tasks:
        await test_db.refresh(task)

    return tasks


@pytest_asyncio.fixture
async def sample_conversation(
    test_db: AsyncSession, mock_user_id: str
) -> Conversation:
    """
    Create sample conversation for testing.

    Args:
        test_db: Test database session
        mock_user_id: Test user ID

    Returns:
        Conversation: Sample conversation with messages
    """
    conversation = Conversation(user_id=mock_user_id)
    test_db.add(conversation)
    await test_db.commit()
    await test_db.refresh(conversation)

    # Add sample messages
    messages = [
        Message(
            conversation_id=conversation.id,
            user_id=mock_user_id,
            role="user",
            content="Hello",
        ),
        Message(
            conversation_id=conversation.id,
            user_id=mock_user_id,
            role="assistant",
            content="Hi! How can I help you today?",
        ),
        Message(
            conversation_id=conversation.id,
            user_id=mock_user_id,
            role="user",
            content="Add a task to buy groceries",
        ),
    ]

    for message in messages:
        test_db.add(message)

    await test_db.commit()

    return conversation


# ============================================================================
# MCP Server Fixture
# ============================================================================

@pytest.fixture
def mcp_server():
    """
    Get MCP server instance for testing.

    Returns:
        MCPServer: MCP server instance
    """
    from backend.mcp.server import create_mcp_server

    return create_mcp_server()
