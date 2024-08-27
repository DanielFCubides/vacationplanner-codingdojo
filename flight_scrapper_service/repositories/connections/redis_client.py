import redis


class RedisClient:
    connection = None

    def __init__(self):
        self.connection = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)