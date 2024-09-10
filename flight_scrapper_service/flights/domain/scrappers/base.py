import logging
from abc import ABC, abstractmethod
from typing import Any, Union, Callable

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from flights.domain.scrappers.models import FlightResults
from utils.urls import DynamicURL


logger = logging.getLogger(__name__)


AVAILABLE_DRIVERS = {
    'firefox': FirefoxOptions(),
}


def create_driver(
    driver_name: str,
    capabilities: dict[str, Any],
    selenium_hub: Union[str, None] = "http://selenium-hub:4444"
):
    options = AVAILABLE_DRIVERS.get(driver_name)
    if not options:
        raise ValueError(f'Driver {driver_name} not available')
    for name, value in capabilities.items():
        options.set_capability(name, value)
    options.add_argument('--incognito')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Remote(
        options=options, command_executor=selenium_hub
    )
    return driver


class Scrapper(ABC):

    create_driver: Callable
    capabilities: dict[str, Any]

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
    def get_flights(self, url: DynamicURL) -> list[FlightResults | None]:
        ...
