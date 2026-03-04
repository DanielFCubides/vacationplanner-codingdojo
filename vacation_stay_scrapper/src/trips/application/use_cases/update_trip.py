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

    async def execute(self, trip_id: str, updated_trip: Trip, owner_id: str) -> Trip:
        """
        Update a trip owned by the authenticated user.

        Verifies the trip exists and belongs to the given owner before
        applying the update. Both "not found" and "wrong owner" raise
        EntityNotFound to avoid leaking trip existence to other users.

        Args:
            trip_id: Trip identifier string
            updated_trip: Trip entity with updates applied
            owner_id: Authenticated user ID (JWT sub claim)

        Returns:
            Updated trip

        Raises:
            EntityNotFound: If trip doesn't exist or is not owned by the user
        """
        trip_id_int = int(trip_id)

        existing_trip = await self._repository.find_by_owner(trip_id_int, owner_id)
        if existing_trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        return await self._repository.save(updated_trip)
