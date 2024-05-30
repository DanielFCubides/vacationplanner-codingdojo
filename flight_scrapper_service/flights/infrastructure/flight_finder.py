from typing import Tuple, Union, Any
from constants import RESPONSES_FLYING
from flights.application.search import (
    FlightsRepository
)
from utils import loggers

logger = loggers.setup_logger(logger_name=__name__)


class FlightFinderWithConstant(FlightsRepository):

    def get(
        self, 
        *, 
        id_fly: int, 
        **kwargs
    ) -> Union[Tuple[dict | list, int], None]:
        logger.info(f'Start getting a response with id {id_fly}')
        try:
            flight = RESPONSES_FLYING[id_fly]
            logger.info(
                f'Flight found :: flight {id_fly}'
            )
            return flight
        except KeyError:
            logger.error(
                f'Flight not found :: flight ID {id_fly}'
            )
            return None
        except Exception as e:
            logger.error(
                f'Unexpected error {e}'
            )
            raise

    def get_all(self) -> list[dict[str, Any]]:
        flights = RESPONSES_FLYING.values()
        logger.info(f'Successfully return flights :: flight qty {len(flights)}')
        return flights



