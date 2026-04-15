import os
import tempfile

import pytest

# Set required env vars before any app import so Config picks them up
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("SECURE_MODE", "true")


@pytest.fixture(scope="function")
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_PATH"] = db_path

    from app.main import create_app

    application = create_app()
    application.config.update(
        TESTING=True,
        RATELIMIT_ENABLED=False,  # disable rate limiting in tests
        WTF_CSRF_ENABLED=False,
    )

    yield application

    os.close(db_fd)
    os.unlink(db_path)
    # Reset so next fixture call gets a fresh DB path
    os.environ.pop("DATABASE_PATH", None)


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def insecure_app():
    """App with SECURE_MODE=false for testing insecure endpoints."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_PATH"] = db_path
    os.environ["SECURE_MODE"] = "false"

    from app.main import create_app

    application = create_app()
    application.config.update(TESTING=True, RATELIMIT_ENABLED=False)

    yield application

    os.close(db_fd)
    os.unlink(db_path)
    os.environ["SECURE_MODE"] = "true"
    os.environ.pop("DATABASE_PATH", None)


@pytest.fixture(scope="function")
def insecure_client(insecure_app):
    return insecure_app.test_client()


# ---------------------------------------------------------------------------
# Helpers shared across test modules
# ---------------------------------------------------------------------------

VALID_USER = {"username": "testuser", "password": "Password1!"}
ADMIN_USER = {"username": "adminuser", "password": "Admin123!"}


def register(client, username, password):
    return client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )


def login(client, username, password):
    return client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )


def register_and_login(client, creds=None):
    creds = creds or VALID_USER
    register(client, creds["username"], creds["password"])
    resp = login(client, creds["username"], creds["password"])
    return resp.get_json()
