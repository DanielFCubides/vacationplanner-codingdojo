"""
Trip Aggregate Root

Main entity representing a complete trip with all its components.
Matches frontend Trip model in Models.ts
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from ..value_objects.trip_status import TripStatus
from ..value_objects.budget import Budget
from .flight import Flight
from .traveler import Traveler
from .activity import Activity
from .accommodation import Accommodation


@dataclass
class Trip:
    """
    Trip aggregate root
    
    Central entity that encapsulates all trip-related data and behavior.
    Matches the frontend Trip interface for seamless integration.
    """
    # Core properties
    id: Optional[int]
    name: str
    destination: str
    start_date: date
    end_date: date
    status: TripStatus
    
    # Collections (match frontend model exactly)
    travelers: List[Traveler] = field(default_factory=list)
    flights: List[Flight] = field(default_factory=list)
    accommodations: List[Accommodation] = field(default_factory=list)
    activities: List[Activity] = field(default_factory=list)
    
    # Budget (match frontend budget structure)
    budget: Optional[Budget] = None
    
    # Metadata
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    def __post_init__(self):
        """Validate trip data"""
        if not self.name or not self.name.strip():
            raise ValueError("Trip name cannot be empty")
        if not self.destination or not self.destination.strip():
            raise ValueError("Destination cannot be empty")
        if self.start_date > self.end_date:
            raise ValueError("End date must be after start date")
    
    @property
    def duration_days(self) -> int:
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    # Traveler management
    
    def add_traveler(self, traveler: Traveler):
        """Add a traveler to the trip"""
        if any(t.email == traveler.email for t in self.travelers):
            raise ValueError(f"Traveler {traveler.email} already added")
        self.travelers.append(traveler)
    
    def remove_traveler(self, traveler_id: str):
        """Remove a traveler from the trip"""
        self.travelers = [t for t in self.travelers if t.id != traveler_id]
    
    def get_owner(self) -> Optional[Traveler]:
        """Get the trip owner"""
        return next((t for t in self.travelers if t.is_owner()), None)
    
    # Flight management
    
    def add_flight(self, flight: Flight):
        """Add a flight to the trip"""
        self.flights.append(flight)
    
    def remove_flight(self, flight_id: str):
        """Remove a flight from the trip"""
        self.flights = [f for f in self.flights if f.id != flight_id]
    
    def get_confirmed_flights(self) -> List[Flight]:
        """Get all confirmed flights"""
        return [f for f in self.flights if f.status == "confirmed"]
    
    # Accommodation management
    
    def add_accommodation(self, accommodation: Accommodation):
        """Add an accommodation to the trip"""
        self.accommodations.append(accommodation)
    
    def remove_accommodation(self, accommodation_id: str):
        """Remove an accommodation from the trip"""
        self.accommodations = [
            a for a in self.accommodations if a.id != accommodation_id
        ]
    
    def get_confirmed_accommodations(self) -> List[Accommodation]:
        """Get all confirmed accommodations"""
        return [a for a in self.accommodations if a.is_confirmed()]
    
    @property
    def total_accommodation_cost(self) -> float:
        """Calculate total accommodation cost"""
        return sum(a.total_price.amount for a in self.accommodations)
    
    # Activity management
    
    def add_activity(self, activity: Activity):
        """Add an activity to the trip"""
        self.activities.append(activity)
    
    def remove_activity(self, activity_id: str):
        """Remove an activity from the trip"""
        self.activities = [a for a in self.activities if a.id != activity_id]
    
    def get_booked_activities(self) -> List[Activity]:
        """Get all booked activities"""
        return [a for a in self.activities if a.is_booked()]
    
    # Budget management
    
    def set_budget(self, budget: Budget):
        """Set the trip budget"""
        self.budget = budget
    
    @property
    def total_spent(self) -> float:
        """Calculate total amount spent"""
        if self.budget:
            return self.budget.spent.amount
        return 0.0
    
    @property
    def is_over_budget(self) -> bool:
        """Check if trip is over budget"""
        if not self.budget:
            return False
        return self.budget.is_over_budget
    
    # Status checks
    
    def is_confirmed(self) -> bool:
        """Check if trip is confirmed"""
        return self.status == TripStatus.CONFIRMED
    
    def is_planning(self) -> bool:
        """Check if trip is in planning stage"""
        return self.status == TripStatus.PLANNING
    
    def is_completed(self) -> bool:
        """Check if trip is completed"""
        return self.status == TripStatus.COMPLETED
    
    # Summary methods
    
    @property
    def summary(self) -> dict:
        """Get trip summary"""
        return {
            "name": self.name,
            "destination": self.destination,
            "duration": self.duration_days,
            "travelers": len(self.travelers),
            "flights": len(self.flights),
            "accommodations": len(self.accommodations),
            "activities": len(self.activities),
            "status": self.status.value,
            "budget_spent": self.total_spent if self.budget else 0
        }
    
    def __str__(self) -> str:
        return f"{self.name} to {self.destination} ({self.start_date} - {self.end_date})"
