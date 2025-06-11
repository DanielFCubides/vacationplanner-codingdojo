import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import Callable, Any, Union

from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infrastructure.scrappers.base import Scrapper
from domain.models import FlightResults, FlightResult, Flight, SearchParams
from utils.urls import DynamicURL

logger = logging.getLogger(__name__)


class Avianca(Scrapper):

    driver = None
    name = 'Avianca'
    capabilities: dict[str, Any] = {
        'se:name': name,
        'acceptInsecureCerts': True,
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
                #url = DynamicURL.from_url(self.config.base_url)
                #url.set_query_params(search_params.to_dict())
                breakpoint()
                wait = WebDriverWait(driver, timeout=self.config.timeout)
                logging.debug(f'Trying with driver {driver}')
                driver.get('https://www.avianca.com/')
                driver.add_cookie(
                    {
                        'name': 'avsite',
                        'value': 'ns',
                        'domain': 'avianca.com',
                        'path': '/',
                        'httpOnly': False
                    }
                )
                driver.refresh()
                print(driver.execute_script("return navigator.webdriver"))
                accept_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                accept_button.click()
                get_flights_v2(driver, search_params)

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


def get_flights_v2(driver, params: SearchParams) -> None:
    breakpoint()
    origin_button = WebDriverWait(driver, timeout=10).until(
        EC.element_to_be_clickable((By.ID, "originBtn"))
    )
    origin_button.click()
    input_origin_button = WebDriverWait(driver, timeout=10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "control_field_input"))
    )
    input_origin_button.send_keys(params.origin)

    origin_cities = WebDriverWait(driver, timeout=10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "station-control-list_item_link-code"))
    )
    origin_city = next(
        filter(
            lambda city_: city_.text == params.origin,
            origin_cities
        ), None
    )
    if not origin_city:
        raise ValueError(f'Origin {params.origin} not found')
    origin_city.click()

    # Destination
    destination_button = WebDriverWait(driver, timeout=10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "control_field-inbound"))
    )
    destination_button.click()
    input_destination = WebDriverWait(destination_button, timeout=10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "control_field_input"))
    )
    if not input_destination.get_attribute('placeholder') == 'Hacia':
        raise AttributeError('Destination button not found')

    input_destination.send_keys(params.destination)
    WebDriverWait(driver, timeout=15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "control_options_type--stations"))
    )
    destination_cities = WebDriverWait(driver, timeout=15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "station-control-list_item_link-code"))
    )
    destination_city = next(
        filter(
            lambda des_city_: des_city_.text == params.destination,
            destination_cities
        ), None
    )
    destination_city.click()

    select_dates(driver, params)
    select_passengers(driver, params)

    # Search button
    search_button = driver.find_element(By.ID, "searchButton")
    search_button.click()


def select_dates(driver, params: SearchParams):

    def goto_month(target: datetime.date):
        target_str = target.strftime("%b %Y")  # e.g. "May 2025"
        prev_btn = "date-picker_controls_button--prev"
        next_btn = "date-picker_controls_button--next"
        month_sel = "ngb-dp-month-name"

        while True:
            # read the two visible month headers
            headers = [
                el.text.strip()
                for el in driver.find_elements(By.CLASS_NAME, month_sel)
            ]
            if target_str.upper() in headers:
                return

            # parse the first visible month
            first = headers[0]
            first_date = datetime.strptime(first, "%b %Y").date()

            # decide a direction
            if target.date() < first_date:
                driver.find_element(By.CLASS_NAME, prev_btn).click()
            else:
                driver.find_element(By.CLASS_NAME, next_btn).click()
            time.sleep(0.5)

    def click_day(d: datetime.date):
        # match the aria-label format exactly: "9-5-2025"
        aria = f"{d.day}-{d.month}-{d.year}"
        cell = driver.find_element(
            By.CSS_SELECTOR,
            f"div[role='gridcell'][aria-label='{aria}']"
        )
        cell.click()
        time.sleep(0.3)

    # --- USAGE ---
    # 1) If you need to open the picker, do it here, e.g.:
    # driver.find_element(By.CSS_SELECTOR, ".control_options_title").click()

    # Select departure date
    goto_month(params.departure)
    click_day(params.departure)

    # Select a return date
    goto_month(params.return_date)
    click_day(params.return_date)

def select_passengers(driver, params: SearchParams):
    pax_options = driver.find_elements(By.CLASS_NAME, "pax-control_selector_item")
    pax_choice = None
    for pax in pax_options:
        pax_element = pax.find_element(By.CLASS_NAME, "pax-control_selector_item_label-text")
        if not pax_element.text.strip() == 'Adultos':
            continue
        pax_choice = pax

    add_passenger_button = pax_choice.find_element(By.CLASS_NAME, "plus")
    for _ in range(params.passengers - 1):
        add_passenger_button.click()
        time.sleep(0.5)

    confirm_button = driver.find_element(By.CLASS_NAME, "control_options_selector_action_button")
    confirm_button.click()
