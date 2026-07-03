"""
Update Accommodation Status Use Case (PRD-07)

Updates the status of a single accommodation within an owner's trip, enforcing
the accommodation state machine via the Trip aggregate.
"""
from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateAccommodationStatusUseCase:
    """Use case for updating an accommodation's status."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self, trip_id: str, accommodation_id: str, new_status: str, owner_id: str
    ) -> Trip:
        """
        Update an accommodation's status on a trip owned by the authenticated user.

        Raises:
            EntityNotFound: trip missing or not owned by the user
            ChildNotFound: accommodation not present on the trip
            InvalidStatusTransition: illegal status move
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.update_accommodation_status(accommodation_id, new_status)

        return await self._repository.save(trip)
