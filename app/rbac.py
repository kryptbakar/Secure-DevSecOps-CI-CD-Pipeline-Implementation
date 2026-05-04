from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request, session

from .audit import log_action


def _try_api_key_auth() -> bool:
    """Check for a Bearer token and authenticate via API key. Returns True on success."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return False
    from .api_keys import _lookup_user  # local import avoids circular dependency
    user = _lookup_user(header[7:])
    if user:
        g.api_user = user
        return True
    return False


def requires_auth(f):
    """Require a valid session OR a valid API key (Bearer token)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            if not getattr(g, "api_user", None):
                _try_api_key_auth()
            if not session.get("user_id") and not getattr(g, "api_user", None):
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
