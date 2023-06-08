import logging
from abc import ABC, abstractmethod
from functools import partial
from http import HTTPStatus
from typing import Optional, Union

import requests
from requests.models import Response

from exceptions import HTTPException
from utils import logger as default_logger


class Connector(ABC):

    _protocol: str

    def __init__(
        self, url: str,
        logger_formatter: Optional[logging.Formatter] = None
    ):
        self.url = url
        self._get_logger(formatter=logger_formatter)

    def _get_logger(self, formatter: logging.Formatter):
        logger = default_logger.setup_logger(
            logger_name=__name__, log_file=__file__,
            formatter=formatter
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

    def make_request(
        self,
        method: str,
        service: str,
        params: dict,
        **kwargs: Union[dict, None]
    ):
        _method = method.lower()
        if _method not in self._allowed_methods:
            raise HTTPException(f'send function does not support method {method}')

        params = (
            {'json': params}
            if _method != 'get'
            else {'data': params}
        )
        function = partial(getattr(requests, _method.lower()), **params)
        try:
            response = function(url=f"{self.url}/{service}")
            self._validate_response(response)
        except HTTPException as e:
            self.logger.exception(f'{self.__class__.__name__} error:: {str(e)}')
            raise e

        return response.json()

    @staticmethod
    def _validate_response(response: Response):
        if (
            HTTPStatus.BAD_REQUEST <= response.status_code
            <= HTTPStatus.INTERNAL_SERVER_ERROR
        ):
            raise HTTPException(f'{response.status_code}, {response.json()}')