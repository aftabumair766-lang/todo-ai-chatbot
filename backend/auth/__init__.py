"""
Authentication module for Better Auth JWT integration.

Constitution Compliance: Principle IV (Security First - JWT validation)
"""

from backend.auth.better_auth import get_current_user, AuthenticationError

__all__ = ["get_current_user", "AuthenticationError"]
