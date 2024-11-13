from decimal import Decimal
from unittest.mock import Mock

import pytest
from constants import config
from flights.domain.models import FlightResults, FlightResult, Flight
from flights.domain.publishers.redis.publisher import RedisPublisher
from flights.domain.repositories.redis.repository import RedisRepository


class TestGetFlightsAPI:

    endpoint = '/get_flights'

    def _configure_redis_response(self, flights):
        redis_side_effects = [
            flight
            for result in flights.results
            for key, flight in result.to_dict().items()
        ]
        keys = []
        for index, result in enumerate(flights.results, start=1):
            for type_, flight in result.to_dict().items():
                keys.append(f'simulated_hash:{type_}:{index}')
        return keys, redis_side_effects

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

    def test_get_flights_no_cached_results(
        self, test_client, mock_scrapper,
        mock_flights_results, bootstrap_fixture,
        mock_create_driver_function, mock_redis,
        mock_config
    ):
        test_airline = mock_config['Default']['airline']
        publisher = mock_config['Default']['publisher']
        repository = mock_config['Default']['repository']
        mock_redis.scan.return_value = 0, []
        bootstrap_fixture(
            test_airline,
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=mock_flights_results
            ),
            repositories={
                repository: RedisRepository(client_factory=Mock(return_value=mock_redis))
            },
            publishers={
                publisher: RedisPublisher(client_factory=Mock(return_value=mock_redis))
            }
        )
        response = test_client.post(self.endpoint, json={
            'airline': test_airline,
            'search_params': {
                'origin': 'origin',
                'destination': 'destination',
                'arrival_date': '2023-10-10',
                'return_date': '2023-10-20'
            }
        })
        assert response.status_code == 200
        assert response.json['count'] == 1

    def test_get_flights_cached_results(
        self, test_client, mock_scrapper,
        mock_flights_results, bootstrap_fixture, mock_create_driver_function,
        mock_redis, mock_config
    ):
        test_airline = mock_config['Default']['airline']
        publisher = mock_config['Default']['publisher']
        repository = mock_config['Default']['repository']
        keys, redis_side_effects = self._configure_redis_response(mock_flights_results)
        mock_redis.scan.return_value = len(keys), keys
        mock_redis.hgetall.side_effect = redis_side_effects
        bootstrap_fixture(
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=mock_flights_results
            ),
            repositories={
                repository: RedisRepository(
                    client_factory=Mock(return_value=mock_redis)
                )
            },
            publishers={
                publisher: RedisPublisher(client_factory=Mock(return_value=mock_redis))
            }
        )
        response = test_client.post(self.endpoint, json={
            'airline': test_airline,
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
        mock_redis.scan.return_value = 0, []
        bootstrap_fixture(
            'test_airline',
            scrappers=mock_scrapper(
                create_driver=Mock(),
                returned_value=FlightResults(results=[])
            ),
            repositories={'redis': RedisRepository(Mock(return_value=mock_redis))},
            publishers={'redis': RedisPublisher(Mock(return_value=mock_redis))}
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
        mock_create_driver_function, mock_config
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
        self, test_client, mock_create_driver_function
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
        assert response.json['errors']['airline'] == "Missing value"

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
