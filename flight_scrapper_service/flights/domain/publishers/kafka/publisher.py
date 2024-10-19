import logging

from confluent_kafka import Producer

from flights.domain.models import SearchParams
from flights.domain.publishers.base_publisher import SearchPublisher

logger = logging.getLogger(__name__)
TOPIC_NAME = 'search-params'


class KafkaPublisher(SearchPublisher):

    def __init__(self, producer: Producer):
        self.producer = producer

    def publish_search_params(self, search_params: SearchParams) -> None:
        params = search_params.to_dict().__str__()
        self.producer.produce(TOPIC_NAME, key="key", value=params)
        self.producer.flush()
