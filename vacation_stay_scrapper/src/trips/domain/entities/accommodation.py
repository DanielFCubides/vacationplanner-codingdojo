"""
Accommodation Entity

Represents accommodation/lodging during the trip.
"""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..value_objects.money import Money


@dataclass
class Accommodation:
    """
    Accommodation entity
    
    Represents a place to stay during the trip (hotel, airbnb, etc.).
    """
    # Required fields (no defaults)
    id: str
    name: str
    type: str  # hotel, airbnb, hostel, resort
    check_in: date
    check_out: date
    price_per_night: Money
    total_price: Money
    rating: float
    amenities: List[str]
    
    # Optional fields (with defaults)
    status: str = "pending"  # confirmed, pending, cancelled
    image: Optional[str] = None
    
    def __post_init__(self):
        """Validate accommodation data"""
        if not self.name or not self.name.strip():
            raise ValueError("Accommodation name cannot be empty")
        if self.type not in ["hotel", "airbnb", "hostel", "resort"]:
            raise ValueError(f"Invalid accommodation type: {self.type}")
        if self.check_in >= self.check_out:
            raise ValueError("Check-out date must be after check-in date")
        if self.rating < 0 or self.rating > 5:
            raise ValueError("Rating must be between 0 and 5")
        if self.status not in ["confirmed", "pending", "cancelled"]:
            raise ValueError(f"Invalid status: {self.status}")
    
    @property
    def nights(self) -> int:
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days
    
    def is_confirmed(self) -> bool:
        """Check if accommodation is confirmed"""
        return self.status == "confirmed"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type}) - {self.nights} nights"
