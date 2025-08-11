import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from app.config import settings
from typing import Optional, AsyncGenerator
import json

class Storage:
    def __init__(self):
        self.redis = None
        self.memory_store = {}
        
        if settings.REDIS_URL:
            try:
                self.redis = aioredis.from_url(settings.REDIS_URL)
            except Exception as e:
                print(f"Redis connection error: {e}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Optional[aioredis.Redis], None]:
        if self.redis:
            yield self.redis
        else:
            yield None

    async def check_idempotency(self, key: str) -> bool:
        async with self.get_connection() as conn:
            if conn:
                return await conn.exists(f"idemp:{key}") == 1
            return key in self.memory_store

    async def set_idempotency(self, key: str, ttl: int = 86400):
        async with self.get_connection() as conn:
            if conn:
                await conn.setex(f"idemp:{key}", ttl, "1")
            else:
                self.memory_store[key] = True

    async def save_result(self, job_id: str, result: dict, ttl: int = 86400):
        async with self.get_connection() as conn:
            if conn:
                await conn.setex(f"result:{job_id}", ttl, json.dumps(result))
            else:
                self.memory_store[f"result:{job_id}"] = result

storage = Storage()