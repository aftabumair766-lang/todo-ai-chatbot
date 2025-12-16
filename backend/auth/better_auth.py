"""
Better Auth JWT Middleware

Validates JWT tokens from Better Auth and extracts user identity.
Constitution Compliance: Principle IV (Security First - all requests authenticated)
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Security scheme for FastAPI documentation
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """
    Custom exception for authentication failures.

    Automatically returns 401 Unauthorized with appropriate error message.
    """

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token from Better Auth.

    Args:
        token: JWT token string from Authorization header

    Returns:
        dict: Decoded token payload containing user claims

    Raises:
        AuthenticationError: If token is invalid, expired, or signature fails

    Constitution Compliance:
    - Principle IV: Security First (validates all tokens)
    - Verifies signature using BETTER_AUTH_SECRET
    - Validates issuer matches BETTER_AUTH_ISSUER
    - Checks token expiration

    Token Payload Expected Format:
    {
        "sub": "user_id_from_better_auth",
        "iss": "https://auth.yourdomain.com",
        "exp": 1234567890,
        "iat": 1234567890,
        ...
    }
    """
    try:
        # Debug logging
        logger.info(f"🔍 DEBUG: Verifying token")
        logger.info(f"🔍 Token (first 50 chars): {token[:50]}...")
        logger.info(f"🔍 Secret (first 20 chars): {settings.BETTER_AUTH_SECRET[:20]}...")
        logger.info(f"🔍 Issuer: {settings.BETTER_AUTH_ISSUER}")

        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
            },
            issuer=settings.BETTER_AUTH_ISSUER,
        )

        # Validate required claims
        if "sub" not in payload:
            logger.warning("JWT token missing 'sub' claim")
            raise AuthenticationError("Invalid token: missing user identifier")

        logger.debug(f"JWT token validated for user: {payload['sub']}")
        return payload

    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during JWT validation: {str(e)}")
        raise AuthenticationError("Token validation failed")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to extract and validate current user from JWT.

    Usage:
        @app.post("/api/chat")
        async def chat_endpoint(
            user_id: str = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            # user_id is automatically extracted from JWT
            ...

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        str: User ID (from 'sub' claim in JWT)

    Raises:
        AuthenticationError: If token is missing or invalid

    Constitution Compliance:
    - Principle IV: Security First (all endpoints protected)
    - Principle II: Stateless (no session storage, JWT validated each request)
    """
    if not credentials:
        raise AuthenticationError("Missing authentication token")

    # Extract token from "Bearer <token>" format
    token = credentials.credentials

    # DEVELOPMENT MODE: Accept simple test tokens
    if settings.ENVIRONMENT == "development":
        # Accept "dev", "test", or any token starting with "dev-"
        if token in ["dev", "test"] or token.startswith("dev-"):
            logger.info(f"✅ DEV MODE: Accepting test token")
            return "test-user"

    # Verify token and extract user_id
    payload = verify_jwt_token(token)
    user_id = payload["sub"]

    return user_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[str]:
    """
    FastAPI dependency for optional authentication.

    Use this for endpoints that can work with or without authentication.

    Args:
        credentials: Optional HTTP Bearer token

    Returns:
        str | None: User ID if authenticated, None otherwise

    Constitution Compliance:
    - Principle IV: Security First (validates if present, but doesn't require)
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_jwt_token(token)
        return payload["sub"]
    except AuthenticationError:
        # Invalid token provided - return None for optional auth
        return None
