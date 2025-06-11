from abc import ABC, abstractmethod
from typing import Optional

from domain.models import SearchParams, FlightResults


class FlightsFinder(ABC):

    @abstractmethod
    def get_flights(self, search_params: SearchParams) -> Optional[FlightResults]:
        """
        Get flights based on search parameters
        """
        ...
