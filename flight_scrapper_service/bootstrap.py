import importlib
import inspect
import logging

from domain.search.base import FlightsFinder
from infrastructure.publishers.kafka.publisher import KafkaPublisher
from infrastructure.publishers.redis.publisher import RedisPublisher
from infrastructure.repositories.redis.repository import RedisRepository
from infrastructure.scrappers.base import Scrapper, DriverFactory
from utils.connections.kafka_client import kafka_client
from utils.connections.redis_client import get_redis_client

logger = logging.Logger(__name__)

SCRAPPER_BASE_MODULE = 'infrastructure.scrappers'
FINDERS_BASE_MODULE = 'domain.search'


def bootstrap():
    dependencies = {
        'scrappers': get_available_scrappers(),
        'finders': get_available_finders(),
        'repositories': get_available_repositories(),
        'publishers' : get_available_publishers(),
    }
    return dependencies


def get_available_scrappers():
    classes: dict[str, Scrapper] = {}
    scrapper_file_name = 'scrapper.py'

    base_module = importlib.resources.files(SCRAPPER_BASE_MODULE)
    for resource in base_module.iterdir():
        if not resource.is_dir() and resource.name == '__pycache__':
            continue

        module_name = resource / scrapper_file_name
        if not module_name.is_file():
            logger.warning(f'Scrapper file not found in: {module_name}')
            continue

        try:
            spec = importlib.util.spec_from_file_location(
                f"{SCRAPPER_BASE_MODULE}.{resource}.scrapper",
                str(module_name)
            )
            if spec is None or spec.loader is None:
                logger.warning(f"Cannot create import spec for {module_name}")
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.exception(f"Failed to load module {module_name}: {e}")

        scrapper_cls = None
        for name, member in inspect.getmembers(module, inspect.isclass):
            if (
                'scrapper' in name.lower()
                and issubclass(member, Scrapper)
                and member is not Scrapper
            ):
                scrapper_cls = member
                logger.info(f'Scrapper found: {member}')
                break

        if not scrapper_cls:
            logger.warning(f'Scrapper class not found in {module_name}')
            continue

        try:
            instance = scrapper_cls(drivers_factory=DriverFactory)
            classes[resource.name] = instance
        except Exception as e:
            logger.exception(f"Failed to create instance of {scrapper_cls}: {e}")

    return classes


def get_available_finders():
    classes = {}

    base = importlib.resources.files(FINDERS_BASE_MODULE)
    for resource in base.iterdir():
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
        'memory': FlightsMemoryRepository(),
    }


def get_available_publishers():
    return {
        'redis': RedisPublisher(client_factory=get_redis_client),
        'kafka': KafkaPublisher(producer=kafka_client()),
        'memory': MemoryPublisher(),
    }
