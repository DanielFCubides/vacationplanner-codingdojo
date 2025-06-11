import logging
from decimal import Decimal
from typing import Callable, Union, Any

from flights.domain.models import SearchParams, FlightResults, FlightResult, Flight
from flights.domain.scrappers.base import Scrapper

logger = logging.getLogger(__name__)


class DummyScrapper(Scrapper):

    def __init__(
        self,
        create_driver: Callable[[str, dict, Union[str, None]], Any]
    ) -> None:
        self.create_driver = create_driver

    def get_flights(self, search_params: SearchParams) -> FlightResults | None:
        logger.info(f"Getting flights for {search_params}")
        return FlightResults(
            results=[FlightResult(
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