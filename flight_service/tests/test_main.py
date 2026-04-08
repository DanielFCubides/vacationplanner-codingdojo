import importlib
import importlib.util
import types

import pytest

from main import app_factory



class TestAppFactory:

    def test_app_factory_returns_rest_main_callable(self):
        main_callable = app_factory('rest')

        assert callable(main_callable)
        assert main_callable.__name__ == 'main'


    def test_app_factory_handles_module_missing_main(self, monkeypatch):
        fake_module = types.ModuleType('presentations.fake.main')
        monkeypatch.setattr(importlib.util, 'find_spec', lambda module: True)
        monkeypatch.setattr(importlib, 'import_module', lambda module: fake_module)

        assert app_factory('fake') is False


    @pytest.mark.parametrize(
        'raised_exc',
        [
            ModuleNotFoundError('missing module'),
            ImportError('failed import'),
            AttributeError('missing attr'),
            RuntimeError('unexpected error'),
        ]
    )
    def test_app_factory_handles_all_exceptions(self, monkeypatch, raised_exc):
        monkeypatch.setattr(importlib.util, 'find_spec', lambda module: True)

        def _import_module(module_path):
            raise raised_exc

        monkeypatch.setattr(importlib, 'import_module', _import_module)

        assert app_factory('rest') is False
