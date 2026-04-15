import sqlite3
from contextlib import contextmanager

from flask import g


def init_db(app, database_path: str) -> None:
    """Initialize database and create tables if they do not exist."""

    def get_conn() -> sqlite3.Connection:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        return conn

    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )
        conn.commit()

    @app.before_request
    def _open_db():
        if "db" not in g:
            g.db = get_conn()

    @app.teardown_request
    def _close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()


@contextmanager
def tx() -> sqlite3.Connection:
    """Return the request-bound sqlite connection."""
    db = g.db
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
