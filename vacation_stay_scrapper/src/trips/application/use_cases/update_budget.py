"""
Update Budget Use Case

Replaces the Budget total and Budget categories of an owner's existing
trip. Spent is re-derived by the aggregate, never taken from the caller.
"""
from typing import List

from ...domain.entities.trip import Trip
from ...domain.repositories.trip_repository import ITripRepository
from ...domain.value_objects.budget import BudgetCategory
from ...domain.value_objects.money import Money
from ....shared.domain.exceptions import EntityNotFound


class UpdateBudgetUseCase:
    """Use case for editing the budget of an existing trip."""

    def __init__(self, repository: ITripRepository):
        self._repository = repository

    async def execute(
        self,
        trip_id: str,
        total: Money,
        categories: List[BudgetCategory],
        owner_id: str,
    ) -> Trip:
        """
        Set the budget of a trip owned by the authenticated user.

        Raises:
            EntityNotFound: trip missing or not owned by the user
            ValueError: blank or duplicate category name
        """
        trip = await self._repository.find_by_owner(int(trip_id), owner_id)
        if trip is None:
            raise EntityNotFound(entity_type="Trip", entity_id=trip_id)

        trip.update_budget(total, categories)

        return await self._repository.save(trip)
