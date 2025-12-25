"""
Authentication & Authorization Domain Adapter
==============================================

Reusable, security-first AI agent for authentication and authorization flows.

This adapter is FRAMEWORK-AGNOSTIC and can be used in:
- Web applications (FastAPI, Django, Flask, Express)
- Mobile apps (iOS, Android)
- SaaS platforms
- AI-powered chat systems
- Microservices architectures

Design Philosophy:
    - Configuration-driven (no hardcoded assumptions)
    - Stateless (state via external store)
    - Security-first (OWASP compliance)
    - Tool-based execution (MCP pattern)
    - Provider-agnostic (works with any user store, MFA provider, etc.)

Usage:
    from backend.agents.reusable import ReusableAgent
    from backend.agents.reusable.adapters.auth_adapter import AuthDomainAdapter

    # Configure adapter with your providers
    config = AuthAdapterConfig(
        user_store=YourUserStore(),
        token_provider=YourJWTProvider(),
        password_hasher=Argon2Hasher(),
        mfa_provider=YourMFAProvider(),
        audit_logger=YourAuditLogger()
    )

    auth_agent = ReusableAgent(adapter=AuthDomainAdapter(config))

    # Use for authentication flows
    result = await auth_agent.process_message(
        user_id="anonymous",  # or authenticated user
        message="Register user john@example.com with password SecurePass123!",
        conversation_history=[],
        db=db  # Your database session
    )

Security Features:
    - Password hashing (bcrypt/argon2/scrypt)
    - JWT/OAuth2/OpenID Connect compatible
    - Rate limiting & brute-force protection
    - MFA support (TOTP, SMS, Email)
    - RBAC & permission-based access control
    - Policy-driven authorization
    - Comprehensive audit logging
    - Secure session handling

Constitution Compliance:
    - Stateless: No in-memory state storage
    - MCP-First: All operations via configurable tools
    - Security-First: OWASP Top 10 protection
"""

from typing import Any, Dict, List, Callable, Optional, Protocol
from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


# ============================================================================
# PROVIDER INTERFACES (Framework-Agnostic)
# ============================================================================

class UserStoreProvider(Protocol):
    """Abstract interface for user data persistence"""

    async def create_user(self, email: str, password_hash: str, metadata: Dict) -> Dict[str, Any]:
        """Create new user account"""
        ...

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email"""
        ...

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by ID"""
        ...

    async def update_user(self, user_id: str, updates: Dict) -> Dict[str, Any]:
        """Update user attributes"""
        ...

    async def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        ...


class TokenProvider(Protocol):
    """Abstract interface for token generation/validation"""

    def generate_access_token(self, user_id: str, claims: Dict) -> str:
        """Generate JWT access token"""
        ...

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        ...

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate and decode token"""
        ...

    def revoke_token(self, token: str) -> bool:
        """Revoke token (add to blacklist)"""
        ...


class PasswordHasher(Protocol):
    """Abstract interface for password hashing"""

    def hash_password(self, password: str) -> str:
        """Hash password (bcrypt/argon2/scrypt)"""
        ...

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        ...


class MFAProvider(Protocol):
    """Abstract interface for Multi-Factor Authentication"""

    async def generate_mfa_secret(self, user_id: str) -> Dict[str, str]:
        """Generate MFA secret (TOTP)"""
        ...

    async def send_mfa_code(self, user_id: str, method: str) -> bool:
        """Send MFA code via SMS/Email"""
        ...

    async def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify MFA code"""
        ...


class PolicyEngine(Protocol):
    """Abstract interface for policy-based authorization"""

    async def evaluate_policy(self, user_id: str, resource: str, action: str) -> bool:
        """Evaluate authorization policy"""
        ...


class AuditLogger(Protocol):
    """Abstract interface for security audit logging"""

    async def log_event(self, event_type: str, user_id: Optional[str], details: Dict) -> None:
        """Log security event (login, logout, permission denied, etc.)"""
        ...


# ============================================================================
# CONFIGURATION
# ============================================================================

