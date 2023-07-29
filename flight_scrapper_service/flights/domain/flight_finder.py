from typing import Union
from flight_scrapper_service.flights.application.search import (
    FlightsRepository
)


class FlightFinder:

    def __init__(
            self,
            *,
            repository: FlightsRepository
    ):
        self.repository = repository

    
    def search(
            self, 
            *, 
            id_fly: int
    ) -> Union[(dict, list), int]:
        return self.repository.get(
            id_fly=id_fly
        )
