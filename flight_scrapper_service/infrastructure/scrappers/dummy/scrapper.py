import logging
from datetime import time, datetime, timedelta
from decimal import Decimal
from typing import Callable, Union, Any

from domain.models import SearchParams, FlightResults, Flight, Flights
from infrastructure.scrappers.base import Scrapper

logger = logging.getLogger(__name__)


class DummyScrapper(Scrapper):

    def __init__(
        self,
        create_driver: Callable[[str, dict, Union[str, None]], Any],
    ) -> None:
        self.create_driver = create_driver

    def get_flights(self, search_params: SearchParams) -> FlightResults | None:
        logger.info(f"Getting flights for {search_params}")
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