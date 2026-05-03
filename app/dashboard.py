from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, session

from .audit import log_action
from .db import tx
from .rbac import requires_role

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.get("")
@requires_role("admin")
def dashboard_page():
    return render_template("dashboard.html")


@bp.get("/security")
@requires_role("admin")
def security_data():
    """JSON payload consumed by the admin dashboard."""
    with tx() as db:
        recent_logins = db.execute(
            """
            SELECT username, action, ip_address, timestamp, success
            FROM   audit_logs
            WHERE  action IN ('LOGIN_SUCCESS','LOGIN_FAILED','LOGIN_BLOCKED')
            ORDER  BY timestamp DESC LIMIT 50
            """
        ).fetchall()

        failed_24h = db.execute(
            """
            SELECT username, COUNT(*) AS count, MAX(timestamp) AS last_attempt
            FROM   audit_logs
            WHERE  action = 'LOGIN_FAILED'
              AND  timestamp > datetime('now','-24 hours')
            GROUP  BY username
            ORDER  BY count DESC LIMIT 20
            """
        ).fetchall()

        locked_accounts = db.execute(
            """
            SELECT username, failed_attempts, locked_until, last_attempt
            FROM   account_lockouts
            WHERE  locked_until > datetime('now')
            """
        ).fetchall()

        api_key_usage = db.execute(
            """
            SELECT ak.key_prefix, ak.name, u.username, ak.last_used, ak.is_active
            FROM   api_keys ak
            JOIN   users u ON u.id = ak.user_id
            ORDER  BY ak.last_used DESC LIMIT 20
            """
        ).fetchall()

        users = db.execute(
            "SELECT id, username, role, is_active, created_at, last_login FROM users ORDER BY id"
        ).fetchall()

        audit_log = db.execute(
            """
            SELECT user_id, username, action, resource, ip_address, timestamp, success
            FROM   audit_logs
            ORDER  BY timestamp DESC LIMIT 100
            """
        ).fetchall()

        vuln_stats = db.execute(
            """
            SELECT action, COUNT(*) AS count
            FROM   audit_logs
            WHERE  action IN (
                'LOGIN_FAILED','LOGIN_BLOCKED','ACCESS_DENIED',
                'API_KEY_AUTH_FAILED','CSRF_VIOLATION'
            )
            AND    timestamp > datetime('now','-7 days')
            GROUP  BY action
            """
        ).fetchall()

    log_action("DASHBOARD_VIEW")

    return jsonify({
        "recent_logins": [dict(r) for r in recent_logins],
        "failed_login_stats_24h": [dict(r) for r in failed_24h],
        "locked_accounts": [dict(r) for r in locked_accounts],
        "api_key_usage": [dict(r) for r in api_key_usage],
        "users": [dict(r) for r in users],
        "recent_audit_log": [dict(r) for r in audit_log],
        "vulnerability_stats_7d": [dict(r) for r in vuln_stats],
    })


@bp.post("/users/<int:user_id>/deactivate")
@requires_role("admin")
def deactivate_user(user_id: int):
    if user_id == session.get("user_id"):
        return jsonify({"error": "cannot deactivate your own account"}), 400
    with tx() as db:
        db.execute("UPDATE users SET is_active=0 WHERE id=?", (user_id,))
    log_action("USER_DEACTIVATE", resource=f"user:{user_id}")
    return jsonify({"ok": True})


@bp.post("/users/<int:user_id>/activate")
@requires_role("admin")
def activate_user(user_id: int):
    with tx() as db:
        db.execute("UPDATE users SET is_active=1 WHERE id=?", (user_id,))
    log_action("USER_ACTIVATE", resource=f"user:{user_id}")
    return jsonify({"ok": True})


@bp.post("/users/<int:user_id>/role")
@requires_role("admin")
def change_role(user_id: int):
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if role not in ("user", "admin"):
        return jsonify({"error": "role must be 'user' or 'admin'"}), 400
    with tx() as db:
        db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    log_action("USER_ROLE_CHANGE", resource=f"user:{user_id}", details={"new_role": role})
    return jsonify({"ok": True})


@bp.delete("/lockouts/<username>")
@requires_role("admin")
def clear_lockout(username: str):
    with tx() as db:
        db.execute("DELETE FROM account_lockouts WHERE username=?", (username,))
    log_action("LOCKOUT_CLEARED", resource=f"user:{username}")
    return jsonify({"ok": True})