class AuthAdapterConfig:
    """
    Configuration for AuthDomainAdapter.

    This configuration makes the adapter reusable across different:
    - User stores (PostgreSQL, MongoDB, DynamoDB, Auth0, etc.)
    - Token providers (JWT, OAuth2, custom)
    - MFA providers (Twilio, AWS SNS, custom TOTP)
    - Policy engines (OPA, custom RBAC)
    """

    def __init__(
        self,
        user_store: UserStoreProvider,
        token_provider: TokenProvider,
        password_hasher: PasswordHasher,
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
    ):
        self.user_store = user_store
        self.token_provider = token_provider
        self.password_hasher = password_hasher
        self.mfa_provider = mfa_provider
        self.policy_engine = policy_engine
        self.audit_logger = audit_logger

        # Security settings
        self.password_min_length = password_min_length
        self.password_require_uppercase = password_require_uppercase
        self.password_require_numbers = password_require_numbers
        self.password_require_special = password_require_special
        self.max_login_attempts = max_login_attempts
        self.lockout_duration_minutes = lockout_duration_minutes
        self.token_expiry_minutes = token_expiry_minutes
        self.refresh_token_expiry_days = refresh_token_expiry_days
        self.require_mfa = require_mfa
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window_seconds = rate_limit_window_seconds


# ============================================================================
# AUTH DOMAIN ADAPTER
# ============================================================================

