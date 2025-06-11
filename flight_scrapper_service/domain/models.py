from dataclasses import dataclass
from datetime import datetime, timedelta, time
from decimal import Decimal
from functools import cached_property
from typing import Optional, ClassVar

from typing_extensions import Self


@dataclass
class SearchParams:
    origin: str
    destination: str
    departure: datetime
    return_date: Optional[datetime] = ""
    passengers: Optional[int] = 1
    checked_baggage: Optional[int] = 0
    carry_on_baggage: Optional[int] = 0
    currency: Optional[str] = "COP"

    def to_dict(self) -> dict:
        return {
            'origin': self.origin,
            'destination': self.destination,
            'departure': self.departure.strftime('%Y-%m-%d::%H:%M:%S'),
            'return_date': self.return_date.strftime('%Y-%m-%d::%H:%M:%S'),
            'passengers': self.passengers,
            'checked_baggage': self.checked_baggage,
            'carry_on_baggage': self.carry_on_baggage,
            'currency': self.currency
        }


@dataclass
class Flight:
    date: datetime
    departure_time: time
    landing_time: time
    price: Decimal
    flight_time: timedelta

    _DT_FMT: ClassVar[str] = "%Y-%m-%d"
    _T_FMT: ClassVar[str] = "%H:%M"

    def to_dict(self) -> dict[str, str]:
        return {
            "date": self.date.strftime(self._DT_FMT),
            "departure_time": self.departure_time.strftime(self._T_FMT),
            "landing_time": self.landing_time.strftime(self._T_FMT),
            "price": str(self.price),
            "flight_time": str(self.flight_time.total_seconds()),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls(
            date=datetime.strptime(data["date"], cls._DT_FMT),
            departure_time=datetime.strptime(data["departure_time"], cls._T_FMT).time(),
            landing_time=datetime.strptime(data["landing_time"], cls._T_FMT).time(),
            price=Decimal(data["price"]),
            flight_time=timedelta(seconds=float(data["flight_time"])),
        )


@dataclass
class Flights:
    outbound_flight: Flight
    return_flights: Optional[list[Flight]]

    _DT_FMT: ClassVar[str] = "%Y-%m-%d"
    _T_FMT: ClassVar[str] = "%H:%M"

    def to_dict(self) -> dict:
        return {
            "outbound": self.outbound_flight.to_dict(),
            "return_flights": [
                rf.to_dict()
                for rf in self.return_flights or []
            ],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        ob = d["outbound"]
        of = Flight.from_dict(ob)
        rf_list = d["return_flights"]
        rf_objs = [
            Flight.from_dict(rf) for rf in rf_list
        ]
        return cls(
            outbound_flight=of,
            return_flights=rf_objs or None
        )

    @cached_property
    def flatten_results(self) -> list[dict[str, dict[str, str]]]:
        outbound = self.outbound_flight.to_dict()
        if not self.return_flights:
            return [{"outbound": outbound, "return_in": []}]
        flatten_results = []
        for rf in self.return_flights:
            return_flight = rf.to_dict()
            flatten_results.append({
                "outbound": outbound,
                "return_in": return_flight
            })
        return flatten_results

    @classmethod
    def unflatten_results(cls, flat: list[dict[str, dict[str, str]]]) -> Self:
        grouped: dict = {}
        for entry in flat:
            ob_data = entry["outbound"]
            rf_data = entry["return_in"]
            key = 'outbound'
            if key not in grouped:
                grouped[key] = Flight.from_dict(ob_data)
                grouped["returns"] = []

            if rf_data:
                grouped["returns"].append(Flight.from_dict(rf_data))

        results = cls(
            outbound_flight=grouped["outbound"],
            return_flights=grouped["returns"]
        )
        return results


@dataclass
class FlightResult:
    pass


@dataclass
class FlightResults:
    results: Optional[list[Flights]] = None
