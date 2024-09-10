from decimal import Decimal
from unittest.mock import Mock

import pytest

from flights.infrastructure.avianca import FlightFinderAvianca
from flights.domain.scrappers.models import SearchParams, FlightResults, FlightResult
from utils.urls import DynamicURL
from datetime import datetime


class TestFlightsFinder:

    @pytest.fixture
    def mock_flights_results(self):
        return FlightResults(
            outbound=FlightResult(
                price=Decimal('250.00'),
                flight_time="2h 30m",
                departure_time="08:00",
                landing_time="10:30"
            ),
            return_in=FlightResult(
                price=Decimal('200.00'),
                flight_time="1h 45m",
                departure_time="15:00"
            )
        )

    @pytest.fixture
    def mock_search_params(self):
        return SearchParams(
            origin="BGT",
            destination="MDE",
            arrival_date=datetime(2023, 5, 15),
            return_date=datetime(2023, 5, 20),
            passengers=2,
            currency="COP"
        )

    def test_initialization_with_valid_url_and_scrapper(
        self, mock_scrapper
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper()
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper
        )

        assert flight_finder.url == mock_url
        assert flight_finder._scrapper == scrapper

    def test_get_flights_returns_results(
        self, mock_scrapper, mock_flights_results, mock_search_params
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            returned_value=mock_flights_results
        )
        flight_finder = FlightFinderAvianca(url=mock_url, scrapper=scrapper)
        returned_results = flight_finder.get_flights(mock_search_params)

        assert returned_results == mock_flights_results
        scrapper.get_flights.assert_called_once_with(mock_url)

    def test_handles_empty_flight_results(
        self, mock_scrapper, mock_flights_results, mock_search_params
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            returned_value=mock_flights_results
        )
        flight_finder = FlightFinderAvianca(url=mock_url, scrapper=scrapper)
        results = flight_finder.get_flights(mock_search_params)

        assert results == mock_flights_results

    def test_handles_exceptions_in_get_flights(
        self, mock_scrapper, mock_search_params
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            side_effect=Exception("Mocked exception")
        )
        flight_finder = FlightFinderAvianca(url=mock_url, scrapper=scrapper)

        with pytest.raises(Exception):
            flight_finder.get_flights(mock_search_params)
        scrapper.get_flights.assert_called_once_with(mock_url)
