from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.audit_log import setup_audit_logging
from app.config import settings
from app.db import SessionLocal
from app.routers import (
    admin,
    ai,
    applications,
    auth,
    community,
    feedback,
    notifications,
    opportunities,
    profile,
    saved_searches,
)
from app.services import configure_storage_mode, create_schema_and_seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize audit logging on startup
    setup_audit_logging()
    
    if settings.demo_mode == "demo":
        configure_storage_mode("demo")
        yield
        return

    db = SessionLocal()
    try:
        create_schema_and_seed(db)
        configure_storage_mode("database")
    except Exception:
        if settings.demo_mode == "auto":
            configure_storage_mode("demo")
        else:
            raise
    finally:
        db.close()
    yield


app = FastAPI(
    title="Intern Tracker API",
    version="0.1.0",
    description="API for discovering and tracking student opportunities.",
    lifespan=lifespan,
    docs_url="/api/v1/docs",  # Documentation at /api/v1/docs
    redoc_url="/api/v1/redoc",  # ReDoc at /api/v1/redoc
    openapi_url="/api/v1/openapi.json"  # OpenAPI schema
)

# Security: Restrict hosts (if configured)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Configure CORS with restrictions
allowed_origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=["Content-Type", "Authorization", "X-Admin-Token", "X-Demo-Token"],
    expose_headers=settings.cors_expose_headers,
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Security: Custom middleware to add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    if settings.enable_security_headers:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "microphone=(), camera=(), geolocation=(), payment=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # default to no caching, but keep a policy a route chose itself (public opportunity listings are cacheable)
        if "cache-control" not in response.headers:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
    
    return response


app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(opportunities.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(saved_searches.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
