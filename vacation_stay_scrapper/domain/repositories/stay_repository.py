"""
Stay Repository Interface.

Defines contract for stay data access.
"""
from abc import ABC, abstractmethod
from typing import List

from domain.models.stay import Stay, StaySearchCriteria


class StayRepository(ABC):
    """
    Abstract repository for stay search operations.
    
    Provides interface for finding accommodation options.
    """
    
    @abstractmethod
    async def search(self, criteria: StaySearchCriteria) -> List[Stay]:
        """
        Search for stays based on criteria.
        
        Args:
            criteria: Search criteria for stays
            
        Returns:
            List of stays matching the criteria
        """
        pass
    
    @abstractmethod
    async def find_by_location(self, location: str, limit: int = 20) -> List[Stay]:
        """
        Find stays by location.
        
        Args:
            location: Location to search in
            limit: Maximum number of results
            
        Returns:
            List of stays in the location
        """
        pass
    
    @abstractmethod
    async def get_featured_stays(self, limit: int = 10) -> List[Stay]:
        """
        Get featured/popular stays.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of featured stays
        """
        pass
