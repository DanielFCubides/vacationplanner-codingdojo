from decimal import Decimal

from flights.domain.models import FlightResults, SearchParams, FlightResult, Flight
from flights.domain.repositories.base import FlightsRepository


class FlightsMemoryRepository(FlightsRepository):
    def get_flight_results(self, search_params: SearchParams) -> FlightResults | list[None]:
        return FlightResults(
            results= [FlightResult(
                    outbound=Flight(
                        price=Decimal('250.00'),
                        flight_time="2h 30m",
                        departure_time="08:00",
                        landing_time="10:30"
                    ),
                    return_in=Flight(
                        price=Decimal('200.00'),
                        flight_time="1h 45m",
                        departure_time="15:00"
                    )
                )],
            search_params=search_params
        )

    def save_flight(self, flight: FlightResults) -> str:
        pass