import pytest

from flights.domain.repositories.base import FlightsRepository
from flights.domain.models import FlightResult, FlightResults, Flight, SearchParams
from utils.flight_hash import create_search_params_hash


class FakeFlightsRepository(FlightsRepository):
    def __init__(self):
        self.client = {}
        self.search_params_list = []

    def get_flight_results(
        self, search_params: SearchParams
    ) -> FlightResults | list[None]:
        hash_ = create_search_params_hash(search_params)
        flights = {}
        keys = list(filter(lambda k: hash_ in k, self.client.keys()))
        if not keys:
            return []
        for key in keys:
            _, flight_type, index = key.rsplit(':')
            data = self.client[key]
            flights[index].update({flight_type: Flight(**data)})

        results = [
            FlightResult(
                outbound=flight.get('outbound'),
                return_in=flight.get('return_in'),
            )
            for flight in flights.values()
        ]
        return FlightResults(results=results)

    def save_flight(self, flights: FlightResults) -> None:
        base_hash = create_search_params_hash(flights.search_params)
        for index, data in enumerate(flights.results, start=1):
            for flight_type, flight in data.to_dict().items():
                key = f"{base_hash}:{flight_type}:{index}"
                self.client[key] = flight

        self.search_params_list.append(flights.search_params)


@pytest.fixture
def fake_repository():
    return FakeFlightsRepository()
