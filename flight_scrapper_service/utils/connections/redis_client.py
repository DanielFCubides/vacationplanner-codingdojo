import redis


def get_redis_client(
    host: str = 'redis-cache',
    port: int = 6379,
    database: int = 0
):
    return redis.Redis(
        host=host,
        port=port,
        db=database,
        decode_responses=True
    )
