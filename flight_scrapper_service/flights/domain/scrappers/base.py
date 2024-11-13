import logging
from abc import ABC, abstractmethod
from typing import Any, Union, Callable

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from flights.domain.models import FlightResults, SearchParams
from constants import config

logger = logging.getLogger(__name__)


AVAILABLE_DRIVERS = {
    'firefox': FirefoxOptions(),
}


def create_driver(
    driver_name: str,
    capabilities: dict[str, Any],
    selenium_hub: Union[str, None] = None
):
    options = AVAILABLE_DRIVERS.get(driver_name)
    if not options:
        raise ValueError(f'Driver {driver_name} not available')
    for name, value in capabilities.items():
        options.set_capability(name, value)
    options.add_argument('--incognito')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")

    hub = selenium_hub or f"{config['Selenium']['host']}:{config['Selenium']['port']}"
    driver = webdriver.Remote(
        options=options, command_executor=hub
    )
    return driver


class Scrapper(ABC):

    create_driver: Callable
    capabilities: dict[str, Any]
    name: str

    def _initialize_config(self):
        assert self.name, 'Scrapper class needs name attribute'
        self.config = type(
            'Config',
            (),
            {**config[f'Scrappers.{self.name}']}
        )
        self.config()

    def _initialize_driver(self):
        for driver_name in AVAILABLE_DRIVERS.keys():
            try:
                driver = self.create_driver(driver_name, self.capabilities)
                yield driver
            except exceptions.WebDriverException as e:
                logger.error(f'Failed to initialize {driver_name}: {e}')
            finally:
                self.quit_driver(driver)

    def quit_driver(self, driver):
        try:
            driver.quit()
        except exceptions.WebDriverException as e:
            logger.error(f"Error while quitting WebDriver: {str(e)}")

    @abstractmethod
    def get_flights(self, search_params: SearchParams) -> FlightResults | None:
        ...
