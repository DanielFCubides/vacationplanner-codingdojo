from datetime import date
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from starlette import status
from services.flight_scrapper import FlightScrapper
from utils.connector import HTTPConnector

app = FastAPI()
FLIGHT_SCRAPPER_SERVICE = 'localhost:8000/'
http_connector = HTTPConnector(FLIGHT_SCRAPPER_SERVICE)
flight_services = FlightScrapper(http_connector)


class SearchParams(BaseModel):
    origin: str
    destination: str
    arrival_date: date
    passengers: int = 1
    checked_baggage: int = 0
    carry_on_baggage: int = 1
    return_date: Optional[date] = None


@app.get('/')
def index():
    return {'message': 'health-check'}, status.HTTP_200_OK


@app.post('/vacation-plan', status_code=status.HTTP_200_OK)
def get_vacation_plan(search_params: SearchParams) -> dict:
    flights = flight_services.get_flights(
        search_params={
            "origin": search_params.origin,
            "destination": search_params.destination,
            "arrival_date": search_params.arrival_date,
            "passengers": search_params.passengers,
            "return_date": search_params.return_date,
            "checked_baggage": search_params.checked_baggage,
            "carry_on_baggage": search_params.carry_on_baggage
        }
    )
    return flights
