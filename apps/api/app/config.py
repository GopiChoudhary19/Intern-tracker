from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INTERN_TRACKER_", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/intern_tracker"
    demo_token: str = "demo-student-token"
    demo_email: str = "demo@student.edu"
    demo_phone: str = "+910000000000"
    demo_mode: str = "database"
    cors_allowed_origins: str = "http://localhost:3000"
    auth_debug: bool = False
    auth_otp_ttl_minutes: int = 10
    auth_session_ttl_days: int = 30
    auth_otp_request_limit: int = 5
    auth_otp_request_window_minutes: int = 15
    auth_otp_verify_attempt_limit: int = 5
    admin_token: str | None = None
    google_oauth_url: str | None = None
    github_oauth_url: str | None = None
    linkedin_oauth_url: str | None = None
    
    # Email settings for OTP (HTTP API)
    resend_api_key: str | None = None
    
    # Security settings
    secure_cookies: bool = True  # Use Secure flag on cookies (only for HTTPS)
    samesite_cookies: str = "strict"  # SameSite policy: strict, lax, none
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    cors_expose_headers: list[str] = ["X-Total-Count", "X-Page-Number"]
    
    # Rate limiting
    otp_rate_limit_per_window: int = 5  # Max OTP requests
    otp_rate_limit_window_minutes: int = 15  # Time window for OTP
    login_rate_limit_per_window: int = 10  # Max login attempts  
    login_rate_limit_window_minutes: int = 15  # Time window for login
    
    # Security headers
    enable_security_headers: bool = True
    csp_header: str = "default-src 'self'"


settings = Settings()
