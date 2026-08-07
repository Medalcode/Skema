import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()

@pytest.mark.asyncio
async def test_classify_endpoint(client: TestClient):
    payload = {
        "text": "The database is very slow and queries are taking too long.",
        "metadata": {"source": "github_issues"}
    }
    response = client.post("/classify", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["category"] == "Performance" or data["category"] == "Infrastructure"
    assert data["confidence"] > 0

@pytest.mark.asyncio
async def test_submit_feedback(client: TestClient):
    # Primero clasificamos algo para obtener un ID
    payload = {"text": "A new defect is found"}
    res = client.post("/classify", json=payload)
    class_id = res.json()["id"]

    # Enviamos feedback
    feedback = {
        "classification_id": class_id,
        "corrected_category": "Bug",
        "is_correct": True,
        "notes": "Yes, it is a bug."
    }
    response = client.post("/api/feedback", json=feedback)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_dashboard_home(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
