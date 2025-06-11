import logging

from confluent_kafka import Producer

from constants import config
from domain.models import SearchParams
from infrastructure.publishers.base_publisher import SearchPublisher

logger = logging.getLogger(__name__)


class KafkaPublisher(SearchPublisher):

    def __init__(self, producer: Producer):
        self.producer = producer

    def publish_search_params(self, search_params: SearchParams) -> None:
        params = search_params.to_dict().__str__()
        self.producer.produce(
            config['Default']['publish_channel'], key="key", value=params
        )
        self.producer.flush()
