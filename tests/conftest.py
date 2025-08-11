import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-api-key")
    monkeypatch.setenv("WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("EXTERNAL_API_KEY", "ext-key")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")