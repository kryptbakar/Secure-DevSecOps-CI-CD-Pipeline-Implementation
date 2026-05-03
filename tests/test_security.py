"""Security-focused tests — injection, auth bypass, lockout, RBAC, input validation."""
import pytest
from tests.conftest import login, register, register_and_login

# ---------------------------------------------------------------------------
# SQL injection — secure endpoint must resist all payloads
# ---------------------------------------------------------------------------

SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "'; DROP TABLE items; --",
    "' UNION SELECT id, username, password_hash, created_at FROM users --",
    "1' AND SLEEP(5) --",
    "admin'--",
]


@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
def test_secure_search_resists_sql_injection(client, payload):
    """Parameterized query must return 0 results, not crash or leak data."""
    register_and_login(client)
    client.post("/items", json={"title": "legitimate item"})

    r = client.get(f"/items/search_secure?q={payload}")
    # Should not error out
    assert r.status_code in (200, 400)
    if r.status_code == 200:
        data = r.get_json()
        # Must not return rows matching the injection pattern
        for item in data.get("items", []):
            assert item["title"] == "legitimate item"


def test_insecure_search_available_when_secure_mode_off(insecure_client):
    """Insecure endpoint should be reachable when SECURE_MODE=false."""
    register_and_login(insecure_client)
    r = insecure_client.get("/items/search_insecure?q=test")
    assert r.status_code == 200
    assert r.get_json()["mode"] == "insecure"


def test_insecure_search_blocked_in_secure_mode(client):
    register_and_login(client)
    r = client.get("/items/search_insecure?q=test")
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Auth bypass attempts
# ---------------------------------------------------------------------------

def test_unauthenticated_items_list(client):
    r = client.get("/items")
    assert r.status_code == 401


def test_unauthenticated_item_create(client):
    r = client.post("/items", json={"title": "x"})
    assert r.status_code == 401


def test_unauthenticated_search(client):
    r = client.get("/items/search_secure?q=x")
    assert r.status_code == 401


def test_unauthenticated_dashboard(client):
    r = client.get("/dashboard/security")
    assert r.status_code == 401


def test_non_admin_dashboard_blocked(client):
    register_and_login(client)   # registers with default 'user' role
    r = client.get("/dashboard/security")
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Account lockout & exponential backoff
# ---------------------------------------------------------------------------

def test_account_lockout_after_max_attempts(app, client):
    """After MAX_LOGIN_ATTEMPTS failures the account must be locked."""
    max_attempts = app.config["MAX_LOGIN_ATTEMPTS"]
    register(client, "victim", "Correct1!")

    for _ in range(max_attempts):
        r = login(client, "victim", "WrongPass1!")
        # Each should be 401 until locked
        assert r.status_code in (401, 429)

    # Next attempt should be 429 (locked) or 401
    r = login(client, "victim", "WrongPass1!")
    assert r.status_code in (429, 401)

    # Even correct password should be blocked while locked
    r = login(client, "victim", "Correct1!")
    assert r.status_code in (429, 401)


def test_correct_login_clears_lockout_counter(client):
    """A successful login resets the failure counter."""
    register(client, "bob", "Correct1!")

    # Fail twice (below lockout threshold)
    login(client, "bob", "Wrong1!")
    login(client, "bob", "Wrong1!")

    # Succeed
    r = login(client, "bob", "Correct1!")
    assert r.status_code == 200

    # Subsequent failures should start the counter fresh
    r2 = login(client, "bob", "Wrong1!")
    assert r2.status_code == 401


# ---------------------------------------------------------------------------
# Password policy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("password,expected_status", [
    ("short",        400),   # too short
    ("alllowercase1!", 400), # no uppercase
    ("ALLUPPERCASE1!", 400), # no lowercase
    ("NoDigitHere!",  400),  # no digit
    ("NoSpecial1",    400),  # no special char
    ("Valid1Pass!",   201),  # valid
])
def test_password_policy(client, password, expected_status):
    r = register(client, "pwtest", password)
    assert r.status_code == expected_status


# ---------------------------------------------------------------------------
# Input validation / sanitisation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("title", [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
])
def test_xss_payloads_stripped_from_title(client, title):
    register_and_login(client)
    r = client.post("/items", json={"title": title + " safe"})
    # Request should succeed or fail gracefully — never echo raw script tags
    if r.status_code == 201:
        stored = r.get_json()["item"]["title"]
        assert "<script>" not in stored
        assert "onerror" not in stored


def test_null_byte_in_title_stripped(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "hello\x00world"})
    if r.status_code == 201:
        assert "\x00" not in r.get_json()["item"]["title"]


def test_empty_json_body(client):
    register_and_login(client)
    r = client.post("/items", data="not json", content_type="text/plain")
    assert r.status_code in (400, 415)


def test_missing_title_field(client):
    register_and_login(client)
    r = client.post("/items", json={"body": "no title here"})
    assert r.status_code == 400


def test_oversized_title_rejected(client):
    register_and_login(client)
    r = client.post("/items", json={"title": "A" * 300})
    # Either 400 (rejected) or 201 (truncated to 200) — never store > 200 chars
    if r.status_code == 201:
        assert len(r.get_json()["item"]["title"]) <= 200


# ---------------------------------------------------------------------------
# Username validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("username", [
    "ab",            # too short
    "a" * 33,        # too long
    "user name",     # space
    "user@name",     # @ not allowed
    "../etc/passwd", # path traversal attempt
])
def test_invalid_usernames_rejected(client, username):
    r = register(client, username, "Valid1Pass!")
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Session behaviour
# ---------------------------------------------------------------------------

def test_session_cleared_on_logout(client):
    register_and_login(client)
    client.post("/auth/logout")
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_csrf_token_returned_on_login(client):
    register_and_login(client)
    data = login(client, **{"username": "testuser", "password": "Password1!"}).get_json()
    # login fixture already logged in; just verify token structure
    # (re-login may get 200 because session was already live)
    r = client.get("/auth/csrf")
    assert r.status_code == 200
    assert "csrf_token" in r.get_json()


# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------

def test_create_and_list_api_key(client):
    register_and_login(client)
    r = client.post("/api-keys", json={"name": "test-key"})
    assert r.status_code == 201
    data = r.get_json()
    assert "key" in data
    assert data["key"].startswith("sk_")

    r2 = client.get("/api-keys")
    assert r2.status_code == 200
    assert len(r2.get_json()["api_keys"]) == 1


def test_revoke_api_key(client):
    register_and_login(client)
    r = client.post("/api-keys", json={"name": "to-revoke"})
    key_id = r.get_json()  # contains ok, key, prefix
    # get the id from the list
    keys = client.get("/api-keys").get_json()["api_keys"]
    kid = keys[0]["id"]

    r2 = client.delete(f"/api-keys/{kid}")
    assert r2.status_code == 200


def test_api_key_auth(client):
    register_and_login(client)
    raw_key = client.post("/api-keys", json={"name": "bearer"}).get_json()["key"]
    client.post("/auth/logout")

    r = client.get("/items", headers={"Authorization": f"Bearer {raw_key}"})
    assert r.status_code == 200


def test_invalid_api_key_rejected(client):
    r = client.get("/items", headers={"Authorization": "Bearer sk_invalid_key_value"})
    assert r.status_code == 401


def test_api_keys_require_auth(client):
    r = client.get("/api-keys")
    assert r.status_code == 401
