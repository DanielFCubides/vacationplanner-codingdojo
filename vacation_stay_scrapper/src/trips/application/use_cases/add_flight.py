"""
Add Flight Use Case

Adds a single flight to an owner's existing trip, leaving the rest of the
trip (travelers, other flights, accommodations, activities) untouched.
"""
from ...domain.entities.trip import Trip
from ...domain.entities.flight import Flight
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class AddFlightUseCase:
    """Use case for adding a flight to an existing trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self, trip_id: str, flight: Flight, owner_id: str
    ) -> Trip:
        """
        Append a flight to a trip owned by the authenticated user.

        Raises:
            EntityNotFound: trip missing or not owned by the user
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.add_flight(flight)

        return await self._repository.save(trip)
