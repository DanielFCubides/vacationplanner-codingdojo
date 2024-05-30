import json
import pytest

from http import HTTPStatus

from main import app
from unittest.mock import Mock
from constants import RESPONSES_FLYING


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_random_int(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(
        "random.randint",
        mock.make_request
    )
    return mock


class TestGetFlights:

    def test_get_flights_success(self, client, mock_random_int):
        mock_random_int.make_request.return_value = 4
        response = client.get('/flights')
        assert response.status_code == HTTPStatus.OK.value
        assert json.loads(response.text) == RESPONSES_FLYING[4]

    def test_get_flights_error_with_status_400(self, client, mock_random_int):
        mock_random_int.make_request.return_value = 5
        response = client.get('/flights')
        assert response.status_code == HTTPStatus.NOT_FOUND.value

    def test_get_flights_error_with_status_500(self, client):
        client.side_effect = Exception('Boom!')
        with pytest.raises(Exception) as e:
            response = client.get('/flights')
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR.value
