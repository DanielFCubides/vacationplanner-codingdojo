"""
In-Memory Trip Repository

Implementation of trip repository using in-memory storage.
"""
from typing import List, Optional, Dict
from datetime import date

from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository


class InMemoryTripRepository(ITripRepository):
    """
    In-memory implementation of trip repository
    
    Uses a dictionary for storage. Suitable for development and testing.
    """
    
    def __init__(self):
        """Initialize repository with empty storage"""
        self._storage: Dict[int, Trip] = {}
        self._next_id: int = 1
    
    async def save(self, trip: Trip) -> Trip:
        """
        Save trip to memory
        
        Args:
            trip: Trip to save
            
        Returns:
            Saved trip
        """
        # Assign ID if not yet persisted
        if trip.id is None:
            trip.id = self._next_id
            self._next_id += 1

        # Update timestamps
        if trip.created_at is None:
            trip.created_at = date.today()
        trip.updated_at = date.today()

        # Store trip
        self._storage[trip.id] = trip
        return trip
    
    async def find_by_id(self, trip_id: int) -> Optional[Trip]:
        """
        Find trip by ID

        Args:
            trip_id: Trip integer identifier

        Returns:
            Trip if found, None otherwise
        """
        return self._storage.get(trip_id)
    
    async def find_all(self) -> List[Trip]:
        """
        Get all trips
        
        Returns:
            List of all trips
        """
        return list(self._storage.values())
    
    async def delete(self, trip_id: int) -> bool:
        """
        Delete trip from memory

        Args:
            trip_id: Trip integer identifier

        Returns:
            True if deleted, False if not found
        """
        if trip_id in self._storage:
            del self._storage[trip_id]
            return True
        return False

    async def exists(self, trip_id: int) -> bool:
        """
        Check if trip exists

        Args:
            trip_id: Trip integer identifier

        Returns:
            True if exists, False otherwise
        """
        return trip_id in self._storage
    
    def count(self) -> int:
        """Get total number of trips"""
        return len(self._storage)
    
    def clear(self):
        """Clear all trips (useful for testing)"""
        self._storage.clear()
