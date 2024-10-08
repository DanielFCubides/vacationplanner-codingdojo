import importlib
import inspect
import logging

from flights.application.search import FlightsFinder
from flights.domain.repositories.redis.repository import RedisRepository
from flights.domain.scrappers.base import Scrapper, create_driver
from utils.connections.redis_client import get_redis_client

logger = logging.Logger(__name__)

SCRAPPER_BASE_MODULE = 'flights.domain.scrappers'
FINDERS_BASE_MODULE = 'flights.infrastructure'


def bootstrap():
    dependencies = {
        'driver_factory': create_driver,
        'scrappers': get_available_scrappers(),
        'finders': get_available_finders(),
        'repositories': get_available_repositories(),
    }
    return dependencies


def get_available_scrappers():
    classes = {}
    scrapper_file_name = 'scrapper'
    for resource in importlib.resources.files(SCRAPPER_BASE_MODULE).iterdir():
        if resource.is_dir() and resource.name != '__pycache__':
            spec = importlib.util.spec_from_file_location(
                scrapper_file_name, f'{resource}/{scrapper_file_name}.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            member, class_ = next(
                filter(
                    lambda mc: 'scrapper' in mc[0].lower() and inspect.isclass(mc[1]) and issubclass(mc[1], Scrapper),
                    inspect.getmembers(module)
                ),
                (None, None)
            )
            logger.info(f'Scrapper found: {member}')
            classes[resource.stem] = class_(create_driver=create_driver)
    return classes


def get_available_finders():
    classes = {}
    for resource in importlib.resources.files(FINDERS_BASE_MODULE).iterdir():
        if not resource.is_file() or resource.name in ['__pycache__', '__init__.py']:
            continue
        spec = importlib.util.spec_from_file_location(resource.name, resource)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        member, class_ = next(
            filter(
                lambda mc: resource.stem in mc[0].lower()
                and inspect.isclass(mc[1])
                and issubclass(mc[1], FlightsFinder),
                inspect.getmembers(module)
            ),
            (None, None)
        )
        logger.info(f'Scrapper found: {member}')
        classes[resource.stem] = class_
    return classes


def get_available_repositories():
    return {
        'redis': RedisRepository(client_factory=get_redis_client),
    }
