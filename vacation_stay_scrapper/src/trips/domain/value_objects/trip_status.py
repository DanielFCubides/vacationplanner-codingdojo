"""
Trip Status Value Object

Represents the current status of a trip.
"""
from enum import Enum


class TripStatus(str, Enum):
    """
    Trip status enumeration
    
    Represents the various states a trip can be in.
    """
    PLANNING = "planning"        # Trip is being planned
    CONFIRMED = "confirmed"      # All bookings confirmed
    IN_PROGRESS = "in_progress"  # Trip is currently happening
    COMPLETED = "completed"      # Trip has ended
    CANCELLED = "cancelled"      # Trip was cancelled
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, status: str) -> "TripStatus":
        """Create TripStatus from string"""
        return cls(status.lower())
