import dataclasses
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclasses.dataclass
class SearchParams:
    origin: str
    destination: str
    arrival_date: datetime
    return_date: Optional[datetime] = ""
    passengers: Optional[int] = 1
    checked_baggage: Optional[int] = 0
    carry_on_baggage: Optional[int] = 0
    currency: Optional[str] = "COP"


@dataclasses.dataclass
class FlightResult:
    price: Decimal
    flight_time: str
    departure_time: str
    landing_time: Optional[str] = None  # only outbound flight


@dataclasses.dataclass
class FlightResults:
    outbound: FlightResult
    return_in: FlightResult
