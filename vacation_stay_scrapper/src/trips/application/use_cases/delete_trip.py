"""
Delete Trip Use Case

Handles trip deletion.
"""
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class DeleteTripUseCase:
    """Use case for deleting a trip"""
    
    def __init__(self, repository: ITripRepository):
        """
        Initialize use case
        
        Args:
            repository: Trip repository implementation
        """
        self._repository = repository
    
    async def execute(self, trip_id: str) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: Trip identifier string
            
        Returns:
            True if deleted successfully
            
        Raises:
            EntityNotFound: If trip doesn't exist
        """
        trip_id_int = int(trip_id)

        # Check if trip exists
        exists = await self._repository.exists(trip_id_int)
        if not exists:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        # Delete trip
        return await self._repository.delete(trip_id_int)
