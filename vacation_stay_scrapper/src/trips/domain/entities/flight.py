"""
Flight Entity

Represents a flight booking within a trip.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects.airport import Airport
from ..value_objects.money import Money


@dataclass
class Flight:
    """
    Flight entity
    
    Represents a single flight booking with departure and arrival details.
    """
    id: str
    airline: str
    flight_number: str
    departure_airport: Airport
    arrival_airport: Airport
    departure_time: datetime
    arrival_time: datetime
    price: Money
    cabin_class: str = "Economy"
    status: str = "pending"
    duration: Optional[str] = None
    stops: int = 0
    
    def __post_init__(self):
        """Validate flight data"""
        if self.departure_time >= self.arrival_time:
            raise ValueError("Arrival time must be after departure time")
        if self.stops < 0:
            raise ValueError("Number of stops cannot be negative")
    
    @property
    def route(self) -> str:
        """Get flight route string"""
        return f"{self.departure_airport.code} → {self.arrival_airport.code}"
    
    def is_direct(self) -> bool:
        """Check if flight is direct (no stops)"""
        return self.stops == 0
    
    def __str__(self) -> str:
        return f"{self.airline} {self.flight_number} - {self.route}"
