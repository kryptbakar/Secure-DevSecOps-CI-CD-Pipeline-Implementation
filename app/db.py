import sqlite3
from contextlib import contextmanager

from flask import g
from werkzeug.security import generate_password_hash


def init_db(app, database_path: str) -> None:
    """Initialize database schema and wire per-request connection lifecycle."""

    def get_conn() -> sqlite3.Connection:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                username         TEXT    UNIQUE NOT NULL,
                password_hash    TEXT    NOT NULL,
                role             TEXT    NOT NULL DEFAULT 'user',
                is_active        INTEGER NOT NULL DEFAULT 1,
                created_at       TEXT    NOT NULL,
                last_login       TEXT,
                email            TEXT,
                phone            TEXT,
                address          TEXT,
                notes            TEXT
            );

            CREATE TABLE IF NOT EXISTS items (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                body       TEXT,
                created_at TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS account_lockouts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT    UNIQUE NOT NULL,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until    TEXT,
                last_attempt    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS api_keys (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                key_hash   TEXT    UNIQUE NOT NULL,
                key_prefix TEXT    NOT NULL,
                name       TEXT,
                created_at TEXT    NOT NULL,
                last_used  TEXT,
                is_active  INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                username   TEXT,
                action     TEXT    NOT NULL,
                resource   TEXT,
                ip_address TEXT,
                user_agent TEXT,
                details    TEXT,
                timestamp  TEXT    NOT NULL,
                success    INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS demo_products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                price       REAL    NOT NULL,
                description TEXT
            );
            """
        )

        # Seed demo products if the table is empty
        if conn.execute("SELECT COUNT(*) FROM demo_products").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO demo_products (name, category, price, description) VALUES (?,?,?,?)",
                [
                    ("iPhone 15 Pro",           "Smartphones", 999.00,  "Apple flagship with titanium frame and A17 Pro chip"),
                    ("MacBook Air M3",           "Laptops",    1299.00,  "Fanless Apple silicon laptop, 18-hour battery"),
                    ("Samsung Galaxy S24",       "Smartphones",  799.00, "Android flagship with Galaxy AI features"),
                    ("Sony WH-1000XM5",          "Audio",        349.00, "Industry-leading noise cancelling headphones"),
                    ("AirPods Pro 2nd Gen",      "Audio",        249.00, "Apple earbuds with adaptive transparency"),
                    ("Dell XPS 15",              "Laptops",     1599.00, "OLED 4K display, Intel Core i9, RTX 4060"),
                    ("iPad Pro M4",              "Tablets",     1099.00, "Ultra-thin Apple tablet with M4 chip"),
                    ("Google Pixel 8",           "Smartphones",  699.00, "Pure Android, 7 years of updates, Tensor G3"),
                    ("Bose QuietComfort 45",     "Audio",        279.00, "Comfortable ANC headphones, 24h battery"),
                    ("Microsoft Surface Pro 9",  "Tablets",      999.00, "Detachable Windows 11 Pro tablet with LTE option"),
                ],
            )
        
        # Add profile columns if they don't exist (safe migration)
        def column_exists(table: str, column: str) -> bool:
            r = conn.execute(f"PRAGMA table_info({table})").fetchall()
            return any(col[1] == column for col in r)
        
        if not column_exists("users", "email"):
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if not column_exists("users", "phone"):
            conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        if not column_exists("users", "address"):
            conn.execute("ALTER TABLE users ADD COLUMN address TEXT")
        if not column_exists("users", "notes"):
            conn.execute("ALTER TABLE users ADD COLUMN notes TEXT")
        
        # Seed demo users for IDOR lab if the table is empty
        import datetime
        now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            # Create demo users with profile data for IDOR testing
            demo_users = [
                {
                    "username": "alice",
                    "password": "Alice@1234",
                    "email": "alice@example.com",
                    "phone": "+1-555-0101",
                    "address": "123 Main St, Springfield, IL 62701",
                    "notes": "Alice's private notes - confidential project planning",
                },
                {
                    "username": "bob",
                    "password": "Bob@1234",
                    "email": "bob@example.com",
                    "phone": "+1-555-0102",
                    "address": "456 Oak Ave, Portland, OR 97201",
                    "notes": "Bob's notes - upcoming interview schedule",
                },
                {
                    "username": "charlie",
                    "password": "Charlie@1234",
                    "email": "charlie@example.com",
                    "phone": "+1-555-0103",
                    "address": "789 Pine Rd, Denver, CO 80202",
                    "notes": "Charlie's notes - sensitive customer data",
                },
                {
                    "username": "diana",
                    "password": "Diana@1234",
                    "email": "diana@example.com",
                    "phone": "+1-555-0104",
                    "address": "321 Elm St, Austin, TX 78701",
                    "notes": "Diana's notes - personal financial records",
                },
            ]
            
            for user in demo_users:
                password_hash = generate_password_hash(user["password"])
                conn.execute(
                    "INSERT INTO users (username, password_hash, role, created_at, email, phone, address, notes) VALUES (?,?,?,?,?,?,?,?)",
                    (user["username"], password_hash, "user", now, user["email"], user["phone"], user["address"], user["notes"]),
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
def tx():
    """Yield the request-bound connection; commit on success, rollback on error."""
    db = g.db
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
