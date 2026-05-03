from __future__ import annotations

import re


class ValidationError(Exception):
    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.field = field


_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")

# Patterns that signal SQL injection attempts (block even on secure endpoints)
_SQL_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"'.*--",
        r";\s*drop\b",
        r";\s*delete\b",
        r";\s*insert\b",
        r"\bunion\b.*\bselect\b",
        r"\bexec\s*\(",
        r"\bxp_\w+",
    ]
]


def _strip_tags(text: str) -> str:
    """Remove HTML/XML tags from text without requiring bleach."""
    try:
        import bleach
        return bleach.clean(text, tags=[], strip=True)
    except ImportError:
        return re.sub(r"<[^>]+>", "", text)


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Strip HTML tags, remove null bytes, and enforce max length."""
    if not isinstance(text, str):
        raise ValidationError("Expected string input")
    cleaned = _strip_tags(text).replace("\x00", "")
    return cleaned[:max_length]


def validate_username(username: str) -> str:
    username = username.strip()
    if not username:
        raise ValidationError("Username is required", "username")
    if not _USERNAME_RE.match(username):
        raise ValidationError(
            "Username must be 3–32 characters: letters, digits, and underscores only",
            "username",
        )
    return username


def validate_password(password: str) -> str:
    if not password:
        raise ValidationError("Password is required", "password")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters", "password")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter", "password")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter", "password")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit", "password")
    if not re.search(r"[@$!%*?&]", password):
        raise ValidationError(
            "Password must contain at least one special character: @$!%*?&",
            "password",
        )
    return password


def validate_item_title(title: str) -> str:
    title = sanitize_text((title or "").strip(), max_length=200)
    if not title:
        raise ValidationError("Title is required", "title")
    return title


def validate_item_body(body: str) -> str:
    return sanitize_text(body or "", max_length=10_000)


def validate_search_query(q: str) -> str:
    q = sanitize_text((q or "").strip(), max_length=100)
    for pattern in _SQL_INJECTION_PATTERNS:
        if pattern.search(q):
            raise ValidationError("Invalid search query", "q")
    return q
