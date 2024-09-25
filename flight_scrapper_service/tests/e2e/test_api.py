import uuid
from decimal import Decimal
from unittest.mock import Mock

import pytest
from flights.domain.models import FlightResults, FlightResult, Flight


class TestGetFlightsAPI:

    endpoint = '/get_flights'

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

    def test_get_flights_valid_request(
        self, test_client, mock_scrapper,
        mock_flights_results, bootstrap_fixture,
        mock_create_driver_function, mock_redis
    ):
        bootstrap_fixture(
            'test_airline',
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=mock_flights_results
            )
        )
        response = test_client.post(self.endpoint, json={
            'airline': 'test_airline',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 200
        assert response.json['count'] == 1

    def test_get_flights_empty_results(
        self, test_client, bootstrap_fixture, mock_scrapper,
        mock_create_driver_function, mock_redis
    ):
        bootstrap_fixture(
            'test_airline',
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=[]
            )
        )
        response = test_client.post(self.endpoint, json={
            'airline': 'test_airline',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })

        assert response.status_code == 200
        assert response.json == {
            'count': 0,
            'flights': {
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20',
                'results': []
            }
        }

    def test_get_flights_unavailable_airline(
        self, test_client, bootstrap_fixture,
        mock_create_driver_function, mock_redis
    ):
        bootstrap_fixture()
        response = test_client.post(self.endpoint, json={
            'airline': 'avianca',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 400
        assert response.json.get('error')

    def test_get_flights_missing_airline(
        self, test_client, mock_create_driver_function, mock_redis
    ):
        response = test_client.post(self.endpoint, json={
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 400
        assert response.json['error'] == "Missing parameter: 'airline'"

    def test_get_flights_missing_required_search_params(
        self, test_client, mock_create_driver_function, mock_redis
    ):
        response = test_client.post(self.endpoint, json={
            'airline': 'avianca',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
            }
        })
        assert response.status_code == 400
        assert response.json['error'] == "Missing search_params: arrival_date"

    def test_get_flights_missing_search_params(
        self, test_client, mock_create_driver_function, mock_redis
    ):
        response = test_client.post(self.endpoint, json={
            'airline': 'test_airline'
        })
        assert response.status_code == 400
        assert response.json['error'] == 'Missing search_params'
