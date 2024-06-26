import logging
from abc import ABC, abstractmethod
from functools import partial
from http import HTTPStatus
from typing import Optional, Union

import requests
from requests import RequestException
from requests.models import Response

from constants import MIN_FAILURE_ATTEMPTS, MIN_DELAY_ATTEMPT
from exceptions import HTTPException
from utils import logger as default_logger
from utils.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(
    exceptions=(HTTPException, RequestException),
    delay=MIN_DELAY_ATTEMPT,
    failure_attempts=MIN_FAILURE_ATTEMPTS
)


class Connector(ABC):

    _protocol: str

    def __init__(
        self, url: str,
        logger_formatter: Optional[logging.Formatter] = None
    ):
        self.url = url
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        self._get_logger(formatter=logger_formatter)

    def _get_logger(self, formatter: logging.Formatter):
        logger = default_logger.setup_logger(
            logger_name=__name__, formatter=formatter
        )
        self.logger = logger

    @abstractmethod
    def make_request(
        self,
        method: str,
        service: str,
        params: dict,
        **kwargs: Union[dict, None]
    ):
        """Send Information"""


class HTTPConnector(Connector):

    _allowed_methods = ['get', 'post', 'put', 'patch', 'options']
    _protocol = 'HTTP'

    def __init__(self, url: str):
        super().__init__(url)

    @circuit_breaker
    def make_request(
        self,
        method: str,
        service: str,
        params: dict,
        **kwargs: Union[dict, None]
    ):
        _method = method.lower()
        if _method not in self._allowed_methods:
            msg = f'Connection Interrupted :: method {method} not supported'
            self.logger.error(f'Connection Interrupted :: {msg}')
            raise HTTPException(msg)

        params = (
            {'json': params}
            if _method != 'get'
            else {'data': params}
        )
        function = partial(getattr(requests, _method.lower()), **params)
        url = f"{self.url}/{service}"
        try:
            response = function(url=url)
            self._validate_response(response)
            return response.json()
        except RequestException as e:
            self.logger.warning(f'Connection Refused :: url: {url} {e.args[0]}')
            raise HTTPException(e.args[0])

    def _validate_response(self, response: Response):
        # passthrough for every status code below 400
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise HTTPException(f'{response.status_code}, {response.text}')

        self.logger.debug(
            f'Connection successfully :: url: {response.url} '
            f'response: {response.text}'
        )
