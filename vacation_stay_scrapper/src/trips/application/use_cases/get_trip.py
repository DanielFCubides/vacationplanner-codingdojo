"""
Get Trip Use Cases

Handles retrieval of trips.
"""
from typing import List, Optional

from ...domain.entities.trip import Trip
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
    
    async def execute(self, trip_id: str, owner_id: str) -> Trip:
        """
        Get a trip by ID scoped to the authenticated owner.

        Only returns the trip if it belongs to the given owner.
        Raises EntityNotFound if the trip does not exist or belongs
        to a different user — both cases look the same to the caller
        to avoid leaking trip existence to unauthorized users.

        Args:
            trip_id: Trip identifier string
            owner_id: Authenticated user ID (JWT sub claim)

        Returns:
            Trip entity

        Raises:
            EntityNotFound: If trip doesn't exist or is not owned by the user
        """
        trip_id_int = int(trip_id)
        trip = await self._repository.find_by_owner(trip_id_int, owner_id)

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
    
    async def execute(self, owner_id: str) -> List[Trip]:
        """
        Get all trips belonging to the authenticated owner.

        Args:
            owner_id: Authenticated user ID (JWT sub claim)

        Returns:
            List of trips owned by the user
        """
        return await self._repository.find_all_by_owner(owner_id)
