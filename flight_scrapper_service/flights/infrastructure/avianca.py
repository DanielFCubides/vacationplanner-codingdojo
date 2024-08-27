import uuid
from typing import Optional

from flights.application.search import FlightsRepository
from flights.domain.scrappers.base import Scrapper
from flights.domain.scrappers.models import SearchParams, FlightResults
from utils.urls import DynamicURL


class FlightFinderAvianca(FlightsRepository):

    def __init__(self, url: Optional[DynamicURL], scrapper: Scrapper):
        self.url = url
        self._scraper = scrapper

    def get_flights(self, search_params: SearchParams) -> list[FlightResults | None]:
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
        results = self._scraper.get_flights(self.url)
        return results


class FlightFinder1(FlightsRepository):

    def __init__(self, url: str, scrapper: Scrapper, api_key: str):
        self._url = url
        self._api_key = api_key
        self._scrapper = scrapper

    def get_flights(self, search_params: SearchParams) -> list[FlightResults | None]:
        body = {
            "customerId": "0f9ef31c-e69b-43c0-89c7-b2a7a0356d67",
            "journeyPriceRequests": [
                {
                    "currency": search_params.currency,
                    "destination": search_params.destination,
                    "origin": search_params.origin,
                    "pax": {
                        "ADT": search_params.passengers,
                        "CHD": 0,
                        "INF": 0,
                        "TNG": 0
                    },
                    "pointOfSale": {
                        "Country": "",
                        "posCode": "CO"
                    },
                    "details": {
                        "allPrice": [
                            {
                                "begin": search_params.arrival_date,
                                "end": search_params.arrival_date
                            }
                        ],
                    },
                    "filters": {
                        "MaxConnectingSegments": [
                            "20"
                        ],
                        "requestedJourneyNumber": [
                            "1"
                        ],
                        "tripType": [
                            "RT"
                        ]
                    },
                    "id": "1"
                },
                {
                    "currency": search_params.currency,
                    "destination": search_params.origin,
                    "origin": search_params.destination,
                    "pax": {
                        "ADT": search_params.passengers,
                        "CHD": 0,
                        "INF": 0,
                        "TNG": 0
                    },
                    "pointOfSale": {
                        "Country": "",
                        "posCode": "CO"
                    },
                    "details": {
                        "allPrice": [
                            {
                                "begin": search_params.return_date,
                                "end": search_params.return_date
                            }
                        ],
                    },
                    "filters": {
                        "MaxConnectingSegments": [
                            "20"
                        ],
                        "requestedJourneyNumber": [],
                        "tripType": [
                            "RT"
                        ]
                    },
                    "id": "2"
                }
            ],
            "prospectId": ""
        }
        results = self._scrapper.get_flights(self._url, body, self._api_key)
        return results
