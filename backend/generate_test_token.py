"""
Generate a test JWT token for development

This creates a valid JWT token that the backend will accept for testing.
"""

from jose import jwt
from datetime import datetime, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.insert(0, '/home/umair/todo-chatbot')

# Import actual backend config
from backend.config import get_settings

settings = get_settings()
SECRET = settings.BETTER_AUTH_SECRET
ISSUER = settings.BETTER_AUTH_ISSUER

def generate_test_token(user_id: str = "test-user") -> str:
    """Generate a test JWT token valid for 7 days"""

    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=7)

    payload = {
        "sub": user_id,  # User ID
        "iss": ISSUER,   # Issuer
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(expires.timestamp()),  # Expiration
    }

    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return token


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test-user"
    token = generate_test_token(user_id)

    print("=" * 60)
    print("🔑 Test JWT Token Generated")
    print("=" * 60)
    print(f"\nUser ID: {user_id}")
    print(f"\nYour Token (copy this):\n")
    print(token)
    print("\n" + "=" * 60)
    print("\n✅ Paste this token into the frontend authentication screen")
    print("   (Valid for 7 days)\n")
