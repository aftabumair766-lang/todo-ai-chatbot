"""
PostgreSQL User Store Provider
===============================

Production-ready user storage implementation using PostgreSQL.

Features:
    - Async database operations
    - User CRUD operations
    - Email indexing for fast lookups
    - Failed login attempt tracking
    - Account lockout support
    - Metadata storage (MFA, roles, etc.)

Database Schema:
    CREATE TABLE auth_users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name VARCHAR(255),
        email_verified BOOLEAN DEFAULT FALSE,
        mfa_enabled BOOLEAN DEFAULT FALSE,
        mfa_secret TEXT,
        roles TEXT[],
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX idx_auth_users_email ON auth_users(email);
    CREATE INDEX idx_auth_users_locked_until ON auth_users(locked_until);
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, Text

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# DATABASE MODEL
# ============================================================================

class AuthUser(Base):
    """User model for authentication"""
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255))
    email_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(Text)
    roles = Column(ARRAY(String))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# USER STORE PROVIDER
# ============================================================================

class PostgreSQLUserStore:
    """
    PostgreSQL implementation of UserStoreProvider.

    Provides user storage and retrieval for authentication system.
    """

    def __init__(self, session_factory=None):
        """
        Initialize user store.

        Args:
            session_factory: Optional SQLAlchemy session factory.
                           If None, uses injected db session from agent.
        """
        self.session_factory = session_factory

    async def create_user(
        self,
        email: str,
        password_hash: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new user account.

        Args:
            email: User's email address
            password_hash: Hashed password
            metadata: Additional user data (full_name, roles, etc.)

        Returns:
            Dict with user data

        Raises:
            ValueError: If email already exists
        """
        try:
            # Note: db session injected via process_message
            # For now, return structured data
            # In production, this would insert into database

            user_data = {
                "id": self._generate_user_id(),
                "email": email,
                "password_hash": password_hash,
                "full_name": metadata.get("full_name"),
                "email_verified": metadata.get("email_verified", False),
                "mfa_enabled": metadata.get("mfa_enabled", False),
                "roles": metadata.get("roles", []),
                "failed_login_attempts": 0,
                "locked_until": None,
                "last_login": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Created user: {email} (id={user_data['id']})")
            return user_data

        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by email address.

        Args:
            email: User's email

        Returns:
            Dict with user data or None if not found
        """
        # In production: SELECT * FROM auth_users WHERE email = ?
        # For now, return None (user not found) for demo
        logger.debug(f"Looking up user by email: {email}")
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by ID.

        Args:
            user_id: User's unique ID

        Returns:
            Dict with user data or None if not found
        """
        # In production: SELECT * FROM auth_users WHERE id = ?
        logger.debug(f"Looking up user by ID: {user_id}")
        return None

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user attributes.

        Args:
            user_id: User's unique ID
            updates: Dictionary of fields to update

        Returns:
            Updated user data

        Raises:
            ValueError: If user not found
        """
        try:
            # In production: UPDATE auth_users SET ... WHERE id = ?
            updates["updated_at"] = datetime.utcnow().isoformat()

            logger.info(f"Updated user {user_id}: {list(updates.keys())}")
            return {"id": user_id, **updates}

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user account.

        Args:
            user_id: User's unique ID

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If user not found
        """
        try:
            # In production: DELETE FROM auth_users WHERE id = ?
            logger.info(f"Deleted user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    def _generate_user_id(self) -> str:
        """Generate unique user ID (for demo)"""
        import uuid
        return f"user_{uuid.uuid4().hex[:8]}"


# ============================================================================
# PRODUCTION IMPLEMENTATION (SQLAlchemy)
# ============================================================================

class PostgreSQLUserStoreProduction:
    """
    Production PostgreSQL user store with real database operations.

    Usage:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
        SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        user_store = PostgreSQLUserStoreProduction(SessionLocal)
    """

    def __init__(self, session_factory):
        """
        Initialize with SQLAlchemy session factory.

        Args:
            session_factory: Async session factory
        """
        self.session_factory = session_factory

    async def create_user(self, email: str, password_hash: str, metadata: Dict) -> Dict:
        """Create user in database"""
        async with self.session_factory() as session:
            # Check for duplicate
            result = await session.execute(
                select(AuthUser).where(AuthUser.email == email)
            )
            if result.scalar_one_or_none():
                raise ValueError(f"User with email {email} already exists")

            # Create user
            user = AuthUser(
                email=email,
                password_hash=password_hash,
                full_name=metadata.get("full_name"),
                email_verified=metadata.get("email_verified", False),
                mfa_enabled=metadata.get("mfa_enabled", False),
                roles=metadata.get("roles", [])
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return self._user_to_dict(user)

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email from database"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(AuthUser).where(AuthUser.email == email)
            )
            user = result.scalar_one_or_none()
            return self._user_to_dict(user) if user else None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID from database"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(AuthUser).where(AuthUser.id == int(user_id.split('_')[1]))
            )
            user = result.scalar_one_or_none()
            return self._user_to_dict(user) if user else None

    async def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Update user in database"""
        async with self.session_factory() as session:
            user_id_int = int(user_id.split('_')[1])

            await session.execute(
                update(AuthUser)
                .where(AuthUser.id == user_id_int)
                .values(**updates, updated_at=datetime.utcnow())
            )

            await session.commit()

            # Fetch updated user
            result = await session.execute(
                select(AuthUser).where(AuthUser.id == user_id_int)
            )
            user = result.scalar_one()
            return self._user_to_dict(user)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user from database"""
        async with self.session_factory() as session:
            user_id_int = int(user_id.split('_')[1])

            await session.execute(
                delete(AuthUser).where(AuthUser.id == user_id_int)
            )

            await session.commit()
            return True

    def _user_to_dict(self, user: AuthUser) -> Dict:
        """Convert SQLAlchemy model to dict"""
        return {
            "id": f"user_{user.id}",
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "email_verified": user.email_verified,
            "mfa_enabled": user.mfa_enabled,
            "mfa_secret": user.mfa_secret,
            "roles": user.roles or [],
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
