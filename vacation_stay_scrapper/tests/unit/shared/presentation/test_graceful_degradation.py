"""
Unit tests for GracefulDegradationService.

Behaviour is checked through the public decorator, not the private
strategy registry:
    - default *_strategy functions are auto-registered
    - custom strategies passed to the constructor are merged in
    - unhandled exceptions are re-raised
"""
from unittest.mock import Mock

import pytest

from src.shared.domain.exceptions import (
    ServiceUnavailable,
    UnknownException,
)
from src.shared.presentation.exception_handlers import GracefulDegradationService


class TestGracefulDegradationService:

    def test_default_strategy_handles_service_unavailable(self):
        search_params = {'origin': 'a', 'destination': 'b', 'arrival_date': '20'}
        func = Mock(side_effect=ServiceUnavailable('service is unavailable'))
        service = GracefulDegradationService()

        result = service.handle_exception(func)(search_params=search_params)

        assert isinstance(result, dict)
        assert result['message']
        assert result['status'] == 'degraded'
        assert result['context'] == search_params

    def test_custom_strategy_is_merged_with_defaults(self):
        custom = Mock(return_value={'message': 'custom'})
        service = GracefulDegradationService(
            exception_handlers={UnknownException: custom}
        )

        custom_result = service.handle_exception(
            Mock(side_effect=UnknownException('boom'))
        )()
        default_result = service.handle_exception(
            Mock(side_effect=ServiceUnavailable('down'))
        )()

        assert custom_result == {'message': 'custom'}
        custom.assert_called_once()
        assert default_result['status'] == 'degraded'

    def test_unhandled_exception_is_reraised(self):
        service = GracefulDegradationService()

        with pytest.raises(RuntimeError):
            service.handle_exception(Mock(side_effect=RuntimeError('boom')))()
