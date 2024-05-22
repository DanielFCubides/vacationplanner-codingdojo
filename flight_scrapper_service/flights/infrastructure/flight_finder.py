from typing import Tuple, Union
from constants import RESPONSES_FLYING
from flights.application.search import (
    FlightsRepository
)
from http import HTTPStatus
from utils import loggers

logger = loggers.setup_logger(logger_name=__name__)

class FlightFinderWithConstant(FlightsRepository):

    def get(
        self, 
        *, 
        id_fly: int, 
        **kwargs
    ) -> Tuple[dict | list, int]:
        logger.info(f'Start getting a response with id {id_fly}')
        if id_fly <= 4:
            info = (RESPONSES_FLYING[id_fly], HTTPStatus.OK.value)
            logger.info(
                f'Get a correct response :: flights {info[0]} and status {info[1]}'
            )
            return info
        
        elif id_fly == 5:
            info = {"t": "Hello World"}, HTTPStatus.BAD_REQUEST.value
            logger.warning(
                f'Get a bad request :: flights {info[0]} and status {info[1]}'
            )
            return info
        
        else:
            info = {}, HTTPStatus.INTERNAL_SERVER_ERROR.value
            logger.exception(
                f'Get an internal server error :: flights {info[0]} and status {info[1]}'
            )
            return info

    def get_all(self):
        flight = RESPONSES_FLYING.values()
        return flight



