import os
from typing import Optional

import redis
from constants import config


def _get_password():
    password_file = os.getenv("REDIS_PASSWORD_FILE")
    if password_file:
        try:
            with open(password_file, encoding="utf-8") as file:
                return file.read().strip()
        except OSError as exc:
            raise RuntimeError("Unable to read Redis password file") from exc
    return os.getenv("REDIS_PASSWORD")


def get_redis_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: int = 0
):
    return redis.Redis(
        host=host or config['Redis']['host'],
        port=int(port or config['Redis']['port']),
        db=database,
        password=_get_password(),
        decode_responses=True
    )
