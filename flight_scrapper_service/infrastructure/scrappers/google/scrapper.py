import logging
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional
from dateutil import parser

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from domain.models import SearchParams, FlightResults, Flights, Flight
from infrastructure.scrappers.base import Scrapper, DriverFactory
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)

class GoogleFlightsScrapper(Scrapper):

    driver = None
    name = 'Google'
    capabilities: dict[str, Any] = {
        'se:name': name,
        'acceptInsecureCerts': True,
    }

    def __init__(
        self,
        drivers_factory: DriverFactory
    ) -> None:

        self.drivers_factory = drivers_factory
        self._initialize_config()


    def get_flights(self, search_params: SearchParams) -> FlightResults | None:
        for driver in self._initialize_driver():
            wait = WebDriverWait(driver, timeout=10)
            breakpoint()
            driver.get('https://www.google.com/travel/flights')
            self.select_region(driver)
            origin = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        ".//input[starts-with(@aria-label, '¿Desde dónde')]"
                    )
                )
            )
            origin.click()
            origin_input = wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="i23"]/div[6]/div[2]/div[2]/div[1]/div/input'
                ))
            )
            origin_input.click()
            origin_input.clear()
            origin_input.send_keys(search_params.origin)
            cities = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'P1pPOe'))
            )
            if not cities:
                raise ValueError("No origin cities found")
            city = next(filter(lambda city_: city_.text == search_params.origin, cities), None)
            city.click()

            destination = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    ".//input[starts-with(@aria-label, '¿A dónde')]"
                ))
            )
            destination.click()
            destination_input = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'input[role="combobox"][aria-autocomplete="both"][aria-label^="¿A dónde quieres ir"]'
                ))
            )
            destination_input.click()
            destination_input.clear()
            destination_input.send_keys(search_params.destination)
            destination_city = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'li[data-code="{search_params.destination}"]'))
            )
            if not destination_city:
                raise ValueError("No destination city found")

            destination_city.click()
            self.select_dates(driver, search_params)

            search_button = wait.until(
                EC.presence_of_element_located((
                    By.CLASS_NAME, 'xFFcie'
                ))
            )
            search_button.click()

            flights = self.get_outbound_flights(driver, search_params)
            print(flights)
            if not flights:
                raise ValueError("No flights found")
            return FlightResults(results=flights)
        return None

    def select_region(self, driver):
        wait = WebDriverWait(driver, timeout=10)
        btn = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[jsname='mIwxtb']"))
        )
        btn.click()
        available_regions = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ZxnBY'))
        )
        latin_region = next(
            filter(
                lambda co_: co_.text == 'Español (Latinoamérica)',
                available_regions
            ), None
        )
        if not latin_region:
            raise ValueError("No Latin America region found")
        latin_region.click()
        accept_btn = driver.find_elements(By.CSS_SELECTOR, "button[jsname='tHuhgf']")
        accept_btn[1].click()
        time.sleep(0.5)

    def select_dates(self, driver, search_params: SearchParams):
        wait = WebDriverWait(driver, timeout=10)
        departure_date = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                ".//input[starts-with(@aria-label, 'Salida')]"
            ))
        )
        departure_date.click()

        def click_date(target: datetime.date):
            target_iso = target.strftime('%Y-%m-%d')
            cell = driver.find_element(
                By.CSS_SELECTOR,
                f"div[jsname='Mgvhmd'] div[role='gridcell'][data-iso='{target_iso}']"
            )
            cell.click()
            time.sleep(0.5)

        click_date(search_params.departure)
        click_date(search_params.return_date)

        search_button = driver.find_element(By.CLASS_NAME, 'WXaAwc')
        search_button.click()

    def get_outbound_flights(self, driver, search_params: SearchParams):
        wait = WebDriverWait(driver, timeout=10)
        outbound_flights = len(wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'yR1fYc'))
        ))
        flights = []
        for index in range(outbound_flights):
            try:
                flight = wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'yR1fYc'))
                )[index]
                flight_data = self.extract_flight_data(driver, flight, search_params)
                if not flight_data:
                    continue
                flights.append(flight_data)
            except Exception as e:
                logger.error(f"Error extracting outbound flight data: {e}")
                break
        return flights

    def extract_flight_data(self, driver, flight_element, search_params: SearchParams) -> Optional[Flights]:
        wait = WebDriverWait(driver, timeout=10)

        def _extract_time(time_str: str) -> time:
            time_str = time_str.replace('.', '')
            dt = parser.parse(time_str)
            return dt.time()

        def _parse_duration(duration_str: str) -> timedelta:
            m = re.match(r'(?:(\d+)\s*h)?\s*(?:(\d+)\s*min)?', duration_str)
            if not m:
                raise ValueError(f"Couldn't parse duration from {duration_str!r}")
            _hours = int(m.group(1)) if m.group(1) else 0
            _minutes = int(m.group(2)) if m.group(2) else 0
            return timedelta(hours=_hours, minutes=_minutes)

        def _extract_data(flight, outbound: bool ) -> Optional[Flight]:
            hours = flight.find_element(By.CLASS_NAME, 'mv1WYe')
            _departure_time = hours.find_element(
                By.XPATH, ".//span[contains(@aria-label, 'Hora de salida')]"
            ).text
            departure_time = _extract_time(_departure_time)

            _landing_time = hours.find_element(
                By.XPATH, ".//span[contains(@aria-label, 'Hora de llegada')]"
            ).text
            landing_time = _extract_time(_landing_time)

            time_duration = flight.find_element(By.CLASS_NAME, 'Ak5kof').text.split('\n')[0]
            flight_time = _parse_duration(time_duration)

            price = flight.find_element(
                    By.CLASS_NAME, 'U3gSDe'
            ).find_element(By.CLASS_NAME, 'YMlIz').text.split(' ')[1]

            return Flight(
                date=search_params.departure if outbound else search_params.return_date,
                departure_time=departure_time,
                landing_time=landing_time,
                price=Decimal(re.sub(r'[^\d.]', '', price)),
                flight_time=flight_time,
            )

        try:
            flight = _extract_data(
                flight_element.find_element(By.CLASS_NAME, 'KhL0De'),
                outbound=True
            )

            flight_element.click()
            time.sleep(0.5)

            flights = Flights(
                outbound_flight=flight,
                return_flights=[]
            )
            flights.return_flights.extend([
                _extract_data(return_flight, outbound=False)
                for return_flight in wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'KhL0De'))
                )
            ])

            driver.back()
            time.sleep(1)
            return flights
        except Exception as e:
            driver.back()
            logger.error(f"Error extracting flight data: {e}")
            return None
