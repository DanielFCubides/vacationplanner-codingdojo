import os
import redis.asyncio as redis
from typing import AsyncIterator


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))


def _get_redis_password() -> str | None:
    password_file = os.getenv("REDIS_PASSWORD_FILE")
    if password_file:
        try:
            with open(password_file, encoding="utf-8") as file:
                return file.read().strip()
        except OSError as exc:
            raise RuntimeError("Unable to read Redis password file") from exc
    return os.getenv("REDIS_PASSWORD")

async def get_redis_client() -> AsyncIterator[redis.Redis]:
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=_get_redis_password(),
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
