"""
Add Activity Use Case

Adds a single activity to an owner's existing trip, leaving the rest of the
trip (travelers, flights, accommodations, other activities) untouched.
"""
from ...domain.entities.trip import Trip
from ...domain.entities.activity import Activity
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class AddActivityUseCase:
    """Use case for adding an activity to an existing trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self, trip_id: str, activity: Activity, owner_id: str
    ) -> Trip:
        """
        Append an activity to a trip owned by the authenticated user.

        Raises:
            EntityNotFound: trip missing or not owned by the user
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.add_activity(activity)

        return await self._repository.save(trip)
