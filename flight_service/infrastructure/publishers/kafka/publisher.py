import logging
from typing import Callable

from confluent_kafka import Producer

from constants import config
from domain.models import SearchParams
from infrastructure.publishers.base_publisher import SearchPublisher
from utils.connections.kafka_client import kafka_client_factory

logger = logging.getLogger(__name__)


class KafkaPublisher(SearchPublisher):

    def __init__(self, producer_factory: Callable):
        self.producer = producer_factory()

    def publish_search_params(self, search_params: SearchParams) -> None:
        params = search_params.to_dict().__str__()
        self.producer.produce(
            config['Default']['publish_channel'], key="key", value=params
        )
        self.producer.flush()


def create_kafka_publisher(producer_factory: Callable = kafka_client_factory) -> KafkaPublisher:
    return KafkaPublisher(producer_factory=producer_factory())