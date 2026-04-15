import os
import warnings


class Config:
    def __init__(self) -> None:
        secret = os.environ.get("SECRET_KEY")
        if not secret:
            warnings.warn(
                "SECRET_KEY not set — using insecure default. "
                "Set the SECRET_KEY environment variable before deploying to production.",
                RuntimeWarning,
                stacklevel=2,
            )
            secret = "dev-only-insecure-default-DO-NOT-USE-IN-PRODUCTION"

        self.SECRET_KEY = secret
        self.DATABASE_PATH = os.environ.get("DATABASE_PATH", "app.db")

        # Secure/insecure demo mode: when False, insecure endpoints are exposed
        self.SECURE_MODE = os.environ.get("SECURE_MODE", "true").lower() == "true"

        # Session cookie security
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
        self.SESSION_COOKIE_SAMESITE = "Lax"
        # Session lifetime in seconds (default 1 hour)
        self.PERMANENT_SESSION_LIFETIME = int(
            os.environ.get("SESSION_LIFETIME", "3600")
        )

        # Login lockout policy
        self.MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "5"))
        self.LOCKOUT_DURATION_SECONDS = int(
            os.environ.get("LOCKOUT_DURATION_SECONDS", "300")
        )

        # Rate limiting backend (memory for dev, redis:// in prod)
        self.RATELIMIT_STORAGE_URI = os.environ.get(
            "RATELIMIT_STORAGE_URI", "memory://"
        )
