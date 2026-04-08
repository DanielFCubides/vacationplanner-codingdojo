import redis
from constants import config


def get_redis_client(
    host: str = config['Redis']['host'],
    port: int = config['Redis']['port'],
    database: int = 0
):
    return redis.Redis(
        host=host,
        port=port,
        db=database,
        decode_responses=True
    )
