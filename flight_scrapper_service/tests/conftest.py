from unittest.mock import Mock, create_autospec

import pytest

from flights.bootstrap import get_available_finders, get_available_scrappers
from flights.domain.scrappers.base import Scrapper
from presentations.rest.main import create_app


@pytest.fixture
def mock_create_driver_function(monkeypatch):
    mock = Mock()
    monkeypatch.setattr('flights.domain.scrappers.base.create_driver', mock)
    return mock


@pytest.fixture
def mock_scrapper():
    scrapper = create_autospec(Scrapper)

    def scrapper_factory(**kwargs):
        scrapper.get_flights.return_value = kwargs.get('returned_value', [])
        scrapper.get_flights.side_effect = kwargs.get('side_effect', None)
        return scrapper

    return scrapper_factory


@pytest.fixture
def bootstrap_fixture(monkeypatch, mock_scrapper, mock_create_driver_function):
    def _bootstrap(airline: str = 'test_airline', scrappers=None, finders=None):
        real_scrappers = {airline: get_available_scrappers().popitem()[1]}
        real_finders = {airline: get_available_finders().popitem()[1]}
        dependencies = {
            'driver_factory': mock_create_driver_function,
            'scrappers': {airline: scrappers} if scrappers else real_scrappers,
            'finders': {airline: finders} if finders else real_finders
        }
        monkeypatch.setattr(
            'presentations.rest.main.dependencies',
            dependencies
        )
    return _bootstrap


@pytest.fixture
def test_client(bootstrap_fixture):
    app_ = create_app()
    app_.testing = True
    client = app_.test_client()
    return client

