import logging
from typing import Optional

from domain.search.base import FlightsFinder
from infrastructure.repositories.base import FlightsRepository
from infrastructure.publishers.base_publisher import SearchPublisher
from infrastructure.scrappers.base import Scrapper
from domain.models import SearchParams, FlightResults

logger = logging.getLogger(__name__)


class AviancaFlightsFinder(FlightsFinder):

    _flight_types = ('outbound', 'return_in')

    def __init__(
        self,
        scrapper: Scrapper,
        repository: FlightsRepository,
        publisher: SearchPublisher
    ):
        self._scrapper = scrapper
        self._repository = repository
        self._publisher = publisher

    def get_flights(self, search_params: SearchParams) -> Optional[FlightResults]:
        logger.info(
            f'Start getting a response with origin {search_params.origin} '
            f'and destination {search_params.destination}'
        )
        # search params are the unique ID for a flight result
        self._emit_message(search_params)
        saved_results = self._repository.get_flight_results(search_params)
        if saved_results.results:
            return saved_results

        _search_params = {
            "origin1": search_params.origin,
            "destination1": search_params.destination,
            "departure1": search_params.departure,
            "adt1": search_params.passengers,
            "tng1": 0,
            "chd1": 0,
            "inf1": 0,
            "origin2": search_params.destination,
            "destination2": search_params.origin,
            "departure2": search_params.return_date,
            "adt2": search_params.passengers,
            "tng2": 0,
            "chd2": 0,
            "inf2": 0,
            "currency": search_params.currency,
            "posCode": "CO"
        }
        flights = self._scrapper.get_flights(search_params)
        if flights.results:
            self._repository.save_flight(flights, search_params)
        return flights

    def _emit_message(self, search_params):
        #self._publisher.publish_search_params(search_params)
        ...
