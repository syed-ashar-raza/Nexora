from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_invalid_message():
    response = client.post(
        "/v1/chat",
        json={"model": "nexora-mock", "messages": []},
    )
    assert response.status_code == 422
