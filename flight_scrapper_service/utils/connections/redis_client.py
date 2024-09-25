import redis


class RedisClient:

    client = None
    initialize: bool = False

    def __init__(self, host='redis-cache', port=6379):
        self.host = host
        self.port = port

    def get_client(self, db=0):
        return redis.Redis(host=self.host, port=self.port, db=db, decode_responses=True)
