from __future__ import annotations

import datetime
import hashlib
import secrets
from functools import wraps

from flask import Blueprint, g, jsonify, request, session

from .audit import log_action
from .db import tx
from .rbac import requires_auth

bp = Blueprint("api_keys", __name__, url_prefix="/api-keys")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def generate_api_key(user_id: int, name: str | None = None) -> str:
    """Create a new API key. Returns the raw key — store it, it won't be shown again."""
    raw = "sk_" + secrets.token_urlsafe(32)
    with tx() as db:
        db.execute(
            "INSERT INTO api_keys (user_id, key_hash, key_prefix, name, created_at) VALUES (?,?,?,?,?)",
            (user_id, _hash_key(raw), raw[:10], name, _now()),
        )
    log_action("API_KEY_CREATED", details={"name": name, "prefix": raw[:10]})
    return raw


def revoke_api_key(key_id: int, user_id: int) -> bool:
    with tx() as db:
        cur = db.execute(
            "UPDATE api_keys SET is_active=0 WHERE id=? AND user_id=?",
            (key_id, user_id),
        )
    return cur.rowcount > 0


def _lookup_user(raw_key: str) -> dict | None:
    """Resolve a raw API key to its owner; update last_used timestamp."""
    key_hash = _hash_key(raw_key)
    with tx() as db:
        row = db.execute(
            """
            SELECT u.id, u.username, u.role, ak.id AS key_id
            FROM   api_keys ak
            JOIN   users u ON u.id = ak.user_id
            WHERE  ak.key_hash = ? AND ak.is_active = 1 AND u.is_active = 1
            """,
            (key_hash,),
        ).fetchone()
        if row:
            db.execute(
                "UPDATE api_keys SET last_used=? WHERE id=?",
                (_now(), row["key_id"]),
            )
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------


def api_key_auth(f):
    """Authenticate via `Authorization: Bearer <api-key>` header."""

    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return (
                jsonify({"error": "API key required — Authorization: Bearer <key>"}),
                401,
            )

        user = _lookup_user(header[7:])
        if not user:
            log_action("API_KEY_AUTH_FAILED", success=False)
            return jsonify({"error": "invalid or revoked API key"}), 401

        g.api_user = user
        log_action("API_KEY_AUTH", user_id=user["id"], username=user["username"])
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# CRUD blueprint
# ---------------------------------------------------------------------------


@bp.get("")
@requires_auth
def list_keys():
    uid = session["user_id"]
    with tx() as db:
        rows = db.execute(
            "SELECT id, key_prefix, name, created_at, last_used, is_active FROM api_keys WHERE user_id=?",
            (uid,),
        ).fetchall()
    return jsonify({"api_keys": [dict(r) for r in rows]})


@bp.post("")
@requires_auth
def create_key():
    uid = session["user_id"]
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "unnamed")[:100]
    raw = generate_api_key(uid, name)
    return (
        jsonify(
            {
                "ok": True,
                "key": raw,
                "prefix": raw[:10],
                "warning": "Store this key safely — it will NOT be shown again.",
            }
        ),
        201,
    )


@bp.delete("/<int:key_id>")
@requires_auth
def delete_key(key_id: int):
    uid = session["user_id"]
    if not revoke_api_key(key_id, uid):
        return jsonify({"error": "key not found"}), 404
    log_action("API_KEY_REVOKED", resource=f"key:{key_id}")
    return jsonify({"ok": True})
