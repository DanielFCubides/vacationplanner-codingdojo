import pytest

from flights.domain.repositories.base import FlightsRepository
from flights.domain.models import FlightResult, FlightResults, Flight
from utils.flight_hash import create_search_params_hash


class FakeFlightsRepository(FlightsRepository):
    def __init__(self):
        # Simulating a database with dictionaries for different databases
        self.databases: dict[str, dict[str, dict]] = {
            'return_in': {},
            'outbound': {},
        }

    def get_flight_results(self, results_id: str) -> FlightResults | list[None]:
        flights = {}
        result_id = ""
        for flight_type, database in self.databases.items():
            keys = list(filter(lambda k: results_id in k, database.keys()))
            if not keys:
                return []
            for key in keys:
                _, id_, index = key.rsplit(':')
                if not result_id:
                    result_id = id_
                data = database[key]
                flight_id = data.pop('id_')
                if not flights.get(index):
                    flights[index] = {'id_': flight_id}
                flights[index][flight_type] = Flight(**data)

        results = [
            FlightResult(
                id_=flight.get('id_'),
                outbound=flight.get('outbound'),
                return_in=flight.get('return_in'),
            )
            for flight in flights.values()
        ]
        return FlightResults(id_=result_id, results=results)

    def save_flight(self, flights: FlightResults) -> None:
        base_hash = create_search_params_hash(flights.search_params)
        for index, data in enumerate(flights.results, start=1):
            for flight_type, database in self.databases.items():
                key = f"{base_hash}:{flights.id_}:{index}"
                database[key] = {
                    'id_': getattr(data, 'id_'),
                    **getattr(data, flight_type).to_dict()
                }


@pytest.fixture
def fake_repository():
    return FakeFlightsRepository()
