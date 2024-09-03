import logging
from typing import Optional

from flights.application.search import FlightsRepository
from flights.domain.scrappers.base import Scrapper
from flights.domain.scrappers.models import SearchParams, FlightResults
from utils.urls import DynamicURL


logger = logging.getLogger(__name__)


class FlightFinderAvianca(FlightsRepository):

    def __init__(self, url: Optional[DynamicURL], scrapper: Scrapper):
        self.url = url
        self._scrapper = scrapper

    def get_flights(self, search_params: SearchParams) -> list[FlightResults | None]:
        logger.info(
            f'Start getting a response with origin {search_params.origin} '
            f'and destination {search_params.destination}'
        )
        _search_params = {
            "origin1": search_params.origin,
            "destination1": search_params.destination,
            "departure1": search_params.arrival_date,
            "adt1": search_params.passengers,
            "tng1": 0,
            "chd1": 0,
            "inf1": 0,
            "origin2": search_params.destination,
            "destination2": search_params.origin,
            "departure2": search_params.return_date,
            "adt2": search_params.passengers,
            "tng2": 0,
            "chd2": 0,
            "inf2": 0,
            "currency": search_params.currency,
            "posCode": "CO"
        }
        self.url.set_query_params(_search_params)
        results = self._scrapper.get_flights(self.url)
        return results
