"""
Exception Handlers for FastAPI

Provides graceful degradation and exception handling strategies.
"""
import functools
import inspect
from typing import Callable, Optional, Dict, Type, Any

from ...domain.exceptions import (
    ServiceUnavailable,
    DomainException,
    HTTPException as DomainHTTPException,
    EntityNotFound,
    ValidationError,
    BusinessRuleViolation
)
from ..logging.logger import setup_logger

_logger = setup_logger(logger_name=__name__)

ExceptionStrategy = Callable[[Exception, Dict[str, Any]], Dict[str, Any]]


def service_unavailable_strategy(
    e: ServiceUnavailable,
    **kwargs
) -> Dict[str, Any]:
    """
    Strategy for handling service unavailable errors
    
    Args:
        e: ServiceUnavailable exception
        **kwargs: Context from execution
        
    Returns:
        Fallback response dictionary
    """
    _logger.warning(
        f'Graceful Degradation :: Service unavailable - {str(e)}'
    )
    
    # TODO: Add dead letter queue for unhandled requests
    # TODO: Add request tracking (user_id, request_id, etc.)
    
    return {
        'message': 'Service temporarily unavailable. Please try again later.',
        'status': 'degraded',
        'context': kwargs.get('search_params', {})
    }


def entity_not_found_strategy(
    e: EntityNotFound,
    **kwargs
) -> Dict[str, Any]:
    """Strategy for handling entity not found errors"""
    _logger.warning(f'Entity Not Found :: {str(e)}')
    
    return {
        'message': str(e),
        'entity_type': e.entity_type,
        'entity_id': e.entity_id
    }


def validation_error_strategy(
    e: ValidationError,
    **kwargs
) -> Dict[str, Any]:
    """Strategy for handling validation errors"""
    _logger.warning(f'Validation Error :: {str(e)}')
    
    return {
        'message': 'Validation failed',
        'details': str(e)
    }


class GracefulDegradationService:
    """
    Provides graceful degradation for service exceptions
    
    Allows registering custom exception handling strategies
    """
    
    _exceptions: Dict[Type[Exception], ExceptionStrategy]

    def __init__(
        self,
        exception_handlers: Optional[
            Dict[Type[Exception], ExceptionStrategy]
        ] = None,
    ):
        """
        Initialize Graceful Degradation Service
        
        Args:
            exception_handlers: Custom exception strategies to register
        """
        self._exceptions = {}
        self._get_initial_exception_handlers()
        
        # Merge with custom handlers
        if exception_handlers:
            self._exceptions.update(exception_handlers)

    def _get_initial_exception_handlers(self):
        """
        Auto-discover exception handlers defined as *_strategy functions
        
        Scans module globals for functions ending with '_strategy'
        and registers them based on their first parameter type annotation
        """
        for name, func in globals().items():
            if name.endswith('_strategy') and inspect.isfunction(func):
                signature = inspect.signature(func)
                
                # Get exception type from first parameter annotation
                for param_name, param in signature.parameters.items():
                    if param_name != 'kwargs' and param.annotation != inspect.Parameter.empty:
                        try:
                            if issubclass(param.annotation, Exception):
                                self._exceptions[param.annotation] = func
                                break
                        except TypeError:
                            # Not a class, skip
                            continue

    def handle_exception(self, func: Callable):
        """
        Decorator to wrap function with graceful degradation
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function with exception handling
            
        Usage:
            @graceful_degradation.handle_exception
            def get_flights(search_params):
                # ... implementation
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                # Look for registered handler
                handler = self._exceptions.get(type(e))
                
                if handler:
                    _logger.info(
                        f'Graceful Degradation :: Handling {type(e).__name__} '
                        f'with strategy'
                    )
                    return handler(e, **kwargs)
                
                # No handler found, re-raise
                _logger.error(
                    f'Graceful Degradation :: No handler for {type(e).__name__}'
                )
                raise e

        return wrapper
    
    def register_handler(
        self,
        exception_type: Type[Exception],
        strategy: ExceptionStrategy
    ):
        """
        Register a new exception handler
        
        Args:
            exception_type: Exception class to handle
            strategy: Strategy function to handle the exception
        """
        self._exceptions[exception_type] = strategy
        _logger.info(
            f'Graceful Degradation :: Registered handler for {exception_type.__name__}'
        )
