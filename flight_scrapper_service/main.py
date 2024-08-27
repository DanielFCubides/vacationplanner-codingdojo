import importlib
import logging
import os
from enum import Enum

from flights.bootstrap import bootstrap


logger = logging.getLogger(__name__)


class ServerTypes(Enum):
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"


dependencies = bootstrap()


def app_factory(method: str):
    try:
        root_path = os.path.dirname(__file__)
        module_path = os.path.join(root_path, 'presentations', method, 'main.py')

        if not os.path.exists(module_path):
            logger.error(f"Error: {module_path} does not exist.")
            return False

        spec = importlib.util.spec_from_file_location(f"main", module_path)
        if spec is None:
            logger.error(f"Failed to create module spec for {module_path}")
            return False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'main'):
            module.main()
            return True
        else:
            logger.error("No main() function found in the module.")
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

    executed = app_factory(method.value)
    logger.info(f'Finished executing {method} server with status {executed}')
