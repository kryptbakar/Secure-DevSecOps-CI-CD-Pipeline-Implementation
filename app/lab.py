"""
lab.py — Interactive security demonstration endpoints.

Each endpoint powers a live Attack vs Defend demo in the frontend.
Insecure ("attack") endpoints are gated behind SECURE_MODE=false so
the app is safe by default but can expose vulnerabilities for teaching.
"""
from __future__ import annotations

import datetime
import html as _html

from flask import Blueprint, current_app, jsonify, request, session

from .audit import log_action
from .db import tx
from .rbac import requires_auth
from .validators import sanitize_text

bp = Blueprint("lab", __name__, url_prefix="/lab")

# ---------------------------------------------------------------------------
# App status (used by the home dashboard)
# ---------------------------------------------------------------------------

@bp.get("/status")
def status():
    with tx() as db:
        user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        event_count = db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
        locked_count = db.execute(
            "SELECT COUNT(*) FROM account_lockouts WHERE locked_until > datetime('now')"
        ).fetchone()[0]
        api_key_count = db.execute(
            "SELECT COUNT(*) FROM api_keys WHERE is_active = 1"
        ).fetchone()[0]

    return jsonify({
        "secure_mode": current_app.config.get("SECURE_MODE", True),
        "session_active": bool(session.get("user_id")),
        "username": session.get("username"),
        "role": session.get("role"),
        "stats": {
            "users": user_count,
            "events": event_count,
            "locked_accounts": locked_count,
            "active_api_keys": api_key_count,
        },
    })


# ---------------------------------------------------------------------------
# SQL Injection Lab
# ---------------------------------------------------------------------------

@bp.post("/sqli/attack")
@requires_auth
def sqli_attack():
    """INTENTIONALLY VULNERABLE — string-interpolated SQL query."""
    if current_app.config.get("SECURE_MODE", True):
        return jsonify({
            "blocked": True,
            "reason": "Insecure endpoint is disabled while SECURE_MODE=true.",
            "hint": "Set SECURE_MODE=false to enable this vulnerability for demo.",
        }), 403

    data = request.get_json(silent=True) or {}
    q = (data.get("query") or "").strip()[:500]

    # VULNERABLE: direct string interpolation into SQL
    sql = f"SELECT id, name, category, price, description FROM demo_products WHERE name LIKE '%{q}%'"

    try:
        with tx() as db:
            rows = db.execute(sql).fetchall()
        log_action("LAB_SQLI_ATTACK", details={"query": q, "rows": len(rows)}, success=True)
        return jsonify({
            "ok": True,
            "mode": "attack",
            "sql": sql,
            "results": [dict(r) for r in rows],
            "rows_returned": len(rows),
            "vulnerable": True,
        })
    except Exception as exc:
        return jsonify({
            "ok": False,
            "mode": "attack",
            "sql": sql,
            "error": str(exc),
            "vulnerable": True,
        })


@bp.post("/sqli/defend")
@requires_auth
def sqli_defend():
    """SECURE — parameterized query with input sanitization."""
    data = request.get_json(silent=True) or {}
    q = sanitize_text((data.get("query") or "").strip(), max_length=100)

    sql_template = (
        "SELECT id, name, category, price, description "
        "FROM demo_products WHERE name LIKE ?"
    )
    with tx() as db:
        rows = db.execute(sql_template, (f"%{q}%",)).fetchall()

    log_action("LAB_SQLI_DEFEND", details={"query": q, "rows": len(rows)})
    return jsonify({
        "ok": True,
        "mode": "defend",
        "sql_template": sql_template,
        "bound_params": [f"%{q}%"],
        "results": [dict(r) for r in rows],
        "rows_returned": len(rows),
        "vulnerable": False,
    })


# ---------------------------------------------------------------------------
# XSS Lab
# ---------------------------------------------------------------------------

@bp.post("/xss/attack")
def xss_attack():
    """INTENTIONALLY VULNERABLE — reflects input without sanitization."""
    if current_app.config.get("SECURE_MODE", True):
        return jsonify({
            "blocked": True,
            "reason": "Insecure reflection disabled in SECURE_MODE.",
        }), 403

    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()[:1000]
    log_action("LAB_XSS_ATTACK", details={"content_len": len(content)})
    return jsonify({
        "ok": True,
        "mode": "attack",
        "raw": content,
        "vulnerable": True,
        "note": "This content would be injected directly into innerHTML — script tags execute!",
    })


@bp.post("/xss/defend")
def xss_defend():
    """SECURE — HTML-escaped and tag-stripped output."""
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()[:1000]

    stripped = sanitize_text(content, max_length=1000)
    escaped = _html.escape(content)

    log_action("LAB_XSS_DEFEND")
    return jsonify({
        "ok": True,
        "mode": "defend",
        "original": content,
        "tags_stripped": stripped,
        "html_escaped": escaped,
        "vulnerable": False,
        "note": "Tags stripped + HTML entities escaped — nothing executes.",
    })


