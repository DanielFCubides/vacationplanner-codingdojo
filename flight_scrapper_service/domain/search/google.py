from typing import Optional

from domain.models import SearchParams, FlightResults
from domain.search.base import FlightsFinder
from infrastructure.publishers.base_publisher import SearchPublisher
from infrastructure.repositories.base import FlightsRepository
from infrastructure.scrappers.base import Scrapper


class GoogleFlightsFinder(FlightsFinder):

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
        """
        Get flights from the scrapper and save them to the repository.
        If flights are already saved, return them.
        """
        saved_results = self._repository.get_flight_results(search_params)
        if saved_results.results:
            return saved_results

        flights = self._scrapper.get_flights(search_params)
        if flights.results:
            self._repository.save_flight(flights, search_params)
            #self._publisher.publish(results)

        return flights