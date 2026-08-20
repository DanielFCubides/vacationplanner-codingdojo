from datetime import date

from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository
from ...domain.value_objects.trip_status import TripStatus
from ....shared.domain.exceptions import EntityNotFound


class UpdateTripUseCase:
    def __init__(self, repository: ITripRepository):
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

    async def update_status(self, trip_id: str, owner_id: str, new_status: TripStatus) -> Trip:
        """
        Update the status of a trip owned by the authenticated user.

        Verifies the trip exists and belongs to the given owner before
        applying the status update. Uses the repository's update_status method
        to avoid SQLAlchemy identity map conflicts.

        Args:
            trip_id: Trip identifier string
            owner_id: Authenticated user ID (JWT sub claim)
            new_status: New status to apply to the trip

        Returns:
            Updated trip

        Raises:
            EntityNotFound: If trip doesn't exist or is not owned by the user
        """
        trip_id_int = int(trip_id)

        trip = await self._repository.find_by_owner(trip_id_int, owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        updated = await self._repository.update_status(trip_id_int, str(new_status))

        if not updated:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.status = new_status
        trip.updated_at = date.today()

        return trip
