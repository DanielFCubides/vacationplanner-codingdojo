"""
Stay Repository Interface.

Defines contract for stay data access.
"""
from abc import ABC, abstractmethod
from typing import List

from domain.models.stay import Stay


class StayRepository(ABC):
    """
    Abstract repository for stay search operations.
    
    Provides interface for finding accommodation options.
    """
    
    @abstractmethod
    async def search_by_location(self, location: str, max_guests: int) -> List[Stay]:
        """Search for stays in a location that can accommodate guests."""
        pass
    
    @abstractmethod
    async def find_by_id(self, stay_id) -> Stay:
        """Find stay by ID."""
        pass
