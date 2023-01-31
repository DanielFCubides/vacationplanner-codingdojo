from abc import ABC, abstractmethod

from vacation_stay_scrapper.models import Provider


class Scrapper(ABC):

    provider: Provider

    @abstractmethod
    def make_query(self, search_params: dict) -> list[dict]:
        """Returns a query"""

