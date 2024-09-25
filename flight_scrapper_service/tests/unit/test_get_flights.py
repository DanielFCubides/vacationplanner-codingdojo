import uuid
from decimal import Decimal
from unittest.mock import Mock

import pytest

from flights.infrastructure.avianca import FlightFinderAvianca
from flights.domain.models import SearchParams, FlightResults, FlightResult, Flight
from utils.urls import DynamicURL
from datetime import datetime


class TestFlightsFinder:

    @pytest.fixture
    def mock_flights_results(self):
        return FlightResults(
            id_=uuid.uuid4(),
            results=[
                FlightResult(
                    id_=uuid.uuid4(),
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
                )
            ]
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
        self, mock_scrapper, fake_repository
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper()
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository
        )

        assert flight_finder.url == mock_url
        assert flight_finder._scrapper == scrapper

    def test_get_flights_returns_results(
        self, mock_scrapper, mock_flights_results, mock_search_params,
        fake_repository
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            returned_value=mock_flights_results
        )
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository
        )
        returned_results = flight_finder.get_flights(mock_search_params)

        assert returned_results.get('count') == 1
        assert returned_results.get('flights')
        assert returned_results['flights'].get('arrival_date')
        assert returned_results['flights'].get('return_date')
        assert returned_results['flights'].get('results') == mock_flights_results
        scrapper.get_flights.assert_called_once_with(mock_url)

    def test_returns_saved_flights_if_exist_in_repository(
        self, mock_scrapper, mock_search_params, mock_flights_results,
        fake_repository
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(returned_value=mock_flights_results)
        repository = fake_repository

        # save results before execution
        mock_flights_results.search_params = mock_search_params
        repository.save_flight(mock_flights_results)

        flight_finder = FlightFinderAvianca(mock_url, scrapper, fake_repository)
        result = flight_finder.get_flights(mock_search_params)

        assert result['count'] == 1
        assert 'flights' in result
        assert (
            result['flights']['results'].results[0].outbound.price
            == mock_flights_results.results[0].outbound.price
        )
        assert scrapper.get_flights.call_count == 0

    def test_handles_empty_flight_results(
        self, mock_scrapper, mock_flights_results, mock_search_params,
        fake_repository
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            returned_value=FlightResults(id_=uuid.uuid4(), results=[]),
        )
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository
        )
        results = flight_finder.get_flights(mock_search_params)

        assert results.get('count') == 0
        assert results['flights']['results'].results == []

    def test_handles_exceptions_in_get_flights(
        self, mock_scrapper, mock_search_params, fake_repository
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = mock_scrapper(
            side_effect=Exception("Mocked exception")
        )
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository
        )

        with pytest.raises(Exception):
            flight_finder.get_flights(mock_search_params)
        scrapper.get_flights.assert_called_once_with(mock_url)
