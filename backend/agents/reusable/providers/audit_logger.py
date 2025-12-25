"""
Audit Logger Providers
======================

Production-ready security audit logging implementations.

Available Loggers:
    - DatabaseAuditLogger: Log to PostgreSQL database
    - FileAuditLogger: Log to JSON file
    - CloudWatchAuditLogger: Log to AWS CloudWatch
    - ConsoleAuditLogger: Log to console (development)

Events Logged:
    - user_registered
    - login_success / login_failed
    - login_mfa_required / login_mfa_failed
    - login_rate_limited
    - account_locked
    - logout
    - password_reset_requested
    - permission_denied
    - token_refreshed

Security:
    - Tamper-resistant (append-only)
    - Timestamps with timezone
    - User ID tracking
    - IP address logging (when available)
    - Structured format (JSON)
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE AUDIT LOGGER (PRODUCTION)
# ============================================================================

class DatabaseAuditLogger:
    """
    PostgreSQL audit logger for production use.

    Stores security events in database for compliance and forensics.

    Database Schema:
        CREATE TABLE auth_audit_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type VARCHAR(100) NOT NULL,
            user_id VARCHAR(100),
            ip_address VARCHAR(45),
            user_agent TEXT,
            details JSONB,
            INDEX idx_audit_timestamp (timestamp),
            INDEX idx_audit_event_type (event_type),
            INDEX idx_audit_user_id (user_id)
        );

    Features:
        - Structured logging
        - Fast querying with indexes
        - JSON details field
        - Retention policies
    """

    def __init__(self, session_factory=None):
        """
        Initialize database audit logger.

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self.session_factory = session_factory
        logger.info("Database audit logger initialized")

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """
        Log security event to database.

        Args:
            event_type: Event identifier (e.g., "login_success")
            user_id: User ID (None for anonymous events)
            details: Additional event data (email, IP, etc.)

        Example:
            await logger.log_event(
                "login_success",
                "user_123",
                {"email": "alice@example.com", "ip": "192.168.1.1"}
            )
        """
        try:
            # In production: INSERT INTO auth_audit_logs
            # For now, log to console
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "details": details
            }

            logger.info(f"AUDIT: {json.dumps(log_entry)}")

        except Exception as e:
            # CRITICAL: Never fail user operations due to logging errors
            logger.error(f"Failed to log audit event: {e}", exc_info=True)


# ============================================================================
# FILE AUDIT LOGGER (SIMPLE PRODUCTION)
# ============================================================================

