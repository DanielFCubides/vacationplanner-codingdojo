import functools
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Union

from constants import MIN_DELAY_ATTEMPT, MIN_FAILURE_ATTEMPTS
from exceptions import HTTPException, UnknownException, ServiceUnavailable

logger = logging.getLogger(__name__)


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
            raise ServiceUnavailable('Service is not available at the moment')

        if type(e) not in self.exceptions:
            raise UnknownException('Unhandled Error')

        self._actual_failure_attempts += 1
        self.__last_retry_timestamp = datetime.now()

    def handle_recovery(self):
        last_retry = self.__last_retry_timestamp + timedelta(seconds=self.delay)
        if last_retry <= datetime.now():
            self.state = CircuitBreakerState.CLOSE
            self.__last_retry_timestamp = None
            self._actual_failure_attempts = 0
            return

        raise ServiceUnavailable('Service is not available at the moment')
