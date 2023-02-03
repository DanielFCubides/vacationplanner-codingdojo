from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchParams:
    origin: str
    destination: str
    arrival_date: str
    return_date: str
    number_of_persons: int = 1
    checked_baggages: int = 0
    carry_on_baggages: int = 0


@dataclass
class FlightResult:
    airline: str
    flight_number: str
    cost: float
    arrival_date: str
    return_date: str


class Scrapper(ABC):

    @abstractmethod
    def make_query(self, search_params: SearchParams) -> list[FlightResult]:
        """Returns a query"""
