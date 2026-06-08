from __future__ import annotations

from fastapi.testclient import TestClient

from api_project.app.main import app


client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["record_count"] == 500_000


def test_existing_user_returns_prediction() -> None:
    response = client.get("/prediction/client_000001")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "client_000001"
    assert body["prediction_label"] in (0, 1)
    assert 0.0 <= body["prediction_score"] <= 1.0
    assert body["model_version"] == "bank_marketing_mock_v1"
    for field in ("request_id", "trace_id", "timestamp", "scored_at"):
        assert field in body


def test_missing_user_returns_404() -> None:
    response = client.get("/prediction/client_missing")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "USER_NOT_FOUND"
    assert "client_missing" in body["message"]
    for field in ("request_id", "trace_id", "timestamp"):
        assert field in body


def test_repeated_request_works() -> None:
    first = client.get("/prediction/client_000002")
    second = client.get("/prediction/client_000002")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["user_id"] == second.json()["user_id"]
