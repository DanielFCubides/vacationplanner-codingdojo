"""
Activity Entity

Represents an activity or event during the trip.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

from ..value_objects.money import Money


@dataclass
class Activity:
    """
    Activity entity
    
    Represents a planned activity during the trip.
    """
    id: str
    name: str
    date: date
    cost: Money
    category: str
    status: str = "pending"
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate activity data"""
        if not self.name or not self.name.strip():
            raise ValueError("Activity name cannot be empty")
        if not self.category or not self.category.strip():
            raise ValueError("Activity category cannot be empty")
    
    def is_booked(self) -> bool:
        """Check if activity is booked"""
        return self.status == "booked"
    
    def __str__(self) -> str:
        return f"{self.name} on {self.date}"
