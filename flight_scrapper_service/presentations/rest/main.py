import logging
from collections import OrderedDict
from datetime import datetime

from flask import Flask, request

from constants import AVIANCA_URL
from flights.domain.scrappers.models import SearchParams
from main import dependencies
from utils.urls import DynamicURL


logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    @app.route("/get_flights", methods=['POST'])
    def get_flights():
        # TODO replace this logic for a serialization methods
        try:
            airline = request.json.pop('airline').lower()
            base_url = request.json.pop('base_url', AVIANCA_URL)
            search_data = SearchParams(**request.json.get('search_params'))
        except KeyError as e:
            return {'error': f'Missing parameter: {e}'}, 400
        except TypeError as e:
            try:
                missing_parameters = e.args[0].split(':')[1].strip().replace('\'', '')
                return {'error': f'Missing search_params: {missing_parameters}'}, 400
            except IndexError:
                return {'error': f'Missing search_params'}, 400

        dynamic_url = DynamicURL.from_url(base_url)

        try:
            scrapper = dependencies['scrappers'][airline]
            finder = dependencies['finders'].get(airline)(dynamic_url, scrapper)
        except KeyError as e:
            return {'error': f'Airline dont available: {e}'}, 400

        try:
            results = finder.get_flights(search_data)
            response = OrderedDict(
                count=len(results),
                flights={
                    "arrival_date": search_data.arrival_date,
                    "return_date": search_data.return_date,
                    "results": results
                }
            )
            return response, 200
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
