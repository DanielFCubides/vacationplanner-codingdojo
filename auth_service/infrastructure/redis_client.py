import os
import redis.asyncio as redis
from typing import AsyncIterator


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)

async def get_redis_client() -> AsyncIterator[redis.Redis]:
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
