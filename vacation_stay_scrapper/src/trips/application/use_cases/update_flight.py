"""
Update Flight Use Case

Updates a single flight of an owner's trip by its stable ID, leaving the
rest of the trip (travelers, other flights, accommodations, activities,
budget) untouched.
"""
from ...domain.entities.trip import Trip
from ...domain.entities.flight import Flight
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateFlightUseCase:
    """Use case for updating a single flight within a trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self, trip_id: str, flight: Flight, owner_id: str
    ) -> Trip:
        """
        Replace a single flight on a trip owned by the authenticated user.

        The incoming flight must carry the existing flight's ID so identity
        is preserved (unlike the trip-wide update, which regenerates IDs).

        Raises:
            EntityNotFound: trip missing or not owned by the user
            ChildNotFound: flight not present on the trip
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.replace_flight(flight)

        return await self._repository.save(trip)
