import logging

from flights.domain.models import SearchParams
from flights.domain.repositories.base_publisher import SearchPublisher
from utils.connections.redis_client import RedisClient

logger = logging.getLogger(__name__)


class RedisPublisher(SearchPublisher):

    def __init__(self, client: RedisClient):
        self.client = client.get_client(2)
        self.mode = 'publish'
        self.channel = 'search_params'

    def publish_search_params(self, search_params: SearchParams) -> None:
        params = str(search_params)
        if self.mode == 'queue':
            self._queue_message(params)
        if self.mode == 'publish':
            self.publish_message(params)

    def _queue_message(self, search_params: str):
        self.client.lpush(self.channel, search_params)

    def publish_message(self, search_params: str):
        self.client.publish(self.channel, search_params)
