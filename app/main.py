from __future__ import annotations

from flask import Flask, jsonify, render_template

from .auth import bp as auth_bp
from .config import Config
from .db import init_db
from .items import bp as items_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    cfg = Config()

    # Load config
    app.config["SECRET_KEY"] = cfg.SECRET_KEY

    # Initialize DB
    init_db(app, cfg.DATABASE_PATH)

    # Routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api")
    def api_info():
        return jsonify(
            {
                "name": "devsecops-demo",
                "status": "ok",
                "endpoints": [
                    "/auth/register",
                    "/auth/login",
                    "/auth/logout",
                    "/items",
                    "/items/search?q=...",
                ],
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    return app
