import functools
import inspect

import exceptions
from typing import Callable, Optional
from utils import logger as default_logger


_logger = default_logger.setup_logger(logger_name=__name__)

exception_strategy = Callable[[Exception, ...], dict]


def service_unavailable_strategy(e: exceptions.ServiceUnavailable, **kwargs):
    # TODO add a dead letter queue system to handle unhandled requests
    # TODO add more information to requests (like user id or any other identification)
    _logger.warning(
        f'graceful degradation service :: '
        f'unhandled request due exception {e}'
    )
    return {
        'message': 'We are getting your flights, please be patience',
        'search_params': kwargs.get('search_params', {})
    }


class GracefulDegradationService:

    _exceptions: dict[type[Exception], exception_strategy]


    def __init__(
        self,
        exception_handlers: Optional[dict[type[Exception], exception_strategy]] = None,
    ):
        """
        params:
            exception_handlers:
                dict with exceptions and their respective strategies, those strategies
                must have only 2 arguments (e: Exception, and kwargs:
                context from above execution)
        """
        self._get_initial_exceptions_handlers()
        self.exceptions = self._exceptions | (exception_handlers or {})

    def _get_initial_exceptions_handlers(self):
        """get all the strategy functions in the file"""
        for name, func in globals().items():
            if name.endswith('_strategy') and inspect.isfunction(func):
                signature = inspect.signature(func)
                self._exceptions = {
                    param.annotation: func
                    for _, param in
                    signature.parameters.items()
                    if issubclass(param.annotation, Exception)
                }

    def handle_exception(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                _handler = self.exceptions.get(type(e))
                if not _handler:
                    raise e
                return _handler(e, **kwargs)

        return wrapper
