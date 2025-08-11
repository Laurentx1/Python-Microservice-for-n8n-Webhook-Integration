import hmac
import hashlib
from fastapi import HTTPException, Request, status
from app.config import settings

class InvalidSignatureError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "HMAC"}
        )

def verify_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    api_key_header = request.headers.get("X-API-Key")
    
    valid_key = settings.API_KEY
    if not valid_key:
        return
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if token == valid_key:
            return
    
    if api_key_header and api_key_header == valid_key:
        return
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "Bearer"}
    )

def verify_signature(request: Request, body: bytes):
    if not settings.WEBHOOK_SECRET:
        return
    
    signature = request.headers.get("X-Signature")
    if not signature:
        raise InvalidSignatureError("Missing HMAC signature")
    
    secret = settings.WEBHOOK_SECRET.encode()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={expected_signature}"
    
    if not hmac.compare_digest(expected_signature, signature):
        raise InvalidSignatureError("Invalid HMAC signature")