"""
Flight Entity

Represents a flight booking within a trip.
Matches frontend Flight model in Models.ts
"""
from dataclasses import dataclass
from datetime import datetime

from ..value_objects.airport import Airport
from ..value_objects.money import Money


@dataclass
class Flight:
    """
    Flight entity
    
    Represents a single flight booking with departure and arrival details.
    Matches the frontend Flight interface structure.
    """
    # Required fields (no defaults)
    id: str
    airline: str
    flight_number: str
    departure_airport: Airport
    departure_time: datetime
    arrival_airport: Airport
    arrival_time: datetime
    duration: str  # e.g., "2h 30m"
    price: Money
    
    # Optional fields (with defaults)
    stops: int = 0
    cabin_class: str = "Economy"
    status: str = "pending"  # confirmed, pending, cancelled
    
    def __post_init__(self):
        """Validate flight data"""
        if self.departure_time >= self.arrival_time:
            raise ValueError("Arrival time must be after departure time")
        if self.stops < 0:
            raise ValueError("Number of stops cannot be negative")
        if self.status not in ["confirmed", "pending", "cancelled"]:
            raise ValueError(f"Invalid flight status: {self.status}")
    
    @property
    def departure_city(self) -> str:
        """Get departure city"""
        return self.departure_airport.city
    
    @property
    def arrival_city(self) -> str:
        """Get arrival city"""
        return self.arrival_airport.city
    
    @property
    def route(self) -> str:
        """Get flight route string"""
        return f"{self.departure_airport.code} → {self.arrival_airport.code}"
    
    def is_direct(self) -> bool:
        """Check if flight is direct (no stops)"""
        return self.stops == 0
    
    def is_confirmed(self) -> bool:
        """Check if flight is confirmed"""
        return self.status == "confirmed"
    
    def __str__(self) -> str:
        return f"{self.airline} {self.flight_number} - {self.route}"
