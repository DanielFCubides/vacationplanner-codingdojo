import json
import logging
from typing import Callable

from flights.domain.repositories.base import FlightsRepository
from flights.domain.models import FlightResult, FlightResults, Flight, SearchParams
from utils.flight_hash import create_search_params_hash

logger = logging.getLogger(__name__)


class RedisRepository(FlightsRepository):

    def __init__(self, client_factory: Callable, database: int = 0):
        self.client = client_factory(database=database)

    def get_flight_results(
        self, search_params: SearchParams
    ) -> FlightResults | list[None]:
        hash_ = create_search_params_hash(search_params)
        pattern = f"{hash_}:*:*"
        flights = {}

        _, keys = self.client.scan(0, pattern, count=1000)
        # if there is no data in one database there is no into another
        if not keys:
            logger.info(f'No flights with hash {hash_}')
            return []

        for key in keys:
            _, flight_type, index = key.rsplit(':')
            data = self.client.hgetall(key)
            if not flights.get(index):
                flights[index] = {}
            flights[index].update({flight_type: Flight(**data)})

        flight_data = [
            FlightResult(**data)
            for data in flights.values()
        ]
        return FlightResults(results=flight_data)

    def save_flight(self, flights: FlightResults) -> None:
        hash_ = create_search_params_hash(flights.search_params)
        for index, data in enumerate(flights.results, start=1):
            for flight_type, flight in data.to_dict().items():
                key = f"{hash_}:{flight_type}:{index}"
                self.client.hset(key, mapping=flight)

        # put search params into a list
        self.client.lpush(
            'search_params', json.dumps(flights.search_params.to_dict())
        )
        logger.info(f'Flights {hash_} saved')
