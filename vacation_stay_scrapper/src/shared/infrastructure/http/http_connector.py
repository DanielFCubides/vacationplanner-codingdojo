"""
HTTP Connector

Provides HTTP client functionality with circuit breaker pattern.
"""
import logging
from abc import ABC, abstractmethod
from functools import partial
from http import HTTPStatus
from typing import Optional, Union, Dict, Any

import requests
from requests import RequestException
from requests.models import Response

from ...domain.exceptions import HTTPException as DomainHTTPException
from .circuit_breaker import CircuitBreaker
from ..logging.logger import setup_logger


class Connector(ABC):
    """Abstract base class for connectors"""
    
    _protocol: str

    def __init__(
        self,
        url: str,
        logger_formatter: Optional[logging.Formatter] = None
    ):
        """
        Initialize connector
        
        Args:
            url: Base URL for the service
            logger_formatter: Optional custom log formatter
        """
        self.url = url
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        self._get_logger(formatter=logger_formatter)

    def _get_logger(self, formatter: Optional[logging.Formatter] = None):
        """Setup logger for the connector"""
        logger = setup_logger(
            logger_name=__name__,
            formatter=formatter
        )
        self.logger = logger

    @abstractmethod
    def make_request(
        self,
        method: str,
        service: str,
        params: Dict[str, Any],
        **kwargs
    ) -> Any:
        """
        Make HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            service: Service endpoint path
            params: Request parameters/body
            **kwargs: Additional request options
            
        Returns:
            Response data
        """
        pass


class HTTPConnector(Connector):
    """HTTP connector implementation with circuit breaker"""
    
    _allowed_methods = ['get', 'post', 'put', 'patch', 'options', 'delete']
    _protocol = 'HTTP'

    def __init__(
        self,
        url: str,
        failure_attempts: int = 3,
        delay: int = 60
    ):
        """
        Initialize HTTP connector
        
        Args:
            url: Base URL for the service
            failure_attempts: Number of failures before circuit opens
            delay: Delay in seconds before retrying after circuit opens
        """
        super().__init__(url)
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            exceptions=(DomainHTTPException, RequestException),
            delay=delay,
            failure_attempts=failure_attempts
        )
    
    def make_request(
        self,
        method: str,
        service: str,
        params: Dict[str, Any],
        **kwargs
    ) -> Any:
        """
        Make HTTP request with circuit breaker protection
        
        Args:
            method: HTTP method
            service: Service endpoint
            params: Request parameters
            **kwargs: Additional options
            
        Returns:
            Response JSON data
            
        Raises:
            DomainHTTPException: If request fails or returns error status
        """
        return self.circuit_breaker(self._make_request)(
            method, service, params, **kwargs
        )
    
    def _make_request(
        self,
        method: str,
        service: str,
        params: Dict[str, Any],
        **kwargs
    ) -> Any:
        """Internal method to make HTTP request"""
        _method = method.lower()
        
        # Validate HTTP method
        if _method not in self._allowed_methods:
            msg = f'Method {method} not supported'
            self.logger.error(f'HTTP Connector :: {msg}')
            raise DomainHTTPException(msg)
        
        # Prepare request parameters
        request_params = (
            {'json': params}
            if _method != 'get'
            else {'params': params}
        )
        
        # Build full URL
        url = f"{self.url}/{service}"
        
        # Make request function
        function = partial(
            getattr(requests, _method),
            **request_params
        )
        
        try:
            response = function(url=url)
            self._validate_response(response)
            return response.json()
            
        except RequestException as e:
            self.logger.warning(
                f'HTTP Connector :: Connection refused to {url}: {str(e)}'
            )
            raise DomainHTTPException(str(e))
    
    def _validate_response(self, response: Response):
        """
        Validate HTTP response
        
        Args:
            response: HTTP response object
            
        Raises:
            DomainHTTPException: If response status >= 400
        """
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            error_msg = f'{response.status_code}, {response.text}'
            self.logger.error(f'HTTP Connector :: {error_msg}')
            raise DomainHTTPException(error_msg)
        
        self.logger.debug(
            f'HTTP Connector :: Success - URL: {response.url}, '
            f'Status: {response.status_code}'
        )
