import json
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from starlette import status
from starlette.testclient import TestClient

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