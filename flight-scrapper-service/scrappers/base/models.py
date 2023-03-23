import dataclasses
from datetime import datetime
from typing import Optional

from scrappers.base import base


@dataclasses.dataclass
class SearchParams(base.SearchParams):
    origin: str
    destination: str
    arrival_date: datetime
    return_date: Optional[datetime] = None
    number_of_persons: Optional[int] = 1
    checked_baggages: Optional[int] = 0
    carry_on_baggages: Optional[int] = 0


@dataclasses.dataclass
class Result(base.Result):
    airline: str
    flight_number: str
    cost: float
    arrival_date: datetime
    return_date: Optional[datetime] = None



