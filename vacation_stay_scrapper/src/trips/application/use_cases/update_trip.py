"""
Update Trip Use Case

Handles trip updates.
"""
from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateTripUseCase:
    """Use case for updating an existing trip"""
    
    def __init__(self, repository: ITripRepository):
        """
        Initialize use case
        
        Args:
            repository: Trip repository implementation
        """
        self._repository = repository
    
    async def execute(self, trip_id: str, updated_trip: Trip) -> Trip:
        """
        Update a trip
        
        Args:
            trip_id: Trip identifier string
            updated_trip: Trip entity with updates
            
        Returns:
            Updated trip
            
        Raises:
            EntityNotFound: If trip doesn't exist
        """
        trip_id_int = int(trip_id)

        # Check if trip exists
        existing_trip = await self._repository.find_by_id(trip_id_int)
        if existing_trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        # Save updated trip
        return await self._repository.save(updated_trip)
