from pydantic import BaseModel, Field
from typing import Any, Optional

class WebhookRequest(BaseModel):
    event_type: str
    payload: dict[str, Any]
    callback_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

class WebhookResponse(BaseModel):
    status: str
    job_id: str = Field(..., example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8")
    message: str

class CallbackPayload(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any]

class HealthResponse(BaseModel):
    status: str = "OK"