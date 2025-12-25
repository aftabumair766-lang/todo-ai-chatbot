# Reusable Authentication & Authorization AI Agent

## 📋 Table of Contents
1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Provider Interfaces](#provider-interfaces)
6. [Configuration](#configuration)
7. [Security Features](#security-features)
8. [Usage Examples](#usage-examples)
9. [Integration Guide](#integration-guide)
10. [Best Practices](#best-practices)

---

## Overview

A **framework-agnostic, security-first** AI agent for authentication and authorization that can be used across:

- ✅ Web applications (FastAPI, Django, Flask, Express, Next.js)
- ✅ Mobile apps (iOS, Android, React Native)
- ✅ SaaS platforms
- ✅ AI-powered chat systems
- ✅ Microservices architectures
- ✅ Serverless functions (AWS Lambda, Google Cloud Functions)

### Key Features

**Authentication:**
- User registration with email verification
- Secure login with JWT/OAuth2/OpenID Connect support
- Logout and token revocation
- Token refresh mechanism
- Password reset flows
- Multi-Factor Authentication (TOTP, SMS, Email)

**Authorization:**
- Role-Based Access Control (RBAC)
- Permission-based access
- Policy-driven authorization (integrate with OPA, custom engines)

**Security:**
- Password hashing (bcrypt, argon2, scrypt)
- Rate limiting & brute-force protection
- Account lockout after failed attempts
- Comprehensive audit logging
- OWASP Top 10 compliance
- Secure session handling

---

## Design Philosophy

### 1. Framework-Agnostic

No assumptions about:
- Database (PostgreSQL, MongoDB, DynamoDB, Firebase, Auth0)
- Web framework (FastAPI, Express, Django, Rails)
- Frontend (React, Vue, Angular, mobile apps)
- Deployment (Docker, Kubernetes, serverless)

### 2. Configuration-Driven

All behavior controlled via `AuthAdapterConfig`:

```python
config = AuthAdapterConfig(
    user_store=PostgreSQLUserStore(),       # Swap for MongoDB, DynamoDB, etc.
    token_provider=JWTTokenProvider(),      # Swap for OAuth2, custom
    password_hasher=Argon2Hasher(),         # Swap for bcrypt, scrypt
    mfa_provider=TwilioMFAProvider(),       # Optional MFA
    policy_engine=OPAPolicyEngine(),        # Optional authorization
    audit_logger=CloudWatchAuditLogger()    # Optional audit logging
)
```

### 3. Provider Pattern

Abstract interfaces for all external dependencies:

- `UserStoreProvider` - User data persistence
- `TokenProvider` - Token generation/validation
- `PasswordHasher` - Password hashing
- `MFAProvider` - Multi-Factor Authentication
- `PolicyEngine` - Authorization policies
- `AuditLogger` - Security event logging

**You provide implementations → Agent works across any stack**

### 4. Stateless Architecture

- No in-memory state
- All state via external stores (database, Redis, etc.)
- Horizontally scalable
- Serverless-friendly

### 5. Security-First

- Generic error messages (no user enumeration)
- Secure defaults (strong passwords, short-lived tokens)
- Rate limiting built-in
- Comprehensive audit logging
- Follows OWASP guidelines

---

## Quick Start

### Step 1: Install Dependencies

```bash
pip install pyjwt bcrypt python-multipart
# Or: pip install passlib[argon2] for argon2 hashing
```

### Step 2: Implement Providers

Create minimal implementations:

```python
# providers.py

from backend.agents.reusable.adapters.auth_adapter import (
    UserStoreProvider,
    TokenProvider,
    PasswordHasher
)
import jwt
import bcrypt
from datetime import datetime, timedelta

# User Store (PostgreSQL example)
class PostgreSQLUserStore(UserStoreProvider):
    async def create_user(self, email, password_hash, metadata):
        # Insert into database
        user = await db.execute(
            "INSERT INTO users (email, password_hash, full_name, created_at) VALUES (?, ?, ?, ?)",
            email, password_hash, metadata.get("full_name"), datetime.utcnow()
        )
        return {"id": user.id, "email": email, **metadata}

    async def get_user_by_email(self, email):
        return await db.query("SELECT * FROM users WHERE email = ?", email)

    async def get_user_by_id(self, user_id):
        return await db.query("SELECT * FROM users WHERE id = ?", user_id)

    async def update_user(self, user_id, updates):
        # Update user record
        pass

    async def delete_user(self, user_id):
        # Delete user
        pass


# JWT Token Provider
class JWTTokenProvider(TokenProvider):
    SECRET_KEY = "your-secret-key"  # Use environment variable!

    def generate_access_token(self, user_id, claims):
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=1),
            **claims
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")

    def generate_refresh_token(self, user_id):
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")

    def validate_token(self, token):
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except:
            return None

    def revoke_token(self, token):
        # Add to blacklist (Redis, database, etc.)
        pass


# Password Hasher (bcrypt)
class BcryptHasher(PasswordHasher):
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode(), password_hash.encode())
```

### Step 3: Create Auth Agent

```python
from backend.agents.reusable import ReusableAgent
from backend.agents.reusable.adapters.auth_adapter import (
    AuthDomainAdapter,
    AuthAdapterConfig
)

# Configure adapter
config = AuthAdapterConfig(
    user_store=PostgreSQLUserStore(),
    token_provider=JWTTokenProvider(),
    password_hasher=BcryptHasher(),
    # Security settings
    password_min_length=12,
    max_login_attempts=5,
    lockout_duration_minutes=15
)

# Create agent
auth_agent = ReusableAgent(adapter=AuthDomainAdapter(config))
```

### Step 4: Use the Agent

```python
# Register user
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Register user john@example.com with password SecurePass123!",
    conversation_history=[],
    db=db
)

print(result["response"])
# "Registration successful. Please verify your email."

# Login
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Login user john@example.com with password SecurePass123!",
    conversation_history=[],
    db=db
)

print(result["response"])
# "Login successful"
print(result["tool_calls"][0]["result"]["access_token"])
# "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│         User (Web App / Mobile App)             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│     ReusableAgent (Generic Core)                │
│   - OpenAI API integration                      │
│   - Tool routing                                │
│   - Conversation management                     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│   AuthDomainAdapter (Security Configuration)    │
│   - System prompt (security rules)              │
│   - Tool definitions (register, login, etc.)    │
│   - Tool handlers (security logic)              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Provider Implementations                 │
│   ┌───────────────┬──────────────┬────────────┐ │
│   │ UserStore     │ TokenProvider│ Hasher     │ │
│   │ (PostgreSQL)  │ (JWT)        │ (Argon2)   │ │
│   └───────────────┴──────────────┴────────────┘ │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        External Services                        │
│   - Database (PostgreSQL, MongoDB, etc.)        │
│   - Redis (rate limiting, token blacklist)      │
│   - Email service (verification, password reset)│
│   - SMS service (MFA)                           │
└─────────────────────────────────────────────────┘
```

### Authentication Flow

```
User → "Register with email@example.com"
   ↓
ReusableAgent → Calls register_user tool
   ↓
AuthDomainAdapter → _register_user_handler
   ↓
1. Validate email format
2. Validate password strength (min 12 chars, uppercase, numbers, special)
3. Check for duplicate email (via UserStoreProvider)
4. Hash password (via PasswordHasher)
5. Create user (via UserStoreProvider)
6. Log event (via AuditLogger)
   ↓
Return: {"success": True, "user_id": "123", "message": "Registration successful"}
   ↓
Agent formats response → "Registration successful. Please verify your email."
   ↓
User receives response
```

---

## Provider Interfaces

### 1. UserStoreProvider

Abstracts user data persistence.

```python
class UserStoreProvider(Protocol):
    async def create_user(self, email: str, password_hash: str, metadata: Dict) -> Dict:
        """Create new user account"""
        ...

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Retrieve user by email"""
        ...

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Retrieve user by ID"""
        ...

    async def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Update user attributes"""
        ...

    async def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        ...
```

**Example Implementations:**
- PostgreSQL (SQLAlchemy, asyncpg)
- MongoDB (motor)
- DynamoDB (boto3)
- Firebase Auth
- Auth0
- Custom REST API

### 2. TokenProvider

Abstracts token generation/validation.

```python
class TokenProvider(Protocol):
    def generate_access_token(self, user_id: str, claims: Dict) -> str:
        """Generate JWT access token (short-lived: 1 hour)"""
        ...

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token (long-lived: 30 days)"""
        ...

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate and decode token"""
        ...

    def revoke_token(self, token: str) -> bool:
        """Revoke token (add to blacklist)"""
        ...
```

**Example Implementations:**
- JWT (PyJWT)
- OAuth2 (authlib)
- Paseto tokens
- Custom tokens
- Third-party (Auth0, Firebase tokens)

### 3. PasswordHasher

Abstracts password hashing.

```python
class PasswordHasher(Protocol):
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt/argon2/scrypt"""
        ...

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        ...
```

**Example Implementations:**
- Bcrypt (bcrypt library)
- Argon2 (passlib[argon2])
- Scrypt (passlib)

### 4. MFAProvider (Optional)

Abstracts Multi-Factor Authentication.

```python
class MFAProvider(Protocol):
    async def generate_mfa_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret (TOTP)"""
        ...

    async def send_mfa_code(self, user_id: str, method: str) -> bool:
        """Send MFA code via SMS/Email"""
        ...

    async def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify MFA code"""
        ...
```

**Example Implementations:**
- TOTP (pyotp)
- SMS (Twilio, AWS SNS)
- Email (SendGrid, AWS SES)

### 5. PolicyEngine (Optional)

Abstracts authorization policies.

```python
class PolicyEngine(Protocol):
    async def evaluate_policy(self, user_id: str, resource: str, action: str) -> bool:
        """Evaluate if user can perform action on resource"""
        ...
```

**Example Implementations:**
- OPA (Open Policy Agent)
- Custom RBAC
- AWS IAM policies
- Casbin

### 6. AuditLogger (Optional)

Abstracts security event logging.

```python
class AuditLogger(Protocol):
    async def log_event(self, event_type: str, user_id: Optional[str], details: Dict) -> None:
        """Log security event (login, logout, permission denied, etc.)"""
        ...
```

**Example Implementations:**
- CloudWatch Logs
- Elasticsearch
- Database table
- File logging
- SIEM integration

---

## Configuration

### AuthAdapterConfig

```python
class AuthAdapterConfig:
    def __init__(
        self,
        # Required providers
        user_store: UserStoreProvider,
        token_provider: TokenProvider,
        password_hasher: PasswordHasher,

        # Optional providers
        mfa_provider: Optional[MFAProvider] = None,
        policy_engine: Optional[PolicyEngine] = None,
        audit_logger: Optional[AuditLogger] = None,

        # Security settings
        password_min_length: int = 12,
        password_require_uppercase: bool = True,
        password_require_numbers: bool = True,
        password_require_special: bool = True,
        max_login_attempts: int = 5,
        lockout_duration_minutes: int = 15,
        token_expiry_minutes: int = 60,
        refresh_token_expiry_days: int = 30,
        require_mfa: bool = False,

        # Rate limiting
        rate_limit_requests: int = 10,
        rate_limit_window_seconds: int = 60
    )
```

### Example Configurations

**Minimal (Development):**
```python
config = AuthAdapterConfig(
    user_store=InMemoryUserStore(),      # Simple dict storage
    token_provider=SimpleJWTProvider(),   # Basic JWT
    password_hasher=BcryptHasher(),       # bcrypt
    password_min_length=8,                # Relaxed for dev
    max_login_attempts=10                 # More forgiving
)
```

**Production (High Security):**
```python
config = AuthAdapterConfig(
    user_store=PostgreSQLUserStore(),
    token_provider=JWTTokenProvider(),
    password_hasher=Argon2Hasher(),       # Argon2 (most secure)
    mfa_provider=TwilioMFAProvider(),     # SMS MFA
    policy_engine=OPAPolicyEngine(),      # Policy-based authz
    audit_logger=CloudWatchLogger(),      # Centralized logging
    password_min_length=16,               # Strong passwords
    password_require_special=True,
    max_login_attempts=3,                 # Strict lockout
    lockout_duration_minutes=30,
    token_expiry_minutes=15,              # Short-lived tokens
    require_mfa=True,                     # Always require MFA
    rate_limit_requests=5                 # Strict rate limiting
)
```

**Enterprise (Compliance):**
```python
config = AuthAdapterConfig(
    user_store=EnterpriseUserStore(),     # AD, LDAP, Okta
    token_provider=OAuth2Provider(),      # OAuth2/OIDC
    password_hasher=PBKDF2Hasher(),       # FIPS-compliant
    mfa_provider=HardwareTokenProvider(), # YubiKey, etc.
    policy_engine=CasbinEngine(),         # RBAC + ABAC
    audit_logger=SIEMLogger(),            # SIEM integration
    password_min_length=20,
    max_login_attempts=2,
    lockout_duration_minutes=60,
    require_mfa=True
)
```

---

## Security Features

### 1. Password Security

**Validation:**
- Minimum length (default: 12 characters)
- Uppercase requirement
- Numbers requirement
- Special characters requirement

**Hashing:**
- Supports bcrypt, argon2, scrypt
- Salted hashes
- Configurable work factor

**Example:**
```python
# Weak password rejected
"password123" → "Password too weak: at least one uppercase letter required; at least one special character required"

# Strong password accepted
"SecurePass123!" → "Registration successful"
```

### 2. Brute-Force Protection

**Features:**
- Failed login attempt tracking
- Account lockout after N attempts (default: 5)
- Lockout duration (default: 15 minutes)
- Automatic unlock after duration
- Audit logging of lockout events

**Flow:**
```
Attempt 1 (wrong): failed_attempts = 1
Attempt 2 (wrong): failed_attempts = 2
Attempt 3 (wrong): failed_attempts = 3
Attempt 4 (wrong): failed_attempts = 4
Attempt 5 (wrong): failed_attempts = 5 → Account locked for 15 minutes
Attempt 6 (correct): "Account temporarily locked. Please try again later."
[15 minutes later]
Attempt 7 (correct): Login successful, failed_attempts reset to 0
```

### 3. Rate Limiting

**Protection against:**
- Brute-force attacks
- Credential stuffing
- API abuse

**Configuration:**
```python
config = AuthAdapterConfig(
    rate_limit_requests=10,           # Max 10 requests
    rate_limit_window_seconds=60      # Per 60 seconds
)
```

**Response:**
```
Request 11 within 60s → "Too many requests. Please try again later."
```

### 4. Token Security

**Access Tokens:**
- Short-lived (default: 60 minutes)
- Contains user ID and claims
- JWT signed with secret key
- Expires automatically

**Refresh Tokens:**
- Long-lived (default: 30 days)
- Used to generate new access tokens
- Can be revoked (blacklist)

**Example:**
```python
# Login → Receive both tokens
{
    "access_token": "eyJ...",     # Use for API calls (expires in 1 hour)
    "refresh_token": "eyJ..."     # Use to get new access token
}

# Access token expired → Refresh
refresh_token → new access_token
```

### 5. User Enumeration Prevention

**Security Rule:** Never reveal whether a user exists.

**Bad (reveals user existence):**
```
"User not found" → Attacker knows this email is not registered
"Invalid password" → Attacker knows this email IS registered
```

**Good (generic message):**
```
"Invalid credentials" → Could be wrong email OR wrong password
```

**Implementation:**
```python
# Registration: Duplicate email check
if existing_user:
    return "Registration failed. Please try a different email."
    # NOT: "Email already registered"

# Login: Invalid credentials
if not user or not verify_password(...):
    return "Invalid credentials. Please try again."
    # NOT: "User not found" or "Wrong password"
```

### 6. Audit Logging

**Events Logged:**
- user_registered
- login_success
- login_failed
- login_mfa_required
- login_mfa_failed
- login_rate_limited
- account_locked
- logout
- password_reset_requested
- permission_denied
- token_refreshed

**Log Format:**
```python
{
    "timestamp": "2025-01-15T10:30:00Z",
    "event_type": "login_failed",
    "user_id": "user123",
    "details": {
        "email": "john@example.com",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}
```

---

## Usage Examples

### Example 1: User Registration

```python
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Register user alice@example.com with password StrongPass123!",
    conversation_history=[],
    db=db
)

# Success response
{
    "response": "Registration successful. Please verify your email.",
    "tool_calls": [{
        "tool": "register_user",
        "arguments": {
            "email": "alice@example.com",
            "password": "StrongPass123!"
        },
        "result": {
            "success": True,
            "user_id": "user_001",
            "message": "Registration successful. Please verify your email."
        }
    }]
}
```

### Example 2: User Login

```python
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Login user alice@example.com with password StrongPass123!",
    conversation_history=[],
    db=db
)

# Success response
{
    "response": "Login successful",
    "tool_calls": [{
        "tool": "login_user",
        "result": {
            "success": True,
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "user": {
                "id": "user_001",
                "email": "alice@example.com",
                "full_name": "Alice"
            }
        }
    }]
}
```

### Example 3: Login with MFA

```python
# First attempt (without MFA code)
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Login user bob@example.com with password SecurePass123!",
    conversation_history=[],
    db=db
)

# Response: MFA required
{
    "response": "MFA code required",
    "tool_calls": [{
        "tool": "login_user",
        "result": {
            "error": True,
            "requires_mfa": True,
            "message": "MFA code required"
        }
    }]
}

# Second attempt (with MFA code)
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Login user bob@example.com with password SecurePass123! and MFA code 123456",
    conversation_history=[],
    db=db
)

# Success
{
    "response": "Login successful",
    "tool_calls": [{...}]
}
```

### Example 4: Permission Check

```python
result = await auth_agent.process_message(
    user_id="user_001",
    message="Can I delete project:456?",
    conversation_history=[],
    db=db
)

# Allowed
{
    "response": "Authorized",
    "tool_calls": [{
        "tool": "check_permission",
        "arguments": {
            "user_id": "user_001",
            "resource": "project:456",
            "action": "delete"
        },
        "result": {
            "success": True,
            "allowed": True,
            "message": "Authorized"
        }
    }]
}

# Denied
{
    "response": "Permission denied",
    "tool_calls": [{
        "result": {
            "success": True,
            "allowed": False,
            "message": "Permission denied"
        }
    }]
}
```

### Example 5: Token Refresh

```python
result = await auth_agent.process_message(
    user_id="user_001",
    message="Refresh my access token using refresh token eyJ...",
    conversation_history=[],
    db=db
)

# Success
{
    "response": "Token refreshed",
    "tool_calls": [{
        "tool": "refresh_token",
        "result": {
            "success": True,
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "message": "Token refreshed"
        }
    }]
}
```

---

## Integration Guide

### Integration with FastAPI

```python
# main.py

from fastapi import FastAPI, Depends, HTTPException
from backend.agents.reusable import ReusableAgent
from backend.agents.reusable.adapters.auth_adapter import AuthDomainAdapter, AuthAdapterConfig

app = FastAPI()

# Initialize auth agent
auth_config = AuthAdapterConfig(
    user_store=PostgreSQLUserStore(),
    token_provider=JWTTokenProvider(),
    password_hasher=Argon2Hasher()
)
auth_agent = ReusableAgent(adapter=AuthDomainAdapter(auth_config))

@app.post("/auth/register")
async def register(email: str, password: str, db = Depends(get_db)):
    result = await auth_agent.process_message(
        user_id="anonymous",
        message=f"Register user {email} with password {password}",
        conversation_history=[],
        db=db
    )

    tool_result = result["tool_calls"][0]["result"]

    if tool_result.get("error"):
        raise HTTPException(status_code=400, detail=tool_result["message"])

    return {"user_id": tool_result["user_id"], "message": tool_result["message"]}

@app.post("/auth/login")
async def login(email: str, password: str, db = Depends(get_db)):
    result = await auth_agent.process_message(
        user_id="anonymous",
        message=f"Login user {email} with password {password}",
        conversation_history=[],
        db=db
    )

    tool_result = result["tool_calls"][0]["result"]

    if tool_result.get("error"):
        raise HTTPException(status_code=401, detail=tool_result["message"])

    return {
        "access_token": tool_result["access_token"],
        "refresh_token": tool_result["refresh_token"],
        "user": tool_result["user"]
    }

@app.post("/auth/logout")
async def logout(access_token: str, db = Depends(get_db)):
    result = await auth_agent.process_message(
        user_id="user_from_token",  # Extract from token
        message=f"Logout with token {access_token}",
        conversation_history=[],
        db=db
    )

    return {"message": "Logged out successfully"}
```

### Integration with Express.js

```javascript
// auth.routes.js

const express = require('express');
const { ReusableAgent, AuthDomainAdapter, AuthAdapterConfig } = require('./agents');

const router = express.Router();

// Initialize auth agent
const authConfig = new AuthAdapterConfig({
    userStore: new MongoDBUserStore(),
    tokenProvider: new JWTTokenProvider(),
    passwordHasher: new BcryptHasher()
});

const authAgent = new ReusableAgent({ adapter: new AuthDomainAdapter(authConfig) });

router.post('/register', async (req, res) => {
    const { email, password } = req.body;

    const result = await authAgent.processMessage({
        userId: 'anonymous',
        message: `Register user ${email} with password ${password}`,
        conversationHistory: [],
        db: req.db
    });

    const toolResult = result.toolCalls[0].result;

    if (toolResult.error) {
        return res.status(400).json({ error: toolResult.message });
    }

    res.json({ userId: toolResult.user_id, message: toolResult.message });
});

router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    const result = await authAgent.processMessage({
        userId: 'anonymous',
        message: `Login user ${email} with password ${password}`,
        conversationHistory: [],
        db: req.db
    });

    const toolResult = result.toolCalls[0].result;

    if (toolResult.error) {
        return res.status(401).json({ error: toolResult.message });
    }

    res.json({
        accessToken: toolResult.access_token,
        refreshToken: toolResult.refresh_token,
        user: toolResult.user
    });
});

module.exports = router;
```

### Integration with Mobile Apps

```swift
// AuthService.swift (iOS example)

import Foundation

class AuthService {
    private let authAgentURL = "https://api.yourapp.com/auth"

    func register(email: String, password: String) async throws -> User {
        let request = AuthRequest(
            message: "Register user \(email) with password \(password)"
        )

        let response = try await URLSession.shared.data(from: authAgentURL)
        let result = try JSONDecoder().decode(AuthResponse.self, from: response.data)

        if let error = result.error {
            throw AuthError.registrationFailed(error)
        }

        return result.user
    }

    func login(email: String, password: String) async throws -> AuthTokens {
        let request = AuthRequest(
            message: "Login user \(email) with password \(password)"
        )

        let response = try await URLSession.shared.data(from: authAgentURL)
        let result = try JSONDecoder().decode(AuthResponse.self, from: response.data)

        if let error = result.error {
            throw AuthError.loginFailed(error)
        }

        // Store tokens in Keychain
        KeychainService.save(result.accessToken, for: "access_token")
        KeychainService.save(result.refreshToken, for: "refresh_token")

        return AuthTokens(
            accessToken: result.accessToken,
            refreshToken: result.refreshToken
        )
    }
}
```

---

## Best Practices

### 1. Environment-Specific Configuration

```python
import os

# Development
if os.getenv("ENV") == "development":
    config = AuthAdapterConfig(
        user_store=InMemoryUserStore(),
        password_min_length=8,
        max_login_attempts=10
    )
# Production
else:
    config = AuthAdapterConfig(
        user_store=PostgreSQLUserStore(),
        token_provider=JWTTokenProvider(secret_key=os.getenv("JWT_SECRET")),
        password_hasher=Argon2Hasher(),
        mfa_provider=TwilioMFAProvider(api_key=os.getenv("TWILIO_API_KEY")),
        audit_logger=CloudWatchLogger(),
        password_min_length=16,
        require_mfa=True
    )
```

### 2. Secrets Management

**DON'T:**
```python
# Hardcoded secrets (bad!)
SECRET_KEY = "my-secret-key"
```

**DO:**
```python
# Use environment variables
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Or use secrets manager
import boto3
secrets = boto3.client('secretsmanager')
SECRET_KEY = secrets.get_secret_value(SecretId='jwt-secret')['SecretString']
```

### 3. Database Indexing

Create indexes for performance:

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_locked_until ON users(locked_until);
```

### 4. Rate Limiting

Implement with Redis:

```python
import redis

class RedisRateLimiter:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)

    async def check_rate_limit(self, identifier: str) -> bool:
        key = f"rate_limit:{identifier}"
        count = self.redis.incr(key)

        if count == 1:
            self.redis.expire(key, 60)  # 60 second window

        return count <= 10  # Max 10 requests per minute
```

### 5. Comprehensive Testing

```python
import pytest

@pytest.mark.asyncio
async def test_user_registration():
    config = AuthAdapterConfig(
        user_store=MockUserStore(),
        token_provider=MockTokenProvider(),
        password_hasher=MockHasher()
    )
    agent = ReusableAgent(adapter=AuthDomainAdapter(config))

    result = await agent.process_message(
        user_id="anonymous",
        message="Register user test@example.com with password SecurePass123!",
        conversation_history=[],
        db=None
    )

    assert result["tool_calls"][0]["result"]["success"] == True

@pytest.mark.asyncio
async def test_weak_password_rejected():
    result = await agent.process_message(
        user_id="anonymous",
        message="Register user test@example.com with password weak",
        conversation_history=[],
        db=None
    )

    assert result["tool_calls"][0]["result"]["error"] == True
    assert "Password too weak" in result["tool_calls"][0]["result"]["message"]

@pytest.mark.asyncio
async def test_brute_force_protection():
    # Attempt login 5 times with wrong password
    for i in range(5):
        result = await agent.process_message(
            user_id="anonymous",
            message="Login user alice@example.com with password WrongPassword",
            conversation_history=[],
            db=None
        )

    # 6th attempt should be locked
    result = await agent.process_message(
        user_id="anonymous",
        message="Login user alice@example.com with password CorrectPassword123!",
        conversation_history=[],
        db=None
    )

    assert "Account temporarily locked" in result["tool_calls"][0]["result"]["message"]
```

---

## Summary

**You now have a production-ready, framework-agnostic authentication & authorization AI agent!**

### Key Achievements

✅ **Reusable across ANY stack:**
- Web apps (FastAPI, Django, Express)
- Mobile apps (iOS, Android, React Native)
- Microservices
- Serverless functions

✅ **Security-first:**
- OWASP compliance
- Brute-force protection
- Rate limiting
- Audit logging
- User enumeration prevention

✅ **Configuration-driven:**
- No framework assumptions
- Provider pattern for all dependencies
- Environment-specific configs

✅ **Production features:**
- MFA support
- RBAC & policy-based authorization
- Token refresh
- Password reset flows
- Comprehensive audit trails

### Next Steps

1. ✅ Implement your provider interfaces
2. ✅ Configure `AuthAdapterConfig` for your stack
3. ✅ Integrate with your web/mobile framework
4. ✅ Add comprehensive tests
5. 🚀 Deploy to production!

---

**Questions? Check the code examples or open an issue!** 🔐
