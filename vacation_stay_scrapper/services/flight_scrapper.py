from typing import Any, Union
from utils.connector import Connector
from utils import logger as default_logger


logger = default_logger.setup_logger(
    logger_name=__name__, log_file=__file__
)


class FlightScrapper:

    _search_params = {'origin', 'destination', 'arrival_date'}

    def __init__(self, connector: Connector):
        self._connector = connector

    def get_flights(self, search_params: dict[str, Any]) -> Union[list[None], list[dict]]:
        self._validate_search_params(search_params)
        response = self._connector.make_request(
            method='GET', service='flights', params=search_params
        )
        logger.info(
            f'flight service :: '
            f'resource flights :: gathering {len(response)} flights'
        )
        return response

    def _validate_search_params(self, search_params: dict[str, Any]):
        missing_params = set(search_params.keys()) & self._search_params
        if not missing_params:
            msg = f'missing {self._search_params} parameters on service flights'
            logger.error('flight service :: msg')
            raise ValueError(msg)

