from dataclasses import dataclass, field, fields
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Optional, Any
from uuid import UUID


@dataclass
class SearchParams:
    origin: str
    destination: str
    arrival_date: datetime
    return_date: Optional[datetime] = ""
    passengers: Optional[int] = 1
    checked_baggage: Optional[int] = 0
    carry_on_baggage: Optional[int] = 0
    currency: Optional[str] = "COP"

    def to_dict(self) -> dict:
        return {
            'origin': self.origin,
            'destination': self.destination,
            'arrival_date': self.arrival_date,
            'return_date': self.return_date,
            'passengers': self.passengers,
            'checked_baggage': self.checked_baggage,
            'carry_on_baggage': self.carry_on_baggage,
            'currency': self.currency
        }


@dataclass
class Flight:
    price: Decimal
    flight_time: str
    departure_time: str
    landing_time: Optional[str] = None  # only outbound flight

    def to_dict(self) -> dict[str, Any]:
        def cast_value(value: Any) -> Any:
            if isinstance(value, Decimal):
                return float(value)
            # Add another cast convertion here if needed
            return value

        return {
            field_.name: cast_value(getattr(self, field_.name))
            for field_ in fields(self)
        }


@dataclass
class FlightResult:
    outbound: Flight
    return_in: Flight
    id_: Optional[UUID] = field(default_factory=UUID)

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': str(self.id_),
            'outbound': self.outbound.to_dict(),
            'return_in': self.return_in.to_dict()
        }


@dataclass
class FlightResults:
    results: Optional[list[FlightResult]] = None
    id_: Optional[UUID] = field(default_factory=UUID)
    search_params: Optional[SearchParams] = None

    @cached_property
    def total(self) -> int:
        return len(self.results) if self.results else 0
