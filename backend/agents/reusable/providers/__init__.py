"""
Provider Implementations for Authentication Agent
==================================================

Production-ready implementations of auth adapter provider interfaces.

Available Providers:
    - PostgreSQLUserStore: User storage with PostgreSQL
    - JWTTokenProvider: JWT token generation/validation
    - Argon2PasswordHasher: Secure password hashing with Argon2
    - DatabaseAuditLogger: Security event logging to database

Usage:
    from backend.agents.reusable.providers import (
        PostgreSQLUserStore,
        JWTTokenProvider,
        Argon2PasswordHasher,
        DatabaseAuditLogger
    )

    from backend.agents.reusable.adapters.auth_adapter import AuthAdapterConfig

    config = AuthAdapterConfig(
        user_store=PostgreSQLUserStore(),
        token_provider=JWTTokenProvider(secret_key="your-secret"),
        password_hasher=Argon2PasswordHasher(),
        audit_logger=DatabaseAuditLogger()
    )
"""

from backend.agents.reusable.providers.user_store import PostgreSQLUserStore
from backend.agents.reusable.providers.token_provider import JWTTokenProvider
from backend.agents.reusable.providers.password_hasher import Argon2PasswordHasher
from backend.agents.reusable.providers.audit_logger import DatabaseAuditLogger

__all__ = [
    "PostgreSQLUserStore",
    "JWTTokenProvider",
    "Argon2PasswordHasher",
    "DatabaseAuditLogger"
]
