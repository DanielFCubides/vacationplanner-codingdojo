from typing import Union
from flight_scrapper_service.constants import RESPONSES_FLYING
from flight_scrapper_service.flights.application.search import (
    FlightsRepository
)
from http import HTTPStatus

class FlightFinderWithConstant(FlightsRepository):

    def get(
        self, 
        *, 
        id_fly: int, 
        **kwargs
    ) -> Union[(dict, list), int]:
        
        if id_fly <= 4:
            return RESPONSES_FLYING[id_fly], HTTPStatus.OK.value 
        
        elif id_fly == 5:
            return {"t": "Hello World"}, HTTPStatus.BAD_REQUEST.value
        
        else:
            return {}, HTTPStatus.INTERNAL_SERVER_ERROR.value
