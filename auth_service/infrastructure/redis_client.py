import os
import redis.asyncio as redis
from typing import AsyncIterator

from config import get_secret


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 0)
REDIS_PASSWORD = get_secret("redis_password")

async def get_redis_client() -> AsyncIterator[redis.Redis]:
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
