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
    Every trip must be associated to an owner (the authenticated user who
    initiated the request). The owner_id is expected to be set on the Trip
    entity before calling execute().
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
            trip: Trip entity to create. Must have owner_id set.

        Returns:
            Created trip with generated ID

        Raises:
            ValueError: If trip has no owner_id (defence-in-depth guard)
        """
        if not trip.owner_id or not trip.owner_id.strip():
            raise ValueError("Cannot create a trip without an owner")

        saved_trip = await self._repository.save(trip)

        return saved_trip
