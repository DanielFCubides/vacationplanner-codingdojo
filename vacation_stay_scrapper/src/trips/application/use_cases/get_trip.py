"""
Get Trip Use Cases

Handles retrieval of trips.
"""
from typing import List, Optional

from ...domain.entities.trip import Trip
from ...domain.value_objects.trip_id import TripId
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class GetTripUseCase:
    """Use case for getting a single trip by ID"""
    
    def __init__(self, repository: ITripRepository):
        """
        Initialize use case
        
        Args:
            repository: Trip repository implementation
        """
        self._repository = repository
    
    async def execute(self, trip_id: str) -> Trip:
        """
        Get trip by ID
        
        Args:
            trip_id: Trip identifier string
            
        Returns:
            Trip entity
            
        Raises:
            EntityNotFound: If trip doesn't exist
        """
        trip_id_obj = TripId.from_string(trip_id)
        trip = await self._repository.find_by_id(trip_id_obj)
        
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)
        
        return trip


class GetAllTripsUseCase:
    """Use case for getting all trips"""
    
    def __init__(self, repository: ITripRepository):
        """
        Initialize use case
        
        Args:
            repository: Trip repository implementation
        """
        self._repository = repository
    
    async def execute(self) -> List[Trip]:
        """
        Get all trips
        
        Returns:
            List of all trips
        """
        return await self._repository.find_all()
