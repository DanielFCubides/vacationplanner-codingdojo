from flask import Flask, jsonify
import random

from flights.domain.flight_finder import FlightFinder
from flights.infrastructure.flight_finder import FlightFinderWithConstant

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

    return jsonify(data), status
