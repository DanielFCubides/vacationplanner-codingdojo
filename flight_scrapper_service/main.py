from flask import Flask
from flask import request
from fastapi.responses import JSONResponse
import random

from flight_scrapper_service.flights.domain.flight_finder import FlightFinder
from flight_scrapper_service.flights.infrastructure.flight_finder import FlightFinderWithConstant

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"hello": "<p>Hello, World!</p>"}


@app.route("/flights", methods=['GET'])
def flights():
    id_fly = random.randint(1, 7)

    data, status = FlightFinder(
        repository=FlightFinderWithConstant()
    ).search(
        id_fly=id_fly
    )

    return JSONResponse(content=data, status=status)