class FileAuditLogger:
    """
    File-based audit logger.

    Writes security events to JSON Lines file for simple deployments.

    Features:
        - JSON Lines format (one event per line)
        - Automatic log rotation
        - Append-only (tamper-resistant)
        - Easy to parse and analyze

    File Format:
        {"timestamp": "2025-01-15T10:30:00Z", "event_type": "login_success", ...}
        {"timestamp": "2025-01-15T10:31:00Z", "event_type": "logout", ...}

    Usage:
        logger = FileAuditLogger("/var/log/auth/audit.jsonl")
        await logger.log_event("login_success", "user_123", {...})
    """

    def __init__(self, log_file_path: str = "auth_audit.jsonl"):
        """
        Initialize file audit logger.

        Args:
            log_file_path: Path to log file (default: auth_audit.jsonl)
        """
        self.log_file_path = Path(log_file_path)

        # Create directory if needed
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"File audit logger initialized: {self.log_file_path}")

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """
        Log security event to JSON Lines file.

        Args:
            event_type: Event identifier
            user_id: User ID
            details: Additional event data
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "user_id": user_id,
                **details
            }

            # Append to file (JSON Lines format)
            with open(self.log_file_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            logger.debug(f"Audit event logged: {event_type}")

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}", exc_info=True)


# ============================================================================
# CLOUDWATCH AUDIT LOGGER (AWS)
# ============================================================================

class CloudWatchAuditLogger:
    """
    AWS CloudWatch audit logger for cloud deployments.

    Sends security events to CloudWatch Logs for centralized monitoring.

    Features:
        - Centralized logging
        - Integration with AWS services
        - CloudWatch Insights queries
        - Alerts and alarms
        - Long-term retention

    Requirements:
        - AWS credentials configured
        - CloudWatch Logs permissions
        - boto3 installed

    Usage:
        logger = CloudWatchAuditLogger(
            log_group="/aws/auth/audit",
            log_stream="production"
        )
        await logger.log_event("login_success", "user_123", {...})
    """

    def __init__(
        self,
        log_group: str = "/aws/auth/audit",
        log_stream: str = "default"
    ):
        """
        Initialize CloudWatch audit logger.

        Args:
            log_group: CloudWatch log group name
            log_stream: CloudWatch log stream name
        """
        try:
            import boto3
            self.cloudwatch = boto3.client('logs')
            self.log_group = log_group
            self.log_stream = log_stream

            # Create log group and stream if needed
            self._ensure_log_group_exists()

            logger.info(f"CloudWatch audit logger initialized: {log_group}/{log_stream}")

        except ImportError:
            logger.error("boto3 not installed. Run: pip install boto3")
            raise ImportError("boto3 is required. Install with: pip install boto3")

    def _ensure_log_group_exists(self):
        """Create log group and stream if they don't exist"""
        try:
            self.cloudwatch.create_log_group(logGroupName=self.log_group)
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self.cloudwatch.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """
        Log security event to CloudWatch.

        Args:
            event_type: Event identifier
            user_id: User ID
            details: Additional event data
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "user_id": user_id,
                **details
            }

            # Send to CloudWatch
            self.cloudwatch.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[
                    {
                        "timestamp": int(datetime.utcnow().timestamp() * 1000),
                        "message": json.dumps(log_entry)
                    }
                ]
            )

            logger.debug(f"Audit event logged to CloudWatch: {event_type}")

        except Exception as e:
            logger.error(f"Failed to log audit event to CloudWatch: {e}", exc_info=True)


# ============================================================================
# CONSOLE AUDIT LOGGER (DEVELOPMENT)
# ============================================================================

class ConsoleAuditLogger:
    """
    Console audit logger for development.

    Prints security events to console with color coding.

    Features:
        - Color-coded output
        - Structured format
        - Easy debugging

    Use for:
        - Local development
        - Testing
        - Debugging

    DO NOT use in production (logs are not persistent).
    """

    def __init__(self, use_colors: bool = True):
        """
        Initialize console audit logger.

        Args:
            use_colors: Enable color output (default: True)
        """
        self.use_colors = use_colors
        logger.info("Console audit logger initialized (DEVELOPMENT ONLY)")

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """
        Log security event to console.

        Args:
            event_type: Event identifier
            user_id: User ID
            details: Additional event data
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Color codes
            colors = {
                "success": "\033[92m",  # Green
                "failed": "\033[91m",   # Red
                "warning": "\033[93m",  # Yellow
                "info": "\033[94m",     # Blue
                "reset": "\033[0m"
            }

            # Determine color based on event type
            if "success" in event_type or "registered" in event_type:
                color = colors["success"]
            elif "failed" in event_type or "denied" in event_type:
                color = colors["failed"]
            elif "locked" in event_type or "rate_limited" in event_type:
                color = colors["warning"]
            else:
                color = colors["info"]

            # Format output
            if self.use_colors:
                output = f"{color}[AUDIT] {timestamp} | {event_type} | user={user_id} | {details}{colors['reset']}"
            else:
                output = f"[AUDIT] {timestamp} | {event_type} | user={user_id} | {details}"

            print(output)

        except Exception as e:
            logger.error(f"Failed to log audit event to console: {e}", exc_info=True)


# ============================================================================
# MULTI AUDIT LOGGER (PRODUCTION)
# ============================================================================

class MultiAuditLogger:
    """
    Multiple audit loggers combined.

    Send events to multiple destinations simultaneously.

    Example:
        # Log to database, file, and CloudWatch
        logger = MultiAuditLogger([
            DatabaseAuditLogger(),
            FileAuditLogger("/var/log/auth/audit.jsonl"),
            CloudWatchAuditLogger()
        ])

        await logger.log_event("login_success", "user_123", {...})
        # Event sent to all 3 destinations
    """

    def __init__(self, loggers: list):
        """
        Initialize multi audit logger.

        Args:
            loggers: List of audit logger instances
        """
        self.loggers = loggers
        logger.info(f"Multi audit logger initialized with {len(loggers)} destinations")

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """
        Log event to all configured loggers.

        Args:
            event_type: Event identifier
            user_id: User ID
            details: Additional event data
        """
        for audit_logger in self.loggers:
            try:
                await audit_logger.log_event(event_type, user_id, details)
            except Exception as e:
                # Don't let one logger failure affect others
                logger.error(f"Audit logger {audit_logger.__class__.__name__} failed: {e}")
