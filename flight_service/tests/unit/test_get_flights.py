import pytest

from decimal import Decimal
from unittest.mock import Mock

from domain.search.avianca import AviancaFlightsFinder
from infrastructure.publishers.memory.publisher import MemoryPublisher
from domain.models import SearchParams, FlightResults, Flight, Flights
from datetime import datetime, time, timedelta

from infrastructure.repositories.base import FlightsRepository
from infrastructure.scrappers.avianca.scrapper import AviancaScrapper


class TestFlightsFinder:

    @pytest.fixture
    def mock_flights_results(self):
        return FlightResults(
            results=[
                Flights(
                    outbound_flight=Flight(
                        date=datetime(2023, 5, 15),
                        price=Decimal('250.00'),
                        flight_time=timedelta(hours=2, minutes=30),
                        departure_time=time(8, 0),
                        landing_time=time(10, 30)
                    ),
                    return_flights=[
                        Flight(
                            date=datetime(2023, 5, 20),
                            price=Decimal('200.00'),
                            flight_time=timedelta(hours=1, minutes=45),
                            departure_time=time(15, 0),
                            landing_time=time(17, 0),
                        )
                    ]
                )
            ]
        )

    @pytest.fixture
    def mock_search_params(self):
        return SearchParams(
            origin="BGT",
            destination="MDE",
            departure=datetime(2023, 5, 15),
            return_date=datetime(2023, 5, 20),
            passengers=2,
            currency="COP"
        )

    def test_initialization_with_valid_url_and_scrapper(self):
        fake_repository = Mock(FlightsRepository)
        scrapper = Mock(AviancaScrapper)
        publisher = Mock(MemoryPublisher)
        flight_finder = AviancaFlightsFinder(
            scrapper=scrapper, repository=fake_repository, publisher=publisher
        )
        assert flight_finder._scrapper == scrapper

    def test_get_flights_returns_results(
        self, mock_flights_results, mock_search_params
    ):
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = []

        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.return_value = mock_flights_results

        publisher = Mock(MemoryPublisher)
        flight_finder = AviancaFlightsFinder(
            scrapper=scrapper, repository=fake_repository,
            publisher=publisher
        )
        returned_results = flight_finder.get_flights(mock_search_params)

        assert len(returned_results.results) == 1
        assert returned_results.results[0].outbound_flight
        assert returned_results.results[0].return_flights[0]
        scrapper.get_flights.assert_called_once_with(mock_search_params)

    def test_returns_saved_flights_if_exist_in_repository(
        self, mock_search_params, mock_flights_results
    ):
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.returned_value = mock_flights_results
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = mock_flights_results

        publisher = Mock(MemoryPublisher)
        flight_finder = AviancaFlightsFinder(
            scrapper=scrapper, repository=fake_repository, publisher=publisher
        )
        results = flight_finder.get_flights(mock_search_params)

        flight_result = results.results[0]
        assert flight_result.outbound_flight.date == mock_flights_results.results[0].outbound_flight.date
        assert flight_result.outbound_flight.departure_time == mock_flights_results.results[0].outbound_flight.departure_time
        assert flight_result.outbound_flight.landing_time == mock_flights_results.results[0].outbound_flight.landing_time
        assert flight_result.outbound_flight.flight_time == mock_flights_results.results[0].outbound_flight.flight_time
        assert flight_result.outbound_flight.price == mock_flights_results.results[0].outbound_flight.price
        assert flight_result.return_flights[0].date == mock_flights_results.results[0].return_flights[0].date
        assert flight_result.return_flights[0].departure_time == mock_flights_results.results[0].return_flights[0].departure_time
        assert flight_result.return_flights[0].landing_time == mock_flights_results.results[0].return_flights[0].landing_time
        assert flight_result.return_flights[0].flight_time == mock_flights_results.results[0].return_flights[0].flight_time
        assert flight_result.return_flights[0].price == mock_flights_results.results[0].return_flights[0].price

        assert scrapper.get_flights.call_count == 0

    def test_handles_empty_flight_results(
        self, mock_flights_results, mock_search_params
    ):
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.return_value = FlightResults(results=[])
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = FlightResults(results=[])
        publisher = Mock(MemoryPublisher)
        flight_finder = AviancaFlightsFinder(
            scrapper=scrapper, repository=fake_repository, publisher=publisher
        )
        results = flight_finder.get_flights(mock_search_params)

        assert results.results == []

    def test_handles_exceptions_in_get_flights(
        self, mock_search_params
    ):
        scrapper = Mock(AviancaScrapper)
        scrapper.get_flights.side_effect = Exception("Mocked exception")
        fake_repository = Mock(FlightsRepository)
        fake_repository.get_flight_results.return_value = []
        publisher = Mock(MemoryPublisher)
        flight_finder = AviancaFlightsFinder(
            scrapper=scrapper, repository=fake_repository, publisher=publisher
        )

        with pytest.raises(Exception):
            flight_finder.get_flights(mock_search_params)
        scrapper.get_flights.assert_called_once_with(mock_search_params)
