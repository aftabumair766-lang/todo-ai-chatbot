"""
JWT Token Provider
==================

Production-ready JWT token generation and validation.

Features:
    - Access tokens (short-lived: 1 hour)
    - Refresh tokens (long-lived: 30 days)
    - Token validation and decoding
    - Token revocation via blacklist
    - Claims support (user_id, email, roles)
    - HS256 signing algorithm

Security:
    - Secret key from environment variable
    - Token expiration enforcement
    - Signature verification
    - Blacklist for revoked tokens

Dependencies:
    pip install pyjwt
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
import logging
import os

logger = logging.getLogger(__name__)


class JWTTokenProvider:
    """
    JWT token provider for authentication system.

    Generates and validates JWT tokens with configurable expiration.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expiry_minutes: int = 60,
        refresh_token_expiry_days: int = 30
    ):
        """
        Initialize JWT token provider.

        Args:
            secret_key: Secret key for signing tokens (default: from env)
            algorithm: JWT algorithm (default: HS256)
            access_token_expiry_minutes: Access token lifetime (default: 60)
            refresh_token_expiry_days: Refresh token lifetime (default: 30)
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = algorithm
        self.access_token_expiry_minutes = access_token_expiry_minutes
        self.refresh_token_expiry_days = refresh_token_expiry_days

        # Token blacklist (in production: use Redis)
        self._blacklist: Set[str] = set()

        if self.secret_key == "your-secret-key-change-in-production":
            logger.warning("⚠️  Using default JWT secret key! Set JWT_SECRET_KEY environment variable in production!")

    def generate_access_token(self, user_id: str, claims: Dict[str, Any]) -> str:
        """
        Generate short-lived access token.

        Args:
            user_id: User's unique identifier
            claims: Additional claims (email, roles, etc.)

        Returns:
            JWT access token string

        Example:
            token = provider.generate_access_token(
                user_id="user_123",
                claims={"email": "alice@example.com", "roles": ["user", "admin"]}
            )
        """
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "type": "access",
            "iat": now,  # Issued at
            "exp": now + timedelta(minutes=self.access_token_expiry_minutes),  # Expires
            **claims
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(f"Generated access token for user {user_id} (expires in {self.access_token_expiry_minutes}m)")
        return token

    def generate_refresh_token(self, user_id: str) -> str:
        """
        Generate long-lived refresh token.

        Args:
            user_id: User's unique identifier

        Returns:
            JWT refresh token string

        Example:
            refresh_token = provider.generate_refresh_token("user_123")
        """
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self.refresh_token_expiry_days)
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(f"Generated refresh token for user {user_id} (expires in {self.refresh_token_expiry_days}d)")
        return token

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict, or None if invalid

        Example:
            payload = provider.validate_token(token)
            if payload:
                user_id = payload["user_id"]
                email = payload["email"]
        """
        try:
            # Check blacklist
            if token in self._blacklist:
                logger.warning("Token validation failed: Token is blacklisted")
                return None

            # Decode and verify
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            logger.debug(f"Token validated for user {payload.get('user_id')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Token expired")
            return None

        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """
        Revoke token by adding to blacklist.

        Args:
            token: JWT token to revoke

        Returns:
            True if revoked successfully

        Note:
            In production, use Redis with TTL for blacklist:
            - Key: f"blacklist:{token_hash}"
            - TTL: Token expiration time
            - This prevents memory bloat
        """
        try:
            # Decode to verify it's a valid token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration for revocation
            )

            # Add to blacklist
            self._blacklist.add(token)

            logger.info(f"Revoked token for user {payload.get('user_id')}")
            return True

        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    def decode_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging).

        Args:
            token: JWT token

        Returns:
            Decoded payload (unverified)

        Warning:
            Do NOT use for authentication! Only for debugging/logging.
        """
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None


# ============================================================================
# PRODUCTION IMPLEMENTATION (with Redis Blacklist)
# ============================================================================

class JWTTokenProviderWithRedis(JWTTokenProvider):
    """
    Production JWT provider with Redis-backed token blacklist.

    Advantages over in-memory blacklist:
        - Survives server restarts
        - Shared across multiple instances
        - Automatic expiration (TTL)
        - Scalable

    Usage:
        import redis.asyncio as redis

        redis_client = redis.from_url("redis://localhost:6379")
        provider = JWTTokenProviderWithRedis(
            secret_key="your-secret",
            redis_client=redis_client
        )
    """

    def __init__(self, secret_key: str, redis_client, **kwargs):
        """
        Initialize with Redis client.

        Args:
            secret_key: JWT secret key
            redis_client: Redis async client
            **kwargs: Additional arguments for JWTTokenProvider
        """
        super().__init__(secret_key=secret_key, **kwargs)
        self.redis = redis_client

    async def revoke_token(self, token: str) -> bool:
        """Revoke token using Redis blacklist"""
        try:
            # Decode to get expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            # Calculate TTL (time until token expires)
            exp = payload.get("exp")
            if exp:
                ttl = int(exp - datetime.utcnow().timestamp())
                if ttl > 0:
                    # Add to Redis with TTL
                    await self.redis.setex(
                        f"blacklist:{token}",
                        ttl,
                        "1"
                    )

            logger.info(f"Revoked token for user {payload.get('user_id')} (Redis)")
            return True

        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token checking Redis blacklist"""
        try:
            # Check Redis blacklist
            is_blacklisted = await self.redis.exists(f"blacklist:{token}")
            if is_blacklisted:
                logger.warning("Token validation failed: Token is blacklisted (Redis)")
                return None

            # Decode and verify
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            logger.debug(f"Token validated for user {payload.get('user_id')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Token expired")
            return None

        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}")
            return None
