from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchParams:
    origin: str
    destination: str
    arrivalDate: str
    returnDate: str
    numberOfPersons: int = 1


@dataclass
class FlightResult:
    airline: str
    flightNumber: str
    cost: float
    arrivalDate: str
    returnDate: str


class Scrapper(ABC):

    @abstractmethod
    def make_query(self, search_params: SearchParams) -> list[FlightResult]:
        """Returns a query"""
