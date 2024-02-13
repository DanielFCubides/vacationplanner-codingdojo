import time
from datetime import date
from typing import List

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class AirlineSearch:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get_info_site(self):
        driver = webdriver.Chrome()
        driver.get("http://www.python.org")
        print(driver.title)
        elem = driver.find_element(By.NAME, "q")
        elem.clear()
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        #    print(driver.page_source)
        driver.close()

    def get_flights(self) -> List:
        result = []
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        driver = webdriver.Chrome()
        driver.get("https://www.avianca.com/es/booking/select/?origin1=BOG&destination1=GPS&departure1=2024-06-14&adt1=1&tng1=0&chd1=0&inf1=0&origin2=GPS&destination2=BOG&departure2=2024-06-17&adt2=1&tng2=0&chd2=0&inf2=0&currency=COP&posCode=CO")
        print(driver.title)
        time.sleep(2)
        elem = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        elem.click()
        time.sleep(2)
        elem = driver.find_elements(By.XPATH, "//div[contains(@class,'journey-select_list')]")
        # elem = driver.find_elements(By.XPATH, "//*[@class='journey-select_list']")
        print(elem, len(elem))
        for element in elem:
            city = element.find_element(By.CLASS_NAME, "journey-schedule_station_code").text
            price = element.find_element(By.CLASS_NAME, "price").text
            # result.append(f"city {city}, price {price}")
            result.append({city: price})
            print(city, price)
        driver.close()

        return result

    def get_flights_search(
        self,
        initial_departure_time: date,
        arrival_departure_time: date,
        from_: str,
        to: str,
        passengers: int
    ):
        url = "https://booking.avianca.com/av/booking/avail"
        custom_headers = {
            "user-agent":
                "Mozilla / 5.0(Macintosh;IntelMacOSX10_15_7) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 121.0.0.0Safari / 537.36"
        }
        query_parameters = (
            f"departureDate={initial_departure_time.strftime('%Y-%m-%d')}&tripType=round-trip&from={from_}&to={to}&nbAdults={passengers}"
            f"&nbChildren=0&nbInfants=0&language=ES&returnDate={arrival_departure_time.strftime('%Y-%m-%d')}"
            f"&promoCode=&negoFare=&overrides=%7B%22enableFlexCancelTeaser%22:%22true%22,%22useHPP%22:%22true%22%7D&accessMethod=default&backend=PRD"
        )
        _url = f"{url}?{query_parameters}"
        self.driver.get(_url)
        time.sleep(2)
        print(self.driver.title)
        print(_url)

        return self.driver.title
