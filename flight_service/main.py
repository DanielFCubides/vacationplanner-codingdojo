import importlib
import logging
import os
import sys
from enum import Enum
from typing import Callable, Union

from bootstrap import bootstrap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flight_scrapper')


class ServerTypes(Enum):
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"


dependencies = bootstrap()


def app_factory(method: str) -> Union[Callable | bool]:
    presentations_root = "presentations"
    module_path = f"{presentations_root}.{method}.main"

    try:
        if importlib.util.find_spec(module_path) is None:
            logger.error(f"Error: package {module_path} does not exist.")
            return False

        module = importlib.import_module(module_path)

        if hasattr(module, 'main'):
            return module.main
        else:
            logger.error(f"No main() function found in the module {module_path}.")
            return False

    except ModuleNotFoundError as e:
        logger.error(f"The specified presentation layer does not exist: {method} - {str(e)}")
        return False
    except ImportError as e:
        logger.error(f"Failed to import module {method}: {str(e)}")
    except AttributeError as e:
        logger.error(f"Failed to execute main() in module {method}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error loading and executing module {method}: {str(e)}")

    return False


if __name__ == '__main__':
    method = ServerTypes(os.getenv('SERVER', ServerTypes.REST.value))
    logger.info(f'Starting a {method} server')

    main = app_factory(method.value)
    if not main:
        logger.error('Failed to start main server')
        sys.exit(1)

    main()
    logger.info(f'Finished executing {method} server')
