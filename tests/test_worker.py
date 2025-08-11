import pytest
from app.worker import enrich_data, transform_data, process_webhook_task
from app.config import settings
from app.storage import storage
import time
import json

@pytest.mark.asyncio
async def test_enrich_data():
    payload = {"key": "value"}
    enriched = await enrich_data(payload)
    assert "enriched_at" in enriched
    assert enriched["processed"] is True

def test_transform_data():
    data = {
        "items": [
            {"name": "Item 1", "price": 10},
            {"name": "Item 2", "price": 20}
        ]
    }
    transformed = transform_data(data)
    assert transformed == {
        "transformed": True,
        "original_data": data,
        "items_count": 2,
        "total_value": 30
    }

@pytest.mark.asyncio
async def test_process_webhook_task_success(respx_mock):
    # Mock external API
    respx_mock.post(settings.EXTERNAL_API_URL).mock(return_value=httpx.Response(200))
    # Mock callback
    callback_mock = respx_mock.post("http://callback.example").mock(return_value=httpx.Response(200))
    
    request_data = {
        "event_type": "test",
        "payload": {"order_id": "123", "items": [{"name": "A", "price": 10}]},
        "callback_url": "http://callback.example"
    }
    job_id = "test-job-id"
    
    await process_webhook_task(request_data, job_id, request_data["callback_url"])
    
    # Check that external API was called
    assert respx_mock.calls.call_count == 1
    # Check that callback was called
    assert callback_mock.calls.call_count == 1
    # Check result saved
    result = await storage.memory_store.get(f"result:{job_id}")
    assert result is not None
    assert result["status"] == "success"