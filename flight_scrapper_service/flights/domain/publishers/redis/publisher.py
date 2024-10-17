import logging
from enum import Enum
from typing import Callable
from flights.domain.models import SearchParams
from flights.domain.publishers.base_publisher import SearchPublisher

logger = logging.getLogger(__name__)
CHANNEL_NAME = 'search_params'


class PublishModes(str, Enum):
    QUEUE = 'queue'
    PUBLISH = 'publish'


class RedisPublisher(SearchPublisher):

    def __init__(self, client_factory: Callable):
        self.client = client_factory()
        self.mode = PublishModes.PUBLISH
        self.channel = CHANNEL_NAME

    def publish_search_params(self, search_params: SearchParams) -> None:
        params = str(search_params)
        if self.mode == PublishModes.QUEUE:
            self._queue_message(params)
        if self.mode == PublishModes.PUBLISH:
            self.publish_message(params)

    def _queue_message(self, search_params: str):
        self.client.lpush(self.channel, search_params)

    def publish_message(self, search_params: str):
        self.client.publish(self.channel, search_params)
