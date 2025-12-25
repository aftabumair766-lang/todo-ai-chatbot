"""
Authentication Agent - FastAPI Integration Example
===================================================

Complete working example of using the Authentication Agent with FastAPI.

Features:
    - User registration
    - Login with JWT tokens
    - Logout (token revocation)
    - Token refresh
    - Password reset
    - Permission checking
    - Protected routes

Run:
    cd examples/auth_fastapi
    pip install -r requirements.txt
    uvicorn main:app --reload

Endpoints:
    POST /auth/register - Register new user
    POST /auth/login - Login and get tokens
    POST /auth/logout - Logout and revoke token
    POST /auth/refresh - Refresh access token
    POST /auth/reset-password - Request password reset
    GET /auth/me - Get current user (protected)
    GET /protected - Example protected route
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

# Import reusable auth agent
from backend.agents.reusable import ReusableAgent
from backend.agents.reusable.adapters.auth_adapter import (
    AuthDomainAdapter,
    AuthAdapterConfig
)
from backend.agents.reusable.providers import (
    PostgreSQLUserStore,
    JWTTokenProvider,
    Argon2PasswordHasher,
    ConsoleAuditLogger
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Authentication Agent API",
    description="Production-ready auth API powered by reusable AI agents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# AUTH AGENT CONFIGURATION
# ============================================================================

# Initialize providers
user_store = PostgreSQLUserStore()
token_provider = JWTTokenProvider(
    secret_key="your-secret-key-change-in-production",  # Use env variable!
    access_token_expiry_minutes=60,
    refresh_token_expiry_days=30
)
password_hasher = Argon2PasswordHasher()
audit_logger = ConsoleAuditLogger()

# Configure auth adapter
auth_config = AuthAdapterConfig(
    user_store=user_store,
    token_provider=token_provider,
    password_hasher=password_hasher,
    audit_logger=audit_logger,
    # Security settings
    password_min_length=12,
    password_require_uppercase=True,
    password_require_numbers=True,
    password_require_special=True,
    max_login_attempts=5,
    lockout_duration_minutes=15,
    token_expiry_minutes=60,
    refresh_token_expiry_days=30,
    require_mfa=False  # Enable for production
)

# Create auth agent
auth_agent = ReusableAgent(adapter=AuthDomainAdapter(auth_config))

logger.info("✅ Authentication agent initialized")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr


# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================

async def get_current_user(authorization: str = Header(None)):
    """
    Dependency to get current user from JWT token.

    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"message": f"Hello {user['email']}"}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Extract token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    # Validate token
    payload = token_provider.validate_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "Authentication Agent API",
        "version": "1.0.0"
    }


