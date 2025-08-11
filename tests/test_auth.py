from app.auth import verify_api_key, verify_signature
from fastapi import Request
from app.config import settings
import pytest

def test_verify_api_key_valid():
    request = Request(scope={
        "type": "http",
        "headers": [(b"authorization", b"Bearer test-api-key")]
    })
    verify_api_key(request)

def test_verify_api_key_invalid():
    request = Request(scope={
        "type": "http",
        "headers": [(b"authorization", b"Bearer invalid-key")]
    })
    with pytest.raises(Exception) as exc:
        verify_api_key(request)
    assert "Invalid API Key" in str(exc.value)

def test_verify_signature_valid():
    body = b'{"test": "data"}'
    signature = "sha256=" + hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    request = Request(scope={
        "type": "http",
        "headers": [(b"x-signature", signature.encode())]
    })
    verify_signature(request, body)

def test_verify_signature_invalid():
    request = Request(scope={
        "type": "http",
        "headers": [(b"x-signature", b"invalid-signature")]
    })
    with pytest.raises(Exception) as exc:
        verify_signature(request, b'{"test": "data"}')
    assert "Invalid HMAC" in str(exc.value)