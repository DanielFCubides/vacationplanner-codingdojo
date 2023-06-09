import dataclasses
from typing import Optional
import requests

from bs4 import BeautifulSoup

from scrappers.base.base import Scrapper, SearchParams, Result


class Bs4Scrapper(Scrapper):

    def make_query(self, search_params: SearchParams) -> Optional[BeautifulSoup]:
        search = self.parse_url(search_params)
        page = requests.get(search)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def clean_result(self, scrapper_object: BeautifulSoup) -> list[Result]:
        """TODO: Need implementation"""


