"""
Authentication API Endpoints (Better Auth)

Handles user registration, login, and JWT token generation.
Constitution Compliance: Principle IV (Security First)
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import bcrypt
from jose import jwt

from backend.config import get_settings
from backend.db.session import get_db
from backend.db.models import (
    User,
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


# ============================================================================
# Password Hashing Utilities (using bcrypt directly)
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Bcrypt automatically handles passwords longer than 72 bytes by truncating.
    Uses UTF-8 encoding for proper byte conversion.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash (bcrypt handles 72-byte limit automatically)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hash from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Convert both to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify using bcrypt
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================================================
# JWT Token Generation
# ============================================================================

def create_access_token(user_id: int, email: str) -> str:
    """
    Create JWT access token for authenticated user.

    Token payload:
    - sub: user ID (as string for Better Auth compatibility)
    - email: user email
    - iss: issuer from config
    - exp: expiration time (24 hours from now)
    - iat: issued at time
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=24)

    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "iss": settings.BETTER_AUTH_ISSUER,  # Issuer
        "exp": expire,  # Expiration
        "iat": now,  # Issued at
    }

    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

    return token


# ============================================================================
# Registration Endpoint
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Steps:
    1. Validate email and username are unique
    2. Hash the password
    3. Create user in database
    4. Generate JWT token
    5. Return token and user data

    Constitution Compliance:
    - Principle IV: Security First (password hashed, never stored plaintext)
    - Principle V: Database as Source of Truth
    """
    try:
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        stmt = select(User).where(User.username == user_data.username)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        hashed_password = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Email verification can be added later
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"✅ New user registered: {new_user.email} (ID: {new_user.id})")

        # Generate JWT token
        access_token = create_access_token(new_user.id, new_user.email)

        # Return token and user data
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                is_active=new_user.is_active,
                is_verified=new_user.is_verified,
                created_at=new_user.created_at
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================================================
# Login Endpoint
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    Steps:
    1. Find user by email
    2. Verify password
    3. Check account is active
    4. Generate JWT token
    5. Return token and user data

    Constitution Compliance:
    - Principle IV: Security First (password verification)
    - Principle II: Stateless (JWT token, no session storage)
    """
    try:
        # Find user by email
        stmt = select(User).where(User.email == login_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        logger.info(f"✅ User logged in: {user.email} (ID: {user.id})")

        # Generate JWT token
        access_token = create_access_token(user.id, user.email)

        # Return token and user data
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


# ============================================================================
# Get Current User Info (Protected Route Example)
# ============================================================================

from backend.auth.better_auth import get_current_user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user's information.

    This is a protected route that requires a valid JWT token.
    """
    try:
        # Convert user_id from string to int
        user_id_int = int(user_id)

        stmt = select(User).where(User.id == user_id_int)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )
