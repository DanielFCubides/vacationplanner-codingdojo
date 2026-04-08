import pytest

from infrastructure.repositories.base import FlightsRepository
from domain.models import FlightResults, SearchParams, Flights
from utils.flight_hash import create_search_params_hash


class FakeFlightsRepository(FlightsRepository):
    def __init__(self):
        self.client = {}
        self.search_params_list = []

    def get_flight_results(
        self, search_params: SearchParams
    ) -> FlightResults | list[None]:
        hash_ = create_search_params_hash(search_params)
        flights = []
        keys = list(filter(lambda k: hash_ in k, self.client.keys()))
        if not keys:
            return []

        for key in keys:
            element = self.client[key]
            flight_results = Flights.unflatten_results(element)
            flights.append(flight_results)

        return FlightResults(results=flights)

    def save_flight(self, flights: FlightResults, search_params: SearchParams) -> None:
        base_hash = create_search_params_hash(search_params)
        for index, data in enumerate(flights.results):
            flattened_results = data.flatten_results
            self.client[f'{base_hash}:{index}'] = flattened_results

        self.search_params_list.append(search_params)


@pytest.fixture
def fake_repository():
    return FakeFlightsRepository()
