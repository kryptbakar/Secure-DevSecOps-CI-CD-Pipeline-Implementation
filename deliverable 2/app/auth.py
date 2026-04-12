from __future__ import annotations

import datetime
import time

from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from .audit import log_action
from .db import tx
from .security import generate_csrf_token, limiter
from .validators import ValidationError, validate_password, validate_username

bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------------------------------------------------------
# Lockout helpers
# ---------------------------------------------------------------------------


def _now_str() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def _lockout_row(db, username: str):
    return db.execute(
        "SELECT * FROM account_lockouts WHERE username = ?", (username,)
    ).fetchone()


def _is_locked(row) -> bool:
    if not row or not row["locked_until"]:
        return False
    return row["locked_until"] > _now_str()


def _record_failure(db, username: str) -> None:
    """Increment failure counter; apply exponential backoff lockout."""
    cfg = current_app.config
    max_attempts: int = cfg.get("MAX_LOGIN_ATTEMPTS", 5)
    base_duration: int = cfg.get("LOCKOUT_DURATION_SECONDS", 300)

    now = datetime.datetime.now(datetime.UTC)
    now_str = now.isoformat().replace("+00:00", "Z")
    existing = _lockout_row(db, username)

    if existing:
        n = existing["failed_attempts"] + 1
        locked_until = None
        if n >= max_attempts:
            # Exponential backoff: base_duration * 2^(full_lockouts)
            full_lockouts = n // max_attempts
            secs = min(base_duration * (2**full_lockouts), 86_400)
            locked_until = (
                (now + datetime.timedelta(seconds=secs))
                .isoformat()
                .replace("+00:00", "Z")
            )
        db.execute(
            "UPDATE account_lockouts SET failed_attempts=?, locked_until=?, last_attempt=? WHERE username=?",
            (n, locked_until, now_str, username),
        )
    else:
        db.execute(
            "INSERT INTO account_lockouts (username, failed_attempts, locked_until, last_attempt) VALUES (?,1,NULL,?)",
            (username, now_str),
        )


def _reset_lockout(db, username: str) -> None:
    db.execute("DELETE FROM account_lockouts WHERE username = ?", (username,))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@bp.post("/register")
@limiter.limit("10 per minute")
def register():
    data = request.get_json(silent=True) or {}

    try:
        username = validate_username(data.get("username") or "")
        password = validate_password(data.get("password") or "")
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400

    password_hash = generate_password_hash(password)
    now = _now_str()

    with tx() as db:
        try:
            db.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
                (username, password_hash, "user", now),
            )
        except Exception:
            return jsonify({"error": "username already exists"}), 409

    log_action("USER_REGISTER", username=username)
    return jsonify({"ok": True, "message": "Account created. Please log in."}), 201


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    with tx() as db:
        lockout = _lockout_row(db, username)
        if _is_locked(lockout):
            log_action("LOGIN_BLOCKED", username=username, success=False)
            return (
                jsonify(
                    {
                        "error": "account temporarily locked due to too many failed attempts",
                        "locked_until": lockout["locked_until"],
                    }
                ),
                429,
            )

        row = db.execute(
            "SELECT id, username, password_hash, role, is_active FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not row or not check_password_hash(row["password_hash"], password):
            _record_failure(db, username)
            log_action("LOGIN_FAILED", username=username, success=False)

            # Progressive delay to slow brute force without leaking account existence
            attempt_row = _lockout_row(db, username)
            attempts = attempt_row["failed_attempts"] if attempt_row else 1
            time.sleep(min(0.5 * attempts, 5.0))

            return jsonify({"error": "invalid credentials"}), 401

        if not row["is_active"]:
            return jsonify({"error": "account is disabled"}), 403

        _reset_lockout(db, username)
        db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?", (_now_str(), row["id"])
        )

    # Session rotation: clear old session before writing new data
    session.clear()
    session["user_id"] = int(row["id"])
    session["username"] = row["username"]
    session["role"] = row["role"]
    session["login_time"] = _now_str()
    session.permanent = True

    csrf_token = generate_csrf_token()

    log_action("LOGIN_SUCCESS", user_id=int(row["id"]), username=row["username"])

    return jsonify(
        {
            "ok": True,
            "user": {"id": row["id"], "username": row["username"], "role": row["role"]},
            "csrf_token": csrf_token,
        }
    )


@bp.post("/logout")
def logout():
    log_action("LOGOUT")
    session.clear()
    return jsonify({"ok": True})


@bp.get("/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "not authenticated"}), 401

    with tx() as db:
        row = db.execute(
            "SELECT id, username, role, created_at, last_login FROM users WHERE id = ?",
            (uid,),
        ).fetchone()

    if not row:
        session.clear()
        return jsonify({"error": "user not found"}), 404

    return jsonify(
        {
            "user": {
                "id": row["id"],
                "username": row["username"],
                "role": row["role"],
                "created_at": row["created_at"],
                "last_login": row["last_login"],
            }
        }
    )


@bp.get("/csrf")
def get_csrf():
    """Return (or generate) the current session's CSRF token."""
    if not session.get("user_id"):
        return jsonify({"error": "not authenticated"}), 401
    token = session.get("csrf_token") or generate_csrf_token()
    return jsonify({"csrf_token": token})


@bp.post("/change-password")
def change_password():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "authentication required"}), 401

    data = request.get_json(silent=True) or {}
    current_pw = data.get("current_password") or ""

    try:
        new_pw = validate_password(data.get("new_password") or "")
    except ValidationError as e:
        return jsonify({"error": e.message}), 400

    with tx() as db:
        row = db.execute(
            "SELECT password_hash FROM users WHERE id = ?", (uid,)
        ).fetchone()

        if not row or not check_password_hash(row["password_hash"], current_pw):
            return jsonify({"error": "current password is incorrect"}), 401

        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_pw), uid),
        )

    log_action("PASSWORD_CHANGED")
    session.clear()
    return jsonify({"ok": True, "message": "Password changed. Please log in again."})
