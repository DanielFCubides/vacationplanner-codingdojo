"""
Update Flight Status Use Case (PRD-07)

Updates the status of a single flight within an owner's trip, enforcing the
flight state machine via the Trip aggregate.
"""
from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateFlightStatusUseCase:
    """Use case for updating a flight's status."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self, trip_id: str, flight_id: str, new_status: str, owner_id: str
    ) -> Trip:
        """
        Update a flight's status on a trip owned by the authenticated user.

        A trip that does not exist or is not owned by the user both raise
        EntityNotFound (404), consistent with the other trip use cases and to
        avoid leaking trip existence.

        Raises:
            EntityNotFound: trip missing or not owned by the user
            ChildNotFound: flight not present on the trip
            InvalidStatusTransition: illegal status move
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.update_flight_status(flight_id, new_status)

        return await self._repository.save(trip)
