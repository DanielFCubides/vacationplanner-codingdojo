"""Production entry point for the selected flight-service API adapter."""

import os


def main() -> None:
    server = os.getenv("SERVER", "rest").lower()

    if server == "rest":
        from presentations.rest.main import create_app
        from waitress import serve

        serve(create_app(), host="0.0.0.0", port=8080)
    elif server == "graphql":
        from presentations.graphql.main import create_app
        from waitress import serve

        serve(create_app(), host="0.0.0.0", port=8080)
    elif server == "grpc":
        from presentations.grpc.main import main as grpc_main

        grpc_main()
    else:
        raise ValueError("SERVER must be one of: rest, graphql, grpc")


if __name__ == "__main__":
    main()
