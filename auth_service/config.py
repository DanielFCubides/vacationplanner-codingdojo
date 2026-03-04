import yaml


def get_internal_router() -> dict:
    with open('routes.yml', 'r') as file:
        routes = yaml.safe_load(file)
    return routes


internal_routes = get_internal_router()