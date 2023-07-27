from typing import Callable
from unittest.mock import Mock

import exceptions
from utils.exception_handler import GracefulDegradationService


class TestExceptionHandler:

    reference = GracefulDegradationService

    def test_create_and_exception_handler(self):
        exception_handler = self.reference()
        assert exception_handler
        assert exception_handler.exceptions

        # test default handler
        handler = exception_handler.exceptions.get(
            type(exceptions.ServiceUnavailable())
        )
        assert handler

    def test_create_an_exception_handler_with_more_strategies(self):
        handlers: dict[type[Exception], Callable] = {
            exceptions.UnknownException: lambda *args: None,
            exceptions.HTTPException: lambda *args: None
        }
        exception_handler = self.reference(exception_handlers=handlers)
        assert len(exception_handler.exceptions) == 3
        for exc, value in handlers.items():
            func = exception_handler.exceptions.get(type(exc()))
            assert func
            assert func == value

    def test_exception_handler(self):
        mock = Mock()
        search_params = {'origin': 'a', 'destination': 'b', 'arrival_date': '20'}
        mock.side_effect = exceptions.ServiceUnavailable('service is unavailable')
        exception_handler = self.reference()

        # emulate decorator way
        func = exception_handler.handle_exception(mock)(search_params=search_params)
        assert isinstance(func, dict)
        assert func.get('message')
        assert func.get('search_params') == search_params