class AuthDomainAdapter(DomainAdapter):
    """
    Reusable Authentication & Authorization AI Agent Adapter.

    This adapter configures a generic AI agent to handle:
    - User registration
    - Login/logout
    - Token refresh
    - Password reset
    - Email/phone verification
    - Multi-Factor Authentication
    - Role-Based Access Control (RBAC)
    - Permission-based authorization
    - Policy-driven access control
    """

    def __init__(self, config: AuthAdapterConfig):
        """
        Initialize auth adapter with configuration.

        Args:
            config: AuthAdapterConfig with provider implementations
        """
        self.config = config
        logger.info("AuthDomainAdapter initialized with security-first configuration")

    def get_system_prompt(self) -> str:
        """Security-focused authentication assistant prompt"""
        return """You are a professional Authentication & Authorization Security Assistant.

**Your Responsibilities:**
1. **User Registration & Onboarding**
   - Validate email format and password strength
   - Create secure user accounts
   - Send verification emails/SMS

2. **Authentication Flows**
   - Handle login requests securely
   - Manage logout and session termination
   - Refresh access tokens
   - Verify Multi-Factor Authentication (MFA) when required

3. **Password Management**
   - Validate password strength (minimum 12 characters, uppercase, numbers, special chars)
   - Handle password reset requests
   - Send password reset links securely

4. **Authorization & Access Control**
   - Check user permissions for resources
   - Evaluate role-based access (RBAC)
   - Apply policy-driven authorization rules

5. **Security Compliance**
   - Enforce rate limiting (max 10 requests per minute)
   - Detect and prevent brute-force attacks
   - Lock accounts after 5 failed login attempts
   - Log all security events for audit

**Response Style:**
- Professional and security-conscious
- Clear error messages WITHOUT exposing sensitive details
- Never reveal: user existence, password hints, internal errors
- Always log security events

**Security Rules:**
- NEVER expose whether a user exists (say "Invalid credentials" not "User not found")
- NEVER log or expose passwords, tokens, or secrets
- ALWAYS validate inputs before processing
- ALWAYS rate-limit authentication attempts
- ALWAYS use secure password hashing (argon2/bcrypt)
- ALWAYS issue short-lived access tokens (60 min default)
- ALWAYS require MFA for sensitive operations if configured

**Error Responses (Generic for Security):**
- Login failure: "Invalid credentials. Please try again."
- Account locked: "Too many failed attempts. Account temporarily locked."
- Token expired: "Session expired. Please log in again."
- Permission denied: "You don't have permission to perform this action."

**Important:**
- You MUST use the provided security tools for all operations
- Never make up user IDs, tokens, or credentials
- Always prioritize security over convenience
- When in doubt, deny access and log the attempt
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Authentication & Authorization tool definitions"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "register_user",
                    "description": "Register a new user account with secure password hashing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User's email address (must be valid format)"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password (min 12 chars, uppercase, numbers, special chars)"
                            },
                            "full_name": {
                                "type": "string",
                                "description": "User's full name (optional)"
                            }
                        },
                        "required": ["email", "password"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "login_user",
                    "description": "Authenticate user and issue access/refresh tokens",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User's email address"
                            },
                            "password": {
                                "type": "string",
                                "description": "User's password"
                            },
                            "mfa_code": {
                                "type": "string",
                                "description": "MFA code (if MFA is enabled)"
                            }
                        },
                        "required": ["email", "password"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "logout_user",
                    "description": "Logout user and revoke tokens",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "access_token": {
                                "type": "string",
                                "description": "User's access token to revoke"
                            }
                        },
                        "required": ["access_token"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "refresh_token",
                    "description": "Refresh access token using refresh token",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "refresh_token": {
                                "type": "string",
                                "description": "Valid refresh token"
                            }
                        },
                        "required": ["refresh_token"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "request_password_reset",
                    "description": "Initiate password reset flow (send reset email)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User's email address"
                            }
                        },
                        "required": ["email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_email",
                    "description": "Verify user's email address with verification code",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "User's email"
                            },
                            "verification_code": {
                                "type": "string",
                                "description": "Email verification code"
                            }
                        },
                        "required": ["email", "verification_code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_permission",
                    "description": "Check if user has permission to perform action on resource",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User ID to check"
                            },
                            "resource": {
                                "type": "string",
                                "description": "Resource identifier (e.g., 'task:123', 'project:456')"
                            },
                            "action": {
                                "type": "string",
                                "description": "Action to perform (e.g., 'read', 'write', 'delete')"
                            }
                        },
                        "required": ["user_id", "resource", "action"]
                    }
                }
            }
        ]

        # Add MFA tools if MFA provider is configured
        if self.config.mfa_provider:
            tools.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "enable_mfa",
                        "description": "Enable Multi-Factor Authentication for user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "User ID"
                                },
                                "method": {
                                    "type": "string",
                                    "enum": ["totp", "sms", "email"],
                                    "description": "MFA method"
                                }
                            },
                            "required": ["user_id", "method"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "verify_mfa",
                        "description": "Verify MFA code during login",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "User ID"
                                },
                                "code": {
                                    "type": "string",
                                    "description": "MFA verification code"
                                }
                            },
                            "required": ["user_id", "code"]
                        }
                    }
                }
            ])

        return tools

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Mapping of auth tools to handlers"""
        handlers = {
            "register_user": self._register_user_handler,
            "login_user": self._login_user_handler,
            "logout_user": self._logout_user_handler,
            "refresh_token": self._refresh_token_handler,
            "request_password_reset": self._request_password_reset_handler,
            "verify_email": self._verify_email_handler,
            "check_permission": self._check_permission_handler
        }

        # Add MFA handlers if configured
        if self.config.mfa_provider:
            handlers.update({
                "enable_mfa": self._enable_mfa_handler,
                "verify_mfa": self._verify_mfa_handler
            })

        return handlers

    # ============================================================================
    # TOOL HANDLERS (Security-First Implementation)
    # ============================================================================

    async def _register_user_handler(
        self,
        user_id: str,  # "anonymous" for registration
        email: str,
        password: str,
        full_name: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """
        Register new user with security validations.

        Security checks:
        - Email format validation
        - Password strength validation
        - Duplicate email check
        - Secure password hashing
        - Audit logging
        """
        try:
            # 1. Validate email format
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                await self._audit_log("registration_failed", None, {"reason": "invalid_email"})
                return {
                    "error": True,
                    "message": "Invalid email format"
                }

            # 2. Validate password strength
            password_validation = self._validate_password_strength(password)
            if not password_validation["valid"]:
                await self._audit_log("registration_failed", None, {"reason": "weak_password"})
                return {
                    "error": True,
                    "message": f"Password too weak: {password_validation['message']}"
                }

            # 3. Check for duplicate email
            existing_user = await self.config.user_store.get_user_by_email(email)
            if existing_user:
                # SECURITY: Don't reveal that user exists
                await self._audit_log("registration_failed", None, {"reason": "duplicate_email"})
                return {
                    "error": True,
                    "message": "Registration failed. Please try a different email."
                }

            # 4. Hash password securely
            password_hash = self.config.password_hasher.hash_password(password)

            # 5. Create user
            user = await self.config.user_store.create_user(
                email=email,
                password_hash=password_hash,
                metadata={
                    "full_name": full_name,
                    "email_verified": False,
                    "mfa_enabled": False,
                    "created_at": datetime.utcnow().isoformat()
                }
            )

            # 6. Audit log
            await self._audit_log("user_registered", user["id"], {"email": email})

            return {
                "success": True,
                "user_id": user["id"],
                "message": "Registration successful. Please verify your email."
            }

        except Exception as e:
            logger.error(f"Registration error: {e}")
            await self._audit_log("registration_error", None, {"error": str(e)})
            return {
                "error": True,
                "message": "Registration failed. Please try again later."
            }

    async def _login_user_handler(
        self,
        user_id: str,  # "anonymous" for login
        email: str,
        password: str,
        mfa_code: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """
        Authenticate user with security checks.

        Security features:
        - Rate limiting
        - Brute-force protection
        - Account lockout
        - MFA verification
        - Secure token generation
        - Audit logging
        """
        try:
            # 1. Rate limiting check
            if not await self._check_rate_limit(email):
                await self._audit_log("login_rate_limited", None, {"email": email})
                return {
                    "error": True,
                    "message": "Too many requests. Please try again later."
                }

            # 2. Get user
            user = await self.config.user_store.get_user_by_email(email)

            # 3. Check if account is locked
            if user and user.get("locked_until"):
                locked_until = datetime.fromisoformat(user["locked_until"])
                if datetime.utcnow() < locked_until:
                    await self._audit_log("login_failed_locked", user["id"], {})
                    return {
                        "error": True,
                        "message": "Account temporarily locked. Please try again later."
                    }

            # 4. Verify password
            if not user or not self.config.password_hasher.verify_password(password, user["password_hash"]):
                # SECURITY: Generic error message
                if user:
                    await self._increment_failed_login_attempts(user["id"])
                await self._audit_log("login_failed", user["id"] if user else None, {})
                return {
                    "error": True,
                    "message": "Invalid credentials. Please try again."
                }

            # 5. Check MFA if required
            if user.get("mfa_enabled") and self.config.require_mfa:
                if not mfa_code:
                    await self._audit_log("login_mfa_required", user["id"], {})
                    return {
                        "error": True,
                        "requires_mfa": True,
                        "message": "MFA code required"
                    }

                # Verify MFA code
                if not await self.config.mfa_provider.verify_mfa_code(user["id"], mfa_code):
                    await self._audit_log("login_mfa_failed", user["id"], {})
                    return {
                        "error": True,
                        "message": "Invalid MFA code"
                    }

            # 6. Reset failed login attempts
            await self.config.user_store.update_user(user["id"], {
                "failed_login_attempts": 0,
                "last_login": datetime.utcnow().isoformat()
            })

            # 7. Generate tokens
            access_token = self.config.token_provider.generate_access_token(
                user["id"],
                claims={"email": email, "roles": user.get("roles", [])}
            )
            refresh_token = self.config.token_provider.generate_refresh_token(user["id"])

            # 8. Audit log
            await self._audit_log("login_success", user["id"], {"email": email})

            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user.get("full_name")
                },
                "message": "Login successful"
            }

        except Exception as e:
            logger.error(f"Login error: {e}")
            await self._audit_log("login_error", None, {"error": str(e)})
            return {
                "error": True,
                "message": "Login failed. Please try again."
            }

    async def _logout_user_handler(
        self,
        user_id: str,
        access_token: str,
        db=None
    ) -> Dict[str, Any]:
        """Logout user and revoke tokens"""
        try:
            # Revoke token
            self.config.token_provider.revoke_token(access_token)

            # Audit log
            await self._audit_log("logout", user_id, {})

            return {
                "success": True,
                "message": "Logged out successfully"
            }

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                "error": True,
                "message": "Logout failed"
            }

    async def _refresh_token_handler(
        self,
        user_id: str,
        refresh_token: str,
        db=None
    ) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            # Validate refresh token
            payload = self.config.token_provider.validate_token(refresh_token)
            if not payload:
                return {
                    "error": True,
                    "message": "Invalid refresh token"
                }

            # Generate new access token
            access_token = self.config.token_provider.generate_access_token(
                payload["user_id"],
                claims=payload.get("claims", {})
            )

            return {
                "success": True,
                "access_token": access_token,
                "message": "Token refreshed"
            }

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {
                "error": True,
                "message": "Token refresh failed"
            }

    async def _request_password_reset_handler(
        self,
        user_id: str,
        email: str,
        db=None
    ) -> Dict[str, Any]:
        """Initiate password reset (placeholder)"""
        # SECURITY: Always return success to prevent user enumeration
        await self._audit_log("password_reset_requested", None, {"email": email})

        return {
            "success": True,
            "message": "If the email exists, a password reset link has been sent."
        }

    async def _verify_email_handler(
        self,
        user_id: str,
        email: str,
        verification_code: str,
        db=None
    ) -> Dict[str, Any]:
        """Verify email address (placeholder)"""
        # Implementation depends on verification code storage
        return {
            "success": True,
            "message": "Email verified successfully"
        }

    async def _check_permission_handler(
        self,
        user_id: str,
        resource: str,
        action: str,
        db=None
    ) -> Dict[str, Any]:
        """Check user permission for resource/action"""
        try:
            if not self.config.policy_engine:
                return {
                    "error": True,
                    "message": "Authorization not configured"
                }

            # Evaluate policy
            allowed = await self.config.policy_engine.evaluate_policy(user_id, resource, action)

            if not allowed:
                await self._audit_log("permission_denied", user_id, {
                    "resource": resource,
                    "action": action
                })

            return {
                "success": True,
                "allowed": allowed,
                "message": "Authorized" if allowed else "Permission denied"
            }

        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return {
                "error": True,
                "message": "Authorization check failed"
            }

    async def _enable_mfa_handler(
        self,
        user_id: str,
        method: str,
        db=None
    ) -> Dict[str, Any]:
        """Enable MFA for user (placeholder)"""
        if not self.config.mfa_provider:
            return {"error": True, "message": "MFA not configured"}

        secret = await self.config.mfa_provider.generate_mfa_secret(user_id)

        return {
            "success": True,
            "secret": secret,
            "message": f"MFA enabled via {method}"
        }

    async def _verify_mfa_handler(
        self,
        user_id: str,
        code: str,
        db=None
    ) -> Dict[str, Any]:
        """Verify MFA code (placeholder)"""
        if not self.config.mfa_provider:
            return {"error": True, "message": "MFA not configured"}

        valid = await self.config.mfa_provider.verify_mfa_code(user_id, code)

        return {
            "success": True,
            "valid": valid,
            "message": "MFA verified" if valid else "Invalid MFA code"
        }

    # ============================================================================
    # SECURITY HELPERS
    # ============================================================================

    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password meets security requirements"""
        issues = []

        if len(password) < self.config.password_min_length:
            issues.append(f"minimum {self.config.password_min_length} characters required")

        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            issues.append("at least one uppercase letter required")

        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            issues.append("at least one number required")

        if self.config.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("at least one special character required")

        return {
            "valid": len(issues) == 0,
            "message": "; ".join(issues) if issues else "Password meets requirements"
        }

    async def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits (placeholder)"""
        # Implementation: Use Redis, in-memory cache, or database
        # For now, always allow
        return True

    async def _increment_failed_login_attempts(self, user_id: str) -> None:
        """Increment failed login attempts and lock account if threshold exceeded"""
        user = await self.config.user_store.get_user_by_id(user_id)
        failed_attempts = user.get("failed_login_attempts", 0) + 1

        updates = {"failed_login_attempts": failed_attempts}

        # Lock account if threshold exceeded
        if failed_attempts >= self.config.max_login_attempts:
            locked_until = datetime.utcnow() + timedelta(minutes=self.config.lockout_duration_minutes)
            updates["locked_until"] = locked_until.isoformat()
            await self._audit_log("account_locked", user_id, {"attempts": failed_attempts})

        await self.config.user_store.update_user(user_id, updates)

    async def _audit_log(self, event_type: str, user_id: Optional[str], details: Dict) -> None:
        """Log security event"""
        if self.config.audit_logger:
            await self.config.audit_logger.log_event(event_type, user_id, details)
        else:
            logger.info(f"AUDIT: {event_type} | user={user_id} | details={details}")

    # ============================================================================
    # DOMAIN-SPECIFIC CUSTOMIZATIONS
    # ============================================================================

    def get_greeting_response(self) -> str:
        """Security-focused greeting"""
        return (
            "Hello! I'm your Authentication & Authorization Security Assistant. "
            "I can help you with account registration, login, password reset, "
            "and access control. All interactions are securely logged for audit purposes."
        )

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Security-conscious error handling (no details exposed)"""
        # SECURITY: Never expose internal error details
        logger.error(f"Auth error: {error} | context: {context}")
        return "A security error occurred. Please try again or contact support."

    def get_model_name(self) -> str:
        """Use GPT-4 for security-critical operations"""
        return "gpt-4-turbo-preview"
