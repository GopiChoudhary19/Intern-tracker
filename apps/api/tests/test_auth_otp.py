from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import AuthChallenge
from app.rate_limiter import rate_limit_store
from app.routers import auth as auth_router
from app.services import hash_otp


@pytest.fixture
def db_session(monkeypatch):
    # the OTP endpoints only touch auth_challenges until a code is accepted, so sqlite is enough here
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    AuthChallenge.__table__.create(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(auth_router, "use_demo_store", lambda: False)
    monkeypatch.setattr(settings, "auth_debug", False)
    monkeypatch.setattr(settings, "resend_api_key", None)
    app.dependency_overrides[get_db] = override_get_db
    rate_limit_store.clear()
    yield Session
    app.dependency_overrides.pop(get_db, None)
    rate_limit_store.clear()


def make_challenge(Session, code="123456"):
    with Session() as db:
        challenge = AuthChallenge(
            email="victim@example.com",
            code_hash=hash_otp(code),
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )
        db.add(challenge)
        db.commit()
        return challenge.id


def test_request_otp_never_returns_the_code_outside_debug_mode(client, db_session):
    response = client.post("/api/v1/auth/request-otp", json={"email": "victim@example.com"})

    assert response.status_code == 200
    assert response.json()["development_code"] is None


def test_request_otp_returns_the_code_in_debug_mode(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "auth_debug", True)

    response = client.post("/api/v1/auth/request-otp", json={"email": "dev@example.com"})

    assert response.json()["development_code"] == "000000"


def test_wrong_guesses_burn_the_challenge(client, db_session):
    challenge_id = str(make_challenge(db_session))
    limit = settings.auth_otp_verify_attempt_limit

    statuses = [
        client.post("/api/v1/auth/verify-otp", json={"challenge_id": challenge_id, "otp": f"{guess:06d}"}).status_code
        for guess in range(limit)
    ]
    assert statuses == [401] * (limit - 1) + [429]

    # even the right code no longer works once the challenge is burned
    right = client.post("/api/v1/auth/verify-otp", json={"challenge_id": challenge_id, "otp": "123456"})
    assert right.status_code == 400
    assert right.json()["detail"] == "OTP already used"


def test_expired_challenge_is_rejected(client, db_session):
    with db_session() as db:
        challenge = AuthChallenge(
            email="victim@example.com",
            code_hash=hash_otp("123456"),
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
        db.add(challenge)
        db.commit()
        challenge_id = str(challenge.id)

    response = client.post("/api/v1/auth/verify-otp", json={"challenge_id": challenge_id, "otp": "123456"})

    assert response.status_code == 400
    assert response.json()["detail"] == "OTP has expired"
