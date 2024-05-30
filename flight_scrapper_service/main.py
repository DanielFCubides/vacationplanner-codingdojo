import os
import string
from enum import Enum

from flask import Flask, jsonify
import random

from graphql_server.flask import GraphQLView

from flights.domain.flight_finder import FlightFinder
from flights.infrastructure.flight_finder import (
    FlightFinderWithConstant
)

from presentations.grpc.grpc_hello_world import serve
from presentations.interface import schema


class ServerTypes(Enum):
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"


def create_app(method: string):
    if method == ServerTypes.REST.value:
        app = Flask(__name__)


        @app_.route("/")
        def hello_world():
            return {"hello": "<p>Hello, World!</p>"}

        @app_.route("/flights", methods=['GET'])
        def flights():
            id_fly = random.randint(1, 7)
            try:
                data = FlightFinder(
                    repository=FlightFinderWithConstant()
                ).search(
                    id_fly=id_fly
                )
                if not data:
                    return {},  404
                return jsonify(data), 200
            except Exception:
                return {}, 500

        return app
    if method == ServerTypes.GRPC.value:
        return serve()
    if method == ServerTypes.GRAPHQL.value:
        app = Flask(__name__)

        app.add_url_rule(
            '/graphql_server',
            view_func=GraphQLView.as_view(
                'graphql_server',
                schema=schema.my_schema,
                graphiql=True
            )

        )

        return app


method = ServerTypes(os.getenv('SERVER', ServerTypes.GRPC.value))
app = create_app(method.value)


if __name__ == "__main__":
    if method == ServerTypes.REST or method == ServerTypes.GRAPHQL:
        app.run(host="0.0.0.0", port=8080, debug=True)
    if method == ServerTypes.GRPC:
        app()
