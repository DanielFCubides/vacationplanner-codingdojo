import requests
from bs4 import BeautifulSoup

from vacation_stay_scrapper.scrappers.scrapper import Scrapper


class VivaAirScrapper(Scrapper):

    BASE_URL = 'https://www.kayak.com.co/'
    URL = f'{BASE_URL}/flights/BOG-SMR/2023-04-08/2023-04-15/2adults?sort=bestflight_a'

    def make_query(self, search_params: dict) -> list[dict]:
        response = requests.get(self.URL)
        scrapper = BeautifulSoup(response.content, 'html.parser')
        page = scrapper.find(name='body')
        print(page.prettify())
        pass

