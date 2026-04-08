import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from selenium import webdriver
from selenium.common import exceptions, WebDriverException
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from domain.models import FlightResults, SearchParams
from constants import config

logger = logging.getLogger(__name__)


class DriverFactory:

    DRIVER_OPTIONS = {
        'chrome': ChromeOptions,
        'firefox': FirefoxOptions,
    }

    @classmethod
    def create_driver(
        cls,
        driver: str,
        hub_url: Optional[str] = None,
        capabilities: Optional[dict] = None,
        options: Optional[dict] = None
    ) -> webdriver.Remote:
        """
        Create a remote WebDriver instance for Selenium Grid.

        Args:
            driver (str): Driver type ('chrome', 'firefox', 'edge', 'safari')
            hub_url (str): Selenium Grid hub URL
            capabilities (dict, optional): Additional capabilities to merge with default ones
            options (dict, optional): Browser-specific options as key-value pairs

        Returns:
            webdriver.Remote: Configured remote WebDriver instance

        Raises:
            ValueError: If an unsupported driver type is specified
            WebDriverException: If driver creation fails
        """

        driver = driver.lower()
        hub_url = hub_url or f'{config["Selenium"]["host"]}:{config["Selenium"]["port"]}/wd/hub'
        if driver not in cls.DRIVER_OPTIONS:
            raise ValueError(f"Unsupported driver: {driver}. Supported drivers: {list(cls.DRIVER_OPTIONS.keys())}")

        try:
            options = cls.DRIVER_OPTIONS[driver]()
            driver_options = cls._create_options(driver, options)

            # If no options were created, create a basic options object
            if not driver_options:
                options_class = cls.DRIVER_OPTIONS[driver]
                driver_options = options_class

            logger.info(f"Creating remote {driver} driver with hub URL: {hub_url}")

            return webdriver.Remote(
                command_executor=hub_url,
                options=driver_options
            )

        except Exception as e:
            logger.error(f"Failed to create {driver} driver: {str(e)}")
            raise WebDriverException(f"Failed to create {driver} driver: {str(e)}")

    @staticmethod
    def _create_options(
        driver: str, options: Union[ChromeOptions, FirefoxOptions]
    ) -> ArgOptions:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        if driver == 'chrome':
            return options
        elif driver == 'firefox':
            options.set_preference("useAutomationExtension", False)
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("security.cert_pinning.enforcement_level", 0)
            options.set_preference("security.enterprise_roots.enabled", True)
            return options
        else:
            raise ValueError(f"Unsupported driver: {driver}")



class Scrapper(ABC):

    driver: webdriver.Remote
    drivers_factory: DriverFactory
    capabilities: dict[str, Any]
    name: str

    def _initialize_config(self):
        assert self.name, 'Scrapper class needs name attribute'
        config_key = f'Scrappers.{self.name}'
        if config_key not in config:
            raise ValueError(f"Configuration for {self.name} not found in config file")
        self.config = type(
            'Config',
            (),
            {**config[config_key]}
        )
        self.config()

    def _initialize_driver(self, driver_name: str = None):
        driver_name = driver_name or config["Default"]["scrapper_driver"]
        driver = None
        try:
            driver = self.drivers_factory.create_driver(driver_name)
            if driver_name == 'chrome':
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
            yield driver
        except exceptions.WebDriverException as e:
            logger.error(f'Failed to initialize {driver_name}: {e}')
            raise
        finally:
            if driver:
                self.quit_driver(driver)

    def quit_driver(self, driver):
        try:
            driver.quit()
        except exceptions.WebDriverException as e:
            logger.error(f"Error while quitting WebDriver: {str(e)}")

    @abstractmethod
    def get_flights(self, search_params: SearchParams) -> FlightResults | None:
        ...
