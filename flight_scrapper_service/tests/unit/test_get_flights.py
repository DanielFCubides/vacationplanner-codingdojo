import pytest

from decimal import Decimal
from unittest.mock import Mock

from flights.infrastructure.avianca import FlightFinderAvianca
from flights.domain.repositories.base_publisher import SearchPublisher
from flights.domain.models import SearchParams, FlightResults, FlightResult, Flight
from utils.urls import DynamicURL
from datetime import datetime

from flights.domain.repositories.base import FlightsRepository
from flights.domain.scrappers.avianca.scrapper import AviancaScrapper


class TestFlightsFinder:

    @pytest.fixture
    def mock_flights_results(self):
        return FlightResults(
            results=[
                FlightResult(
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

    def test_initialization_with_valid_url_and_scrapper(self):
        fake_repository = Mock(FlightsRepository)
        mock_url = Mock(spec=DynamicURL)
        scrapper = Mock(AviancaScrapper)
        publisher = Mock(SearchPublisher)
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository, publisher=publisher
        )

        assert flight_finder.url == mock_url
        assert flight_finder._scrapper == scrapper

    def test_get_flights_returns_results(
            self, mock_flights_results, mock_search_params
    ):
        # create Mocks
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = []

        mock_url = Mock(spec=DynamicURL)
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.return_value = mock_flights_results

        # Call function under test
        publisher = Mock(SearchPublisher)
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository,
            publisher=publisher
        )
        returned_results = flight_finder.get_flights(mock_search_params)

        assert returned_results.get('count') == 1
        assert returned_results.get('flights')
        assert returned_results['flights'].get('arrival_date')
        assert returned_results['flights'].get('return_date')
        scrapper.get_flights.assert_called_once_with(mock_url)

    def test_returns_saved_flights_if_exist_in_repository(
        self, mock_search_params, mock_flights_results
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.returned_value = mock_flights_results
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = mock_flights_results

        publisher = Mock(SearchPublisher)
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository, publisher=publisher
        )
        result = flight_finder.get_flights(mock_search_params)

        assert result['count'] == 1
        assert 'flights' in result
        assert (
                result['flights']['results'][0].outbound.price
                == mock_flights_results.results[0].outbound.price
        )
        assert scrapper.get_flights.call_count == 0

    def test_handles_empty_flight_results(
            self, mock_flights_results, mock_search_params
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.return_value = FlightResults(results=[])
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = FlightResults(results=[])
        publisher = Mock(SearchPublisher)
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository, publisher=publisher
        )
        results = flight_finder.get_flights(mock_search_params)

        assert results.get('count') == 0
        assert results['flights']['results'] == []

    def test_handles_exceptions_in_get_flights(
            self, mock_search_params
    ):
        mock_url = Mock(spec=DynamicURL)
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.side_effect = Exception("Mocked exception")
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = []
        publisher = Mock(SearchPublisher)
        flight_finder = FlightFinderAvianca(
            url=mock_url, scrapper=scrapper, repository=fake_repository, publisher=publisher
        )

        with pytest.raises(Exception):
            flight_finder.get_flights(mock_search_params)
        scrapper.get_flights.assert_called_once_with(mock_url)
