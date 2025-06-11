import logging

from domain.models import SearchParams
from infrastructure.publishers.base_publisher import SearchPublisher

logger = logging.getLogger(__name__)


class MemoryPublisher(SearchPublisher):

    def publish_search_params(self, search_params: SearchParams) -> None:
        logger.info(f"Publishing search params: {search_params}")