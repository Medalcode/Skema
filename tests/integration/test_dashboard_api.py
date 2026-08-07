import pytest
from fastapi.testclient import TestClient

from skema.api.main import app


def test_dashboard_review_endpoint(client: TestClient):
    response = client.get("/review")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_dashboard_metrics_endpoint(client: TestClient):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_classify_validation_error(client: TestClient):
    # Text too short (< 5 chars)
    response = client.post("/classify", json={"text": "hi"})
    assert response.status_code == 422  # Unprocessable Entity Pydantic Validation
