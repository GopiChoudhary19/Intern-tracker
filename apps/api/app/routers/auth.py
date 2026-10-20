import json
import secrets
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.audit_log import log_auth_event
from app.config import settings
from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import extract_bearer_token, get_current_user
from app.models import AuthChallenge
from app.rate_limiter import check_rate_limit
from app.schemas import (
    AuthProvider,
    AuthProvidersResponse,
    AuthResponse,
    LogoutResponse,
    RequestOtpRequest,
    RequestOtpResponse,
    VerifyOtpRequest,
)
from app.services import (
    create_session,
    create_user_with_profile,
    get_user_by_identifier,
    hash_otp,
    mask_identifier,
    revoke_session_by_token,
    to_user_profile_response,
    use_demo_store,
)

router = APIRouter(tags=["auth"])

def send_resend_otp(to_email: str, code: str):
    api_key = settings.resend_api_key
    
    if not api_key:
        print("Notice: INTERN_TRACKER_RESEND_API_KEY missing. Real emails skipped.")
        return

    payload = {
        "from": "Intern Tracker <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Your Intern Tracker Login Code",
        "html": f"<p>Your one-time login code for Intern Tracker is: <strong>{code}</strong></p><p>This code will expire in {settings.auth_otp_ttl_minutes} minutes.</p>"
    }
    
    # Send HTTP POST to api.resend.com via urllib to bypass SMTP firewalls completely
    req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(payload).encode("utf-8"))
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        print(f"System: Successfully dispatched live HTTP OTP via Resend to {to_email} (Code: {response.getcode()})")
    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        print(f"System: Resend HTTP Error! {e.code} API Rejected the request. Details: {error_info}")
        if e.code == 403:
             print("System: 403 Forbidden - Ensure you are sending the email to the exact address you registered at resend.com with!")
    except OSError as e:  # URLError, timeouts and connection failures
        print(f"System: Failed to connect to Resend HTTP API. Error details: {e}")

@router.get("/auth/providers", response_model=AuthProvidersResponse)
def list_auth_providers() -> AuthProvidersResponse:
    return AuthProvidersResponse(
        items=[
            AuthProvider(
                id="google",
                label="Google",
                auth_url=settings.google_oauth_url,
                configured=bool(settings.google_oauth_url),
            ),
            AuthProvider(
                id="github",
                label="GitHub",
                auth_url=settings.github_oauth_url,
                configured=bool(settings.github_oauth_url),
            ),
            AuthProvider(
                id="linkedin",
                label="LinkedIn",
                auth_url=settings.linkedin_oauth_url,
                configured=bool(settings.linkedin_oauth_url),
            ),
        ]
    )

