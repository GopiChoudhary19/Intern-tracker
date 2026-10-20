from datetime import UTC, datetime

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.demo_store import DEMO_STORE
from app.models import AuthSession, User
from app.services import use_demo_store


def extract_bearer_token(
    authorization: str | None = None,
    x_demo_token: str | None = None,
) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:]
    if x_demo_token:
        return x_demo_token
    return None


def get_current_user(
    authorization: str | None = Header(default=None),
    x_demo_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = extract_bearer_token(authorization, x_demo_token)

    if use_demo_store():
        if token != settings.demo_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing demo token")
        return DEMO_STORE.user  # type: ignore[return-value]

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    session = db.scalar(
        select(AuthSession)
        .join(AuthSession.user)
        .where(
            AuthSession.token == token,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.now(UTC),
        )
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    return session.user


def get_optional_current_user(
    authorization: str | None = Header(default=None),
    x_demo_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    token = extract_bearer_token(authorization, x_demo_token)

    if use_demo_store():
        if token == settings.demo_token:
            return DEMO_STORE.user  # type: ignore[return-value]
        return None

    if not token:
        return None

    session = db.scalar(
        select(AuthSession)
        .join(AuthSession.user)
        .where(
            AuthSession.token == token,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.now(UTC),
        )
    )
    if session is None:
        return None

    return session.user


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured",
        )
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
