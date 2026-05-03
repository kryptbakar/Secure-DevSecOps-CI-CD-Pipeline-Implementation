from __future__ import annotations

import datetime
import json

from flask import g, request, session


def log_action(
    action: str,
    resource: str | None = None,
    details: dict | None = None,
    success: bool = True,
    user_id: int | None = None,
    username: str | None = None,
) -> None:
    """Write one audit log entry. Silently swallows errors so it never breaks the app."""
    now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
    uid = user_id if user_id is not None else session.get("user_id")
    uname = username or session.get("username")
    ip = request.remote_addr
    ua = (request.headers.get("User-Agent") or "")[:256]
    details_json = json.dumps(details) if details else None

    try:
        db = g.db
        db.execute(
            """
            INSERT INTO audit_logs
                (user_id, username, action, resource, ip_address, user_agent, details, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (uid, uname, action, resource, ip, ua, details_json, now, int(success)),
        )
        db.commit()
    except Exception:
        pass
