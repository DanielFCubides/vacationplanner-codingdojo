"""
Update Flight Use Case

Updates a single flight on a trip by its flight id, preserving the flight's
identity and leaving other trip collections untouched.
"""
from typing import Callable

from ...domain.entities.flight import Flight
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateFlightUseCase:
    """Use case for updating a single flight on a trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self,
        trip_id: str,
        flight_id: str,
        apply_update: Callable[[Flight], Flight],
        owner_id: str,
    ) -> Flight:
        """
        Update a single flight on a trip scoped to the authenticated owner.

        Args:
            trip_id: Trip identifier string
            flight_id: Flight identifier
            apply_update: Callable that mutates the flight with the requested
                changes and returns it (preserves the flight id)
            owner_id: Authenticated user ID (JWT sub claim)

        Returns:
            The updated Flight

        Raises:
            EntityNotFound: If the trip is missing/not owned by the user, or
                the flight does not exist on the trip
        """
        trip_id_int = int(trip_id)

        trip = await self._repository.find_by_owner(trip_id_int, owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        flight = next((f for f in trip.flights if f.id == flight_id), None)
        if flight is None:
            raise EntityNotFound(entity_type="Flight", entity_id=flight_id)

        updated_flight = apply_update(flight)

        return await self._repository.update_flight(updated_flight, trip_id_int)
