import pytest
import httpx
from app.main import app
from app.config import settings
from fastapi.testclient import TestClient
import hmac
import hashlib
import json

client = TestClient(app)

@pytest.fixture
def webhook_payload():
    return {
        "event_type": "test.event",
        "payload": {"key": "value"},
        "callback_url": "http://example.com/callback"
    }

def generate_signature(secret: str, body: bytes) -> str:
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

def test_webhook_success(webhook_payload):
    body = json.dumps(webhook_payload).encode()
    signature = generate_signature(settings.WEBHOOK_SECRET, body)
    
    response = client.post(
        "/webhook",
        json=webhook_payload,
        headers={
            "Authorization": "Bearer test-api-key",
            "X-Signature": signature
        }
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["job_id"] != ""
    assert "processing in background" in data["message"]

def test_webhook_invalid_signature(webhook_payload):
    response = client.post(
        "/webhook",
        json=webhook_payload,
        headers={
            "Authorization": "Bearer test-api-key",
            "X-Signature": "invalid-signature"
        }
    )
    assert response.status_code == 401
    assert "Invalid HMAC" in response.json()["detail"]

def test_webhook_invalid_api_key(webhook_payload):
    response = client.post(
        "/webhook",
        json=webhook_payload,
        headers={"Authorization": "Bearer invalid-key"}
    )
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]

def test_run_task_directly(webhook_payload):
    response = client.post(
        "/run-task",
        json=webhook_payload,
        headers={"Authorization": "Bearer test-api-key"}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}