@app.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Register new user.

    Example:
        POST /auth/register
        {
            "email": "alice@example.com",
            "password": "SecurePass123!",
            "full_name": "Alice"
        }

    Response:
        {
            "user_id": "user_abc123",
            "email": "alice@example.com",
            "message": "Registration successful"
        }
    """
    try:
        # Call auth agent
        result = await auth_agent.process_message(
            user_id="anonymous",
            message=f"Register user {request.email} with password {request.password}" +
                   (f" and name {request.full_name}" if request.full_name else ""),
            conversation_history=[],
            db=None
        )

        # Extract tool result
        if not result.get("tool_calls"):
            raise HTTPException(status_code=500, detail="No tool calls executed")

        tool_result = result["tool_calls"][0]["result"]

        # Check for errors
        if tool_result.get("error"):
            raise HTTPException(status_code=400, detail=tool_result["message"])

        return {
            "user_id": tool_result["user_id"],
            "email": request.email,
            "message": tool_result["message"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Login and receive access/refresh tokens.

    Example:
        POST /auth/login
        {
            "email": "alice@example.com",
            "password": "SecurePass123!"
        }

    Response:
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "user_abc123",
                "email": "alice@example.com",
                "full_name": "Alice"
            }
        }
    """
    try:
        # Call auth agent
        result = await auth_agent.process_message(
            user_id="anonymous",
            message=f"Login user {request.email} with password {request.password}" +
                   (f" and MFA code {request.mfa_code}" if request.mfa_code else ""),
            conversation_history=[],
            db=None
        )

        # Extract tool result
        if not result.get("tool_calls"):
            raise HTTPException(status_code=500, detail="No tool calls executed")

        tool_result = result["tool_calls"][0]["result"]

        # Check for errors
        if tool_result.get("error"):
            status_code = 401 if "credentials" in tool_result["message"].lower() else 400
            raise HTTPException(status_code=status_code, detail=tool_result["message"])

        # Check if MFA required
        if tool_result.get("requires_mfa"):
            return {
                "requires_mfa": True,
                "message": tool_result["message"]
            }

        return {
            "access_token": tool_result["access_token"],
            "refresh_token": tool_result["refresh_token"],
            "token_type": "bearer",
            "expires_in": auth_config.token_expiry_minutes * 60,
            "user": tool_result["user"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/auth/logout")
async def logout(user = Depends(get_current_user), authorization: str = Header(None)):
    """
    Logout and revoke access token.

    Requires:
        Authorization: Bearer <access_token>

    Response:
        {
            "message": "Logged out successfully"
        }
    """
    try:
        # Extract token
        _, token = authorization.split()

        # Call auth agent
        result = await auth_agent.process_message(
            user_id=user["user_id"],
            message=f"Logout with token {token}",
            conversation_history=[],
            db=None
        )

        tool_result = result["tool_calls"][0]["result"]

        if tool_result.get("error"):
            raise HTTPException(status_code=400, detail=tool_result["message"])

        return {"message": tool_result["message"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Logout failed")


@app.post("/auth/refresh")
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.

    Example:
        POST /auth/refresh
        {
            "refresh_token": "eyJ..."
        }

    Response:
        {
            "access_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 3600
        }
    """
    try:
        # Call auth agent
        result = await auth_agent.process_message(
            user_id="anonymous",
            message=f"Refresh token {request.refresh_token}",
            conversation_history=[],
            db=None
        )

        tool_result = result["tool_calls"][0]["result"]

        if tool_result.get("error"):
            raise HTTPException(status_code=401, detail=tool_result["message"])

        return {
            "access_token": tool_result["access_token"],
            "token_type": "bearer",
            "expires_in": auth_config.token_expiry_minutes * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Token refresh failed")


@app.post("/auth/reset-password")
async def reset_password(request: PasswordResetRequest):
    """
    Request password reset email.

    Example:
        POST /auth/reset-password
        {
            "email": "alice@example.com"
        }

    Response:
        {
            "message": "If the email exists, a password reset link has been sent."
        }

    Note: Always returns success to prevent user enumeration
    """
    try:
        result = await auth_agent.process_message(
            user_id="anonymous",
            message=f"Request password reset for {request.email}",
            conversation_history=[],
            db=None
        )

        tool_result = result["tool_calls"][0]["result"]

        return {"message": tool_result["message"]}

    except Exception as e:
        logger.error(f"Password reset error: {e}", exc_info=True)
        # Always return success for security
        return {"message": "If the email exists, a password reset link has been sent."}


@app.get("/auth/me")
async def get_me(user = Depends(get_current_user)):
    """
    Get current user info (protected route).

    Requires:
        Authorization: Bearer <access_token>

    Response:
        {
            "user_id": "user_abc123",
            "email": "alice@example.com",
            "roles": ["user"]
        }
    """
    return {
        "user_id": user["user_id"],
        "email": user.get("email"),
        "roles": user.get("roles", [])
    }


@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    """
    Example protected route.

    Requires:
        Authorization: Bearer <access_token>

    Response:
        {
            "message": "Hello alice@example.com! You are authenticated.",
            "user_id": "user_abc123"
        }
    """
    return {
        "message": f"Hello {user.get('email')}! You are authenticated.",
        "user_id": user["user_id"]
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
