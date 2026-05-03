from __future__ import annotations

import secrets
from functools import wraps

from flask import current_app, g, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Shared limiter instance; initialised via init_security(app)
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def init_security(app) -> None:
    """Attach security middleware to the Flask app."""
    limiter.init_app(app)

    @app.before_request
    def _generate_csp_nonce():
        g.csp_nonce = secrets.token_hex(16)

    @app.after_request
    def _apply_security_headers(response):
        nonce = getattr(g, "csp_nonce", secrets.token_hex(16))

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data:; "
            f"font-src 'self'; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'; "
            f"form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        if current_app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

    @app.context_processor
    def _inject_globals():
        return {
            "csp_nonce": getattr(g, "csp_nonce", ""),
            "secure_mode": current_app.config.get("SECURE_MODE", True),
        }


# ---------------------------------------------------------------------------
# CSRF helpers
# ---------------------------------------------------------------------------

def generate_csrf_token() -> str:
    """Generate a new CSRF token and store it in the session."""
    token = secrets.token_hex(32)
    session["csrf_token"] = token
    return token


def _read_csrf_from_request() -> str:
    """Read the CSRF token from header, JSON body, or form."""
    return (
        request.headers.get("X-CSRF-Token")
        or (request.get_json(silent=True) or {}).get("csrf_token")
        or request.form.get("csrf_token")
        or ""
    )


def csrf_protect(f):
    """Decorator: validate CSRF token for state-changing requests."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return f(*args, **kwargs)

        incoming = _read_csrf_from_request()
        stored = session.get("csrf_token", "")

        if not incoming or not stored or not secrets.compare_digest(incoming, stored):
            return jsonify({"error": "CSRF token missing or invalid"}), 403

        return f(*args, **kwargs)

    return decorated
