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
            logger.info('Get a correct response')
            return RESPONSES_FLYING[id_fly], HTTPStatus.OK.value
        
        elif id_fly == 5:
            logger.warning('Get a bad request')
            return {"t": "Hello World"}, HTTPStatus.BAD_REQUEST.value
        
        else:
            logger.exception('Get an internal server error')
            return {}, HTTPStatus.INTERNAL_SERVER_ERROR.value
