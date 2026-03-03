"""
Stay Repository Interface.

Defines the contract for stay data access and search operations.
"""
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.models.stay import Stay


class StayRepository(ABC):
    """
    Abstract repository for stay search and retrieval operations.
    
    Provides interface for finding accommodation options.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def find_by_id(self, stay_id: UUID) -> Stay:
        """
        Find a stay by its ID.
        
        Args:
            stay_id: The stay identifier
            
        Returns:
            The stay if found
            
        Raises:
            StayNotFoundError: If stay is not found
        """
        pass
