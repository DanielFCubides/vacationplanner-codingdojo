from abc import ABC, abstractmethod

from flights.domain.models import SearchParams


class SearchPublisher(ABC):
    @abstractmethod
    def publish_search_params(self, search_params: SearchParams) -> None:
        """Takes the search params and send it to another system for handle it"""
        ...