import logging
from decimal import Decimal
from typing import Callable, Any, Union

from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from flights.domain.scrappers.base import Scrapper
from flights.domain.models import FlightResults, FlightResult, Flight, SearchParams
from utils.urls import DynamicURL

logger = logging.getLogger(__name__)


class AviancaScrapper(Scrapper):

    driver = None
    name = 'Avianca'
    capabilities: dict[str, Any] = {
        'se:name': name, 'acceptInsecureCerts': True
    }

    def __init__(
        self,
        create_driver: Callable[[str, dict, Union[str, None]], Any]
    ) -> None:
        self.create_driver = create_driver
        self._initialize_config()

    def get_flights(self, search_params: SearchParams) -> FlightResults | list[None]:
        for driver in self._initialize_driver():
            try:
                url = DynamicURL.from_url(self.config.base_url)
                url.set_query_params(search_params.to_dict())
                wait = WebDriverWait(driver, timeout=self.config.timeout)
                logging.debug(f'Trying with driver {driver}')
                driver.get(str(url))
                accept_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                accept_button.click()
                _outbound_flights = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[contains(@class, 'journey-select_list_item')]")
                    )
                )
                if not _outbound_flights:
                    return FlightResults(results=[])

                outbound_flights = self._process_flights(_outbound_flights)
                # take first flight as an example for return flights
                flight = _outbound_flights[0]
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element((By.CLASS_NAME, "page-loader"))
                )
                collapsable_fare_button = WebDriverWait(
                    flight, timeout=self.config.timeout
                ).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'journey_price_fare-select_label')
                    )
                )
                collapsable_fare_button.click()
                fare = WebDriverWait(flight, timeout=self.config.timeout).until(
                    EC.presence_of_element_located(
                        (By.XPATH, ".//div[@class='journey_fares_list_item ng-tns-c12-3 ng-star-inserted']")
                    )
                )
                button = fare.find_element(By.CLASS_NAME, 'fare_button')
                driver.execute_script("arguments[0].click()", button)  # could not be scrolled into viewpoint
                _, *_return_flights = WebDriverWait(driver, timeout=60).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[contains(@class, 'journey-select_list_item')]")
                    )
                )
                if not _return_flights:
                    return FlightResults(results=[])

                return_flights = self._process_flights(_return_flights)
                results = [
                    FlightResult(
                        outbound=outbound, return_in=inbound
                    )
                    for outbound, inbound in zip(outbound_flights, return_flights)
                ]
                return FlightResults(results=results)
            except exceptions.TimeoutException as e:
                logger.exception(str(e))
            except exceptions.WebDriverException as e:
                logger.exception(str(e))

        return FlightResults(results=[])

    def _process_flights(self, flights: list[WebElement],) -> list[Flight]:
        results = [
            Flight(
                price=Decimal(
                    flight.find_element(
                        By.XPATH, ".//span[@class='price text-space-gap']"
                    ).get_attribute('textContent').strip()
                ),
                flight_time=flight.find_element(
                    By.XPATH, ".//div[@class='journey-schedule_duration_time']"
                ).get_attribute('textContent').strip(),
                departure_time=flight.find_element(
                    By.XPATH, ".//div[contains(@class, 'journey-schedule_time-departure')]"
                ).get_attribute('textContent').strip(),
                landing_time=flight.find_element(
                    By.XPATH, ".//div[contains(@class, 'journey-schedule_time-return')]"
                ).get_attribute('textContent').strip(),
            )
            for flight in flights
        ]
        return results
