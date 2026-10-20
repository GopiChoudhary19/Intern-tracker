"""
Audit logging for sensitive operations.
Tracks admin operations, authentication events, and data access patterns.
"""

import logging
from typing import Any

# Configure audit logger
audit_logger = logging.getLogger("audit")
auth_logger = logging.getLogger("auth")


def setup_audit_logging() -> None:
    """Initialize audit logging handlers."""
    # Console handler for audit logs
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - AUDIT - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)
    
    auth_logger.addHandler(handler)
    auth_logger.setLevel(logging.INFO)


def log_admin_action(
    admin_id: str | None,
    action: str,
    resource: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    status: str = "success"
) -> None:
    """
    Log admin actions for audit trail.
    
    Args:
        admin_id: ID of admin performing action
        action: Action performed (CREATE, READ, UPDATE, DELETE)
        resource: Resource type (OPPORTUNITY, USER, FEEDBACK)
        resource_id: ID of resource being acted upon
        details: Additional details about the action
        status: Result status (success, failure, denied)
    """
    message = f"ADMIN_ACTION | action={action} | resource={resource} | status={status}"
    if admin_id:
        message += f" | admin_id={admin_id}"
    if resource_id:
        message += f" | resource_id={resource_id}"
    if details:
        message += f" | details={details}"
    
    if status == "success":
        audit_logger.info(message)
    else:
        audit_logger.warning(message)


def log_auth_event(
    event: str,
    user_id: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    status: str = "success",
    details: dict[str, Any] | None = None
) -> None:
    """
    Log authentication events.
    
    Args:
        event: Event type (LOGIN, LOGOUT, OTP_REQUEST, OTP_VERIFY, SESSION_CREATED, SESSION_REVOKED)
        user_id: User ID if applicable
        email: Email if applicable
        phone: Phone if applicable
        status: Result status (success, failure, denied)
        details: Additional details
    """
    message = f"AUTH_EVENT | event={event} | status={status}"
    if user_id:
        message += f" | user_id={user_id}"
    if email:
        message += f" | email={email}"
    if phone:
        message += f" | phone={phone}"
    if details:
        message += f" | details={details}"
    
    if status == "success":
        auth_logger.info(message)
    else:
        auth_logger.warning(message)


def log_access_attempt(
    endpoint: str,
    user_id: str | None = None,
    access_level: str = "unauthorized",
    details: dict[str, Any] | None = None
) -> None:
    """
    Log access attempts to protected endpoints.
    
    Args:
        endpoint: API endpoint accessed
        user_id: User ID if authenticated
        access_level: Access level (authorized, unauthorized, denied)
        details: Additional details
    """
    message = f"ACCESS_ATTEMPT | endpoint={endpoint} | level={access_level}"
    if user_id:
        message += f" | user_id={user_id}"
    if details:
        message += f" | details={details}"
    
    if access_level != "authorized":
        audit_logger.warning(message)
    else:
        audit_logger.debug(message)


def log_data_access(
    user_id: str,
    resource_type: str,
    resource_count: int = 1,
    filters: dict[str, Any] | None = None
) -> None:
    """
    Log data access patterns for analytics.
    
    Args:
        user_id: User accessing data
        resource_type: Type of resource (OPPORTUNITIES, APPLICATIONS, PROFILE)
        resource_count: Number of resources accessed
        filters: Filters applied to the query
    """
    message = f"DATA_ACCESS | user_id={user_id} | resource={resource_type} | count={resource_count}"
    if filters:
        message += f" | filters={filters}"
    
    audit_logger.info(message)


def log_security_event(
    event: str,
    severity: str = "warning",  # info, warning, critical
    details: dict[str, Any] | None = None
) -> None:
    """
    Log security-relevant events.
    
    Args:
        event: Security event description
        severity: Event severity level
        details: Additional details
    """
    message = f"SECURITY_EVENT | severity={severity} | event={event}"
    if details:
        message += f" | details={details}"
    
    if severity == "critical":
        audit_logger.critical(message)
    elif severity == "warning":
        audit_logger.warning(message)
    else:
        audit_logger.info(message)
