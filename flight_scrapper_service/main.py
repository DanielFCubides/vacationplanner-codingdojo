import string

from flask import Flask, jsonify
import random

from graphql_server.flask import GraphQLView

from flights.domain.flight_finder import FlightFinder
from flights.infrastructure.flight_finder import (
    FlightFinderWithConstant
)

from presentations.grpc.grpc_hello_world import serve
from presentations.graphql import schema


REST = "rest"
GRPC = "grpc"
GRAPHQL = "graphql"


def create_app(method: string):
    if method == REST:
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

        return app
    if method == GRPC:
        return serve()
    if method == GRAPHQL:
        app = Flask(__name__)

        app.add_url_rule(
            '/graphql',
            view_func=GraphQLView.as_view(
                'graphql',
                schema=schema.my_schema,
                graphiql=True  # Habilita la interfaz GraphiQL
            )

        )

        return app



method = GRAPHQL
app = create_app(method)

if __name__ == "__main__":
    if method == REST or method == GRAPHQL:
        app.run(host="0.0.0.0", port=8080, debug=True)
    if method == GRPC:
        app()


