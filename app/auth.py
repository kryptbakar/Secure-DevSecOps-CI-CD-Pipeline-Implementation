from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from .db import tx

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    # Intentionally insecure: storing plaintext passwords (vulnerable-by-design).
    with tx() as db:
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
        except Exception:
            return jsonify({"error": "username already exists"}), 409

    return jsonify({"ok": True}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    with tx() as db:
        row = db.execute(
            "SELECT id, username, password FROM users WHERE username = ?", (username,)
        ).fetchone()

    if not row or row["password"] != password:
        return jsonify({"error": "invalid credentials"}), 401

    session.clear()
    session["user_id"] = int(row["id"])
    session["username"] = row["username"]

    return jsonify({"ok": True, "user": {"id": row["id"], "username": row["username"]}})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})
