"""
Trip Repository Interface

Defines the contract for trip persistence operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.accommodation import Accommodation
from ..entities.flight import Flight
from ..entities.trip import Trip


class ITripRepository(ABC):
    """
    Trip repository interface
    
    Defines operations for persisting and retrieving trips.
    This is a port in the hexagonal architecture.
    """
    
    @abstractmethod
    async def save(self, trip: Trip) -> Trip:
        """
        Save a trip
        
        Args:
            trip: Trip to save
            
        Returns:
            Saved trip
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, trip_id: int) -> Optional[Trip]:
        """
        Find trip by ID
        
        Args:
            trip_id: Trip identifier
            
        Returns:
            Trip if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_owner(self, trip_id: int, owner_id: str) -> Optional[Trip]:
        """
        Find a trip by ID scoped to a specific owner.

        Args:
            trip_id: Trip identifier
            owner_id: Owner user ID

        Returns:
            Trip if found and owned by the given user, None otherwise
        """
        pass

    @abstractmethod
    async def find_all_by_owner(self, owner_id: str) -> List[Trip]:
        """
        Get all trips belonging to a specific owner.

        Args:
            owner_id: Owner user ID

        Returns:
            List of trips owned by the user
        """
        pass
    
    @abstractmethod
    async def delete(self, trip_id: int) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: Trip identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, trip_id: int) -> bool:
        """
        Check if trip exists

        Args:
            trip_id: Trip identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def update_status(self, trip_id: int, status: str) -> bool:
        """
        Update the status of a trip

        Args:
            trip_id: Trip identifier
            status: New status value

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    async def update_flight(self, flight: Flight, trip_id: int) -> Flight:
        """
        Update a single flight in place by its ID, without touching the
        rest of the trip's collections.

        Args:
            flight: Flight entity with updated fields (id must match an existing flight)
            trip_id: Owning trip's identifier

        Returns:
            The updated Flight entity

        Raises:
            EntityNotFound: If the flight does not exist or does not belong to the trip
        """
        pass

    @abstractmethod
    async def update_accommodation(self, accommodation: Accommodation, trip_id: int) -> Accommodation:
        """
        Update a single accommodation in place by its ID, without touching the
        rest of the trip's collections.

        Args:
            accommodation: Accommodation entity with updated fields (id must match an existing accommodation)
            trip_id: Owning trip's identifier

        Returns:
            The updated Accommodation entity

        Raises:
            EntityNotFound: If the accommodation does not exist or does not belong to the trip
        """
        pass
