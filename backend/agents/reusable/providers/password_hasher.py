"""
Password Hasher Providers
==========================

Production-ready password hashing implementations.

Available Hashers:
    - Argon2PasswordHasher (Recommended - Winner of Password Hashing Competition 2015)
    - BcryptPasswordHasher (Industry standard, widely used)
    - ScryptPasswordHasher (Alternative, good for memory-hard hashing)

Security Features:
    - Automatic salting
    - Configurable work factors
    - Constant-time comparison
    - Resistant to timing attacks

Recommendations:
    - Argon2: Best security, modern standard
    - Bcrypt: Battle-tested, widely compatible
    - Scrypt: Good alternative to bcrypt

Dependencies:
    pip install argon2-cffi bcrypt passlib
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# ARGON2 PASSWORD HASHER (RECOMMENDED)
# ============================================================================

class Argon2PasswordHasher:
    """
    Argon2 password hasher (recommended).

    Argon2 won the Password Hashing Competition in 2015 and is the
    current industry standard for password hashing.

    Features:
        - Memory-hard (resistant to GPU attacks)
        - Configurable time/memory costs
        - Built-in salting
        - Three variants: Argon2i, Argon2d, Argon2id (default)

    Security:
        - Time cost: 2 iterations (default)
        - Memory cost: 102400 KB (100 MB)
        - Parallelism: 8 threads
        - Hash length: 16 bytes
        - Salt length: 16 bytes

    Usage:
        hasher = Argon2PasswordHasher()
        hash = hasher.hash_password("SecurePass123!")
        valid = hasher.verify_password("SecurePass123!", hash)
    """

    def __init__(
        self,
        time_cost: int = 2,
        memory_cost: int = 102400,
        parallelism: int = 8
    ):
        """
        Initialize Argon2 hasher.

        Args:
            time_cost: Number of iterations (default: 2)
            memory_cost: Memory usage in KB (default: 100 MB)
            parallelism: Number of parallel threads (default: 8)
        """
        try:
            from argon2 import PasswordHasher
            from argon2.exceptions import VerifyMismatchError, InvalidHash

            self.ph = PasswordHasher(
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism
            )
            self.VerifyMismatchError = VerifyMismatchError
            self.InvalidHash = InvalidHash

            logger.info(f"Argon2 hasher initialized (time={time_cost}, memory={memory_cost}KB)")

        except ImportError:
            logger.error("argon2-cffi not installed. Run: pip install argon2-cffi")
            raise ImportError("argon2-cffi is required. Install with: pip install argon2-cffi")

    def hash_password(self, password: str) -> str:
        """
        Hash password using Argon2.

        Args:
            password: Plain text password

        Returns:
            Argon2 hash string

        Example:
            hash = hasher.hash_password("SecurePass123!")
            # Returns: $argon2id$v=19$m=102400,t=2,p=8$...
        """
        try:
            password_hash = self.ph.hash(password)
            logger.debug("Password hashed successfully with Argon2")
            return password_hash

        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against Argon2 hash.

        Args:
            password: Plain text password to verify
            password_hash: Argon2 hash to verify against

        Returns:
            True if password matches, False otherwise

        Example:
            valid = hasher.verify_password("SecurePass123!", hash)
        """
        try:
            self.ph.verify(password_hash, password)
            logger.debug("Password verified successfully")
            return True

        except self.VerifyMismatchError:
            logger.debug("Password verification failed: Mismatch")
            return False

        except self.InvalidHash:
            logger.error("Invalid hash format")
            return False

        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False


# ============================================================================
# BCRYPT PASSWORD HASHER (INDUSTRY STANDARD)
# ============================================================================

