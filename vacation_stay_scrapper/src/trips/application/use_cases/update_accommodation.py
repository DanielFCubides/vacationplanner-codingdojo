"""
Update Accommodation Use Case

Updates a single accommodation on a trip by its accommodation id, preserving the accommodation's
identity and leaving other trip collections untouched.
"""
from typing import Callable

from ...domain.entities.accommodation import Accommodation
from ...domain.repositories.trip_repository import ITripRepository
from ....shared.domain.exceptions import EntityNotFound


class UpdateAccommodationUseCase:
    """Use case for updating a single accommodation on a trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self,
        trip_id: str,
        accommodation_id: str,
        apply_update: Callable[[Accommodation], Accommodation],
        owner_id: str,
    ) -> Accommodation:
        """
        Update a single accommodation on a trip scoped to the authenticated owner.

        Args:
            trip_id: Trip identifier string
            accommodation_id: Accommodation identifier
            apply_update: Callable that mutates the accommodation with the requested
                changes and returns it (preserves the accommodation id)
            owner_id: Authenticated user ID (JWT sub claim)

        Returns:
            The updated Accommodation

        Raises:
            EntityNotFound: If the trip is missing/not owned by the user, or
                the accommodation does not exist on the trip
        """
        trip_id_int = int(trip_id)

        trip = await self._repository.find_by_owner(trip_id_int, owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        accommodation = next((a for a in trip.accommodations if a.id == accommodation_id), None)
        if accommodation is None:
            raise EntityNotFound(entity_type="Accommodation", entity_id=accommodation_id)

        updated_accommodation = apply_update(accommodation)

        return await self._repository.update_accommodation(updated_accommodation, trip_id_int)