from typing import Any, Union
from utils.connector import Connector


class FlightScrapper:

    _search_params = {'origin', 'destination', 'arrival_date'}

    def __init__(self, connector: Connector):
        self._connector = connector

    def get_flights(self, search_params: dict[str, Any]) -> Union[list[None], list[dict]]:
        self._validate_search_params(search_params)
        response = self._connector.make_request(
            method='GET', service='flights', params=search_params
        )
        return response

    def _validate_search_params(self, search_params: dict[str, Any]):
        missing_params = set(search_params.keys()) & self._search_params
        if not missing_params:
            raise ValueError(
                "search_params is missing the required parameters: "
                f"{self._search_params}"
            )

