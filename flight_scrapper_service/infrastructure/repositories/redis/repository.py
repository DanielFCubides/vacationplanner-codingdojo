import json
import logging
from typing import Callable

from infrastructure.repositories.base import FlightsRepository
from domain.models import FlightResults, SearchParams, Flights
from utils.flight_hash import create_search_params_hash
from utils.json_decoders import FlightsJSONEncoder

logger = logging.getLogger(__name__)


class RedisRepository(FlightsRepository):

    def __init__(self, client_factory: Callable, database: int = 0):
        self.client = client_factory(database=database)

    def _make_hash(self, search_params: SearchParams) -> str:
        return create_search_params_hash(search_params)

    def get_flight_results(
        self, search_params: SearchParams
    ) -> FlightResults | list[None]:
        hash_ = self._make_hash(search_params)
        pattern = f'{hash_}:*'
        keys = self.client.keys(pattern)
        if not keys:
            logger.info(f'No flights found for {hash_}')
            return FlightResults(results=[])
        flights = []

        for key in keys:
            element = self.client.get(key)
            results = json.loads(element)
            flight_results = Flights.unflatten_results(results)
            flights.append(flight_results)
        return FlightResults(results=flights)

    def save_flight(self, flights: FlightResults, search_params) -> None:
        hash_ = self._make_hash(search_params)
        for index, result in enumerate(flights.results):
            flattened_results = result.flatten_results
            payload = json.dumps(flattened_results, cls=FlightsJSONEncoder)
            self.client.set(f'{hash_}:{index}', payload, ex=1800)

        # put search params into a list
        self.client.lpush('search_params', hash_)
        logger.info(f'Flights {hash_} saved')


def create_redis_repository(
    client_factory: Callable = None,
) -> RedisRepository:
    if client_factory is None:
        from utils.connections.redis_client import get_redis_client
        client_factory = get_redis_client

    return RedisRepository(client_factory=client_factory)