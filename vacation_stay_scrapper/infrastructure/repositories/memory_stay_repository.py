"""
In-memory stay repository implementation.

Fast storage for stay data, useful for caching and testing.
"""
from typing import Dict, List
from uuid import UUID

from domain.models.stay import Stay
from domain.repositories.stay_repository import StayRepository


class MemoryStayRepository(StayRepository):
    """
    In-memory implementation of stay repository.
    
    Stores stays in memory using a dictionary.
    Suitable for caching frequently accessed stays.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._stays: Dict[UUID, Stay] = {}
    
    async def search_by_location(
        self, 
        location: str, 
        max_guests: int,
        limit: int = 20
    ) -> List[Stay]:
        """
        Search for stays in a specific location.
        
        Args:
            location: The location to search in
            max_guests: Maximum number of guests to accommodate
            limit: Maximum number of results to return
            
        Returns:
            List of stays matching the criteria
        """
        matching_stays = []
        
        for stay in self._stays.values():
            # Simple location matching (case-insensitive contains)
            if (location.lower() in stay.location.lower() and 
                stay.can_accommodate(max_guests)):
                matching_stays.append(stay)
                
                # Respect the limit
                if len(matching_stays) >= limit:
                    break
        
        return matching_stays
    
    async def find_by_id(self, stay_id: UUID) -> Stay:
        """
        Find a stay by its ID.
        
        Args:
            stay_id: The stay identifier
            
        Returns:
            The stay if found
            
        Raises:
            KeyError: If stay is not found
        """
        if stay_id not in self._stays:
            raise KeyError(f"Stay with ID {stay_id} not found")
        return self._stays[stay_id]
    
    # Additional utility methods
    
    async def add_stay(self, stay: Stay) -> Stay:
        """
        Add a stay to the repository.
        
        Args:
            stay: The stay to add
            
        Returns:
            The added stay
        """
        self._stays[stay.id] = stay
        return stay
    
    async def find_all(self) -> List[Stay]:
        """Get all stays."""
        return list(self._stays.values())
    
    async def count(self) -> int:
        """Get the total count of stays."""
        return len(self._stays)
    
    async def clear(self) -> None:
        """Clear all stays (useful for testing)."""
        self._stays.clear()
    
    async def search_by_type(self, stay_type, limit: int = 20) -> List[Stay]:
        """
        Search for stays by type.
        
        Args:
            stay_type: The type of stay to search for
            limit: Maximum number of results to return
            
        Returns:
            List of stays of the specified type
        """
        matching_stays = []
        
        for stay in self._stays.values():
            if stay.stay_type == stay_type:
                matching_stays.append(stay)
                if len(matching_stays) >= limit:
                    break
        
        return matching_stays
