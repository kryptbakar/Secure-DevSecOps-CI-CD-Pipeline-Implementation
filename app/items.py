from __future__ import annotations

import datetime as _dt

from flask import Blueprint, current_app, g, jsonify, request, session

from .audit import log_action
from .db import tx
from .rbac import requires_auth


def _uid() -> int:
    """Return the authenticated user's ID from session or API key."""
    return session.get("user_id") or getattr(g, "api_user", {}).get("id")
from .validators import (
    ValidationError,
    validate_item_body,
    validate_item_title,
    validate_search_query,
)

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.get("")
@requires_auth
def list_items():
    uid = _uid()
    with tx() as db:
        rows = db.execute(
            "SELECT id, title, body, created_at FROM items WHERE user_id = ? ORDER BY id DESC",
            (uid,),
        ).fetchall()
    return jsonify({"items": [dict(r) for r in rows]})


@bp.post("")
@requires_auth
def create_item():
    uid = _uid()
    data = request.get_json(silent=True) or {}

    try:
        title = validate_item_title(data.get("title") or "")
        body = validate_item_body(data.get("body") or "")
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400

    now = _dt.datetime.now(_dt.UTC).isoformat().replace("+00:00", "Z")
    with tx() as db:
        cur = db.execute(
            "INSERT INTO items (user_id, title, body, created_at) VALUES (?,?,?,?)",
            (uid, title, body, now),
        )
        item_id = cur.lastrowid

    log_action("ITEM_CREATE", resource=f"item:{item_id}", details={"title": title})
    return jsonify({"ok": True, "item": {"id": item_id, "title": title, "body": body}}), 201


@bp.put("/<int:item_id>")
@requires_auth
def update_item(item_id: int):
    uid = _uid()
    data = request.get_json(silent=True) or {}

    try:
        title = validate_item_title(data.get("title") or "")
        body = validate_item_body(data.get("body") or "")
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400

    with tx() as db:
        row = db.execute(
            "SELECT id FROM items WHERE id = ? AND user_id = ?", (item_id, uid)
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        db.execute(
            "UPDATE items SET title = ?, body = ? WHERE id = ? AND user_id = ?",
            (title, body, item_id, uid),
        )

    log_action("ITEM_UPDATE", resource=f"item:{item_id}")
    return jsonify({"ok": True})


@bp.delete("/<int:item_id>")
@requires_auth
def delete_item(item_id: int):
    uid = _uid()
    with tx() as db:
        cur = db.execute(
            "DELETE FROM items WHERE id = ? AND user_id = ?", (item_id, uid)
        )

    if cur.rowcount == 0:
        return jsonify({"error": "not found"}), 404

    log_action("ITEM_DELETE", resource=f"item:{item_id}")
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Dual search endpoints (teaching feature)
# ---------------------------------------------------------------------------

@bp.get("/search_secure")
@requires_auth
def search_secure():
    """SECURE: parameterized query + input validation. Always available."""
    uid = _uid()

    try:
        q = validate_search_query(request.args.get("q") or "")
    except ValidationError as e:
        return jsonify({"error": e.message}), 400

    with tx() as db:
        rows = db.execute(
            "SELECT id, title, body, created_at FROM items "
            "WHERE user_id = ? AND title LIKE ? ORDER BY id DESC",
            (uid, f"%{q}%"),
        ).fetchall()

    return jsonify({
        "items": [dict(r) for r in rows],
        "mode": "secure",
        "note": "Parameterized query + input validation. No SQL injection possible.",
    })


@bp.get("/search_insecure")
@requires_auth
def search_insecure():
    """INTENTIONALLY VULNERABLE to SQL injection — available only when SECURE_MODE=false."""
    if current_app.config.get("SECURE_MODE", True):
        return jsonify({
            "error": "This vulnerable endpoint is disabled in SECURE_MODE.",
            "hint": "Set environment variable SECURE_MODE=false to enable for demos.",
        }), 403

    uid = _uid()
    q = (request.args.get("q") or "").strip()

    # VULNERABLE: direct string interpolation — classic SQL injection vector
    sql = (
        f"SELECT id, title, body, created_at FROM items "
        f"WHERE user_id = {uid} AND title LIKE '%{q}%'"
    )

    with tx() as db:
        try:
            rows = db.execute(sql).fetchall()
        except Exception as exc:
            return jsonify({"error": str(exc), "sql": sql}), 500

    return jsonify({
        "items": [dict(r) for r in rows],
        "mode": "insecure",
        "sql": sql,
        "warning": "DEMO ONLY — intentionally vulnerable to SQL injection.",
    })


@bp.get("/search")
@requires_auth
def search_items():
    """Alias for search_secure (default safe behaviour)."""
    return search_secure()