class BcryptPasswordHasher:
    """
    Bcrypt password hasher (industry standard).

    Bcrypt is the most widely used password hashing algorithm.
    Battle-tested and supported everywhere.

    Features:
        - Adaptive hashing (work factor)
        - Built-in salting
        - Resistant to rainbow tables
        - Constant-time comparison

    Security:
        - Default rounds: 12
        - Each round doubles computation time
        - Rounds=10: ~100ms, Rounds=12: ~300ms

    Usage:
        hasher = BcryptPasswordHasher()
        hash = hasher.hash_password("SecurePass123!")
        valid = hasher.verify_password("SecurePass123!", hash)
    """

    def __init__(self, rounds: int = 12):
        """
        Initialize Bcrypt hasher.

        Args:
            rounds: Number of rounds (default: 12, range: 4-31)
                   Higher = slower but more secure
                   Recommended: 12-14 for production
        """
        try:
            import bcrypt
            self.bcrypt = bcrypt
            self.rounds = rounds

            logger.info(f"Bcrypt hasher initialized (rounds={rounds})")

        except ImportError:
            logger.error("bcrypt not installed. Run: pip install bcrypt")
            raise ImportError("bcrypt is required. Install with: pip install bcrypt")

    def hash_password(self, password: str) -> str:
        """
        Hash password using Bcrypt.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash string

        Example:
            hash = hasher.hash_password("SecurePass123!")
            # Returns: $2b$12$...
        """
        try:
            salt = self.bcrypt.gensalt(rounds=self.rounds)
            password_hash = self.bcrypt.hashpw(password.encode('utf-8'), salt)
            logger.debug(f"Password hashed successfully with Bcrypt (rounds={self.rounds})")
            return password_hash.decode('utf-8')

        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against Bcrypt hash.

        Args:
            password: Plain text password to verify
            password_hash: Bcrypt hash to verify against

        Returns:
            True if password matches, False otherwise

        Example:
            valid = hasher.verify_password("SecurePass123!", hash)
        """
        try:
            result = self.bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
            logger.debug(f"Password verification: {'success' if result else 'failed'}")
            return result

        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False


# ============================================================================
# SCRYPT PASSWORD HASHER (ALTERNATIVE)
# ============================================================================

class ScryptPasswordHasher:
    """
    Scrypt password hasher (alternative).

    Scrypt is a memory-hard key derivation function designed to be
    resistant to hardware attacks.

    Features:
        - Memory-hard (like Argon2)
        - CPU and memory intensive
        - Configurable work factors

    Security:
        - N: CPU/memory cost (default: 2^14 = 16384)
        - r: Block size (default: 8)
        - p: Parallelization (default: 1)

    Usage:
        hasher = ScryptPasswordHasher()
        hash = hasher.hash_password("SecurePass123!")
        valid = hasher.verify_password("SecurePass123!", hash)
    """

    def __init__(self, n: int = 2**14, r: int = 8, p: int = 1):
        """
        Initialize Scrypt hasher.

        Args:
            n: CPU/memory cost parameter (default: 16384)
            r: Block size parameter (default: 8)
            p: Parallelization parameter (default: 1)
        """
        try:
            from passlib.hash import scrypt
            self.scrypt = scrypt
            self.n = n
            self.r = r
            self.p = p

            logger.info(f"Scrypt hasher initialized (N={n}, r={r}, p={p})")

        except ImportError:
            logger.error("passlib not installed. Run: pip install passlib")
            raise ImportError("passlib is required. Install with: pip install passlib")

    def hash_password(self, password: str) -> str:
        """
        Hash password using Scrypt.

        Args:
            password: Plain text password

        Returns:
            Scrypt hash string
        """
        try:
            password_hash = self.scrypt.using(
                rounds=self.n,
                block_size=self.r,
                parallelism=self.p
            ).hash(password)

            logger.debug("Password hashed successfully with Scrypt")
            return password_hash

        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against Scrypt hash.

        Args:
            password: Plain text password to verify
            password_hash: Scrypt hash to verify against

        Returns:
            True if password matches, False otherwise
        """
        try:
            result = self.scrypt.verify(password, password_hash)
            logger.debug(f"Password verification: {'success' if result else 'failed'}")
            return result

        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False


# ============================================================================
# SIMPLE HASHER (DEVELOPMENT ONLY - NOT FOR PRODUCTION!)
# ============================================================================

class SimplePasswordHasher:
    """
    Simple SHA256 hasher for DEVELOPMENT ONLY.

    WARNING: This is NOT secure for production!
    - No salting
    - Fast (vulnerable to brute force)
    - No adaptive work factor

    Use for:
        - Development/testing
        - Non-sensitive data
        - Prototyping

    DO NOT USE in production!
    """

    def __init__(self):
        import hashlib
        self.hashlib = hashlib
        logger.warning("⚠️  SimplePasswordHasher is for DEVELOPMENT ONLY! Use Argon2/Bcrypt in production!")

    def hash_password(self, password: str) -> str:
        """Hash password with SHA256 (INSECURE)"""
        return self.hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password (INSECURE)"""
        return self.hash_password(password) == password_hash
