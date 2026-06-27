from app.main import app
from fastapi.testclient import TestClient


def test_health_check_returns_http_200() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
