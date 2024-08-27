import json
import logging
from collections import OrderedDict

from flask import Flask, request

from flights.domain.scrappers.models import SearchParams
from main import dependencies
from utils.urls import DynamicURL


logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    @app.route("/get_flights", methods=['POST'])
    def get_flights():
        base_data = request.json
        airline = base_data.pop('airline').lower()
        base_url = base_data.pop('base_url', 'https://www.avianca.com/es/booking/select/')
        search_data = SearchParams(**base_data.get('search_params'))
        dynamic_url = DynamicURL.from_url(base_url)
        scrapper = dependencies['scrappers'].get(airline)(
            create_driver=dependencies.get('driver_factory')
        )
        finder = dependencies['finders'].get(airline)(dynamic_url, scrapper)
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

    @app.route("/v2/get_flights", methods=['POST'])
    def get_flight2():
        base_data = request.json
        airline = base_data.pop('airline').lower()
        base_url = base_data.pop('base_url', 'https://www.avianca.com/pricing/api/v1/journeys')
        search_data = SearchParams(**base_data.get('search_params'))
        dynamic_url = base_url
        scrapper = dependencies['scrappers'].get(airline)()
        finder = dependencies['finders'].get(airline)(
            dynamic_url,
            scrapper,
            'd9eaa63c9008987381860a36e0d8c2aa2c6a936b41bf35e42bbe11e97bd452ea'
        )
        results = finder.get_flights(search_data)
        return results, 200

    @app.route("/")
    def hello_world():
        return {"hello": "<p>Hello, World!</p>"}

    return app


def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()
