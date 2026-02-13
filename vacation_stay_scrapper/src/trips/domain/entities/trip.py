"""
Trip Aggregate Root

Main entity representing a complete trip with all its components.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from ..value_objects.trip_id import TripId
from ..value_objects.trip_status import TripStatus
from ..value_objects.money import Money
from .flight import Flight
from .traveler import Traveler
from .activity import Activity


@dataclass
class Trip:
    """
    Trip aggregate root
    
    Central entity that encapsulates all trip-related data and behavior.
    """
    id: TripId
    name: str
    destination: str
    start_date: date
    end_date: date
    status: TripStatus
    travelers: List[Traveler] = field(default_factory=list)
    flights: List[Flight] = field(default_factory=list)
    activities: List[Activity] = field(default_factory=list)
    budget: Optional[Money] = None
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
    
    @property
    def total_cost(self) -> Optional[Money]:
        """Calculate total cost from flights and activities"""
        costs = []
        
        # Add flight costs
        for flight in self.flights:
            costs.append(flight.price)
        
        # Add activity costs
        for activity in self.activities:
            costs.append(activity.cost)
        
        if not costs:
            return None
        
        # Sum all costs (assuming same currency)
        total = costs[0]
        for cost in costs[1:]:
            total = total + cost
        
        return total
    
    def add_traveler(self, traveler: Traveler):
        """Add a traveler to the trip"""
        if traveler in self.travelers:
            raise ValueError(f"Traveler {traveler.email} already added")
        self.travelers.append(traveler)
    
    def add_flight(self, flight: Flight):
        """Add a flight to the trip"""
        self.flights.append(flight)
    
    def add_activity(self, activity: Activity):
        """Add an activity to the trip"""
        self.activities.append(activity)
    
    def is_confirmed(self) -> bool:
        """Check if trip is confirmed"""
        return self.status == TripStatus.CONFIRMED
    
    def is_in_progress(self) -> bool:
        """Check if trip is currently happening"""
        return self.status == TripStatus.IN_PROGRESS
    
    def __str__(self) -> str:
        return f"{self.name} to {self.destination} ({self.start_date} - {self.end_date})"
