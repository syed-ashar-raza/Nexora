from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_chat():
    response = client.post(
        "/v1/chat",
        json={"model": "nexora-mock", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "nexora-mock"
    assert body["content"]

def test_stream():
    response = client.post(
        "/v1/chat/stream",
        json={"model": "nexora-mock", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert response.status_code == 200
    assert "[DONE]" in response.text
