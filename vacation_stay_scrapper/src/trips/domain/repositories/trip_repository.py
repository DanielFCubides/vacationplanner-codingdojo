"""
Trip Repository Interface

Defines the contract for trip persistence operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

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
    async def find_all(self) -> List[Trip]:
        """
        Get all trips
        
        Returns:
            List of all trips
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
