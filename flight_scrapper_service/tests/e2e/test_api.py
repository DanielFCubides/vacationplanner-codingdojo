import json
from datetime import datetime, timedelta, time
from decimal import Decimal
from unittest.mock import Mock

import pytest
from domain.models import FlightResults, Flight, Flights
from domain.search.google import GoogleFlightsFinder
from infrastructure.repositories.redis.repository import RedisRepository
from utils.json_decoders import FlightsJSONEncoder


class TestGetFlightsAPI:

    endpoint = '/get_flights'

    def _configure_redis_response(self, flights):
        redis_side_effects = [
            json.dumps(result.flatten_results, cls=FlightsJSONEncoder)
            for result in flights.results
        ]
        keys = [
            f'simulated_hash:{index}'
            for index in range(len(flights.results))
        ]
        return keys, redis_side_effects

    def _mock_redis_repo(self, mock_redis):
        return RedisRepository(client_factory=Mock(return_value=mock_redis))

    @pytest.fixture
    def mock_flights_results(self):
        return FlightResults(
            results=[
                Flights(
                    outbound_flight=Flight(
                        date=datetime(2020, 1, 1),
                        price=Decimal('250.00'),
                        flight_time=timedelta(hours=2, minutes=30),
                        departure_time=time(8, 0),
                        landing_time=time(10,30)
                    ),
                    return_flights=[
                        Flight(
                            date=datetime(2020, 1, 10),
                            price=Decimal('200.00'),
                            flight_time=timedelta(hours=1, minutes=45),
                            departure_time=time(15, 0),
                            landing_time=time(16, 45)
                        )
                    ]
                )
            ]
        )

    def test_get_flights_no_cached_results(
        self, test_client, mock_scrapper,
        mock_flights_results, bootstrap_fixture,
        mock_create_driver_function, mock_redis,
        mock_config
    ):
        test_airline = mock_config['Default']['airline']
        publisher = mock_config['Default']['publisher']
        repository = mock_config['Default']['repository']
        mock_redis.keys.return_value = []
        bootstrap_fixture(
            test_airline,
            finders=GoogleFlightsFinder,
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=mock_flights_results
            ),
            repositories={

                repository: Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))
            },
            publishers={
                publisher: Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))
            }
        )
        response = test_client.post(self.endpoint, json={
            'airline': test_airline,
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'departure': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_flights_cached_results(
        self, test_client, mock_scrapper,
        mock_flights_results, bootstrap_fixture, mock_create_driver_function,
        mock_redis, mock_config
    ):
        test_airline = mock_config['Default']['airline']
        publisher = mock_config['Default']['publisher']
        repository = mock_config['Default']['repository']
        keys, redis_side_effects = self._configure_redis_response(mock_flights_results)
        mock_redis.keys.return_value = keys
        mock_redis.get.side_effect = redis_side_effects
        bootstrap_fixture(
            finders=GoogleFlightsFinder,
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=mock_flights_results
            ),
            repositories={
                repository: Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))
            },
            publishers={
                publisher: Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))
            }
        )
        response = test_client.post(self.endpoint, json={
            'airline': test_airline,
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'departure': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_flights_empty_results(
        self, test_client, bootstrap_fixture, mock_scrapper,
        mock_create_driver_function, mock_redis
    ):
        mock_redis.keys.return_value = []
        bootstrap_fixture(
            'test_airline',
            finders=GoogleFlightsFinder,
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=FlightResults(results=[])
            ),
            repositories={'redis': Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))},
            publishers={'redis': Mock(side_effect=lambda: self._mock_redis_repo(mock_redis))}
        )
        response = test_client.post(self.endpoint, json={
            'airline': 'test_airline',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'departure': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 200
        assert response.json == []

    def test_get_flights_unavailable_airline(
        self, test_client, bootstrap_fixture,
        mock_create_driver_function, mock_config
    ):
        bootstrap_fixture()
        response = test_client.post(self.endpoint, json={
            'airline': 'avianca',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'departure': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 400
        assert response.json.get('error') == "Dependency 'avianca' dont available"

    def test_get_flights_missing_airline(
        self, test_client, mock_create_driver_function
    ):
        response = test_client.post(self.endpoint, json={
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'departure': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 400
        assert response.json['error'] == "Dependency 'test_airline' dont available"

    def test_get_flights_missing_required_search_params(
        self, test_client, mock_create_driver_function
    ):
        response = test_client.post(self.endpoint, json={
            'airline': 'avianca',
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
            }
        })
        assert response.status_code == 400
        for error in response.json:
            error['msg'] == 'Field Required'
            error['type'] == 'missing'

    def test_get_flights_missing_search_params(
        self, test_client, mock_create_driver_function
    ):
        response = test_client.post(self.endpoint, json={
            'airline': 'test_airline'
        })
        assert response.status_code == 400

        assert len(response.json) > 2
        for error in response.json:
            error['msg'] == 'Field Required'
            error['type'] == 'missing'
