"""
Create Trip Use Case

Handles the creation of new trips.
"""
from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository


class CreateTripUseCase:
    """
    Use case for creating a new trip
    
    Orchestrates the creation process using the repository.
    """
    
    def __init__(self, repository: ITripRepository):
        """
        Initialize use case
        
        Args:
            repository: Trip repository implementation
        """
        self._repository = repository
    
    async def execute(self, trip: Trip) -> Trip:
        """
        Create a new trip
        
        Args:
            trip: Trip entity to create
            
        Returns:
            Created trip with generated ID
        """
        # Save trip to repository
        saved_trip = await self._repository.save(trip)
        
        return saved_trip
