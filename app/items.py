from __future__ import annotations

import datetime as _dt

from flask import Blueprint, jsonify, request, session

from .db import tx

bp = Blueprint("items", __name__, url_prefix="/items")


def _require_user() -> int | None:
    uid = session.get("user_id")
    return int(uid) if uid is not None else None


@bp.get("")
def list_items():
    uid = _require_user()
    if not uid:
        return jsonify({"error": "auth required"}), 401

    with tx() as db:
        rows = db.execute(
            "SELECT id, title, body, created_at FROM items WHERE user_id = ? ORDER BY id DESC",
            (uid,),
        ).fetchall()

    return jsonify({"items": [dict(r) for r in rows]})


@bp.post("")
def create_item():
    uid = _require_user()
    if not uid:
        return jsonify({"error": "auth required"}), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    body = data.get("body") or ""

    if not title:
        return jsonify({"error": "title required"}), 400

    now = _dt.datetime.now(_dt.UTC).isoformat().replace("+00:00", "Z")

    with tx() as db:
        cur = db.execute(
            "INSERT INTO items (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
            (uid, title, body, now),
        )
        item_id = cur.lastrowid

    return jsonify({"ok": True, "item": {"id": item_id, "title": title, "body": body}}), 201


@bp.put("/<int:item_id>")
def update_item(item_id: int):
    uid = _require_user()
    if not uid:
        return jsonify({"error": "auth required"}), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    body = data.get("body") or ""

    with tx() as db:
        row = db.execute(
            "SELECT id FROM items WHERE id = ? AND user_id = ?", (item_id, uid)
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        db.execute(
            (
                "UPDATE items SET title = COALESCE(NULLIF(?, ''), title), "
                "body = ? "
                "WHERE id = ? AND user_id = ?"
            ),
            (title, body, item_id, uid),
        )

    return jsonify({"ok": True})


@bp.delete("/<int:item_id>")
def delete_item(item_id: int):
    uid = _require_user()
    if not uid:
        return jsonify({"error": "auth required"}), 401

    with tx() as db:
        cur = db.execute(
            "DELETE FROM items WHERE id = ? AND user_id = ?",
            (item_id, uid),
        )

    if cur.rowcount == 0:
        return jsonify({"error": "not found"}), 404

    return jsonify({"ok": True})


@bp.get("/search")
def search_items():
    """Intentionally insecure search endpoint (SQL injection risk).

    This is included as a *vulnerable-by-design* example for the course.
    """

    uid = _require_user()
    if not uid:
        return jsonify({"error": "auth required"}), 401

    q = (request.args.get("q") or "").strip()

    # Vulnerability (intended): string concatenation into SQL.
    # Bandit may not always flag this; it is here for demonstration/discussion.
    sql = (
        "SELECT id, title, body, created_at FROM items "
        f"WHERE user_id = {uid} AND title LIKE '%{q}%' ORDER BY id DESC"
    )

    with tx() as db:
        rows = db.execute(sql).fetchall()

    return jsonify({"items": [dict(r) for r in rows], "note": "insecure query demo"})
