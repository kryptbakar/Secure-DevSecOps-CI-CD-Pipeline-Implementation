from __future__ import annotations

import datetime

from flask import Flask, jsonify, render_template, session

from .api_keys import bp as api_keys_bp
from .auth import bp as auth_bp
from .config import Config
from .dashboard import bp as dashboard_bp
from .db import init_db
from .items import bp as items_bp
from .lab import bp as lab_bp
from .profiles import bp as profiles_bp
from .security import init_security


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    cfg = Config()

    # ---------------------------------------------------------------------------
    # Flask config
    # ---------------------------------------------------------------------------
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = cfg.SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SECURE"] = cfg.SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_SAMESITE"] = cfg.SESSION_COOKIE_SAMESITE
    app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(
        seconds=cfg.PERMANENT_SESSION_LIFETIME
    )
    app.config["SECURE_MODE"] = cfg.SECURE_MODE
    app.config["MAX_LOGIN_ATTEMPTS"] = cfg.MAX_LOGIN_ATTEMPTS
    app.config["LOCKOUT_DURATION_SECONDS"] = cfg.LOCKOUT_DURATION_SECONDS
    app.config["RATELIMIT_STORAGE_URI"] = cfg.RATELIMIT_STORAGE_URI
    # Disable rate limiting in test mode
    app.config.setdefault("RATELIMIT_ENABLED", True)

    # ---------------------------------------------------------------------------
    # Extensions & middleware
    # ---------------------------------------------------------------------------
    init_security(app)
    init_db(app, cfg.DATABASE_PATH)

    # ---------------------------------------------------------------------------
    # Blueprints
    # ---------------------------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(api_keys_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(lab_bp)

    # ---------------------------------------------------------------------------
    # Core routes
    # ---------------------------------------------------------------------------

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api")
    def api_info():
        return jsonify({
            "name": "devsecops-demo",
            "version": "2.0.0",
            "status": "ok",
            "secure_mode": cfg.SECURE_MODE,
            "endpoints": {
                "auth": [
                    "POST /auth/register",
                    "POST /auth/login",
                    "POST /auth/logout",
                    "GET  /auth/me",
                    "GET  /auth/csrf",
                    "POST /auth/change-password",
                ],
                "items": [
                    "GET    /items",
                    "POST   /items",
                    "PUT    /items/<id>",
                    "DELETE /items/<id>",
                    "GET    /items/search_secure",
                    "GET    /items/search_insecure  (SECURE_MODE=false only)",
                ],
                "api_keys": [
                    "GET    /api-keys",
                    "POST   /api-keys",
                    "DELETE /api-keys/<id>",
                ],
                "dashboard": [
                    "GET  /dashboard  (admin)",
                    "GET  /dashboard/security  (admin, JSON)",
                ],
            },
        })

    @app.get("/health")
    def health():
        return jsonify({
            "ok": True,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        })

    # ---------------------------------------------------------------------------
    # Session expiry check
    # ---------------------------------------------------------------------------

    @app.before_request
    def _enforce_session_expiry():
        login_time = session.get("login_time")
        if login_time and session.get("user_id"):
            try:
                lt = datetime.datetime.fromisoformat(login_time.replace("Z", "+00:00"))
                if (datetime.datetime.now(datetime.UTC) - lt).total_seconds() > cfg.PERMANENT_SESSION_LIFETIME:
                    session.clear()
            except (ValueError, TypeError):
                session.clear()

    # ---------------------------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------------------------

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "rate limit exceeded", "retry_after": str(e.description)}), 429

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "internal server error"}), 500

    return app
