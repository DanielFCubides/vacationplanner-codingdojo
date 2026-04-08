from decimal import Decimal
from datetime import datetime, time, timedelta

from domain.models import FlightResults, SearchParams, Flight, Flights
from infrastructure.repositories.base import FlightsRepository


class FlightsMemoryRepository(FlightsRepository):

    def get_flight_results(self, search_params: SearchParams) -> FlightResults:
        outbound = Flight(
            date=datetime.now(),
            departure_time=time(hour=8, minute=0),
            landing_time=time(hour=10, minute=30),
            price=Decimal('250.00'),
            flight_time=timedelta(hours=2, minutes=30)
        )

        return_flights = [
            Flight(
                date=datetime.now() + timedelta(days=1),
                departure_time=time(hour=15, minute=0),
                landing_time=time(hour=16, minute=45),
                price=Decimal('200.00'),
                flight_time=timedelta(hours=1, minutes=45)
            )
        ]

        return FlightResults(
            results=[Flights(outbound_flight=outbound, return_flights=return_flights)]
        )

    def save_flight(self, flight: FlightResults, search_params: SearchParams) -> str:
        pass


def create_memory_repository() -> FlightsMemoryRepository:
    return FlightsMemoryRepository()