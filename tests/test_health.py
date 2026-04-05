from fastapi.testclient import TestClient

from recipe_app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
