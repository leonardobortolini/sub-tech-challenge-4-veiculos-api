from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app

client = TestClient(app)


def test_health_check_success(monkeypatch):
    def mock_connect():
        return None

    monkeypatch.setattr(
        "app.main.engine.connect",
        mock_connect,
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "veiculos-api",
        "database": "connected",
    }


def test_health_check_database_error(monkeypatch):
    def mock_connect():
        raise SQLAlchemyError("Database unavailable")

    monkeypatch.setattr(
        "app.main.engine.connect",
        mock_connect,
    )

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"]["database"] == "disconnected"