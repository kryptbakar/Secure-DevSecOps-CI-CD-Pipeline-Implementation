from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Intentionally hardcoded secret (educational / vulnerable-by-design).
    SECRET_KEY: str = "devsecops-demo-hardcoded-secret"

    # Local SQLite database file.
    DATABASE_PATH: str = "app.db"
