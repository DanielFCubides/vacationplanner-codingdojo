import time
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
