"""
Rate limiting implementation for protecting against brute force attacks.
Uses in-memory store for simplicity; for production, consider Redis.
"""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from fastapi import HTTPException, status


class RateLimitWindow(NamedTuple):
    requests: list[datetime]
    limit: int
    window_minutes: int


# In-memory store for rate limit tracking
# Key: "endpoint:identifier" (e.g., "otp_request:user@email.com")
rate_limit_store: dict[str, list[datetime]] = defaultdict(list)

# Keys were never removed, so every email, phone or challenge ever seen stayed in memory for the life of the
# process. Every few minutes, keys with no request in the last day are dropped (all windows are far shorter).
SWEEP_INTERVAL = timedelta(minutes=10)
STALE_AFTER = timedelta(days=1)
_last_sweep = datetime.min.replace(tzinfo=UTC)


def sweep_stale_keys(now: datetime) -> None:
    global _last_sweep
    if now - _last_sweep < SWEEP_INTERVAL:
        return
    _last_sweep = now
    for key in [k for k, times in rate_limit_store.items() if not times or times[-1] < now - STALE_AFTER]:
        del rate_limit_store[key]


def check_rate_limit(
    identifier: str,
    limit: int = 5,
    window_minutes: int = 15,
    operation: str = "otp_request"
) -> bool:
    """
    Check if an operation is within rate limits.
    
    Args:
        identifier: Unique identifier (email, phone, IP, user_id, etc.)
        limit: Maximum requests allowed in the window
        window_minutes: Time window in minutes
        operation: Operation name for logging/tracking
        
    Returns:
        True if the request is allowed, False otherwise
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    key = f"{operation}:{identifier}"
    now = datetime.now(UTC)
    window_start = now - timedelta(minutes=window_minutes)
    sweep_stale_keys(now)

    # Clean up old entries
    rate_limit_store[key] = [
        req_time for req_time in rate_limit_store[key]
        if req_time > window_start
    ]

    # Check if limit exceeded
    if len(rate_limit_store[key]) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many {operation} attempts. Please try again in {window_minutes} minutes."
        )
    
    # Record this request
    rate_limit_store[key].append(now)
    return True


def record_failed_attempt(identifier: str, window_minutes: int = 15, operation: str = "otp_verify") -> int:
    """Record one failure for an identifier and return how many failures it has inside the window."""
    key = f"{operation}:{identifier}"
    now = datetime.now(UTC)
    window_start = now - timedelta(minutes=window_minutes)
    sweep_stale_keys(now)
    rate_limit_store[key] = [t for t in rate_limit_store[key] if t > window_start]
    rate_limit_store[key].append(now)
    return len(rate_limit_store[key])


def reset_rate_limit(identifier: str, operation: str = "otp_request") -> None:
    """
    Reset rate limit for an identifier (e.g., after successful login).
    
    Args:
        identifier: Unique identifier
        operation: Operation name
    """
    key = f"{operation}:{identifier}"
    rate_limit_store.pop(key, None)


def get_remaining_attempts(
    identifier: str,
    limit: int = 5,
    window_minutes: int = 15,
    operation: str = "otp_request"
) -> int:
    """
    Get remaining attempts for an identifier.
    
    Args:
        identifier: Unique identifier
        limit: Maximum requests allowed
        window_minutes: Time window in minutes
        operation: Operation name
        
    Returns:
        Number of remaining attempts
    """
    key = f"{operation}:{identifier}"
    now = datetime.now(UTC)
    window_start = now - timedelta(minutes=window_minutes)
    
    # Clean up old entries
    rate_limit_store[key] = [
        req_time for req_time in rate_limit_store[key]
        if req_time > window_start
    ]
    
    return max(0, limit - len(rate_limit_store[key]))
