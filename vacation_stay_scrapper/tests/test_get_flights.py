import json
from datetime import date, timedelta, datetime
from unittest.mock import MagicMock

import pytest
import requests
from starlette import status
from starlette.testclient import TestClient

from constants import MIN_FAILURE_ATTEMPTS
from exceptions import HTTPException, ServiceUnavailable
from main import app
from utils.connector import HTTPConnector


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_connector(monkeypatch):
    mock = MagicMock(spec=HTTPConnector)
    monkeypatch.setattr(
        'utils.connector.HTTPConnector.make_request',
        mock.make_request
    )
    return mock

@pytest.fixture
def mock_requests_get(monkeypatch):
    mock = MagicMock(spec=requests)
    monkeypatch.setattr(
        'requests.get',
        mock.get
    )
    return mock


class TestFlightAPI:

    def test_get_flights(self, client, mock_connector):
        with open('tests/mock_flights.json', 'r') as file:
            data = json.load(file)
            mock_response = data  # assertion variable
            mock_connector.make_request.return_value = data

        arrival_date = date(2023, 7, 4)
        response = client.get('/vacation-plan', params={
            "origin": "A",
            "destination": "B",
            "arrival_date": arrival_date.isoformat(),
            "passengers": 2,
            "return_date": (arrival_date + timedelta(days=6)).isoformat(),
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_response

    def test_get_no_flights(self, client, mock_connector):
        mock_connector.make_request.return_value = []

        arrival_date = date(2023, 11, 6)
        response = client.get('/vacation-plan', params={
            "origin": "A",
            "destination": "B",
            "arrival_date": arrival_date.isoformat(),
            "passengers": 2,
            "return_date": (arrival_date + timedelta(days=6)).isoformat(),
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_flight_services_unavailable(
        self, client,
        mock_connector,
    ):
        mock_connector.make_request.side_effect = \
            HTTPException('500, Server Error')

        with pytest.raises(HTTPException) as e:
            arrival_date = date(2023, 11, 6)
            client.get('/vacation-plan', params={
                "origin": "A",
                "destination": "B",
                "arrival_date": arrival_date.isoformat(),
                "passengers": 2,
                "return_date": (arrival_date + timedelta(days=6)).isoformat(),
            })

        assert str(e.value) == '500, Server Error'

    def test_flight_services_circuit_breaker(self, client, mock_requests_get):
        mock_requests_get.get.side_effect = HTTPException('400, Bad Request')
        for attempt in range(MIN_FAILURE_ATTEMPTS + 1):
            try:
                client.get('/vacation-plan', params={
                    "origin": "A",
                    "destination": "B",
                    "arrival_date": datetime.now().date().isoformat(),
                    "passengers": 2,
                    "return_date": (datetime.now().date() + timedelta(days=6)).isoformat(),
                })
            except (HTTPException, ServiceUnavailable) as e:
                # After a MIN_FAILURE_ATTEMPTS is reached, exception has to be
                # of type ServiceUnavailable with circuit breaker pattern
                if not isinstance(e, ServiceUnavailable):
                    continue
                assert str(e.args[0]) == 'Service is not available at the moment'