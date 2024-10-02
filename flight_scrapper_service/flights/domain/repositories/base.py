from abc import abstractmethod, ABC
from flights.domain.models import FlightResults, SearchParams


class FlightsRepository(ABC):

    @abstractmethod
    def get_flight_results(
        self, search_params: SearchParams
    ) -> FlightResults | list[None]:
        """Takes the search params and returns the corresponding
        flight result"""
        ...

    @abstractmethod
    def save_flight(self, flight: FlightResults) -> str:
        """
        save a flight with all information
        """
        ...
