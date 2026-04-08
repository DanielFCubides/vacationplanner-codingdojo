import logging
from datetime import datetime

from flask import Flask, request
from pydantic import ValidationError

from constants import config
from domain.models import SearchParams
from infrastructure.feature_flag.flags import feature_flag_client
from infrastructure.feature_flag.memory_provider import WELCOME_MESSAGE_FLAG
from main import dependencies
from presentations.rest.models.inputs import Inputs, SearchParamsInputModel


logger = logging.getLogger(__name__)


def validate(token):

    # RcH2bDSulD_EMPAPNBc8Nl-JKcFttcX2wFOdkPXEc7g
    token_kid = "RcH2bDSulD_EMPAPNBc8Nl-JKcFttcX2wFOdkPXEc7g"
    print(token)

    # decode the jwt, get the KID.


    import requests
    url = "https://keycloack.dfcubidesc.com/realms/habit-tracker/protocol/openid-connect/certs"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    kids = response.json()["keys"]
    print("KID:", kids)
    kids.find(token_kid)



    return True


def create_app():
    app = Flask(__name__)
    repository_name = config['Default']['repository']
    publisher_name = config['Default']['publisher']

    @app.route("/get_flights", methods=['POST'])
    def get_flights():
        try:
            params = Inputs(
                airline=request.json.get('airline', config['Default']['airline']),
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
            repository = dependencies['repositories'][repository_name]()
            publisher = dependencies['publishers'][publisher_name]()
            finder = dependencies['finders'].get(params.airline)(
                scrapper=scrapper,
                repository=repository,
                publisher=publisher
            )
        except KeyError as e:
            return {'error': f'Dependency {e} dont available'}, 400

        try:
            results = finder.get_flights(
                SearchParams(
                    **params.search_params.model_dump()
                )
            )
            return [result.to_dict() for result in results.results], 200
        except Exception as e:
            logger.error(e)
            return {'message': 'Something went wrong'}, 400

    @app.route("/")
    def hello_world():
        is_message_on = feature_flag_client.get_boolean_value(WELCOME_MESSAGE_FLAG, False)
        return {"status": "alive" if is_message_on else "running", "timestamp": datetime.now()}

    return app


def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)
    app.logger.setLevel(logging.INFO)


if __name__ == "__main__":
    main()
