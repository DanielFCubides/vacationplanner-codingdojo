from abc import ABC, abstractmethod

from flights.domain.models import SearchParams, FlightResults


class FlightsFinder(ABC):

    @abstractmethod
    def get_flights(self, search_params: SearchParams) -> FlightResults:
        """
        Obtain flights based on search parameters
        """
        ...
