from typing import Any, Union
from utils.connector import Connector
from utils import logger as default_logger
from utils.exception_handler import GracefulDegradationService

_logger = default_logger.setup_logger(logger_name=__name__)

exception_handler = GracefulDegradationService()


class FlightScrapper:

    _search_params = {'origin', 'destination', 'arrival_date'}

    def __init__(self, connector: Connector):
        self._connector = connector


    # TODO validate a way to do this reusable and interchangeable
    @exception_handler.handle_exception
    def get_flights(
        self, search_params: dict[str, Any]
    ) -> dict:
        response = {'flights': []}
        self._validate_search_params(search_params)
        _response = self._connector.make_request(
            method='POST', service='flights', params=search_params
        )

        if isinstance(_response, list):
            response['flights'] = _response

        if isinstance(_response, dict):
            response['flights'].append(_response)

        _logger.info(
            f'flight service :: '
            f'resource flights :: gathering {len(response.get("flights"))} flights'
        )
        return response

    def _validate_search_params(self, search_params: dict[str, Any]):
        missing_params = set(search_params.keys()) & self._search_params
        if not missing_params:
            msg = f'missing {self._search_params} parameters on service flights'
            _logger.error('flight service :: msg')
            raise ValueError(msg)
