from datetime import date
from typing import Union

from fastapi import FastAPI
from starlette import status
from services.flight_scrapper import FlightScrapper
from utils.connector import HTTPConnector

app = FastAPI()
FLIGHT_SCRAPPER_SERVICE = 'localhost:8000/'
http_connector = HTTPConnector(FLIGHT_SCRAPPER_SERVICE)
flight_services = FlightScrapper(http_connector)


@app.get('/')
def index():
    return {'message': 'hello world'}


@app.get('/vacation-plan', status_code=status.HTTP_200_OK)
def get_vacation_plan(
    origin: str,
    destination: str,
    arrival_date: date,
    passengers: int = 1, return_date: date | None = None,
    checked_baggage: int = 0, carry_on_baggage: int = 1,
) -> Union[list[None], list[dict], dict]:
    flights = flight_services.get_flights(
        search_params={
            "origin": origin,
            "destination": destination,
            "arrival_date": arrival_date,
            "passengers": passengers,
            "return_date": return_date,
            "checked_baggage": checked_baggage,
            "carry_on_baggage": carry_on_baggage
        }
    )
    return flights
