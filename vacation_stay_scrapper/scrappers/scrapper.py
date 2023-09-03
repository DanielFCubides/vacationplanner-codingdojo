from abc import ABC, abstractmethod


class Scrapper(ABC):
    @abstractmethod
    def make_query(self, search_params: dict) -> list[dict]:
        """Returns a query"""

