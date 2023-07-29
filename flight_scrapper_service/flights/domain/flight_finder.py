from typing import Tuple, Union
from flights.application.search import (
    FlightsRepository
)
from utils import loggers

logger = loggers.setup_logger(logger_name=__name__)


class FlightFinder:

    def __init__(
            self,
            *,
            repository: FlightsRepository
    ):
        self.repository = repository

    
    def search(
            self, 
            *, 
            id_fly: int
    ) -> Tuple[dict | list, int]:
        logger.info('Start the service with a repository')
        return self.repository.get(
            id_fly=id_fly
        )
