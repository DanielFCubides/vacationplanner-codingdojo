import json
import logging

from flights.domain.repositories.base import FlightsRepository
from flights.domain.models import FlightResult, FlightResults, Flight
from utils.connections.redis_client import RedisClient
from utils.flight_hash import create_search_params_hash

logger = logging.getLogger(__name__)


class RedisRepository(FlightsRepository):

    databases_mapping: dict = {
        'outbound': 0,
        'return_in': 1,
    }

    def __init__(self, client: RedisClient):
        self.client = client
        self.clients = self.__get_clients()

    def __get_clients(self):
        return {
            key: self.client.get_client(database)
            for key, database in self.databases_mapping.items()
        }

    def get_flight_results(self, results_id: str) -> FlightResults | list[None]:
        pattern = f"{results_id}:*:*"
        flights = {}
        result_id = ""
        for flight_type, database in self.clients.items():
            _, keys = database.scan(0, pattern, count=1000)
            # if there is no data in one database there is no into another
            if not keys:
                logger.info(f'No flights with results_id {results_id}')
                return []

            for key in keys:
                _, id_, index = key.rsplit(':')
                if not result_id:
                    result_id = id_
                data = database.hgetall(key)
                id_ = data.pop('id')
                if not flights.get(index):
                    flights[index] = {'id_': id_}
                flights[index][flight_type] = Flight(**data)

        flight_data = [
            FlightResult(**data)
            for data in flights.values()
        ]
        return FlightResults(id_=result_id, results=flight_data)

    def save_flight(self, flights: FlightResults) -> None:
        hash_ = create_search_params_hash(flights.search_params)
        for index, data in enumerate(flights.results, start=1):
            flight_object = data.to_dict()
            for flight_type, database in self.clients.items():
                key = f"{hash_}:{flights.id_}:{index}"
                mapping = flight_object.get(flight_type)
                mapping['id'] = flight_object.get('id')
                database.hset(key, mapping=mapping)

        # put search params into a list
        database = self.clients.get('outbound')  # improve this selection
        database.lpush('search_params', json.dumps(flights.search_params.to_dict()))
        logger.info(f'Flights saved under key {hash_}')
