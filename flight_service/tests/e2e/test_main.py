import pytest
from main import app_factory

class TestAppFactoryE2E:

    def test_app_factory_loads_existing_rest_implementation():
        """
        Tests that when 'rest' is requested, the factory can
        actually locate and load the presentation.rest.main module
        without any mocking.
        """
        main_callable = app_factory('rest')

        assert callable(main_callable)
        assert main_callable.__name__ == 'main'

    def test_app_factory_fails_for_nonexistent_module():
        """
        Tests that requesting a non-existent method handles
        the absence gracefully and returns False rather than crashing.
        """
        result = app_factory('nonexistent_method')

        assert result is False
