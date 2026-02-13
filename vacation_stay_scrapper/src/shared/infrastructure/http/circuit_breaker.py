"""
Circuit Breaker Pattern Implementation

Prevents cascading failures by opening circuit after consecutive failures.
"""
import functools
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Union, Tuple, Type

from ...domain.exceptions import (
    HTTPException,
    UnknownException,
    ServiceUnavailable
)
from ..logging.logger import setup_logger

logger = setup_logger(logger_name=__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSE = 'close'  # Normal operation, requests pass through
    OPEN = 'open'    # Circuit is open, requests are blocked


class CircuitBreaker:
    """
    Circuit Breaker implementation
    
    Protects against cascading failures by opening the circuit
    after a threshold of consecutive failures.
    """
    
    __last_retry_timestamp: Union[datetime, None] = None

    def __init__(
        self,
        exceptions: Tuple[Type[Exception], ...] = (HTTPException,),
        delay: float = 60,
        failure_attempts: int = 3
    ):
        """
        Initialize Circuit Breaker
        
        Args:
            exceptions: Tuple of exception types to catch
            delay: Delay in seconds before attempting recovery
            failure_attempts: Number of failures before opening circuit
        """
        self.exceptions = exceptions
        self.delay = delay
        self.failure_attempts = failure_attempts
        self._actual_failure_attempts = 0
        self.state = CircuitBreakerState.CLOSE

    def __call__(self, func: Callable):
        """
        Decorator to wrap function with circuit breaker
        
        Args:
            func: Function to protect
            
        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                self.handle_recovery()
            
            try:
                # Execute function
                response = func(*args, **kwargs)
                return response
                
            except Exception as e:
                # Handle errors and potentially open circuit
                self.handle_error(e)
                raise e

        return wrapper

    def handle_error(self, e: Exception):
        """
        Handle error and update circuit state
        
        Args:
            e: Exception that occurred
            
        Raises:
            ServiceUnavailable: If max failures reached
            UnknownException: If exception type is not expected
        """
        # Check if max failures reached
        if self._actual_failure_attempts >= self.failure_attempts:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f'Circuit Breaker :: Circuit OPENED - '
                f'Max retries ({self.failure_attempts}) reached'
            )
            raise ServiceUnavailable(
                'Service is not available at the moment'
            )
        
        # Check if exception type is expected
        if type(e) not in self.exceptions:
            msg = f'Unknown exception: {str(e)}'
            logger.warning(f'Circuit Breaker :: {msg}')
            raise UnknownException(msg)
        
        # Increment failure counter
        self._actual_failure_attempts += 1
        self.__last_retry_timestamp = datetime.now()
        
        logger.warning(
            f'Circuit Breaker :: Failure attempt '
            f'{self._actual_failure_attempts}/{self.failure_attempts}'
        )

    def handle_recovery(self):
        """
        Attempt to recover from open circuit state
        
        Raises:
            ServiceUnavailable: If recovery period hasn't elapsed
        """
        # Check if enough time has passed for recovery
        last_retry = self.__last_retry_timestamp + timedelta(
            seconds=self.delay
        )
        now = datetime.now()
        
        if last_retry <= now:
            # Recovery successful
            recover_after = now - last_retry
            self.state = CircuitBreakerState.CLOSE
            self.__last_retry_timestamp = None
            self._actual_failure_attempts = 0
            
            logger.warning(
                f'Circuit Breaker :: Circuit CLOSED - '
                f'Service recovered after {recover_after.seconds} seconds'
            )
            return
        
        # Still in recovery period
        msg = 'Service is not available at the moment'
        logger.warning(f'Circuit Breaker :: {msg}')
        raise ServiceUnavailable(msg)
