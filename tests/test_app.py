"""Functional tests — basic app behaviour."""
import pytest
from tests.conftest import VALID_USER, login, register, register_and_login


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert "timestamp" in data


def test_api_info(client):
    r = client.get("/api")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------

def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in r.headers
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]


# ---------------------------------------------------------------------------
# Auth — registration
# ---------------------------------------------------------------------------

def test_register_success(client):
    r = register(client, "alice", "Secure1!")
    assert r.status_code == 201
    assert r.get_json()["ok"] is True


def test_register_duplicate(client):
    register(client, "alice", "Secure1!")
    r = register(client, "alice", "Secure1!")
    assert r.status_code == 409


def test_register_weak_password(client):
    r = register(client, "alice", "short")
    assert r.status_code == 400
    assert "field" in r.get_json()


def test_register_invalid_username(client):
    r = register(client, "a", "Secure1!")          # too short
    assert r.status_code == 400
    r2 = register(client, "user name", "Secure1!") # space not allowed
    assert r2.status_code == 400


# ---------------------------------------------------------------------------
# Auth — login
# ---------------------------------------------------------------------------

def test_login_success(client):
    register(client, **VALID_USER)
    r = login(client, **VALID_USER)
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert "csrf_token" in data
    assert data["user"]["username"] == VALID_USER["username"]


def test_login_wrong_password(client):
    register(client, **VALID_USER)
    r = login(client, VALID_USER["username"], "WrongPass1!")
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = login(client, "nobody", "Password1!")
    assert r.status_code == 401


def test_logout(client):
    register_and_login(client)
    r = client.post("/auth/logout")
    assert r.status_code == 200
    # After logout, /auth/me should be 401
    r2 = client.get("/auth/me")
    assert r2.status_code == 401


def test_me_authenticated(client):
    register_and_login(client)
    r = client.get("/auth/me")
    assert r.status_code == 200
    assert r.get_json()["user"]["username"] == VALID_USER["username"]


# ---------------------------------------------------------------------------
# Items — CRUD
# ---------------------------------------------------------------------------

def test_items_require_auth(client):
    r = client.get("/items")
    assert r.status_code == 401


def test_create_and_list_item(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "Hello", "body": "World"})
    assert r.status_code == 201

    r2 = client.get("/items")
    assert r2.status_code == 200
    items = r2.get_json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Hello"


def test_delete_item(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "ToDelete"})
    item_id = r.get_json()["item"]["id"]

    r2 = client.delete(f"/items/{item_id}")
    assert r2.status_code == 200

    r3 = client.get("/items")
    assert r3.get_json()["items"] == []


def test_update_item(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "Old"})
    item_id = r.get_json()["item"]["id"]

    r2 = client.put(f"/items/{item_id}", json={"title": "New", "body": "Updated"})
    assert r2.status_code == 200


def test_delete_other_users_item_fails(client):
    """User A cannot delete User B's item."""
    register(client, "userA", "Password1!")
    login(client, "userA", "Password1!")
    r = client.post("/items", json={"title": "Mine"})
    item_id = r.get_json()["item"]["id"]
    client.post("/auth/logout")

    register(client, "userB", "Password2!")
    login(client, "userB", "Password2!")
    r2 = client.delete(f"/items/{item_id}")
    assert r2.status_code == 404


# ---------------------------------------------------------------------------
# Items — input validation
# ---------------------------------------------------------------------------

def test_create_item_empty_title(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "", "body": "body"})
    assert r.status_code == 400


def test_create_item_strips_html(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "<script>alert(1)</script>Safe Title"})
    # Should succeed; the title stored should not contain the script tag
    assert r.status_code == 201
    stored_title = r.get_json()["item"]["title"]
    assert "<script>" not in stored_title


# ---------------------------------------------------------------------------
# Secure search
# ---------------------------------------------------------------------------

def test_search_secure(client):
    register_and_login(client)
    client.post("/items", json={"title": "apple pie"})
    client.post("/items", json={"title": "banana bread"})

    r = client.get("/items/search_secure?q=apple")
    assert r.status_code == 200
    items = r.get_json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "apple pie"


def test_search_insecure_blocked_in_secure_mode(client):
    register_and_login(client)
    r = client.get("/items/search_insecure?q=test")
    assert r.status_code == 403
