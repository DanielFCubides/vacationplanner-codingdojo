import logging

from flights.application.search import FlightsFinder
from flights.domain.repositories.base import FlightsRepository
from flights.domain.publishers.base_publisher import SearchPublisher
from flights.domain.scrappers.base import Scrapper
from flights.domain.models import SearchParams, FlightResults


logger = logging.getLogger(__name__)


class FlightFinderAvianca(FlightsFinder):

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

    def get_flights(self, search_params: SearchParams) -> dict:
        logger.info(
            f'Start getting a response with origin {search_params.origin} '
            f'and destination {search_params.destination}'
        )
        # search params are the unique ID for a flight results
        self._emit_message(search_params)
        saved_results = self._repository.get_flight_results(search_params)
        if saved_results:
            saved_results.search_params = search_params
            response = self._create_response(saved_results)
            return response

        _search_params = {
            "origin1": search_params.origin,
            "destination1": search_params.destination,
            "departure1": search_params.arrival_date,
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
        results = self._scrapper.get_flights(search_params)
        results.search_params = search_params
        if results.results:
            self._repository.save_flight(results)
        response = self._create_response(results)
        return response

    def _create_response(self, results: FlightResults) -> dict:
        return {
            'count': results.total,
            'flights': {
                "arrival_date": results.search_params.arrival_date.strftime('%Y-%m-%d'),
                "return_date": results.search_params.return_date.strftime('%Y-%m-%d'),
                "results": results.results
            }
        }

    def _emit_message(self, search_params):
        self._publisher.publish_search_params(search_params)
