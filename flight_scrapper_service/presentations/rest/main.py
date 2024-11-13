import logging
from datetime import datetime

from flask import Flask, request
from pydantic import ValidationError

from constants import config
from flights.domain.models import SearchParams
from main import dependencies
from presentations.rest.models.inputs import Inputs, SearchParamsInputModel


logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    repository_name = config['Default']['repository']
    publisher_name = config['Default']['publisher']

    @app.route("/get_flights", methods=['POST'])
    def get_flights():
        try:
            params = Inputs(
                airline=request.json['airline'],
                search_params=SearchParamsInputModel(**request.json.get('search_params', {}))
            )
        except ValidationError as e:
            logger.error(e)
            return e.errors(), 400
        except KeyError as e:
            logger.error(e)
            return {'errors': {'airline': f"Missing value"}}, 400

        try:
            scrapper = dependencies['scrappers'][params.airline]
            repository = dependencies['repositories'][repository_name]
            publisher = dependencies['publishers'][publisher_name]
            finder = dependencies['finders'].get(params.airline)(
                scrapper=scrapper,
                repository=repository,
                publisher=publisher
            )
        except KeyError as e:
            return {'error': f'Airline {e} dont available'}, 400

        try:
            results = finder.get_flights(
                SearchParams(
                    **params.search_params.model_dump()
                )
            )
            return results, 200
        except Exception as e:
            logger.error(e)
            return {'message': 'Something went wrong'}, 400

    @app.route("/")
    def hello_world():
        return {"status": "alive", "timestamp": datetime.now()}

    return app


def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()
