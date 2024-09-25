from abc import abstractmethod, ABC
from flights.domain.models import FlightResults


class FlightsRepository(ABC):

    @abstractmethod
    def get_flight_results(self, results_id: str) -> FlightResults | list[None]:
        """Takes a hash corresponding to the high level identifier of a
        flight results and returns a list"""
        ...

    @abstractmethod
    def save_flight(self, flight: FlightResults) -> str:
        """
        save a flight with all information
        """
        ...
