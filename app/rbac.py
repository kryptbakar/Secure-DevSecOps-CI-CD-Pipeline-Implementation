from __future__ import annotations

from functools import wraps

from flask import g, jsonify, session

from .audit import log_action


def requires_auth(f):
    """Require a valid session (any role)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            # Also allow API-key-authenticated requests (set by api_key_auth decorator)
            if not getattr(g, "api_user", None):
                return jsonify({"error": "authentication required"}), 401
        return f(*args, **kwargs)

    return decorated


def requires_role(*roles: str):
    """Require the user to hold one of the named roles."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            uid = session.get("user_id")
            api_user = getattr(g, "api_user", None)

            if not uid and not api_user:
                return jsonify({"error": "authentication required"}), 401

            user_role = session.get("role") or (api_user or {}).get("role", "user")

            if user_role not in roles:
                log_action(
                    "ACCESS_DENIED",
                    resource=f.__name__,
                    success=False,
                    details={"required": list(roles), "actual": user_role},
                )
                return jsonify({"error": "insufficient privileges"}), 403

            return f(*args, **kwargs)

        return decorated

    return decorator
