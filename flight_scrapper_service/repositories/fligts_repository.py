from abc import abstractmethod, ABC

from repositories.connections.redis_client import RedisClient
import hashlib


class FlightsRepo(ABC):
    @abstractmethod
    def get_flight(
            self,
            *,
            id_fly: int,
    ) -> dict:
        """
        Obtain a flight with all information
        """
        pass

    @abstractmethod
    def save_flight(
            self,
            *,
            flight: dict,
    ) -> int:
        """
        save a flight with all information
        """
        pass


class RedisRepo(FlightsRepo):
    client = RedisClient()

    def get_flight(self, *, id_fly: str) -> dict:
        hash = hashlib.sha1(id_fly.encode('utf8')).hexdigest()
        flight = self.client.connection.hgetall(hash)
        print(flight)
        return flight

    def save_flight(self, *, flight: dict) -> int:
        hash = hashlib.sha1(flight.get("id_flight", "flight_1").encode('utf8')).hexdigest()
        self.client.connection.hset(hash, mapping=flight)
        return 1
