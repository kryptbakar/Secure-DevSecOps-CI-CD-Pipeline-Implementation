import pytest
from app.main import create_app
from app.db import init_db
import os

@pytest.fixture
def client():
    app = create_app()
    # Override config for testing
    app.config.update({
        "TESTING": True,
        "DATABASE_PATH": "test_app.db"
    })
    
    # Init test DB
    with app.app_context():
        init_db(app, "test_app.db")

    with app.test_client() as client:
        yield client

    # Cleanup test DB
    if os.path.exists("test_app.db"):
        os.remove("test_app.db")

def test_health_endpoint(client):
    """Test that the health endpoint is working correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

def test_api_info_endpoint(client):
    """Test that the API info endpoint returns correct status."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "name" in data
