import redis
from constants import config, get_secret


def get_redis_client(
    host: str = config['Redis']['host'],
    port: int = config['Redis']['port'],
    database: int = 0
):
    return redis.Redis(
        host=host,
        port=port,
        db=database,
        password=get_secret('redis_password'),
        decode_responses=True
    )
