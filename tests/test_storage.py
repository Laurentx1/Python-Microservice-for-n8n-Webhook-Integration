import pytest
from app.storage import Storage, storage
import asyncio

@pytest.mark.asyncio
async def test_idempotency_check():
    # Test in-memory storage
    key = "test-key"
    assert await storage.check_idempotency(key) is False
    await storage.set_idempotency(key)
    assert await storage.check_idempotency(key) is True

@pytest.mark.asyncio
async def test_save_result():
    job_id = "test-job"
    result = {"status": "success", "data": {"order_id": 123}}
    await storage.save_result(job_id, result)
    # Check in-memory
    assert storage.memory_store.get(f"result:{job_id}") == result