@router.post("/auth/request-otp", response_model=RequestOtpResponse)
def request_otp(payload: RequestOtpRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> RequestOtpResponse:
    if use_demo_store():
        email = payload.email.strip().lower() if payload.email else settings.demo_email
        phone = payload.phone.strip() if payload.phone else settings.demo_phone
        log_auth_event("OTP_REQUEST", email=email, phone=phone, status="success")
        return RequestOtpResponse(
            challenge_id=DEMO_STORE.user.id,
            message="Demo OTP generated. Use 000000 to continue.",
            channel="email" if email else "phone",
            target_hint=mask_identifier(email=email, phone=phone),
            development_code="000000",
        )

    email = payload.email.strip().lower() if payload.email else None
    phone = payload.phone.strip() if payload.phone else None
    if not email and not phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone is required")

    # Rate limiting: Check OTP request limit
    identifier = email or phone or "unknown"
    try:
        check_rate_limit(
            identifier=identifier,
            limit=settings.auth_otp_request_limit,
            window_minutes=settings.auth_otp_request_window_minutes,
            operation="otp_request"
        )
    except HTTPException:
        log_auth_event("OTP_REQUEST", email=email, phone=phone, status="denied", details={"reason": "rate_limit"})
        raise

    window_start = datetime.now(UTC) - timedelta(minutes=settings.auth_otp_request_window_minutes)
    filters = []
    if email:
        filters.append(AuthChallenge.email == email)
    if phone:
        filters.append(AuthChallenge.phone == phone)
    recent_requests = db.scalar(
        select(func.count(AuthChallenge.id)).where(
            or_(*filters),
            AuthChallenge.created_at >= window_start,
        )
    )
    if recent_requests and recent_requests >= settings.auth_otp_request_limit:
        log_auth_event("OTP_REQUEST", email=email, phone=phone, status="denied", details={"reason": "database_limit"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please wait before trying again.",
        )

    channel = "email" if email else "phone"
    code = "000000" if settings.auth_debug else f"{secrets.randbelow(1000000):06d}"
    
    # Print the OTP to the terminal so the developer can see it locally
    print("==================================================")
    print(f"OTP CODE FOR {identifier}: {code}")
    print("==================================================")

    # Immediately fire off actual email processing in the background!
    if email:
        background_tasks.add_task(send_resend_otp, email, code)

    challenge = AuthChallenge(
        email=email,
        phone=phone,
        code_hash=hash_otp(code),
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.auth_otp_ttl_minutes),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    log_auth_event("OTP_REQUEST", email=email, phone=phone, status="success")

    return RequestOtpResponse(
        challenge_id=challenge.id,
        message=f"A one-time code has been prepared for your {channel}.",
        channel=channel,
        target_hint=mask_identifier(email=email, phone=phone),
        development_code=code if (not settings.resend_api_key or settings.auth_debug) else None,
    )

@router.get("/auth/google/login")
def google_login_redirect():
    """Placeholder for Google OAuth Redirect"""
    raise HTTPException(status_code=501, detail="Google OAuth is not configured on the backend yet. Add an Auth0 or Google Developer Console client architecture here.")

@router.get("/auth/github/login")
def github_login_redirect():
    """Placeholder for GitHub OAuth Redirect"""
    raise HTTPException(status_code=501, detail="GitHub OAuth is not configured on the backend yet. Add an Auth0 or GitHub Developer Console client architecture here.")


@router.post("/auth/verify-otp", response_model=AuthResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if use_demo_store():
        log_auth_event("LOGIN", user_id=str(DEMO_STORE.user.id), status="success")
        return AuthResponse(
            access_token=settings.demo_token,
            refresh_token=f"{settings.demo_token}-refresh",
            user=DEMO_STORE.user,
        )

    challenge = db.get(AuthChallenge, payload.challenge_id)
    if challenge is None:
        log_auth_event("OTP_VERIFY", status="failure", details={"reason": "challenge_not_found"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP challenge not found")
    if challenge.consumed_at is not None:
        log_auth_event("OTP_VERIFY", status="failure", details={"reason": "otp_already_used"})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP already used")
    if challenge.expires_at <= datetime.now(UTC):
        log_auth_event("OTP_VERIFY", status="failure", details={"reason": "otp_expired"})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")
    if challenge.code_hash != hash_otp(payload.otp):
        log_auth_event("OTP_VERIFY", email=challenge.email, phone=challenge.phone, status="failure", details={"reason": "invalid_otp"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")
    if payload.email and challenge.email and payload.email.strip().lower() != challenge.email:
        log_auth_event("OTP_VERIFY", status="failure", details={"reason": "email_mismatch"})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email does not match this OTP")
    if payload.phone and challenge.phone and payload.phone.strip() != challenge.phone:
        log_auth_event("OTP_VERIFY", status="failure", details={"reason": "phone_mismatch"})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone does not match this OTP")

    user = get_user_by_identifier(db, email=challenge.email, phone=challenge.phone)
    if user is None:
        user = create_user_with_profile(
            db,
            email=challenge.email,
            phone=challenge.phone,
            full_name=payload.full_name,
        )

    session = create_session(db, user, provider="otp")
    challenge.consumed_at = datetime.now(UTC)
    db.add(challenge)
    db.commit()

    log_auth_event("LOGIN", user_id=str(user.id), email=challenge.email, phone=challenge.phone, status="success")

    return AuthResponse(
        access_token=session.token,
        refresh_token=session.token,
        user=to_user_profile_response(user),
    )


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(
    authorization: str | None = Header(default=None),
    x_demo_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> LogoutResponse:
    token = extract_bearer_token(authorization, x_demo_token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    revoke_session_by_token(db, token)
    return LogoutResponse(message="Session revoked")