# ---------------------------------------------------------------------------
# Password Hashing Demo
# ---------------------------------------------------------------------------

@bp.post("/hash/demo")
def hash_demo():
    from werkzeug.security import check_password_hash, generate_password_hash

    data = request.get_json(silent=True) or {}
    password = (data.get("password") or "").strip()[:128]

    if not password:
        return jsonify({"error": "password required"}), 400

    hash1 = generate_password_hash(password)
    hash2 = generate_password_hash(password)
    algo = "scrypt" if hash1.startswith("scrypt:") else "pbkdf2:sha256"

    return jsonify({
        "password_shown": False,
        "hash_1": hash1,
        "hash_2": hash2,
        "same_input_different_hash": hash1 != hash2,
        "algorithm": algo,
        "verify_correct": check_password_hash(hash1, password),
        "verify_wrong": check_password_hash(hash1, password + "WRONG"),
        "note": "Each hash is unique due to a random salt — rainbow tables are useless.",
    })


# ---------------------------------------------------------------------------
# Security Headers Info
# ---------------------------------------------------------------------------

@bp.get("/headers/info")
def headers_info():
    secure = current_app.config.get("SESSION_COOKIE_SECURE", False)
    return jsonify({
        "response_headers": [
            {
                "name": "Content-Security-Policy",
                "value": "default-src 'self'; script-src 'self' 'nonce-{dynamic}'; ...",
                "status": "active",
                "severity": "critical",
                "description": "Allowlists which sources can load scripts, styles, images. A valid nonce is required for inline scripts — blocking injected <script> tags.",
                "attack_prevented": "Cross-Site Scripting (XSS)",
            },
            {
                "name": "X-Frame-Options",
                "value": "DENY",
                "status": "active",
                "severity": "high",
                "description": "Prevents this page from being embedded inside an <iframe>. Attackers use invisible iframes to trick users into clicking hidden buttons.",
                "attack_prevented": "Clickjacking",
            },
            {
                "name": "X-Content-Type-Options",
                "value": "nosniff",
                "status": "active",
                "severity": "medium",
                "description": "Stops the browser from guessing the content type of a response. Without this, a crafted upload could be executed as HTML/JS.",
                "attack_prevented": "MIME-type confusion attacks",
            },
            {
                "name": "X-XSS-Protection",
                "value": "1; mode=block",
                "status": "active",
                "severity": "low",
                "description": "Enables the built-in XSS auditor in older browsers. Modern browsers rely on CSP instead, but this header adds defence-in-depth.",
                "attack_prevented": "Reflected XSS (legacy browsers)",
            },
            {
                "name": "Referrer-Policy",
                "value": "strict-origin-when-cross-origin",
                "status": "active",
                "severity": "medium",
                "description": "Only sends the origin (not the full URL path) as the Referer when navigating cross-origin. Prevents leaking session tokens or user IDs embedded in URLs.",
                "attack_prevented": "URL-based information leakage",
            },
            {
                "name": "Permissions-Policy",
                "value": "geolocation=(), camera=(), microphone=()",
                "status": "active",
                "severity": "medium",
                "description": "Explicitly disables access to camera, microphone, and geolocation APIs. Even if an attacker injects JS, they cannot access these sensors.",
                "attack_prevented": "Sensor hijacking via injected scripts",
            },
            {
                "name": "Strict-Transport-Security",
                "value": "max-age=31536000; includeSubDomains",
                "status": "production-only" if not secure else "active",
                "severity": "high",
                "description": "Forces HTTPS for 1 year. Once a browser sees this header it will never connect over plain HTTP, preventing SSL stripping.",
                "attack_prevented": "Man-in-the-middle / SSL stripping",
            },
        ],
        "cookie_flags": [
            {
                "flag": "HttpOnly",
                "active": True,
                "description": "Session cookie is invisible to JavaScript. Even if XSS runs, document.cookie won't expose the session token.",
            },
            {
                "flag": "SameSite=Lax",
                "active": True,
                "description": "Cookie is not sent on cross-site POST requests. Stops CSRF attacks from forging authenticated requests.",
            },
            {
                "flag": "Secure",
                "active": secure,
                "description": "Cookie only transmitted over HTTPS. Enabled automatically in production (FLASK_ENV=production).",
            },
        ],
    })


# ---------------------------------------------------------------------------
# Rate Limit Test
# ---------------------------------------------------------------------------

@bp.post("/rate/test")
@requires_auth
def rate_test():
    log_action("LAB_RATE_TEST")
    return jsonify({
        "ok": True,
        "message": "Request accepted.",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        "user": session.get("username"),
    })


# ---------------------------------------------------------------------------
# Live Events Feed
# ---------------------------------------------------------------------------

@bp.get("/events")
@requires_auth
def lab_events():
    with tx() as db:
        rows = db.execute(
            """
            SELECT user_id, username, action, resource, ip_address, timestamp, success
            FROM   audit_logs
            ORDER  BY id DESC LIMIT 30
            """
        ).fetchall()
    return jsonify({"events": [dict(r) for r in rows]})
