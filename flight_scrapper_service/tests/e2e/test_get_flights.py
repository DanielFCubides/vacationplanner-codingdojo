from http import HTTPStatus
from unittest.mock import Mock
from constants import RESPONSES_FLYING
import pytest
from main import app
import webtest
import json

@pytest.fixture
def client():
    return webtest.TestApp(app)


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
        with pytest.raises(webtest.app.AppError) as e:
            response = client.get('/flights')
            assert response.status_code == HTTPStatus.BAD_REQUEST.value
            assert json.loads(response.text) == {"t": "Hello World"}

    def test_get_flights_error_with_status_500(self, client, mock_random_int):
        mock_random_int.make_request.return_value = 6
        with pytest.raises(webtest.app.AppError) as e:
            response = client.get('/flights')
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR.value
            assert json.loads(response.text) == {}
