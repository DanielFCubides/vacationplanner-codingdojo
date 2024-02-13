from datetime import datetime

from flask import Flask, jsonify
import random

from scrappers.airline1 import airline_scrapper
from flights.domain.flight_finder import FlightFinder
from flights.infrastructure.flight_finder import (
    FlightFinderWithConstant
    )

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"hello": "<p>Hello, World!</p>"}


@app.route("/airline1")
def airline1():
    repository = airline_scrapper.AirlineSearch()
    result = repository.get_flights()
    return result


@app.route("/flights_search")
def flight_finder():
    initial_departure_time = datetime(2024, 2, 13)
    arrival_departure_time = datetime(2024, 2, 23)
    from_ = 'BOG'
    to = 'CTG'
    passengers = 1
    repository = airline_scrapper.AirlineSearch()
    result = repository.get_flights_search(
        initial_departure_time,
        arrival_departure_time,
        from_,
        to,
        passengers
    )
    return jsonify({'title': result})


@app.route("/flights", methods=['GET'])
def flights():
    # TODO: Change method when filter are implemented
    id_fly = random.randint(1, 7)
    data, status = FlightFinder(
        repository=FlightFinderWithConstant()
    ).search(
        id_fly=id_fly
    )

    return jsonify(data), status
