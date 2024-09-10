from abc import ABC, abstractmethod

from flights.domain.scrappers.models import SearchParams, FlightResults


class FlightsRepository(ABC):

    @abstractmethod
    def get_flights(self, search_params: SearchParams) -> FlightResults:
        """
        Obtain flights based on search parameters
        """
        pass
