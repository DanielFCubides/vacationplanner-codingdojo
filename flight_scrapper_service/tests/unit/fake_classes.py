from constants import FLIGHTS
from flights.application.search import FlightsRepository
from flights.domain.scrappers.models import SearchParams, FlightResult
from utils import loggers

logger = loggers.setup_logger(logger_name=__name__)


class FlightFinderWithConstant(FlightsRepository):

    def get_flights(self, search_params: SearchParams) -> list[FlightResult | None]:
        origin = search_params.origin
        destination = search_params.destination
        logger.info(
            f'Start getting a response with origin {origin} '
            f'and destination {destination}'
        )
        try:
            flights = [
                flight
                for flight in FLIGHTS
                if flight["origin"] == origin
                and flight["destination"] == destination
            ]
            if not flights:
                raise KeyError

            logger.info(f'Flights found from {origin} to {destination}')
            results = [
                FlightResult(
                    price=flight.get("price", 0),
                    flight_time=flight.get('fligth_time'),
                    arrival_date=flight.get('arrival_date'),
                    return_date=flight.get('return_date'),
                )
                for flight in flights
            ]
            return results
        except KeyError:
            logger.error(f'Flights not found from {origin} to {destination}')
            return []
        except Exception as e:
            logger.error(f'Unexpected error {e}')
            raise
