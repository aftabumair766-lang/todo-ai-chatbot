"""JWT Authentication Middleware for Better Auth"""
import os
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError


# Better Auth configuration from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key")
BETTER_AUTH_ISSUER = os.getenv("BETTER_AUTH_ISSUER", "https://auth.todo-chatbot.app")
BETTER_AUTH_ALGORITHM = "HS256"

# HTTP Bearer token scheme
security = HTTPBearer()


class JWTAuthMiddleware:
    """
    JWT Authentication Middleware for Better Auth tokens.

    Validates Bearer tokens and extracts user_id from JWT payload.
    """

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                BETTER_AUTH_SECRET,
                algorithms=[BETTER_AUTH_ALGORITHM],
                issuer=BETTER_AUTH_ISSUER
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """
        Extract user_id from JWT token.

        Args:
            token: JWT token string

        Returns:
            User ID string

        Raises:
            HTTPException: If token is invalid or user_id is missing
        """
        payload = JWTAuthMiddleware.decode_token(token)

        # Extract user_id from payload
        # Better Auth typically uses 'sub' (subject) claim for user ID
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security
) -> str:
    """
    FastAPI dependency to get current authenticated user.

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        User ID string

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    user_id = JWTAuthMiddleware.get_user_id_from_token(token)
    return user_id


async def optional_auth(request: Request) -> Optional[str]:
    """
    Optional authentication - returns user_id if token present, None otherwise.

    Usage:
        @app.get("/optional-auth")
        async def route(user_id: Optional[str] = Depends(optional_auth)):
            if user_id:
                return {"authenticated": True, "user_id": user_id}
            return {"authenticated": False}

    Args:
        request: FastAPI request object

    Returns:
        User ID if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        user_id = JWTAuthMiddleware.get_user_id_from_token(token)
        return user_id
    except HTTPException:
        return None
