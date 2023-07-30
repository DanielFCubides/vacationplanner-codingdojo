import functools
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Union

from constants import MIN_DELAY_ATTEMPT, MIN_FAILURE_ATTEMPTS
from exceptions import HTTPException, UnknownException, ServiceUnavailable
from utils import logger as default_logger

logger = default_logger.setup_logger(logger_name=__name__)


class CircuitBreakerState(str, Enum):
    CLOSE = 'close'
    OPEN = 'open'


class CircuitBreaker:

    __last_retry_timestamp: Union[datetime, None]

    def __init__(
        self,
        exceptions: tuple[type[Exception], ...] = (HTTPException, ),
        delay: float = MIN_DELAY_ATTEMPT,
        failure_attempts: int = MIN_FAILURE_ATTEMPTS
    ):
        self.exceptions = exceptions
        self.delay = delay
        self.failure_attempts = failure_attempts
        self._actual_failure_attempts = 0
        self.state = CircuitBreakerState.CLOSE

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == CircuitBreakerState.OPEN:
                self.handle_recovery()
            try:
                response = func(*args, **kwargs)
                return response
            except HTTPException as e:
                self.handle_error(e)
                raise e

        return wrapper

    def handle_error(self, e: Exception):
        if self._actual_failure_attempts >= self.failure_attempts:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                'Error Handling :: maximum retries connection reached '
                'external service unavailable'
            )
            raise ServiceUnavailable('Service is not available at the moment')

        if type(e) not in self.exceptions:
            msg = f'Unknown reason {e.args[0]}'
            logger.warning(f'Error handling :: {msg}')
            raise UnknownException(msg)

        self._actual_failure_attempts += 1
        self.__last_retry_timestamp = datetime.now()
        logging.warning(
            f'Error handling :: '
            f'trying to reach service after {self._actual_failure_attempts} attempts'
        )

    def handle_recovery(self):
        last_retry = self.__last_retry_timestamp + timedelta(seconds=self.delay)
        now = datetime.now()
        if last_retry <= now:
            recover_after = now - last_retry
            self.state = CircuitBreakerState.CLOSE
            self.__last_retry_timestamp = None
            self._actual_failure_attempts = 0
            logger.warning(
                f'Service Recovery :: '
                f'service available after {recover_after.seconds} seconds'
            )
            return

        msg = 'Service is not available at the moment'
        logger.warning(f'Service Recovery :: {msg}')
        raise ServiceUnavailable(msg)
